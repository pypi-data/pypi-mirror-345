import pytz
from datetime import datetime, timedelta
from ffquant.indicators.IndexListIndicator import IndexListIndicator
from ffquant.utils.Logger import stdout_log

class VolSurgeDetection(IndexListIndicator):
    lines = (
        "hsi1",
        "hti1",
        "hhi1",
        "hk_warrant",
        "hk_stock",
        "cnt",
        "hk_future",
        "cnhhkd",
        "hketf_2800",
        "mch1",
        "hketf_2828",
        "mhi1",
        "hketf_3033"
    )
    
    def determine_final_result(self):
        self.lines.hsi1[0] = float('-inf')
        self.lines.hti1[0] = float('-inf')
        self.lines.hhi1[0] = float('-inf')
        self.lines.hk_warrant[0] = float('-inf')
        self.lines.hk_stock[0] = float('-inf')
        self.lines.cnt[0] = float('-inf')
        self.lines.hk_future[0] = float('-inf')
        self.lines.cnhhkd[0] = float('-inf')
        self.lines.hketf_2800[0] = float('-inf')
        self.lines.mch1[0] = float('-inf')
        self.lines.hketf_2828[0] = float('-inf')
        self.lines.mhi1[0] = float('-inf')
        self.lines.hketf_3033[0] = float('-inf')

        current_bar_time = self.data.datetime.datetime(0).replace(tzinfo=pytz.utc).astimezone()
        cache_key_time = current_bar_time
        if current_bar_time.second != 0:
            cache_key_time = current_bar_time.replace(second=0, microsecond=0)
        cache_key_time_str = cache_key_time.strftime('%Y-%m-%d %H:%M:%S')

        result = None
        if cache_key_time_str in self.cache:
            result = self.cache[cache_key_time_str]
        else:
            for i in range(1, 5):
                key = (datetime.strptime(cache_key_time_str, '%Y-%m-%d %H:%M:%S') - timedelta(minutes=i)).strftime('%Y-%m-%d %H:%M:%S')
                if key in self.cache:
                    stdout_log(f"{self.__class__.__name__} use cache key {key} for {cache_key_time_str}")
                    result = self.cache[key]
                    break

        if result is not None:
            result = dict(result)
            for key, value in dict(result['data']).items():
                if key in self.lines.getlinealiases():
                    print(f"key in self.lines. key: {key}, value: {value}")
                    if isinstance(value['vol_type'], float) or isinstance(value['vol_type'], int):
                        line = getattr(self.lines, key)
                        if float(value['vol_type']) != float('-inf'):
                            line[0] = int(value['vol_type'])
                        else:
                            line[0] = line[-1]
            return result['closeTime']
        else:
            return 0

    def prepare_params(self, start_time_str, end_time_str):
        params = {
            'type': 'vol_surge_indicator',
            'key_list': 'vol_level_segment',
            'startTime' : start_time_str,
            'endTime' : end_time_str
        }
        return params