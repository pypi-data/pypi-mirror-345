from backtrader.brokers.bbroker import BackBroker
import backtrader as bt
from ffquant.utils.Logger import stdout_log
from datetime import datetime

class MyBackBrokerCombo(BackBroker):

    def __init__(self, debug=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.brokers = list()
        self.active_broker = None
        self.debug = debug

        # 以下的字段是backtrader要调用的字段 这里只是为了兼容
        self.startingcash = None

    def get_id(self):
        if self.active_broker is not None:
            return self.active_broker.id
        else:
            stdout_log(f"[CRITICAL], {self.__class__.__name__}, get_id failed, no active broker found")
            return None
    id = property(get_id)

    def get_name(self):
        if self.active_broker is not None:
            return self.active_broker.name
        else:
            stdout_log(f"[CRITICAL], {self.__class__.__name__}, get_name failed, no active broker found")
            return None
    name = property(get_name)

    def start(self):
        super().start()
        self.startingcash = 0
        for broker in self.brokers:
            broker.start()
            self.startingcash += broker.startingcash

    def getcash(self):
        cash = 0
        for broker in self.brokers:
            cash += broker.getcash()
        return cash
    
    def getvalue(self, datas=None):
        value = 0
        for broker in self.brokers:
            value += broker.getvalue(datas=datas)
        return value
    
    def getposition(self, data=None):
        position = bt.Position()
        if self.active_broker is not None:
            position = self.active_broker.getposition(data=data)
        else:
            stdout_log(f"[CRITICAL], {self.__class__.__name__}, getposition failed, no active broker found")
        return position
    
    def cancel(self, order):
        ret = False
        if self.active_broker is not None:
            ret = self.active_broker.cancel(order)
        else:
            stdout_log(f"[CRITICAL], {self.__class__.__name__}, cancel failed, no active broker found")
        return ret
    
    def get_pending_orders(self):
        pending_orders = []
        for broker in self.brokers:
            pending_orders += broker.get_pending_orders()
        return pending_orders

    # 获取未完成的订单 这个方法跟get_pending_orders的功能一样 只是为了兼容backtrader的接口
    def get_orders_open(self):
        return self.get_pending_orders()

    def buy(self, owner, data,
            size, price=None, plimit=None,
            exectype=None, valid=None, tradeid=0, oco=None,
            trailamount=None, trailpercent=None,
            parent=None, transmit=True,
            histnotify=False, _checksubmit=True,
            **kwargs):
        order = None
        if self.active_broker is not None:
            order = self.active_broker.buy(owner=owner,
                                           data=data,
                                           size=size, price=price, pricelimit=plimit,
                                           exectype=exectype, valid=valid, tradeid=tradeid,
                                           trailamount=trailamount, trailpercent=trailpercent,
                                           parent=parent, transmit=transmit,
                                           histnotify=histnotify,
                                           _checksubmit=_checksubmit,
                                           **kwargs)
        return order

    def sell(self, owner, data,
             size, price=None, plimit=None,
             exectype=None, valid=None, tradeid=0, oco=None,
             trailamount=None, trailpercent=None,
             parent=None, transmit=True,
             histnotify=False, _checksubmit=True,
             **kwargs):
        order = None
        if self.active_broker is not None:
            order = self.active_broker.sell(owner=owner,
                                            data=data,
                                            size=size, price=price, pricelimit=plimit,
                                            exectype=exectype, valid=valid, tradeid=tradeid,
                                            trailamount=trailamount, trailpercent=trailpercent,
                                            parent=parent, transmit=transmit,
                                            histnotify=histnotify,
                                            _checksubmit=_checksubmit,
                                            **kwargs)
        return order
    
    def get_notification(self):
        notif = None
        if self.active_broker is not None:
            notif = self.active_broker.get_notification()
        else:
            stdout_log(f"[CRITICAL], {self.__class__.__name__}, get_notification failed, no active broker found")
        return notif

    # 对于实时情况而言 next方法会被频繁调用 每一次调用都会触发更新订单信息 所以 需要控制频率
    def next(self):
        for broker in self.brokers:
            broker.next()

    def get_order(self, order_id, sync=False):
        order = None
        if self.active_broker is not None:
            order = self.active_broker.get_order(order_id)
        else:
            stdout_log(f"[CRITICAL], {self.__class__.__name__}, get_order failed, no active broker found")
        return order

    def add_broker(self, broker):
        if broker not in self.brokers:
            self.brokers.append(broker)
            if len(self.brokers) == 1:
                self.active_broker = broker
        else:
            stdout_log(f"[CRITICAL], {self.__class__.__name__}, add_broker failed, broker already exists")

    def addcommissioninfo(self, comminfo, name=None):
        if self.active_broker is not None:
            self.active_broker.addcommissioninfo(comminfo, name=name)
        else:
            stdout_log(f"[CRITICAL], {self.__class__.__name__}, addcommissioninfo failed, no active broker found")

    def getcommissioninfo(self, data):
        if self.active_broker is not None:
            return self.active_broker.getcommissioninfo(data)
        else:
            stdout_log(f"[CRITICAL], {self.__class__.__name__}, getcommissioninfo failed, no active broker found")
            return None

    def _determine_active_broker(self, data):
        changed = False
        prev_active_broker = self.active_broker
        for broker in self.brokers:
            if broker._is_active(data):
                if self.active_broker is None or self.active_broker != broker:
                    changed = True
                    self.active_broker = broker
                break

        return changed, prev_active_broker, self.active_broker
    
    def _peek_active_broker(self, data):
        will_change = False
        prev_active_broker = self.active_broker
        new_active_broker = None

        # brokers这个队列的先后顺序是有意义的 如果在active_broker前面的broker是活跃的 那就认为是将要发生切换
        for broker in self.brokers:
            if broker == self.active_broker:
                break

            if (not broker._is_active(data)) and broker._is_active(data, peek=True):
                will_change = True
                new_active_broker = broker
                break

        if not will_change and self.active_broker._is_active(data) and not self.active_broker._is_active(data, peek=True):
            for broker in self.brokers:
                if broker == self.active_broker:
                    continue

                if broker._is_active(data, peek=True):
                    will_change = True
                    new_active_broker = broker
                    break
        return will_change, prev_active_broker, new_active_broker

    def _is_active(self, data):
        if self.active_broker is not None:
            return self.active_broker._is_active()
        else:
            return False