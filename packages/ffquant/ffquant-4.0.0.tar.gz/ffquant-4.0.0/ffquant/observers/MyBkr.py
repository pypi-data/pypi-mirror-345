import backtrader as bt
import pytz
import ffquant.utils.global_backtest_data as global_backtest_data

__ALL__ = ['MyBkr']

# 用于记录账户价值、k线数据、仓位信息
# 通过cerebro加进去的Observer 会为每个strategy都加一个Observer 所以这里操作全局变量的时候 需要去重
class MyBkr(bt.observers.Broker):
    def __init__(self):
        super(MyBkr, self).__init__()
        self.broker_values = global_backtest_data.broker_values
        self.klines = global_backtest_data.klines
        self.positions = global_backtest_data.positions

    def start(self):
        super(MyBkr, self).start()
        self.broker_values.clear()
        self.klines.clear()
        self.positions.clear()

    # 这个next方法会在策略的next方法之后执行
    def next(self):
        super(MyBkr, self).next()

        # 记录账户价值 需要去重
        dt = self.data.datetime.datetime(0).replace(tzinfo=pytz.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")
        is_duplicate = False
        for item in self.broker_values:
            if item['datetime'] == dt:
                is_duplicate = True
                break
        if not is_duplicate:
            msg = {
                "datetime": dt,
                "value": self.lines.value[0]
            }
            self.broker_values.append(msg)

        for i in range(0, len(self.datas)):
            symbol = self.datas[i].p.symbol

            # 记录k线 需要去重
            symbol_klines = self.klines.get(symbol, [])
            dt = self.datas[i].datetime.datetime(0).replace(tzinfo=pytz.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")
            is_duplicate = False
            for item in symbol_klines:
                if item['datetime'] == dt:
                    is_duplicate = True
                    break
            if not is_duplicate:
                symbol_klines.append({
                    "datetime": dt,
                    "open": self.datas[i].open[0],
                    "high": self.datas[i].high[0],
                    "low": self.datas[i].low[0],
                    "close": self.datas[i].close[0]
                })
                self.klines[symbol] = symbol_klines

            # 记录仓位 需要去重
            symbol_positions = self.positions.get(symbol, [])
            is_duplicate = False
            for item in symbol_positions:
                if item['datetime'] == dt:
                    is_duplicate = True
                    break
            if not is_duplicate:
                symbol_positions.append({
                    "datetime": dt,
                    "size": self._owner.getposition(data=self.datas[i]).size,
                    "price": self._owner.getposition(data=self.datas[i]).price
                })
                self.positions[symbol] = symbol_positions
