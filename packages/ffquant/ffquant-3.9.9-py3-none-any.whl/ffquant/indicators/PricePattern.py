import backtrader as bt
import os
import pytz
from datetime import datetime, timedelta, timezone
import time
import requests
from ffquant.utils.Logger import stdout_log
from ffquant.indicators.IndexListIndicator import IndexListIndicator

__ALL__ = ['PricePattern']

class PricePattern(IndexListIndicator):
    params = (
        ('url', os.getenv('INDEX_COLLECT_LIST_URL', default='http://192.168.25.127:8285/index/collect/list')),
        ('symbol', 'PV_MONITOR:HSI1'),
    )

    lines = (
        'close',
        'turnover',
        'premium',
    )

    def handle_api_resp(self, result):
        result_time_str = datetime.fromtimestamp(result['timeClose'] / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
        self.cache[result_time_str] = result

    # 子类需要实现这个方法 决定最后返回给backtrader框架的indicator结果
    def determine_final_result(self):
        self.lines.close[0] = float('-inf')
        self.lines.turnover[0] = float('-inf')
        self.lines.premium[0] = float('-inf')

        current_bar_time = self.data.datetime.datetime(0).replace(tzinfo=pytz.utc).astimezone()
        cache_key_time = current_bar_time
        if current_bar_time.second != 0:
            cache_key_time = current_bar_time.replace(second=0, microsecond=0)
        cache_key_time_str = cache_key_time.strftime('%Y-%m-%d %H:%M:%S')

        result = None
        if cache_key_time_str in self.cache:
            result = self.cache[cache_key_time_str]
        elif self.p.inherit:
            for i in range(1, 5):
                key = (datetime.strptime(cache_key_time_str, '%Y-%m-%d %H:%M:%S') - timedelta(minutes=i)).strftime('%Y-%m-%d %H:%M:%S')
                if key in self.cache:
                    stdout_log(f"{self.__class__.__name__} use cache key {key} for {cache_key_time_str}")
                    result = self.cache[key]
                    break

        if result is not None:
            for key, value in dict(result).items():
                if key in self.lines.getlinealiases():
                    if key == 'timeOpen' or key == 'timeClose':
                        continue

                    if key == 'close' or key == 'turnover' or key == 'premium':
                        line = getattr(self.lines, key)
                        line[0] = float(value)
            return result['timeClose']
        else:
            return 0

    def prepare_params(self, start_time_str, end_time_str):
        params = {
            'symbol': 'PV_MONITOR:HSI1',    # 这个信号只针对这个symbol
            'interval': '30S',
            'startTime' : start_time_str,
            'endTime' : end_time_str
        }

        return params

    def batch_fetch(self, start_time: datetime, end_time: datetime):
        start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
        end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')

        params = self.prepare_params(start_time_str, end_time_str)

        retry_count = 0
        max_retry_count = self.p.max_retries
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
                results.sort(key=lambda x: x['timeClose'])
                for result in results:
                    self.handle_api_resp(result)
                break
            time.sleep(1)