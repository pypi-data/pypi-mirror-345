import backtrader as bt
import pytz
import ffquant.utils.global_backtest_data as global_backtest_data

__ALL__ = ['MyTimeReturn']

# 通过cerebro加进去的Observer 会为每个strategy都加一个Observer 所以这里操作全局变量的时候 需要去重
class MyTimeReturn(bt.observers.TimeReturn):
    def __init__(self):
        super(MyTimeReturn, self).__init__()
        self.treturns = global_backtest_data.treturns

    def start(self):
        super(MyTimeReturn, self).start()
        self.treturns.clear()

    # 这个next方法会在策略的next方法之后执行
    def next(self):
        super(MyTimeReturn, self).next()
        dt = self.data.datetime.datetime(0).replace(tzinfo=pytz.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")
        is_duplicate = False
        for item in self.treturns:
            if item['datetime'] == dt:
                is_duplicate = True
                break
        if not is_duplicate:
            msg = {
                "datetime": dt,
                "timereturn": self.lines.timereturn[0]
            }
            self.treturns.append(msg)
