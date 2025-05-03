import pytz
from datetime import datetime, timedelta
from ffquant.indicators.IndexListIndicator import IndexListIndicator
from ffquant.utils.Logger import stdout_log
from ffquant.indicators.BaseIndicator import BaseIndicator

class PriceTrendDescribe(IndexListIndicator):
    lines = (
        "current_dir",
        "main_trend_id",
        "price_position",
        "is_small_trend"
    )

    def determine_final_result(self):
        self.lines.main_trend_id[0] = float('-inf')
        self.lines.price_position[0] = float('-inf')
        self.lines.current_dir[0] = float('-inf')
        self.lines.is_small_trend[0] = float('-inf')

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
                    if isinstance(value, float) or isinstance(value, int):
                        line = getattr(self.lines, key)
                        line[0] = float(value)
            return result['closeTime']
        else:
            return 0

    def prepare_params(self, start_time_str, end_time_str):
        key_list = 'price_pattern'

        params = {
            'type': 'price_trend_describe',
            'key_list': key_list,
            'startTime' : start_time_str,
            'endTime' : end_time_str
        }
        return params