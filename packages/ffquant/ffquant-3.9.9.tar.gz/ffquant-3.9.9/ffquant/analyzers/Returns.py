import backtrader as bt

class Returns(bt.analyzers.Returns):
    _TANN = {
        bt.TimeFrame.Seconds: 5_896_800.0,
        bt.TimeFrame.Minutes: 98_280.0,
        bt.TimeFrame.Days: 252.0,
        bt.TimeFrame.Weeks: 52.0,
        bt.TimeFrame.Months: 12.0,
        bt.TimeFrame.Years: 1.0,
    }

    def start(self):
        super(Returns, self).start()
        self._value_start = self.strategy.broker.getvalue()
        self._tcount = 0

    def stop(self):        
        super(Returns, self).stop()
        self._value_end = self.strategy.broker.getvalue()

        self.rets['rtot'] = rtot = self._value_end / self._value_start - 1.0
        self.rets['ravg'] = ravg = rtot / self._tcount

        timeframe = self.data.p.timeframe
        compression = self.data.p.compression
        tann = self._TANN.get(timeframe) / compression

        days_in_year = 252.0
        bars_per_day = tann / days_in_year

        self.rets['rnorm'] = rnorm = (1 + rtot / (self._tcount / bars_per_day)) ** days_in_year - 1
        self.rets['rnorm100'] = rnorm100 = rnorm * 100.0

    def _on_dt_over(self):
        self._tcount += 1