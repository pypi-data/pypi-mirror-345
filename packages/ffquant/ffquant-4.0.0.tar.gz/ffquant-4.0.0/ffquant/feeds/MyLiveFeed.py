import pandas as pd
import backtrader as bt
import requests
import os
from datetime import datetime, timedelta, timezone
import time
import pytz
import queue
from ffquant.utils.Logger import stdout_log
from ffquant.symbols.BaseSymbol import BaseSymbol

__ALL__ = ['MyLiveFeed']

# 该DataFeed用于实时策略 基本流程介绍如下
# 1. 准备backfill的数据 一次性拉取到本地 放到hist_data_q
# 2. _load方法 非常重要 它是backtrader框架来找DataFeed获取新K线的地方
# 注意 在同一个K线的时间段 _load方法会被调用很多次 所以 需要判断当前时间段所代表的K线是否已经被返回了
# 如果已经返回了 那就忽略 如果还没有被返回 那就调用API接口获取 并保存到live_data_list中 如果API接口没有获取到数据 那就沿用上一个K线
class MyLiveFeed(bt.feeds.DataBase):
    params = (
        ('url', os.getenv('SYMBOL_INFO_LIST_URL', default='http://192.168.25.127:8285/symbol/info/list')),
        ('symbol', None),
        ('timeframe', bt.TimeFrame.Minutes),
        ('compression', 1),
        ('debug', False),
        ('max_retries', 15),
        ('backpeek_size', 5),
        ('backfill_size', 0),
        ('check_backfill_size', True),
        ('market', 'HKEX'),
        ('inherit', True)
    )

    lines = (('turnover'),)

    def __init__(self):
        super(MyLiveFeed, self).__init__()

        self.symbol_obj = None
        if isinstance(self.p.symbol, BaseSymbol):
            self.symbol_obj = self.p.symbol
            self.p.symbol = self.p.symbol.__str__()

        self.live_data_list = list()
        self.hist_data_q = queue.Queue()

        self.dropped_kline_time_list = list()

    def islive(self):
        return True

    def is_tradable(self, dt: datetime) -> bool:
        dt = dt.astimezone()

        if self.symbol_obj is not None and isinstance(self.symbol_obj, BaseSymbol):
            return self.symbol_obj.is_trading_time(dt)

        # MyLiveFeed中调用is_tradable时 传入的是k线的结束时间 这里需要计算出K线开始时间
        if self.p.timeframe == bt.TimeFrame.Minutes:
            dt = dt - timedelta(minutes=self.p.compression)
        elif self.p.timeframe == bt.TimeFrame.Seconds:
            dt = dt - timedelta(seconds=self.p.compression)
        if self.p.market == 'HKEX':
            if dt.weekday() == 6 or (dt.weekday() == 5 and dt.hour >= 3) or (dt.weekday() == 0 and dt.hour < 9):
                return False

            # 星期六凌晨3点前的夜盘 允许
            if dt.weekday() == 5 and dt.hour < 3:
                return True

            open_time = dt.replace(hour=9, minute=30, second=0, microsecond=0) - timedelta(minutes=15)
            brk_start_time = dt.replace(hour=12, minute=0, second=0, microsecond=0)
            brk_end_time = dt.replace(hour=13, minute=0, second=0, microsecond=0)
            close_time = dt.replace(hour=16, minute=30, second=0, microsecond=0)

            night_open_time = close_time.replace(hour=17, minute=30, second=0, microsecond=0) - timedelta(minutes=15)
            night_close_time = close_time.replace(hour=3, minute=0, second=0, microsecond=0)    # 该日凌晨3点夜盘收盘时间
            next_night_close_time = close_time.replace(hour=3, minute=0, second=0, microsecond=0) + timedelta(days=1)   # 次日凌晨3点夜盘收盘时间

            return dt < night_close_time or open_time <= dt < brk_start_time or brk_end_time <= dt < close_time or night_open_time <= dt < next_night_close_time
        elif self.p.market == 'NYSE':
            if dt.weekday() == 6 or (dt.weekday() == 5 and dt.hour >= 4) or (dt.weekday() == 0 and dt < dt.replace(hour=21, minute=30, second=0, microsecond=0)):
                return False

            # 星期六凌晨4点前的夜盘 允许
            if dt.weekday() == 5 and dt.hour < 4:
                return True

            open_time = dt.replace(hour=21, minute=30, second=0, microsecond=0) - timedelta(minutes=15)
            close_time = dt.replace(hour=4, minute=0, second=0, microsecond=0)

            return dt < close_time or open_time <= dt
        elif self.p.market == 'ALL':
            return True

    # start方法的调用先于next 但是start方法被调用时 strategy的minperiod还没有被确定 next方法被调用时 strategy的minperiod已经确定
    # 需要根据策略的minperiod来限制backfill_size 所以限制backfill_size需要在next方法中
    def next(self, datamaster=None, ticks=True):
        if len(self) == 0:
            # 为什么要在这里清空列表？
            # 举个例子 如果进行resample compression=2 策略开始执行在奇数分钟时 第一根1分钟k线会被不断地drop掉 len(self)会不断地返回0
            # 从而导致live_data_list不断地累积无用的数据
            # backtrader框架是在DataFeed对象的lines上直接修改来达到resample的目的 也就是说直接删掉奇数分钟的数据
            self.live_data_list.clear()

            running_strats = self._env.runningstrats
            max_minperiod = max([strat._minperiod for strat in running_strats])
            if self.p.check_backfill_size and self.p.backfill_size > max_minperiod:
                stdout_log(f"[CRITICAL], {self.__class__.__name__}, backfill_size({self.p.backfill_size}) > max_minperiod({max_minperiod}), use max_minperiod - 1 as backfill_size")
                self.p.backfill_size = max_minperiod - 1
            self.prepare_backfill_data()
        return super().next(datamaster, ticks)

    # 获取backfill数据 一次性拉取到本地 并填充缺失的k线
    def prepare_backfill_data(self):
        if self.p.backfill_size > 0:
            self.hist_data_q = queue.Queue()

            now = datetime.now()
            end_time = now.replace(second=0, microsecond=0)
            start_time = end_time - timedelta(minutes=self.p.backfill_size * self.p.compression)
            if self.p.timeframe == bt.TimeFrame.Seconds:
                end_time = now.replace(second=(now.second // self.p.compression) * self.p.compression, microsecond=0).astimezone()
                start_time = end_time - timedelta(seconds=self.p.backfill_size * self.p.compression)

            end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')
            start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')

            params = {
                'startTime': start_time_str,
                'endTime': end_time_str,
                'symbol': self.p.symbol
            }
            if self.p.timeframe == bt.TimeFrame.Seconds:
                params['interval'] = f'{self.p.compression}S'

            if self.p.debug:
                stdout_log(f"{self.__class__.__name__}, backfill params: {params}")

            response = requests.get(self.p.url, params=params).json()
            if self.p.debug:
                stdout_log(f"{self.__class__.__name__}, backfill response: {response}")

            if response.get('code') != '200':
                raise ValueError(f"API request failed: {response}")

            results = response.get('results', [])
            results.sort(key=lambda x: x['timeClose'])

            last_time_close = None
            for result in results:
                time_close = result["timeClose"]
                if not self.is_tradable(datetime.fromtimestamp(time_close / 1000.0, timezone.utc)):
                    continue

                if last_time_close is not None:
                    # fill missing klines
                    interval = 60 * self.p.compression
                    if self.p.timeframe == bt.TimeFrame.Seconds:
                        interval = self.p.compression
                    if time_close > last_time_close + interval * 1000:
                        missing_ts = last_time_close + interval * 1000
                        while missing_ts < time_close:
                            missing_kline_time = datetime.fromtimestamp(missing_ts / 1000.0, timezone.utc)
                            if self.is_tradable(missing_kline_time):
                                if self.p.debug:
                                    missing_kline_local_time_str = datetime.fromtimestamp(missing_ts / 1000.0, timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S')
                                    stdout_log(f"{self.__class__.__name__}, missing kline time: {missing_kline_local_time_str}")

                                # 找到缺失的K线 填充策略就是沿用上一根K线的close价格 vol和turnover为0
                                v = self.hist_data_q.queue[-1]
                                if v is not None:
                                    new_v = {
                                        'timeOpen': missing_ts - interval * 1000,
                                        'timeClose': missing_ts,
                                        'createTime': 0,    # 约定：只要是沿用的价格数据 createTime和updateTime都为0
                                        'updateTime': 0,    # 约定：只要是沿用的价格数据 createTime和updateTime都为0
                                        'symbol': v['symbol'],
                                        'open': v['close'],
                                        'high': v['close'],
                                        'low': v['close'],
                                        'close': v['close'],
                                        'vol': 0.0,
                                        'turnover': 0.0,
                                        'type': v['type']
                                    }
                                    self.hist_data_q.put(new_v)
                            else:
                                if self.p.debug:
                                    missing_kline_local_time_str = datetime.fromtimestamp(missing_ts / 1000.0, timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S')
                                    stdout_log(f"{self.__class__.__name__}, skip non-tradetime missing kline time: {missing_kline_local_time_str}")
                            missing_ts += interval * 1000

                self.hist_data_q.put(result)
                last_time_close = time_close

            if self.p.backfill_size != self.hist_data_q.qsize():
                stdout_log(f"{self.__class__.__name__}, backfill data size({self.hist_data_q.qsize()}) != backfill_size({self.p.backfill_size}). Set backfill_size to {self.hist_data_q.qsize()}")
                self.p.backfill_size = self.hist_data_q.qsize()

    # 注意 这个方法在同一个K线的时间段 会被调用很多次 所以需要判断K线是否已经被返回
    def _load(self):
        if not self.hist_data_q.empty():
            history_item = self.hist_data_q.get()
            self.lines.datetime[0] = bt.date2num(datetime.fromtimestamp(history_item['timeClose'] / 1000.0, timezone.utc))
            self.lines.open[0] = history_item['open']
            self.lines.high[0] = history_item['high']
            self.lines.low[0] = history_item['low']
            self.lines.close[0] = history_item['close']
            self.lines.volume[0] = history_item['vol']
            self.lines.turnover[0] = history_item['turnover']
            if self.p.debug:
                stdout_log(f"{self.__class__.__name__}, hist_data_q size: {self.hist_data_q.qsize() + 1}, backfill from history, kline datetime: {self.lines.datetime.datetime(0).replace(tzinfo=pytz.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S')}")

            # heartbeat info print
            self.print_heartbeat_info(history_item['createTime'])

            self.live_data_list.append(history_item)
            return True

        now = datetime.now()
        cur_kline_local_time = now.replace(second=0, microsecond=0).astimezone()
        start_time = cur_kline_local_time - timedelta(minutes=self.p.compression)
        if self.p.timeframe == bt.TimeFrame.Seconds:
            cur_kline_local_time = now.replace(second=(now.second // self.p.compression) * self.p.compression, microsecond=0).astimezone()
            start_time = cur_kline_local_time - timedelta(seconds=self.p.compression)

        # 准备K线的默认值
        self.lines.datetime[0] = bt.date2num(cur_kline_local_time.replace(tzinfo=pytz.utc))
        self.lines.open[0] = float('-inf')
        self.lines.high[0] = float('-inf')
        self.lines.low[0] = float('-inf')
        self.lines.close[0] = float('-inf')
        self.lines.volume[0] = float('-inf')
        self.lines.turnover[0] = float('-inf')

        if len(self.live_data_list) > 0:
            prev_live_data = self.live_data_list[len(self.live_data_list) - 1]
            if prev_live_data is not None:
                prev_kline_local_time = datetime.fromtimestamp(prev_live_data['timeClose'] / 1000.0, timezone.utc).astimezone()
                if prev_kline_local_time >= cur_kline_local_time:
                    # 因为_load在同一个K线时间段被调用很多次 所以 需要判断当前时间段所代表的K线是否已经被返回了
                    return  # kline already exists
                else:
                    pass
                    # new kline
                    # because market data API denotes Kline by open time, while backtrader denotes Kline by close time
                    # start_time = datetime.fromtimestamp(prev_live_data['timeClose'] / 1000.0, timezone.utc).astimezone()

        end_time = start_time + timedelta(minutes=self.p.compression)
        if self.p.timeframe == bt.TimeFrame.Seconds:
            end_time = start_time + timedelta(seconds=self.p.compression)

        # 如果当前K线处于不可交易时段 就直接return
        if not self.is_tradable(end_time.astimezone(pytz.utc)):
            if end_time.strftime('%Y-%m-%d %H:%M:%S') not in self.dropped_kline_time_list:
                stdout_log(f"{self.__class__.__name__}, kline time: {end_time.strftime('%Y-%m-%d %H:%M:%S')} is not tradable. Drop")
                self.dropped_kline_time_list.append(end_time.strftime('%Y-%m-%d %H:%M:%S'))
            time.sleep(3)
            return

        start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
        end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')

        retry_count = 0
        while retry_count < self.p.max_retries:
            retry_count += 1

            params = {
                'startTime': start_time_str,
                'endTime': end_time_str,
                'symbol': self.p.symbol
            }

            if self.p.timeframe == bt.TimeFrame.Seconds:
                params['interval'] = f'{self.p.compression}S'

            if self.p.debug:
                stdout_log(f"{self.__class__.__name__}, fetch data params: {params}")

            response = requests.get(self.p.url, params=params).json()
            if self.p.debug:
                stdout_log(f"{self.__class__.__name__}, fetch data response: {response}")

            if response.get('code') != '200':
                raise ValueError(f"API request failed: {response}")

            results = response.get('results', [])
            if results is not None and len(results) > 0:
                bar = results[0]
                self.live_data_list.append(bar)

                self.lines.datetime[0] = bt.date2num(datetime.fromtimestamp(bar['timeClose'] / 1000.0, timezone.utc))
                self.lines.open[0] = bar['open']
                self.lines.high[0] = bar['high']
                self.lines.low[0] = bar['low']
                self.lines.close[0] = bar['close']
                self.lines.volume[0] = bar['vol']
                self.lines.turnover[0] = bar['turnover']

                # heartbeat info print
                self.print_heartbeat_info(bar['createTime'])
                return True
            else:
                retry_interval_s = 1
                time.sleep(retry_interval_s)

        if self.p.inherit:
            # 如果通过API没有获取到K线数据 那就尝试沿用前面的K线来充当
            self.backpeek_for_result(cur_kline_local_time)
        # heartbeat info print
        self.print_heartbeat_info(self.live_data_list[len(self.live_data_list) - 1]['createTime'])
        return True

    # 把前面的K线的数据沿用过来 当作当前的K线的价格
    # 注意 在沿用之前 需要历史窗口中的K线都更新一遍 防止出现一直不变的水平价格线
    def backpeek_for_result(self, cur_kline_local_time):
        # update backpeek window
        end_time = cur_kline_local_time

        # because market data API denotes Kline by open time, while backtrader denotes Kline by close time
        start_time = end_time - timedelta(minutes=self.p.backpeek_size * self.p.compression)
        if self.p.timeframe == bt.TimeFrame.Seconds:
            start_time = end_time - timedelta(seconds=self.p.backpeek_size * self.p.compression)

        end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')
        start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
        params = {
            'startTime': start_time_str,
            'endTime': end_time_str,
            'symbol': self.p.symbol
        }

        if self.p.timeframe == bt.TimeFrame.Seconds:
            params['interval'] = f'{self.p.compression}S'

        if self.p.debug:
            stdout_log(f"{self.__class__.__name__}, update backpeek window params: {params}")

        response = requests.get(self.p.url, params=params).json()
        if self.p.debug:
            stdout_log(f"{self.__class__.__name__}, update backpeek window response: {response}")

        if response.get('code') != '200':
            raise ValueError(f"API request failed: {response}")
        results = response.get('results', [])
        results.sort(key=lambda x: x['timeClose'])
        for result in results:
            for i in range(0, len(self.live_data_list)):
                if self.live_data_list[i]['timeClose'] == result['timeClose']:
                    self.live_data_list[i] = result
                    break

        if len(self.live_data_list) > 0:
            prev_live_data = self.live_data_list[len(self.live_data_list) - 1]
            if prev_live_data is not None:
                self.lines.datetime[0] = bt.date2num(datetime.fromtimestamp(cur_kline_local_time.timestamp(), timezone.utc))
                self.lines.open[0] = prev_live_data['close']
                self.lines.high[0] = prev_live_data['close']
                self.lines.low[0] = prev_live_data['close']
                self.lines.close[0] = prev_live_data['close']
                self.lines.volume[0] = 0.0

                # 延续前面K线的turnover时 如果直接设置turnover为0 会影响量的指标的计算 所以这里做了特殊处理 取前3个K线的turnover的平均值
                turnover_fix_size = min(3, len(self))
                turnover_fix_sum = 0
                for i in range(0, turnover_fix_size):
                    turnover_fix_sum += self.lines.turnover[-i - 1]
                self.lines.turnover[0] = turnover_fix_sum / turnover_fix_size

                interval = 60 * self.p.compression
                if self.p.timeframe == bt.TimeFrame.Seconds:
                    interval = self.p.compression
                self.live_data_list.append({
                    'timeOpen': (int(cur_kline_local_time.timestamp()) - interval) * 1000,
                    'timeClose': int(cur_kline_local_time.timestamp()) * 1000,
                    'createTime': 0,    # 约定：只要是沿用的价格数据 createTime和updateTime都为0
                    'updateTime': 0,    # 约定：只要是沿用的价格数据 createTime和updateTime都为0
                    'symbol': self.p.symbol,
                    'open': self.lines.open[0],
                    'high': self.lines.high[0],
                    'low': self.lines.low[0],
                    'close': self.lines.close[0],
                    'vol': 0.0,
                    'turnover': self.lines.turnover[0],
                    'type': prev_live_data['type']
                })

                kline_local_time_str = cur_kline_local_time.astimezone().strftime('%Y-%m-%d %H:%M:%S')
                backpeek_time_str = datetime.fromtimestamp(prev_live_data['timeClose'] / 1000.0, timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S')
                stdout_log(f"[CRITICAL], {self.__class__.__name__}, kline time: {kline_local_time_str} use backpeek from {backpeek_time_str}")
                return True
        return False

    # 这里的打印是为了监控的目的
    def print_heartbeat_info(self, create_time=0):
        kline_time_str = self.lines.datetime.datetime(0).replace(tzinfo=pytz.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S')
        create_time_str = datetime.fromtimestamp(create_time / 1000.0, timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S')
        stdout_log(f"[INFO], {self.__class__.__name__}, kline time: {kline_time_str}, create time: {create_time_str}, open: {self.lines.open[0]}, high: {self.lines.high[0]}, low: {self.lines.low[0]}, close: {self.lines.close[0]}")