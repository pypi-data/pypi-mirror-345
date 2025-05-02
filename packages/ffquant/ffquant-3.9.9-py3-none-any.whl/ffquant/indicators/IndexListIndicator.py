import backtrader as bt
import os
import pytz
import requests
from datetime import datetime, timedelta, timezone
import time
from ffquant.utils.Logger import stdout_log

__ALL__ = ['IndexListIndicator']

class IndexListIndicator(bt.Indicator):
    params = (
        ('symbol', 'CAPITALCOM:HK50'),
        ('debug', None),
        ('test', None),
        ('url', os.getenv('INDEX_LIST_URL', default='http://192.168.25.127:8285/index/list')),
        ('max_retries', 40),
        ('timeframe', bt.TimeFrame.Minutes),
        ('compression', 1),
        ('inherit', False),
        ('minperiod', 1),
        ('retry_interval_s', 1.0),
    )

    TEST = False
    DEBUG = False

    def __init__(self):
        super().__init__()
        self.addminperiod(self.p.minperiod)

        if self.p.test is None:
            self.p.test = self.TEST

        if self.p.debug is None:
            self.p.debug = self.DEBUG

        self.cache = {}

    # 根节点的openTime和closeTime表示属于哪根K线，子节点的openTime和closeTime表示信号的原材料的时间
    def handle_api_resp(self, result):
        result_time_str = datetime.fromtimestamp(result['closeTime'] / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
        self.cache[result_time_str] = result

    # 子类需要实现这个方法 决定最后返回给backtrader框架的indicator结果
    def determine_final_result(self):
        pass

    def next(self):
        super().next()
        cur_bar_local_time = self.data.datetime.datetime(0).replace(tzinfo=pytz.utc).astimezone()
        cur_bar_local_time_str = cur_bar_local_time.strftime('%Y-%m-%d %H:%M:%S')

        # 实时模式
        is_live = self.data.islive()
        if is_live:
            # 如果不在缓存中 则请求数据
            # index/list接口只提供1分钟维度的数据 K线的时间是30秒 那么就沿用前面的00秒的数据
            if cur_bar_local_time_str not in self.cache:
                # 只有在00秒的时候才请求数据
                if cur_bar_local_time.second == 0:
                    tdelta = timedelta(minutes=1)
                    start_time = cur_bar_local_time - tdelta
                    end_time = cur_bar_local_time
                    self.batch_fetch(start_time, end_time)

                    # 如果缓存中还是没有数据 那就更新更早的数据 让沿用的时候使用的是最新的数据
                    if cur_bar_local_time_str not in self.cache and self.p.inherit:
                        if self.p.debug:
                            stdout_log(f"{self.__class__.__name__}, update values of last 5 minutes for value inheriting")
                        start_time = cur_bar_local_time - timedelta(minutes=5)
                        end_time = cur_bar_local_time
                        self.batch_fetch(start_time, end_time)
                else:
                    # 当前k线是位于30秒的时候 沿用前面的00秒的数据 但要确保缓存中的数据是最新的
                    start_time = cur_bar_local_time - timedelta(minutes=5)
                    end_time = cur_bar_local_time
                    self.batch_fetch(start_time, end_time)
            else:
                if self.p.debug:
                    stdout_log(f"{self.__class__.__name__}, current_time_str: {cur_bar_local_time_str}, hit cache: {self.cache[cur_bar_local_time_str]}")
        else:
            # 非实时模式 一次性把所有的数据都捞回来
            if len(self.cache) == 0:
                start_time_str = self.data.p.start_time
                start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S').astimezone()
                if self.data.p.backfill_size > 0:
                    tdelta = timedelta(seconds=self.data.p.backfill_size * self.data.p.compression)
                    if self.data.p.timeframe == bt.TimeFrame.Minutes:
                        tdelta = timedelta(minutes=self.data.p.backfill_size * self.data.p.compression)
                    start_time = start_time - tdelta

                end_time_str = self.data.p.end_time
                end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')
                self.batch_fetch(start_time, end_time)

            if cur_bar_local_time_str in self.cache:
                if self.p.debug:
                    stdout_log(f"{self.__class__.__name__}, current_time_str: {cur_bar_local_time_str}, hit cache: {self.cache[cur_bar_local_time_str]}")

        # 不管是实时模式还是非实时模式 都在此判断最终应该返回什么数值
        actual_time_millis = self.determine_final_result()

        # Replace -info with previous value. Starting value is zero. heartbeat info print
        for line_name in self.lines.getlinealiases():
            line = getattr(self.lines, line_name)
            kline_local_time_str = cur_bar_local_time.astimezone().strftime('%Y-%m-%d %H:%M:%S')
            actual_time_str = datetime.fromtimestamp(actual_time_millis / 1000.0, timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S')

            # 这里的打印最终会输出到标准输出日志中 这样的日志被用于分析行情的延迟等问题
            stdout_log(f"[INFO], {self.__class__.__name__}, kline time: {kline_local_time_str}, actual_time: {actual_time_str}, {line_name}: {line[0]}")

    def prepare_params(self, start_time_str, end_time_str):
        pass

    def batch_fetch(self, start_time: datetime, end_time: datetime):
        start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
        end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')

        params = self.prepare_params(start_time_str, end_time_str)

        retry_count = 0
        max_retry_count = self.p.max_retries

        # 这里需要区分加载的数据是不是实时数据 如果不是 重试只有一次
        live_mark_dt = (datetime.now().replace(second=0, microsecond=0) - timedelta(minutes=2)).astimezone()
        if start_time.astimezone() < live_mark_dt:
            max_retry_count = 1

        while retry_count < max_retry_count:
            retry_count += 1
            if self.p.debug:
                stdout_log(f"{self.__class__.__name__}, fetch data params: {params}, url: {self.p.url}")

            response = requests.get(self.p.url, params=params).json()
            if self.p.debug:
                stdout_log(f"{self.__class__.__name__}, fetch data response: {response}")

            if response.get('code') != '200':
                raise ValueError(f"{self.__class__.__name__}, API request failed: {response}")

            if response.get('results') is not None and len(response['results']) > 0:
                results = response['results']
                results.sort(key=lambda x: x['closeTime'])
                for result in results:
                    self.handle_api_resp(result)
                break

            if retry_count < max_retry_count:
                time.sleep(self.p.retry_interval_s)