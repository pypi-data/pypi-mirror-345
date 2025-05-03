import backtrader as bt
import os
import pytz
import requests
from datetime import datetime, timedelta, timezone
import time
from ffquant.utils.Logger import stdout_log

__ALL__ = ['BaseIndicator']

class BaseIndicator(bt.Indicator):
    params = (
        ('url', os.getenv('SIGNAL_LIST_URL', default='http://192.168.25.127:8285/signal/list')),
        ('symbol', 'CAPITALCOM:HK50'),
        ('max_retries', 15),        # 请求行情的HTTP接口的重试次数 每次重试间隔为1秒 默认最大重试15次 如果最大重试次数内没有成功则沿用上一根K线的数据
        ('version', None),          # 指标版本 该参数的优先级高于通过BaseIndicator.VERSION指定的版本号
        ('test', None),             # 指标测试模式 该参数的优先级高于通过BaseIndicator.TEST指定的测试模式
        ('debug', None),            # 指标调试模式 该参数的优先级高于通过BaseIndicator.DEBUG指定的调试模式
    )

    # 对于都一个时间区间 信号HTTP接口返回的数据都是一样的 这里缓存在静态变量中是为了防止重复请求
    http_resp_cache = {}

    VERSION = 'V2024120921'         # 指标版本号 用户通过给BaseIndicator.VERSION赋值来指定指标版本号
    TEST = False                    # 指标测试模式 用户通过给BaseIndicator.TEST赋值来指定指标测试模式
    DEBUG = False                   # 指标调试模式 用户通过给BaseIndicator.DEBUG赋值来指定指标调试模式

    def __init__(self):
        super(BaseIndicator, self).__init__()
        if self.p.test is None:
            self.p.test = self.TEST

        if self.p.debug is None:
            self.p.debug = self.DEBUG

        if self.p.test:
            self.p.url = self.p.url + "/test"

        if self.p.version is None:
            self.p.version = self.VERSION

        self.cache = {}

    # 子类需要实现这个方法 用于处理HTTP接口返回的数据项 把返回的字符串映射为数字
    # 每一个response的item的数据结构如下：
    # {
	# 	'createTime': 1738826517873,
	# 	'closeTime': 1738826540000,
	# 	'openTime': 1738826510000,
	# 	'TYPE_ACTIVE_BUY_SELL_DIRECTION_V2024120921': {
	# 		'value': 'NA',
	# 		'openTime': 1738826400000,
	# 		'closeTime': 1738826460000
	# 	},
	# 	'TYPE_TREND_W_V2024120921': {
	# 		'value': 'BULLISH',
	# 		'openTime': 1738826400000,
	# 		'closeTime': 1738826460000
	# 	}
	# }
    # 根节点的openTime和closeTime表示属于哪根K线，子节点的openTime和closeTime表示信号的原材料的时间
    def handle_api_resp(self, result):
        pass

    # 子类需要实现这个方法 决定最后返回给backtrader框架的indicator结果
    def determine_final_result(self):
        pass

    # 子类需要实现这个方法 返回指标的内部key 比如：TYPE_TREND_W，注意它返回的值不能包含信号版本
    def get_internal_key(self):
        pass

    def next(self):
        cur_bar_local_time = self.data.datetime.datetime(0).replace(tzinfo=pytz.utc).astimezone()
        cur_bar_local_time_str = cur_bar_local_time.strftime('%Y-%m-%d %H:%M:%S')

        # 实时模式
        is_live = self.data.islive()
        if is_live:
            if len(self.cache) == 0:
                # 在加载数据的最开始进行数据回填
                backfill_size = self.data.p.backfill_size
                if backfill_size > 0:
                    now = datetime.now()
                    end_time = now.replace(second=0, microsecond=0)
                    start_time = end_time - timedelta(minutes=backfill_size * self.data.p.compression)
                    if self.data.p.timeframe == bt.TimeFrame.Seconds:
                        end_time = now.replace(second=(now.second // self.data.p.compression) * self.data.p.compression, microsecond=0).astimezone()
                        start_time = end_time - timedelta(seconds=backfill_size * self.data.p.compression)

                    start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
                    end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')

                    params = self.prepare_params(start_time_str, end_time_str)

                    # fill with -inf
                    interval = 60 * self.data.p.compression
                    if self.data.p.timeframe == bt.TimeFrame.Seconds:
                        interval = self.data.p.compression
                    cur_time = start_time
                    while cur_time < end_time:
                        # HTTP请求是open标记法 cache的key是close标记法 所以需要先递增cur_time
                        cur_time = cur_time + timedelta(seconds=interval)
                        self.cache[cur_time.strftime('%Y-%m-%d %H:%M:%S')] = {'value': float('-inf'), 'create_time': 0, 'raw_material_time': 0}

                    if self.p.debug:
                        stdout_log(f"{self.__class__.__name__}, fetch data params: {params}, url: {self.p.url}")

                    response = requests.get(self.p.url, params=params).json()
                    if self.p.debug:
                        stdout_log(f"{self.__class__.__name__}, fetch data response: {response}")

                    if response.get('code') != '200':
                        raise ValueError(f"{self.__class__.__name__}, API request failed: {response}")
                    results = response.get('results', [])
                    results.sort(key=lambda x: x['closeTime'])

                    for result in results:
                        self.handle_api_resp(result)

            # 如果不在缓存中 则请求数据
            if cur_bar_local_time_str not in self.cache:
                start_time = cur_bar_local_time - timedelta(minutes=self.data.p.compression)
                if self.data.p.timeframe == bt.TimeFrame.Seconds:
                    start_time = cur_bar_local_time - timedelta(seconds=self.data.p.compression)
                start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
                end_time = cur_bar_local_time

                end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')

                params = self.prepare_params(start_time_str, end_time_str)

                # fill with -inf
                interval = 60 * self.data.p.compression
                if self.data.p.timeframe == bt.TimeFrame.Seconds:
                    interval = self.data.p.compression
                cur_time = start_time
                while cur_time < end_time:
                    # HTTP请求是open标记法 cache的key是close标记法 所以需要先递增cur_time
                    cur_time = cur_time + timedelta(seconds=interval)
                    self.cache[cur_time.strftime('%Y-%m-%d %H:%M:%S')] = {'value': float('-inf'), 'create_time': 0, 'raw_material_time': 0}

                key = f"{self.p.symbol}_{start_time_str}_{end_time_str}"
                response = BaseIndicator.http_resp_cache.get(key, None)
                if response is None:
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

                        BaseIndicator.http_resp_cache[key] = response
                        if response.get('results') is not None and len(response['results']) > 0:
                            results = response['results']
                            results.sort(key=lambda x: x['closeTime'])
                            for result in results:
                                self.handle_api_resp(result)
                            break
                        time.sleep(1)
                else:
                    if self.p.debug:
                        stdout_log(f"{self.__class__.__name__}, use cached response: {response}")
                    if response.get('results') is not None and len(response['results']) > 0:
                        results = response['results']
                        results.sort(key=lambda x: x['closeTime'])
                        if results[len(results) - 1].get(self.get_internal_key(), None) is None:
                            if self.p.debug:
                                stdout_log(f"{self.__class__.__name__}, cached response's last result has no {self.get_internal_key()}, refresh data params: {params}, url: {self.p.url}")

                            time.sleep(1)
                            response = requests.get(self.p.url, params=params).json()
                            if self.p.debug:
                                stdout_log(f"{self.__class__.__name__}, refresh data response: {response}")

                            if response.get('code') != '200':
                                raise ValueError(f"{self.__class__.__name__}, API request failed: {response}")

                            BaseIndicator.http_resp_cache[key] = response
                            results = response['results']
                            results.sort(key=lambda x: x['closeTime'])

                        for result in results:
                            self.handle_api_resp(result)
            else:
                if self.p.debug:
                    stdout_log(f"{self.__class__.__name__}, current_time_str: {cur_bar_local_time_str}, hit cache: {self.cache[cur_bar_local_time_str]['value']}")
        else:
            # 非实时模式 一次性把所有的数据都捞回来
            if len(self.cache) == 0:
                start_time_str = self.data.p.start_time
                start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
                end_time_str = self.data.p.end_time
                end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')
                backfill_size = self.data.p.backfill_size

                interval = 60 * self.data.p.compression
                if self.data.p.timeframe == bt.TimeFrame.Seconds:
                    interval = self.data.p.compression
                if backfill_size > 0:
                    start_time = start_time - timedelta(seconds=backfill_size * interval)
                    start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')

                params = self.prepare_params(start_time_str, end_time_str)

                # fill with -inf
                cur_time = start_time
                while cur_time < end_time:
                    # HTTP请求是open标记法 cache的key是close标记法 所以需要先递增cur_time
                    cur_time = cur_time + timedelta(seconds=interval)
                    self.cache[cur_time.strftime('%Y-%m-%d %H:%M:%S')] = {'value': float('-inf'), 'create_time': 0, 'raw_material_time': 0}

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
            elif cur_bar_local_time_str in self.cache:
                if self.p.debug:
                    stdout_log(f"{self.__class__.__name__}, current_time_str: {cur_bar_local_time_str}, hit cache: {self.cache[cur_bar_local_time_str]['value']}")

        # 不管是实时模式还是非实时模式 都在此判断最终应该返回什么数值
        create_time = self.determine_final_result()

        # Replace -info with previous value. Starting value is zero. heartbeat info print
        for line_name in self.lines.getlinealiases():
            line = getattr(self.lines, line_name)
            if line[0] == float('-inf'):
                if len(self) > 1:
                    stdout_log(f"[CRITICAL], {self.__class__.__name__}, kline time: {cur_bar_local_time.astimezone().strftime('%Y-%m-%d %H:%M:%S')}, line[0] inherited from line[-1]: {line[-1]}")
                    line[0] = line[-1]
                else:
                    line[0] = 0
            kline_local_time_str = cur_bar_local_time.astimezone().strftime('%Y-%m-%d %H:%M:%S')
            create_local_time_str = datetime.fromtimestamp(create_time / 1000.0, timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S')

            # 这里的打印最终会输出到标准输出日志中 这样的日志被用于分析行情的延迟等问题
            stdout_log(f"[INFO], {self.__class__.__name__}, kline time: {kline_local_time_str}, create_time: {create_local_time_str}, {line_name}: {line[0]}")

    def prepare_params(self, start_time_str, end_time_str):
        params = {
            'startTime' : start_time_str,
            'endTime' : end_time_str,
            'symbol' : self.p.symbol
        }

        if self.data.p.timeframe == bt.TimeFrame.Seconds:
            params['interval'] = f'{self.data.p.compression}S'

        return params