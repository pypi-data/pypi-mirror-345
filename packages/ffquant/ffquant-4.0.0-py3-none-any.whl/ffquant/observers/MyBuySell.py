import backtrader as bt
import pytz
import ffquant.utils.global_backtest_data as global_backtest_data
from backtrader.lineiterator import LineIterator

__ALL__ = ['MyBuySell']

# 用于记录买卖点、指标的值的信息
# 通过cerebro加进去的Observer 会为每个strategy都加一个Observer 所以这里操作全局变量的时候 需要去重
class MyBuySell(bt.observers.BuySell):

    def __init__(self):
        super(MyBuySell, self).__init__()
        self.indcs = global_backtest_data.indcs

    def start(self):
        super(MyBuySell, self).start()

        strategy = self._owner
        for ind in strategy._lineiterators[LineIterator.IndType]:
            cur_key = f"{strategy.__class__.__name__}.{ind.__class__.__name__}"

            existing_cnt = 0
            for k, v in self.indcs.items():
                if k == cur_key or k.startswith(f"{cur_key}-"):
                    existing_cnt += 1
            if existing_cnt > 0:
                self.indcs[f"{cur_key}-{existing_cnt + 1}"] = []
            else:
                self.indcs[cur_key] = []

    # 这个next方法会在策略的next方法之后执行
    def next(self):
        super(MyBuySell, self).next()

        indc_cnt_dict = {}
        strategy = self._owner
        for indc in strategy._lineiterators[LineIterator.IndType]:
            key = f"{strategy.__class__.__name__}.{indc.__class__.__name__}"
            indc_cnt = indc_cnt_dict.get(key, 0)
            indc_cnt_dict[key] = indc_cnt + 1

            indicator_values = self.indcs[key if indc_cnt == 0 else f"{key}-{indc_cnt + 1}"]
            indicator_values.append(indc[0])