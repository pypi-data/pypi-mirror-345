import backtrader as bt
from ffquant.utils.Logger import stdout_log
import pytz
import math

__ALL__ = ['FakeFeed']

class FakeFeed(bt.feeds.DataBase):
    params = (
        ('symbol', None),
        ('original_data', None),
        ('debug', False)
    )

    lines = (('turnover'),)

    def __init__(self):
        super(FakeFeed, self).__init__()
        self.original_data = self.p.original_data

    def islive(self):
        return self.original_data.islive()

    def _load(self):
        if self.islive():
            if len(self.original_data) == len(self):
                self.lines.datetime[0] = self.original_data.lines.datetime[0]
                self.lines.open[0] = self.original_data.lines.open[0]
                self.lines.high[0] = self.original_data.lines.high[0]
                self.lines.low[0] = self.original_data.lines.low[0]
                self.lines.close[0] = self.original_data.lines.close[0]
                self.lines.volume[0] = self.original_data.lines.volume[0]
                self.lines.turnover[0] = self.original_data.lines.turnover[0]
                return True
            else:
                return
        else:
            orig_data_size = len(self.original_data.array)
            self_data_size = len(self)
            if self_data_size <= orig_data_size:
                self.lines.datetime[0] = self.original_data.lines.datetime.array[self_data_size - 1]
                self.lines.open[0] = self.original_data.lines.open.array[self_data_size - 1]
                self.lines.high[0] = self.original_data.lines.high.array[self_data_size - 1]
                self.lines.low[0] = self.original_data.lines.low.array[self_data_size - 1]
                self.lines.close[0] = self.original_data.lines.close.array[self_data_size - 1]
                self.lines.volume[0] = self.original_data.lines.volume.array[self_data_size - 1]
                self.lines.turnover[0] = self.original_data.lines.turnover.array[self_data_size - 1]
                return True
            return False