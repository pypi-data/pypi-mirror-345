from backtrader.brokers.bbroker import BackBroker
from backtrader.order import Order
from datetime import datetime, timedelta
import backtrader as bt
import pytz
from ffquant.symbols.CAPITALCOM_HK50 import CAPITALCOM_HK50
from ffquant.symbols.HKEX_Future import HKEX_Future

class MyBackBroker(BackBroker):

    params = (
        ('conc', False),
    )

    def __init__(self, id=None, name="tv", debug=False, *args, **kwargs):
        super().__init__()

        self.id = id
        self.name = name

        self.debug = debug

    def _try_exec(self, order):
        data = order.data

        popen = getattr(data, 'tick_open', None)
        if popen is None:
            popen = data.open[0]
        phigh = getattr(data, 'tick_high', None)
        if phigh is None:
            phigh = data.high[0]
        plow = getattr(data, 'tick_low', None)
        if plow is None:
            plow = data.low[0]
        pclose = getattr(data, 'tick_close', None)
        if pclose is None:
            pclose = data.close[0]

        pcreated = order.created.price
        plimit = order.created.pricelimit

        if order.exectype == Order.Market:
            self._try_exec_market(order, popen, phigh, plow, pclose)

        elif order.exectype == Order.Close:
            self._try_exec_close(order, pclose)

        elif order.exectype == Order.Limit:
            self._try_exec_limit(order, popen, phigh, plow, pcreated)

        elif (order.triggered and
              order.exectype in [Order.StopLimit, Order.StopTrailLimit]):
            self._try_exec_limit(order, popen, phigh, plow, plimit)

        elif order.exectype in [Order.Stop, Order.StopTrail]:
            self._try_exec_stop(order, popen, phigh, plow, pcreated, pclose)

        elif order.exectype in [Order.StopLimit, Order.StopTrailLimit]:
            self._try_exec_stoplimit(order,
                                     popen, phigh, plow, pclose,
                                     pcreated, plimit)

        elif order.exectype == Order.Historical:
            self._try_exec_historical(order)

    def _try_exec_market(self, order, popen, phigh, plow, pclose=None):
        ago = 0
        if self.p.coc and order.info.get('coc', True):
            dtcoc = order.created.dt
            exprice = order.created.pclose
        else:
            if not self.p.coo and order.data.datetime[0] <= order.created.dt:
                return    # can only execute after creation time

            dtcoc = None
            exprice = popen

            if self.p.conc:
                exprice = pclose

        if order.isbuy():
            p = self._slip_up(phigh, exprice, doslip=self.p.slip_open)
        else:
            p = self._slip_down(plow, exprice, doslip=self.p.slip_open)

        self._execute(order, ago=0, price=p, dtcoc=dtcoc)

    def _execute(self, order, ago=None, price=None, cash=None, position=None,
                 dtcoc=None):

        # ago = None is used a flag for pseudo execution
        if ago is not None and price is None:
            return  # no psuedo exec no price - no execution

        if self.p.filler is None or ago is None:
            # Order gets full size or pseudo-execution
            size = order.executed.remsize
        else:
            # Execution depends on volume filler
            size = self.p.filler(order, price, ago)
            if not order.isbuy():
                size = -size

        # Get comminfo object for the data
        comminfo = self.getcommissioninfo(order.data)

        # Check if something has to be compensated
        if order.data._compensate is not None:
            data = order.data._compensate
            cinfocomp = self.getcommissioninfo(data)  # for actual commission
        else:
            data = order.data
            cinfocomp = comminfo

        # Adjust position with operation size
        if ago is not None:
            # Real execution with date
            position = self.positions[data]
            pprice_orig = position.price

            psize, pprice, opened, closed = position.pseudoupdate(size, price)

            # if part/all of a position has been closed, then there has been
            # a profitandloss ... record it
            pnl = comminfo.profitandloss(-closed, pprice_orig, price)
            cash = self.cash
        else:
            pnl = 0
            if not self.p.coo:
                price = pprice_orig = order.created.price
            else:
                # When doing cheat on open, the price to be considered for a
                # market order is the opening price and not the default closing
                # price with which the order was created
                if order.exectype == Order.Market:
                    price = pprice_orig = order.data.open[0]
                else:
                    price = pprice_orig = order.created.price
            
            # cheat on next close
            if self.p.conc:
                price = pprice_orig = order.data.close[0]

            psize, pprice, opened, closed = position.update(size, price)

        # "Closing" totally or partially is possible. Cash may be re-injected
        if closed:
            # Adjust to returned value for closed items & acquired opened items
            if self.p.shortcash:
                closedvalue = comminfo.getvaluesize(-closed, pprice_orig)
            else:
                closedvalue = comminfo.getoperationcost(closed, pprice_orig)

            closecash = closedvalue
            if closedvalue > 0:  # long position closed
                closecash /= comminfo.get_leverage()  # inc cash with lever

            cash += closecash + pnl * comminfo.stocklike
            # Calculate and substract commission
            closedcomm = comminfo.getcommission(closed, price)
            cash -= closedcomm

            if ago is not None:
                # Cashadjust closed contracts: prev close vs exec price
                # The operation can inject or take cash out
                cash += comminfo.cashadjust(-closed,
                                            position.adjbase,
                                            price)

                # Update system cash
                self.cash = cash
        else:
            closedvalue = closedcomm = 0.0

        popened = opened
        if opened:
            if self.p.shortcash:
                openedvalue = comminfo.getvaluesize(opened, price)
            else:
                openedvalue = comminfo.getoperationcost(opened, price)

            opencash = openedvalue
            if openedvalue > 0:  # long position being opened
                opencash /= comminfo.get_leverage()  # dec cash with level

            cash -= opencash  # original behavior

            openedcomm = cinfocomp.getcommission(opened, price)
            cash -= openedcomm

            if cash < 0.0:
                # execution is not possible - nullify
                opened = 0
                openedvalue = openedcomm = 0.0

            elif ago is not None:  # real execution
                if abs(psize) > abs(opened):
                    # some futures were opened - adjust the cash of the
                    # previously existing futures to the operation price and
                    # use that as new adjustment base, because it already is
                    # for the new futures At the end of the cycle the
                    # adjustment to the close price will be done for all open
                    # futures from a common base price with regards to the
                    # close price
                    adjsize = psize - opened
                    cash += comminfo.cashadjust(adjsize,
                                                position.adjbase, price)

                # record adjust price base for end of bar cash adjustment
                position.adjbase = price

                # update system cash - checking if opened is still != 0
                self.cash = cash
        else:
            openedvalue = openedcomm = 0.0

        if ago is None:
            # return cash from pseudo-execution
            return cash

        execsize = closed + opened

        if execsize:
            # Confimrm the operation to the comminfo object
            comminfo.confirmexec(execsize, price)

            # do a real position update if something was executed
            position.update(execsize, price, data.datetime.datetime())

            if closed and self.p.int2pnl:  # Assign accumulated interest data
                closedcomm += self.d_credit.pop(data, 0.0)

            # Execute and notify the order
            order.execute(dtcoc or data.datetime[ago],
                          execsize, price,
                          closed, closedvalue, closedcomm,
                          opened, openedvalue, openedcomm,
                          comminfo.margin, pnl,
                          psize, pprice)

            order.addcomminfo(comminfo)

            self.notify(order)
            self._ococheck(order)

        if popened and not opened:
            # opened was not executed - not enough cash
            order.margin()
            self.notify(order)
            self._ococheck(order)
            self._bracketize(order, cancel=True)

    def _is_active(self, data, peek=False):
        kline_time = data.datetime.datetime(0).replace(tzinfo=pytz.utc).astimezone()
        if peek:
            if data.p.timeframe == bt.TimeFrame.Minutes:
                kline_time = kline_time + timedelta(minutes=data.p.compression)
            elif data.p.timeframe == bt.TimeFrame.Seconds:
                kline_time = kline_time + timedelta(seconds=data.p.compression)

        ret = False
        if self.name == 'tv':
            if data.p.symbol == "CAPITALCOM:HK50":
                ret = CAPITALCOM_HK50().is_trading_time(kline_time)
        elif self.name == 'futu':
            if data.p.symbol == "CAPITALCOM:HK50":
                ret = HKEX_Future().is_trading_time(kline_time)
        return ret