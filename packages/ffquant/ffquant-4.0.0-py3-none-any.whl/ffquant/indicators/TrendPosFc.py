import pytz
from datetime import datetime, timedelta
from ffquant.indicators.IndexListIndicator import IndexListIndicator
from ffquant.utils.Logger import stdout_log
from ffquant.indicators.BaseIndicator import BaseIndicator

class TrendPosFc(IndexListIndicator):
    lines = (
        "trendFC",
        "trendFCV2",
        "ptnOrgCode",
        "a0",
        "a1",
        "a2",
        "b0",
        "b1",
        "b2",
        "openTime",
        "closeTime"
    )

    def determine_final_result(self):
        self.lines.trendFC[0] = 0
        self.lines.trendFCV2[0] = 0
        self.lines.ptnOrgCode[0] = 0
        self.lines.a0[0] = 0
        self.lines.a1[0] = 0
        self.lines.a2[0] = 0
        self.lines.b0[0] = 0
        self.lines.b1[0] = 0
        self.lines.b2[0] = 0
        self.lines.openTime[0] = 0
        self.lines.closeTime[0] = 0


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
                    if isinstance(value, bool):
                        line = getattr(self.lines, key)
                        line[0] = 1 if value else 0
                    elif isinstance(value, float) or isinstance(value, int):
                        line = getattr(self.lines, key)
                        line[0] = float(value)
            return result['closeTime']
        else:
            return 0

    def prepare_params(self, start_time_str, end_time_str):
        key_list = 'trend_pos_fc'
        if self.p.test:
            key_list = f'trend_pos_fc_{BaseIndicator.VERSION}'

        params = {
            'type': 'trend_fc',
            'key_list': key_list,
            'startTime' : start_time_str,
            'endTime' : end_time_str
        }
        return params