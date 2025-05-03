from ffquant.indicators.BaseIndicator import BaseIndicator
from datetime import datetime, timedelta
import pytz
from ffquant.utils.Logger import stdout_log

__ALL__ = ['AggSignalV3']

class AggSignalV3(BaseIndicator):
    (BEARISH_WITH_LARGE_PULL_BACK,
     BEARISH_WITH_SMALL_PULL_BACK,
     INVERSE_TO_BEARISH,
     CONT_BEARISH,
     FLUCT_BEARISH,
     NA,
     FLUCT_BULLISH,
     CONT_BULLISH,
     INVERSE_TO_BULLISH,
     BULLISH_WITH_SMALL_PULL_BACK,
     BULLISH_WITH_LARGE_PULL_BACK) = (-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5)

    lines = ('agg_sig', 'delay')

    def __init__(self):
        super(AggSignalV3, self).__init__()
        self.addminperiod(1)

    def handle_api_resp(self, item):
        internal_key = self.get_internal_key()
        result_time_str = datetime.fromtimestamp(item['closeTime'] / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
        root_create_time = item['createTime']
        leaf = item.get(internal_key, {})

        if leaf.get('value', None) is not None:
            self.cache[result_time_str]['create_time'] = root_create_time
            self.cache[result_time_str]['raw_material_time'] = leaf['closeTime']
            if leaf['value'] == 'BEARISH_WITH_LARGE_PULL_BACK':
                self.cache[result_time_str]['value'] = self.BEARISH_WITH_LARGE_PULL_BACK
            elif leaf['value'] == 'BEARISH_WITH_SMALL_PULL_BACK':
                self.cache[result_time_str]['value'] = self.BEARISH_WITH_SMALL_PULL_BACK
            elif leaf['value'] == 'INVERSE_TO_BEARISH':
                self.cache[result_time_str]['value'] = self.INVERSE_TO_BEARISH
            elif leaf['value'] == 'CONT_BEARISH':
                self.cache[result_time_str]['value'] = self.CONT_BEARISH
            elif leaf['value'] == 'FLUCT_BEARISH':
                self.cache[result_time_str]['value'] = self.FLUCT_BEARISH
            elif leaf['value'] == 'FLUCT_BULLISH':
                self.cache[result_time_str]['value'] = self.FLUCT_BULLISH
            elif leaf['value'] == 'CONT_BULLISH':
                self.cache[result_time_str]['value'] = self.CONT_BULLISH
            elif leaf['value'] == 'INVERSE_TO_BULLISH':
                self.cache[result_time_str]['value'] = self.INVERSE_TO_BULLISH
            elif leaf['value'] == 'BULLISH_WITH_SMALL_PULL_BACK':
                self.cache[result_time_str]['value'] = self.BULLISH_WITH_SMALL_PULL_BACK
            elif leaf['value'] == 'BULLISH_WITH_LARGE_PULL_BACK':
                self.cache[result_time_str]['value'] = self.BULLISH_WITH_LARGE_PULL_BACK
            elif leaf['value'] == 'NA':
                self.cache[result_time_str]['value'] = self.NA

        if self.p.debug:
            stdout_log(f"{self.__class__.__name__}, result_time_str: {result_time_str}, {internal_key}: {item.get(internal_key, None)}")

    # 它的返回值表示这个信号的生成时间戳 目的是让BaseIndicator打印信号的生成延迟
    def determine_final_result(self):
        current_bar_time = self.data.datetime.datetime(0).replace(tzinfo=pytz.utc).astimezone()
        current_bar_time_str = current_bar_time.strftime('%Y-%m-%d %H:%M:%S')
        self.lines.agg_sig[0] = self.cache[current_bar_time_str]['value']

        root_create_time = self.cache[current_bar_time_str]['create_time']
        line = getattr(self.lines, 'delay', None)
        if line is not None:
            leaf_close_time = self.cache[current_bar_time_str]['raw_material_time']
            self.lines.delay[0] = (root_create_time - leaf_close_time) / 1000.0

        return root_create_time

    def get_internal_key(self):
        return 'TYPE_AGG_SIGNAL_V3' if self.p.version is None else f'TYPE_AGG_SIGNAL_V3_{str(self.p.version).upper()}'