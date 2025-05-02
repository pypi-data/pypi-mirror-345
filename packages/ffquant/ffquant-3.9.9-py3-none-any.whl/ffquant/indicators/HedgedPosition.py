import pytz
from datetime import datetime, timedelta
from ffquant.indicators.IndexListIndicator import IndexListIndicator
from ffquant.utils.Logger import stdout_log
from ffquant.indicators.BaseIndicator import BaseIndicator

class HedgedPosition(IndexListIndicator):
    lines = (
        "hedgedPos",
        'resisByCha',
        'hedgedPosCha',
        'resisByDu',
        'resisBySFB',
        'isHedgedShPos',
        'isHedgedLnPos',
        'activeBS'
    )
    
    def determine_final_result(self):
        self.lines.hedgedPos[0] = float('-inf')
        self.lines.resisByCha[0] = float('-inf')
        self.lines.hedgedPosCha[0] = float('-inf')
        self.lines.resisByDu[0] = float('-inf')
        self.lines.resisBySFB[0] = float('-inf')
        self.lines.isHedgedShPos[0] = float('-inf')
        self.lines.isHedgedLnPos[0] = float('-inf')
        self.lines.activeBS[0] = float('-inf')

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
                        if float(value) != float('-inf'):
                            line[0] = float(value)
                        else:
                            line[0] = line[-1]
            return result['closeTime']
        else:
            return 0

    def prepare_params(self, start_time_str, end_time_str):
        key_list = 'hedged_position'
        if self.p.test:
            key_list = f'hedged_position_{BaseIndicator.VERSION}'

        params = {
            'type': 'trend_pattern',
            'key_list': key_list,
            'startTime' : start_time_str,
            'endTime' : end_time_str
        }
        return params