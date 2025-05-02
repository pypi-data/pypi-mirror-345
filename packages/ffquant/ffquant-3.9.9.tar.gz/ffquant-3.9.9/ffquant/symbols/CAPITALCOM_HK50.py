from ffquant.symbols.BaseSymbol import BaseSymbol
from datetime import time

class CAPITALCOM_HK50(BaseSymbol):

    def __init__(self):
        super(CAPITALCOM_HK50, self).__init__(symbol="HK50", exchange="CAPITALCOM")

    def _init_trading_hours(self):
        trading_hours = {}
        trading_hours[0] = [(time(6, 0), time(23, 59, 59))]
        trading_hours[1] = [(time(0, 0), time(5, 0)), (time(6, 0), time(23, 59, 59))]
        trading_hours[2] = [(time(0, 0), time(5, 0)), (time(6, 0), time(23, 59, 59))]
        trading_hours[3] = [(time(0, 0), time(5, 0)), (time(6, 0), time(23, 59, 59))]
        trading_hours[4] = [(time(0, 0), time(5, 0)), (time(6, 0), time(23, 59, 59))]
        trading_hours[5] = [(time(0, 0), time(5, 0))]

        return trading_hours
    
    def __str__(self):
        return "CAPITALCOM:HK50"