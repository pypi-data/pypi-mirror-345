import backtrader as bt
import pytz
from datetime import datetime, timedelta, timezone
from ffquant.indicators.IndexListIndicator import IndexListIndicator
from ffquant.utils.Logger import stdout_log

__ALL__ = ['ProdBuySellSeqZyj']

class ProdBuySellSeqZyj(IndexListIndicator):
    lines = (
        "futureSeq",
        "bearSeq",
        "zyjMinMaxDiffChange",
        "zyjMinMaxDiff",
        "futureZyj",
        "etf",
        "bullZyj",
        "closeTime",
        "indexSeq",
        "bear",
        "lvetfSeq",
        "openTime",
        "stock",
        "stockZyj",
        "cnetfSeq",
        "etfZyj",
        "bullSeq",
        "stockSeq",
        "etfSeq",
        "lvetf",
        "indx",
        "cnetf",
        "indexZyj",
        "cnetfZyj",
        "lvetfZyj",
        "future",
        "bull",
        "bearZyj",
    )

    def handle_api_resp(self, result):
        result_time_str = datetime.fromtimestamp(result['closeTime'] / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
        self.cache[result_time_str] = result

    # 子类需要实现这个方法 决定最后返回给backtrader框架的indicator结果
    def determine_final_result(self):
        self.lines.futureSeq[0] = float('-inf')
        self.lines.bearSeq[0] = float('-inf')
        self.lines.zyjMinMaxDiffChange[0] = float('-inf')
        self.lines.zyjMinMaxDiff[0] = float('-inf')
        self.lines.futureZyj[0] = float('-inf')
        self.lines.etf[0] = float('-inf')
        self.lines.bullZyj[0] = float('-inf')
        self.lines.closeTime[0] = float('-inf')
        self.lines.indexSeq[0] = float('-inf')
        self.lines.bear[0] = float('-inf')
        self.lines.lvetfSeq[0] = float('-inf')
        self.lines.openTime[0] = float('-inf')
        self.lines.stock[0] = float('-inf')
        self.lines.stockZyj[0] = float('-inf')
        self.lines.cnetfSeq[0] = float('-inf')
        self.lines.etfZyj[0] = float('-inf')
        self.lines.bullSeq[0] = float('-inf')
        self.lines.stockSeq[0] = float('-inf')
        self.lines.etfSeq[0] = float('-inf')
        self.lines.lvetf[0] = float('-inf')
        self.lines.indx[0] = float('-inf')
        self.lines.cnetf[0] = float('-inf')
        self.lines.indexZyj[0] = float('-inf')
        self.lines.cnetfZyj[0] = float('-inf')
        self.lines.lvetfZyj[0] = float('-inf')
        self.lines.future[0] = float('-inf')
        self.lines.bull[0] = float('-inf')
        self.lines.bearZyj[0] = float('-inf')

        current_bar_time = self.data.datetime.datetime(0).replace(tzinfo=pytz.utc).astimezone()
        cache_key_time = current_bar_time
        if current_bar_time.second != 0:
            cache_key_time = current_bar_time.replace(second=0, microsecond=0)
        cache_key_time_str = cache_key_time.strftime('%Y-%m-%d %H:%M:%S')

        result = None
        if cache_key_time_str in self.cache:
            result = self.cache[cache_key_time_str]

        if result is not None:
            for key, value in dict(result).items():
                if key in self.lines.getlinealiases():
                    if key == 'openTime' or key == 'closeTime':
                        continue

                    if str(key).endswith('Seq') or str(key).endswith('Zyj') or str(key).endswith('Diff') or str(key).endswith('DiffChange'):
                        line = getattr(self.lines, key)
                        line[0] = float(value)
                    elif str(value) != '':
                        if key == 'index':
                            key = 'indx'
                        line = getattr(self.lines, key)
                        if str(value) == 'B':
                            line[0] = 1
                        elif str(value) == 'S':
                            line[0] = -1
            return result['closeTime']
        else:
            return 0

    def prepare_params(self, start_time_str, end_time_str):
        params = {
            'symbol': "HSI",    # 这个信号只针对HSI 所以在这里写死
            'type': 'index_zyj',
            'key_list': 'prod_bs_seq_zyj',
            'startTime' : start_time_str,
            'endTime' : end_time_str
        }

        return params