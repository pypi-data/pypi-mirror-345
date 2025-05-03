from ffquant.symbols.BaseSymbol import BaseSymbol
from datetime import time

class HKEX_Future(BaseSymbol):

    def __init__(self, symbol='', exchange=None):
        super(HKEX_Future, self).__init__(symbol=symbol, exchange=exchange)

    def _init_trading_hours(self):
        trading_hours = {}
        trading_hours[0] = [(time(9, 15), time(12, 0)), (time(13, 0), time(16, 30)), (time(17, 15), time(23, 59, 59))]
        trading_hours[1] = [(time(0, 0), time(3, 0)), (time(9, 15), time(12, 0)), (time(13, 0), time(16, 30)), (time(17, 15), time(23, 59, 59))]
        trading_hours[2] = [(time(0, 0), time(3, 0)), (time(9, 15), time(12, 0)), (time(13, 0), time(16, 30)), (time(17, 15), time(23, 59, 59))]
        trading_hours[3] = [(time(0, 0), time(3, 0)), (time(9, 15), time(12, 0)), (time(13, 0), time(16, 30)), (time(17, 15), time(23, 59, 59))]
        trading_hours[4] = [(time(0, 0), time(3, 0)), (time(9, 15), time(12, 0)), (time(13, 0), time(16, 30)), (time(17, 15), time(23, 59, 59))]
        trading_hours[5] = [(time(0, 0), time(3, 0))]

        return trading_hours
    
    def __str__(self):
        return self.symbol