import backtrader as bt
from ffquant.utils.Logger import Logger, stdout_log
import pytz
import requests
from ffquant.utils.Apollo import Apollo
from datetime import timedelta, datetime
import time
import ffquant.utils.global_backtest_data as global_backtest_data
from ffquant.utils.backtest_data_serialize import prepare_data_for_pickle
from ffquant.brokers.MyBrokerCombo import MyBrokerCombo
from ffquant.brokers.MyBackBrokerCombo import MyBackBrokerCombo
import copy

class BaseStrategy(bt.Strategy):
    params = (
        ('name', None),
        ('logger', None),
        ('debug', None),
        ('test', None),
        ("check_chosen_strat", False)
    )

    def __init__(self):
        if self.p.name is None:
            raise ValueError('name should not be None')

        if self.p.logger is not None:
            self.logger = self.p.logger
        elif self.p.name is not None:
            self.logger = Logger(self.p.name)

        self.apollo = Apollo()
        if self.logger is not None and self.logger.name is not None:
            # namespace名字长度限制为32
            self.apollo = Apollo(namespace=self.logger.name[-32:])

        self.TRADE_INTERVAL_SECONDS = 3

        self.backfill_net_pos_size = 0

    def next(self):
        if len(self) - self.data.p.backfill_size == 1:
            self.start()

        if isinstance(self.broker, MyBackBrokerCombo) or isinstance(self.broker, MyBrokerCombo):
            will_change, prev_broker, new_broker = self.broker._peek_active_broker(self.data)
            if will_change:
                self.before_active_broker_change(prev_broker, new_broker)

            changed, prev_broker, new_broker = self.broker._determine_active_broker(self.data)
            if changed:
                self.after_active_broker_changed(prev_broker, new_broker)

    def initialize(self):
        pass

    def start(self):
        pass

    def stop(self):
        opt_params = dict()
        opt_param_keys = global_backtest_data.opt_param_keys
        for key in opt_param_keys:
            opt_params[key] = getattr(self.p, key)

        opt_result = dict()
        opt_result['opt_params'] = opt_params
        opt_result['backtest_data'] = copy.deepcopy(prepare_data_for_pickle(script_name=''))
        global_backtest_data.opt_results.append(opt_result)

    def get_perf_stats(self, port):
        result = None
        try:
            url = f"http://127.0.0.1:{port}/api/stats"
            return requests.get(url).json()
        except Exception as e:
            stdout_log(f"Failed to get performance stats. return None")
        return result

    # 如果是回测模式 永远返回True 如果是实时模式 需要判断下一根k线的时间是否大于当前时间
    def should_continue_current_kline(self):
        return len(self) > self.data.p.backfill_size

    def is_backfill_done(self):
        return self.should_continue_current_kline()

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                message = ('BUY EXECUTED, Size: %.2f, Price: %.2f' %
                    (order.executed.size,
                     order.executed.price)) + f", Order id: {order.ref}"
                if order.info.get('message', None) is not None:
                    message = message + f", message: {order.info['message']}"
                if order.info.get('origin', None) is not None:
                    message = message + f", origin: {order.info['origin']}"
                self.logger.info(message)
            else:  # Sell
                message = ('SELL EXECUTED, Size: %.2f, Price: %.2f' %
                    (order.executed.size,
                     order.executed.price)) + f", Order id: {order.ref}"
                if order.info.get('message', None) is not None:
                    message = message + f", message: {order.info['message']}"
                if order.info.get('origin', None) is not None:
                    message = message + f", origin: {order.info['origin']}"
                self.logger.info(message)

        elif order.status in [order.Cancelled, order.Margin, order.Rejected]:
            self.logger.info(f"Order Cancelled/Margin/Rejected. Order id: {order.ref}")

    def trade_open_long(self, message="", origin=""):
        if self.is_backfill_done():
            if self.data.islive():
                time.sleep(self.TRADE_INTERVAL_SECONDS)
            order = self.buy(exectype=bt.Order.Market, size=self.p.order_size, is_close_pos=False, message=message, origin=origin)
            if order is not None:
                self.logger.info(f"trade_open_long, order id: {order.ref}, message: {message}, origin: {origin}")
            return order
        else:
            self.backfill_net_pos_size += self.p.order_size
            return None

    def trade_open_short(self, message="", origin=""):
        if self.is_backfill_done():
            if self.data.islive():
                time.sleep(self.TRADE_INTERVAL_SECONDS)
            order = self.sell(exectype=bt.Order.Market, size=self.p.order_size, is_close_pos=False, message=message, origin=origin)
            if order is not None:
                self.logger.info(f"trade_open_short, order id: {order.ref}, message: {message}, origin: {origin}")
            return order
        else:
            self.backfill_net_pos_size -= self.p.order_size
            return None

    def trade_close(self, message="", origin=""):
        if self.is_backfill_done():
            if self.data.islive():
                time.sleep(self.TRADE_INTERVAL_SECONDS)
            order = None
            if self.position.size > 0:
                order = self.sell(exectype=bt.Order.Market, size=abs(self.position.size), is_close_pos=True, message=message, origin=origin)
            elif self.position.size < 0:
                order = self.buy(exectype=bt.Order.Market, size=abs(self.position.size), is_close_pos=True, message=message, origin=origin)
            if order is not None:
                self.logger.info(f"trade_close, order id: {order.ref}, message: {message}, origin: {origin}")
            return order
        else:
            self.backfill_net_pos_size = 0
            return None

    def trade_open_long_limit(self, price, message="", origin=""):
        if self.data.islive():
            time.sleep(self.TRADE_INTERVAL_SECONDS)
        if not self.data.islive() or (self.data.islive() and self.broker.name == "tv"):
            price = price + self.price_diff
        order = self.buy(exectype=bt.Order.Limit, price=price, size=self.p.order_size, is_close_pos=False, message=message, origin=origin)
        if order is not None:
            self.logger.info(f"trade_open_long_limit, order id: {order.ref}, price: {price}, message: {message}, origin: {origin}")
        return order

    def trade_open_short_limit(self, price, message="", origin=""):
        if self.data.islive():
            time.sleep(self.TRADE_INTERVAL_SECONDS)
        order = self.sell(exectype=bt.Order.Limit, price=price, size=self.p.order_size, is_close_pos=False, message=message, origin=origin)
        if order is not None:
            self.logger.info(f"trade_open_short_limit, order id: {order.ref}, price: {price}, message: {message}, origin: {origin}")
        return order

    def trade_close_long_limit(self, price, message="", origin=""):
        if self.data.islive():
            time.sleep(self.TRADE_INTERVAL_SECONDS)
        order = self.sell(exectype=bt.Order.Limit, price=price, size=self.p.order_size, is_close_pos=True, message=message, origin=origin)
        if order is not None:
            self.logger.info(f"trade_close_long_limit, order id: {order.ref}, price: {price}, message: {message}, origin: {origin}")
        return order

    def trade_close_short_limit(self, price, message="", origin=""):
        if self.data.islive():
            time.sleep(self.TRADE_INTERVAL_SECONDS)
        if not self.data.islive() or (self.data.islive() and self.broker.name == "tv"):
            price = price + self.price_diff
        order = self.buy(exectype=bt.Order.Limit, price=price, size=self.p.order_size, is_close_pos=True, message=message, origin=origin)
        if order is not None:
            self.logger.info(f"trade_close_short_limit, order id: {order.ref}, price: {price}, message: {message}, origin: {origin}")
        return order

    def cancel_orders(self):
        if self.data.islive():
            time.sleep(self.TRADE_INTERVAL_SECONDS)
        self.fluct_limit_order_needed = False
        p_orders = self.broker.get_orders_open()
        if len(p_orders) > 0:
            self.logger.info(f"Pending order count: {len(p_orders)}")
            for p_order in p_orders:
                self.logger.info(f"Cancel pending order: {p_order.ref}")
                self.cancel(p_order)

    def before_active_broker_change(self, prev_broker, new_broker):
        self.logger.info(f"before_active_broker_change, active broker will change from {prev_broker} to {new_broker}")

    def after_active_broker_changed(self, prev_broker, new_broker):
        self.logger.info(f"after_active_broker_changed, active broker changed from {prev_broker} to {new_broker}")