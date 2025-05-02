from ffquant.symbols.BaseSymbol import BaseSymbol
from datetime import time

class HK_Stock(BaseSymbol):

    def __init__(self, symbol='', exchange=None):
        super(HK_Stock, self).__init__(symbol=symbol, exchange=exchange)

    def _init_trading_hours(self):
        trading_hours = {}
        trading_hours[0] = [(time(9, 0), time(12, 0)), (time(13, 0), time(16, 0))]
        trading_hours[1] = [(time(9, 0), time(12, 0)), (time(13, 0), time(16, 0))]
        trading_hours[2] = [(time(9, 0), time(12, 0)), (time(13, 0), time(16, 0))]
        trading_hours[3] = [(time(9, 0), time(12, 0)), (time(13, 0), time(16, 0))]
        trading_hours[4] = [(time(9, 0), time(12, 0)), (time(13, 0), time(16, 0))]

        return trading_hours
    
    def __str__(self):
        return self.symbol