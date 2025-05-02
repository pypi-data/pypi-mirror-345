from ffquant.indicators.BaseIndicator import BaseIndicator
from datetime import datetime, timedelta
import pytz
from ffquant.utils.Logger import stdout_log

__ALL__ = ['Fluctuation']

class Fluctuation(BaseIndicator):
    (FLUCT_BEARISH_L10,
     FLUCT_BEARISH_L9,
     FLUCT_BEARISH_L8,
     FLUCT_BEARISH_L7,
     FLUCT_BEARISH_L6,
     FLUCT_BEARISH_L5,
     FLUCT_BEARISH_L4,
     FLUCT_BEARISH_L3,
     FLUCT_BEARISH_L2,
     FLUCT_BEARISH_L1,
     NA,
     FLUCT_BULLISH_L1,
     FLUCT_BULLISH_L2,
     FLUCT_BULLISH_L3,
     FLUCT_BULLISH_L4,
     FLUCT_BULLISH_L5,
     FLUCT_BULLISH_L6,
     FLUCT_BULLISH_L7,
     FLUCT_BULLISH_L8,
     FLUCT_BULLISH_L9,
     FLUCT_BULLISH_L10) = (-10, -9, -8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

    lines = ('fluct', 'delay')

    def __init__(self):
        super(Fluctuation, self).__init__()
        self.addminperiod(1)

    def handle_api_resp(self, item):
        internal_key = self.get_internal_key()
        result_time_str = datetime.fromtimestamp(item['closeTime'] / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
        root_create_time = item['createTime']
        leaf = item.get(internal_key, {})

        if leaf.get('value', None) is not None:
            self.cache[result_time_str]['create_time'] = root_create_time
            self.cache[result_time_str]['raw_material_time'] = leaf['closeTime']
            if leaf['value'] == 'FLUCT_BULLISH_L10':
                self.cache[result_time_str]['value'] = self.FLUCT_BULLISH_L10
            elif leaf['value'] == 'FLUCT_BULLISH_L9':
                self.cache[result_time_str]['value'] = self.FLUCT_BULLISH_L9
            elif leaf['value'] == 'FLUCT_BULLISH_L8':
                self.cache[result_time_str]['value'] = self.FLUCT_BULLISH_L8
            elif leaf['value'] == 'FLUCT_BULLISH_L7':
                self.cache[result_time_str]['value'] = self.FLUCT_BULLISH_L7
            elif leaf['value'] == 'FLUCT_BULLISH_L6':
                self.cache[result_time_str]['value'] = self.FLUCT_BULLISH_L6
            elif leaf['value'] == 'FLUCT_BULLISH_L5':
                self.cache[result_time_str]['value'] = self.FLUCT_BULLISH_L5
            elif leaf['value'] == 'FLUCT_BULLISH_L4':
                self.cache[result_time_str]['value'] = self.FLUCT_BULLISH_L4
            elif leaf['value'] == 'FLUCT_BULLISH_L3':
                self.cache[result_time_str]['value'] = self.FLUCT_BULLISH_L3
            elif leaf['value'] == 'FLUCT_BULLISH_L2':
                self.cache[result_time_str]['value'] = self.FLUCT_BULLISH_L2
            elif leaf['value'] == 'FLUCT_BULLISH_L1':
                self.cache[result_time_str]['value'] = self.FLUCT_BULLISH_L1
            elif leaf['value'] == 'FLUCT_BEARISH_L1':
                self.cache[result_time_str]['value'] = self.FLUCT_BEARISH_L1
            elif leaf['value'] == 'FLUCT_BEARISH_L2':
                self.cache[result_time_str]['value'] = self.FLUCT_BEARISH_L2
            elif leaf['value'] == 'FLUCT_BEARISH_L3':
                self.cache[result_time_str]['value'] = self.FLUCT_BEARISH_L3
            elif leaf['value'] == 'FLUCT_BEARISH_L4':
                self.cache[result_time_str]['value'] = self.FLUCT_BEARISH_L4
            elif leaf['value'] == 'FLUCT_BEARISH_L5':
                self.cache[result_time_str]['value'] = self.FLUCT_BEARISH_L5
            elif leaf['value'] == 'FLUCT_BEARISH_L6':
                self.cache[result_time_str]['value'] = self.FLUCT_BEARISH_L6
            elif leaf['value'] == 'FLUCT_BEARISH_L7':
                self.cache[result_time_str]['value'] = self.FLUCT_BEARISH_L7
            elif leaf['value'] == 'FLUCT_BEARISH_L8':
                self.cache[result_time_str]['value'] = self.FLUCT_BEARISH_L8
            elif leaf['value'] == 'FLUCT_BEARISH_L9':
                self.cache[result_time_str]['value'] = self.FLUCT_BEARISH_L9
            elif leaf['value'] == 'FLUCT_BEARISH_L10':
                self.cache[result_time_str]['value'] = self.FLUCT_BEARISH_L10
            elif leaf['value'] == 'NA':
                self.cache[result_time_str]['value'] = self.NA

        if self.p.debug:
            stdout_log(f"{self.__class__.__name__}, result_time_str: {result_time_str}, {internal_key}: {item.get(internal_key, None)}")

    # 它的返回值表示这个信号的生成时间戳 目的是让BaseIndicator打印信号的生成延迟
    def determine_final_result(self):
        current_bar_time = self.data.datetime.datetime(0).replace(tzinfo=pytz.utc).astimezone()
        current_bar_time_str = current_bar_time.strftime('%Y-%m-%d %H:%M:%S')
        self.lines.fluct[0] = self.cache[current_bar_time_str]['value']

        root_create_time = self.cache[current_bar_time_str]['create_time']
        line = getattr(self.lines, 'delay', None)
        if line is not None:
            leaf_close_time = self.cache[current_bar_time_str]['raw_material_time']
            self.lines.delay[0] = (root_create_time - leaf_close_time) / 1000.0

        return root_create_time

    def get_internal_key(self):
        return 'TYPE_FLUCTUATION' if self.p.version is None else f'TYPE_FLUCTUATION_{str(self.p.version).upper()}'