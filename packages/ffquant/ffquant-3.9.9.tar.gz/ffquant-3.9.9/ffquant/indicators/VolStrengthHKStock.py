import backtrader as bt
import pytz
from datetime import datetime, timedelta, timezone
from ffquant.indicators.IndexListIndicator import IndexListIndicator
from ffquant.utils.Logger import stdout_log
from ffquant.indicators.BaseIndicator import BaseIndicator
from ffquant.symbols.HK_Stock import HK_Stock

class VolStrengthHKStock(IndexListIndicator):
    lines = (
        "VolumeStrengthRankLevelTest",
        "volumeRankLevel",
        "volumeStrengthTodayCoverDays",
        "today",
        "volumeIntraU",
        "consecutiveDays",
        "window20",
        "VolumeEqualizationLevel",
        "days7",
        "VolumeLevelWithSpeed",
        "closeTime",
        "openTime"
    )

    def next(self):
        cur_bar_local_time = self.data.datetime.datetime(0).replace(tzinfo=pytz.utc).astimezone()

        hk_stock_sym = HK_Stock()
        if not hk_stock_sym.is_trading_time(cur_bar_local_time):
            self.determine_final_result()
            return

        super().next()

    # 子类需要实现这个方法 决定最后返回给backtrader框架的indicator结果
    def determine_final_result(self):
        self.lines.VolumeStrengthRankLevelTest[0] = float('-inf')
        self.lines.volumeRankLevel[0] = float('-inf')
        self.lines.volumeStrengthTodayCoverDays[0] = float('-inf')
        self.lines.today[0] = float('-inf')
        self.lines.volumeIntraU[0] = float('-inf')
        self.lines.consecutiveDays[0] = float('-inf')
        self.lines.window20[0] = float('-inf')
        self.lines.VolumeEqualizationLevel[0] = float('-inf')
        self.lines.days7[0] = float('-inf')
        self.lines.VolumeLevelWithSpeed[0] = float('-inf')
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
                    line = getattr(self.lines, key)
                    line[0] = float(value)
            return result['closeTime']
        else:
            return 0

    def prepare_params(self, start_time_str, end_time_str):
        params = {
            'symbol': "hk_stock",
            'type': 'indicator_volume_strength',
            'key_list': 'vol_list',
            'startTime' : start_time_str,
            'endTime' : end_time_str
        }

        return params