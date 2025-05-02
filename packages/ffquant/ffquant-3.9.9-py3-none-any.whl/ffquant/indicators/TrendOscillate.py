import pytz
from datetime import datetime, timedelta
from ffquant.indicators.IndexListIndicator import IndexListIndicator
from ffquant.utils.Logger import stdout_log
from ffquant.indicators.BaseIndicator import BaseIndicator

__ALL__ = ['TrendOscillate']

class TrendOscillate(IndexListIndicator):
    lines = (
        "trendDir",
        "validTrendDir",
        "oscUpperBound",
        "subTrendSize",
        "mainTrendSize",
        "mainTrendTsFm",
        "trendOscSize",
        "trendOscUpDn",
        "trendOscTsFm",
        "oscLowerBound",
        "isOscillating",
        "subTrendTsFm",
        "mainTrendPattern",
        "mainTrendId",
        "closeTime",
        "openTime",
    )

    # 子类需要实现这个方法 决定最后返回给backtrader框架的indicator结果
    def determine_final_result(self):
        self.lines.trendDir[0] = float('-inf')
        self.lines.validTrendDir[0] = float('-inf')
        self.lines.oscUpperBound[0] = float('-inf')
        self.lines.subTrendSize[0] = float('-inf')
        self.lines.mainTrendSize[0] = float('-inf')
        self.lines.mainTrendTsFm[0] = float('-inf')
        self.lines.trendOscSize[0] = float('-inf')
        self.lines.trendOscUpDn[0] = float('-inf')
        self.lines.trendOscTsFm[0] = float('-inf')
        self.lines.oscLowerBound[0] = float('-inf')
        self.lines.isOscillating[0] = float('-inf')
        self.lines.subTrendTsFm[0] = float('-inf')
        self.lines.mainTrendPattern[0] = float('-inf')
        self.lines.mainTrendId[0] = float('-inf')
        self.lines.closeTime[0] = 0
        self.lines.openTime[0] = 0

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
                    if key != 'trendDir' and key != 'validTrendDir' and key != 'isOscillating':
                        if isinstance(value, float) or isinstance(value, int):
                            line = getattr(self.lines, key)
                            line[0] = float(value)
                    elif str(value) != '':
                        line = getattr(self.lines, key)
                        if str(value) == 'UP':
                            line[0] = 1
                        elif str(value) == 'DOWN':
                            line[0] = -1
                        elif str(value).lower() == 'true':
                            line[0] = 1
                        elif str(value).lower() == 'false':
                            line[0] = 0
            return result['closeTime']
        else:
            return 0

    def prepare_params(self, start_time_str, end_time_str):
        key_list = 'trend_and_oscillation'
        if self.p.test:
            key_list = f'trend_and_oscillation_{BaseIndicator.VERSION}'

        params = {
            'symbol': self.p.symbol,
            'type': 'index_zyj',
            'key_list': key_list,
            'startTime' : start_time_str,
            'endTime' : end_time_str
        }

        return params