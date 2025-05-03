from ffquant.symbols.BaseSymbol import BaseSymbol
from datetime import time

class US_Stock(BaseSymbol):

    def __init__(self, symbol='', exchange=None):
        super(US_Stock, self).__init__(symbol=symbol, exchange=exchange)

    def _init_trading_hours(self):
        trading_hours = {}
        trading_hours[0] = [(time(16, 0), time(21, 29)), (time(21, 30), time(23, 59, 59))]
        trading_hours[1] = [(time(0, 0), time(3, 59)), (time(4, 0), time(8, 0)), (time(16, 0), time(21, 29)), (time(21, 30), time(23, 59, 59))]
        trading_hours[2] = [(time(0, 0), time(3, 59)), (time(4, 0), time(8, 0)), (time(16, 0), time(21, 29)), (time(21, 30), time(23, 59, 59))]
        trading_hours[3] = [(time(0, 0), time(3, 59)), (time(4, 0), time(8, 0)), (time(16, 0), time(21, 29)), (time(21, 30), time(23, 59, 59))]
        trading_hours[4] = [(time(0, 0), time(3, 59)), (time(4, 0), time(8, 0)), (time(16, 0), time(21, 29)), (time(21, 30), time(23, 59, 59))]
        trading_hours[5] = [(time(0, 0), time(3, 59)), (time(4, 0), time(8, 0))]

        return trading_hours
    
    def __str__(self):
        return self.symbol