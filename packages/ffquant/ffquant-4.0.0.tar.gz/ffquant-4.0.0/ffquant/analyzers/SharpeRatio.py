import backtrader as bt
import numpy as np

class SharpeRatio(bt.Analyzer):

    params = (
        ('riskfreerate', 0.01),
    )

    _TANN = {
        bt.TimeFrame.Seconds: 5_896_800.0,
        bt.TimeFrame.Minutes: 98_280.0,
        bt.TimeFrame.Days: 252.0,
        bt.TimeFrame.Weeks: 52.0,
        bt.TimeFrame.Months: 12.0,
        bt.TimeFrame.Years: 1.0,
    }

    def __init__(self):
        self._value_start = None
        self._value_end = None
        self._tcount = None
        self.timereturn = bt.analyzers.TimeReturn()

    def start(self):
        super(SharpeRatio, self).start()
        self._value_start = self.strategy.broker.getvalue()
        self._tcount = 0

    def stop(self):
        super(SharpeRatio, self).stop()
        self._value_end = self.strategy.broker.getvalue()

        rtot = self._value_end / self._value_start - 1.0

        timeframe = self.data.p.timeframe
        compression = self.data.p.compression
        tann = self._TANN.get(timeframe) / compression

        days_in_year = 252.0
        bars_per_day = tann / days_in_year

        annual_return = (1 + rtot / (self._tcount / bars_per_day)) ** days_in_year - 1

        std_per_bar = np.std([item['timereturn'] for item in self.timereturn.get_analysis().values()])
        std_annual = std_per_bar * np.sqrt(days_in_year * bars_per_day)

        sharpe = "NaN"
        if std_annual != 0:
            sharpe = (annual_return - self.p.riskfree_rate) / std_annual

        self.rets['sharperatio'] = sharpe

    def _on_dt_over(self):
        self._tcount += 1