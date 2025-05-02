import backtrader as bt
from datetime import datetime, timedelta
import os
import requests
import json
from backtrader.utils.py3 import queue
import collections
from backtrader.position import Position
import getpass
from ffquant.utils.Logger import stdout_log
from urllib.parse import urlencode
import pytz
from ffquant.symbols.CAPITALCOM_HK50 import CAPITALCOM_HK50
from ffquant.symbols.HKEX_Future import HKEX_Future

__ALL__ = ['MyBroker']

class MyBroker(bt.BrokerBase):
    # 以下是交易账号的对应关系 TV代表TradingView
    (TV_SIM1, TV_SIM2, TV_SIM3, TV_SIM4, TV_SIM5, TV_TEST1, TV_TEST2, TV_TEST3, FUTU_SIM1, FUTU_REAL) = ("14078173", "14267474", "14267483", "15539511", "15539514", "15539534", "15539537", "15539538", "9598674", "281756473194939823")

    def __init__(self, id=None, name="tv", debug=False, *args, **kwargs):
        super(MyBroker, self).__init__(*args, **kwargs)
        self.base_url = 'http://192.168.25.247:8220'
        self.id = id  # 交易账号的ID 参考上面的对应关系
        self.name = name # 券商的名字 tv或者futu
        self.cash = None # 账户的现金余额
        self.value = None # 账户的总市值

        self.orders = {} # 订单信息缓存
        self.pending_orders = list() # 未完成的订单
        self.notifs = queue.Queue() # 等待发送到策略的通知
        self.debug = debug
        self.positions = collections.defaultdict(Position) # symbol维度记录仓位信息
        self.MIN_UPDATE_INTERVAL_SECONDS = 10 # 更新仓位和账户信息的间隔 因为券商有请求频率限制 所以不能太频繁
        self.last_cashvalue_update_ts = 0    # 最后一次更新账户信息的时间
        self.last_order_update_ts = 0   # 最后一次更新订单信息的时间
        self.last_position_update_ts = 0    # 最后一次更新仓位信息的时间

        # 以下的字段是backtrader要调用的字段 这里只是为了兼容
        self.startingcash = None

    def start(self):
        super().start()
        self.startingcash = self.getcash(sync=True)

    # 获取账户信息 非实时
    def getcash(self, sync=False):
        self._update_cashvalue(force_update=sync)
        return self.cash

    # 获取账户总市值 非实时
    def getvalue(self, datas=None, sync=False):
        self._update_cashvalue(force_update=sync)
        return self.value

    # 获取仓位 非实时
    def getposition(self, data=None, sync=False):
        position = bt.Position()

        symbol = self._convert_symbol(data.p.symbol)
        self._update_positions(force_update=(not self.positions.__contains__(symbol)) or sync)
        position = self.positions[symbol]

        if self.debug:
            stdout_log(f"{self.__class__.__name__}, getposition, symbol: {symbol}, position size: {position.size}, price: {position.price}")

        return position

    # 取消订单 需要传入backtrader的Order对象
    def cancel(self, order):
        order_id = order.ref
        url = self.base_url + f"/cancel/order/{self.name}/{self.id}"
        data = {
            "tradeId": order_id,
        }
        payload = urlencode({"content": json.dumps(data)})
        if self.debug:
            stdout_log(f"{self.__class__.__name__}, cancel, payload: {payload}")

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.post(url, headers=headers, data=payload).json()
        if self.debug:
            stdout_log(f"{self.__class__.__name__}, cancel, response: {response}")

        ret = True
        code = response['code']
        if code != '200':
            stdout_log(f"[CRITICAL], {self.__class__.__name__}, cancel failed, url: {url}, payload: {payload}, response: {response}")
            ret = False
        return ret

    # 获取未完成的订单
    def get_pending_orders(self, sync=False):
        self._update_orders(force_update=sync)
        return self.pending_orders

    # 获取未完成的订单 这个方法跟get_pending_orders的功能一样 只是为了兼容backtrader的接口
    def get_orders_open(self, sync=False):
        return self.get_pending_orders(sync=sync)

    # 提交订单 所有的buy和sell都通过这个方法实现
    def submit(self, order, **kwargs):
        url = self.base_url + f"/place/order/{self.name}/{self.id}"

        # is_close_pos用来标识是否是平仓 如果不传则认为是开仓
        side = None
        if order.ordtype == bt.Order.Buy:
            if kwargs.get('is_close_pos', False):
                side = 'close'
            else:
                side = 'long'
        elif order.ordtype == bt.Order.Sell:
            if kwargs.get('is_close_pos', False):
                side = 'cover'
            else:
                side = 'short'

        order.size = abs(order.size)
        # 这里的username是为了建立linux的用户名和券商账户的对应关系 追踪是谁在提交订单 以及订单的权限控制
        username = getpass.getuser()
        username = username[8:] if username.startswith('jupyter-') else username

        # message一般包含了触发订单的原因
        msg = ""
        if kwargs.get("message", None) is not None:
            msg = msg + kwargs.get("message")

        data = {
            "symbol": self._convert_symbol(order.data.p.symbol),
            "side": side,
            "qty": order.size,
            "price": order.price,
            "type": "market" if order.exectype == bt.Order.Market else "limit",
            "username": username,
            "message": msg
        }
        payload = urlencode({"content": json.dumps(data)})
        if self.debug:
            stdout_log(f"{self.__class__.__name__}, submit, payload: {payload}")

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.post(url, headers=headers, data=payload).json()
        if self.debug:
            stdout_log(f"{self.__class__.__name__}, submit, response: {response}")

        order_id = None
        if response.get('code') == "200":
            order_id = response['results']
            order.status = bt.Order.Submitted
            order.ref = order_id
            for key, value in kwargs.items():
                if key == "origin" and (value is None or value == ''):
                    value = "Unknown"
                order.addinfo(**{key: value})

            self.orders[order_id] = order

            kline_local_time_str = order.data.datetime.datetime(0).replace(tzinfo=pytz.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S')
            # 这里的打印是为了在日志中体现出成功订单的信息 用于监控目的
            stdout_log(f"[INFO], {self.__class__.__name__}, kline time: {kline_local_time_str}, submit success, url: {url}, data: {data}, response: {response}")
        else:
            # 这里的打印是为了在日志中体现出失败订单的信息 用于监控目的
            stdout_log(f"[CRITICAL], {self.__class__.__name__}, submit failed, url: {url}, payload: {payload}, response: {response}")

        return order

    def buy(self, owner, data, size, price=None, plimit=None, exectype=None, valid=None, tradeid=0, oco=None, trailamount=None, trailpercent=None, **kwargs):
        order = bt.order.BuyOrder(owner=owner, data=data, size=size, price=price, pricelimit=plimit, exectype=exectype, valid=valid, tradeid=tradeid, oco=oco, trailamount=trailamount, trailpercent=trailpercent)
        return self.submit(order, **kwargs)

    def sell(self, owner, data, size, price=None, plimit=None, exectype=None, valid=None, tradeid=0, oco=None, trailamount=None, trailpercent=None, **kwargs):
        order = bt.order.SellOrder(owner=owner, data=data, size=size, price=price, pricelimit=plimit, exectype=exectype, valid=valid, tradeid=tradeid, oco=oco, trailamount=trailamount, trailpercent=trailpercent)
        return self.submit(order, **kwargs)
    
    # 这个方法是被backtrader框架调用的 策略不要调用这个方法
    def get_notification(self):
        notif = None
        try:
            notif = self.notifs.get(False)
        except queue.Empty:
            pass

        return notif

    # 对于实时情况而言 next方法会被频繁调用 每一次调用都会触发更新订单信息 所以 需要控制频率
    def next(self):
        self._update_orders()

        # Update positions
        self._update_positions()

        # Update cash & value
        self._update_cashvalue()

    def get_order(self, order_id, sync=False):
        self._update_orders(force_update=sync)
        return self.orders.get(order_id, None)

    def _update_cashvalue(self, force_update=False):
        if force_update or datetime.now().timestamp() - self.last_cashvalue_update_ts > self.MIN_UPDATE_INTERVAL_SECONDS:
            self.last_cashvalue_update_ts = datetime.now().timestamp()
            url = self.base_url + f"/balance/{self.name}/{self.id}"
            response = requests.get(url).json()
            if self.debug:
                stdout_log(f"{self.__class__.__name__}, _update_cashvalue, balance response: {response}")
            if response.get('code') == "200" and response['results'] is not None:
                self.cash = response['results']['balance']
                self.value = response['results']['netValue']
            else:
                stdout_log(f"[CRITICAL], {self.__class__.__name__}, balance query failed, url: {url}, response: {response}")

    def _update_positions(self, force_update=False):
        if force_update or datetime.now().timestamp() - self.last_position_update_ts > self.MIN_UPDATE_INTERVAL_SECONDS:
            self.last_position_update_ts = datetime.now().timestamp()

            url = self.base_url + f"/positions/{self.name}/{self.id}"
            response = requests.get(url).json()

            if self.debug:
                stdout_log(f"{self.__class__.__name__}, _update_positions, positions response: {response}")

            if response.get('code') == "200":
                if self.positions.__len__() > 0:
                    self.positions.clear()
                for pos in response['results']:
                    if pos['qty'] != 0:
                        self.positions[pos['symbol']] = bt.Position(size=pos['qty'] if pos['tradeSide'] == 'buy' else -pos['qty'], price=pos['avgPrice'])
            else:
                stdout_log(f"[CRITICAL], {self.__class__.__name__}, positions query failed, url: {url}, response: {response}")

    def _update_orders(self, force_update=False):
        if force_update or datetime.now().timestamp() - self.last_order_update_ts > self.MIN_UPDATE_INTERVAL_SECONDS:
            self.last_order_update_ts = datetime.now().timestamp()

            # Update order status 这里更新的是从策略生命周期中发出的订单的状态
            trade_ids = []
            for order_id, order in self.orders.items():
                # Completed和Cancelled的订单不会再变为其他状态 所以不再需要更新
                if order.status != bt.Order.Completed and order.status != bt.Order.Cancelled:
                    trade_ids.append(order_id)
            if len(trade_ids) > 0:
                url = self.base_url + f"/orders/query/{self.name}/{self.id}"
                data = {
                    "tradeIdList": trade_ids
                }
                payload = urlencode({"content": json.dumps(data)})

                if self.debug:
                    stdout_log(f"{self.__class__.__name__}, next, order query payload: {payload}")

                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }

                response = requests.post(url, headers=headers, data=payload).json()
                if self.debug:
                    stdout_log(f"{self.__class__.__name__}, next, order query response: {response}")
                if response.get('code') == "200":
                    for item in response['results']:
                        item_status = None
                        # 这里是alisa接口的订单状态和backtrader的订单状态的映射
                        if item['orderStatus'] == "pending" or item['orderStatus'] == "working":
                            item_status = bt.Order.Submitted
                        elif item['orderStatus'] == "cancelled":
                            item_status = bt.Order.Cancelled
                        elif item['orderStatus'] == "filled":
                            item_status = bt.Order.Completed
                        elif item['orderStatus'] == "rejected":
                            item_status = bt.Order.Rejected

                        order = self.orders.get(item['tradeId'], None)
                        if order is not None and order.status != item_status:
                            if self.debug:
                                stdout_log(f"{self.__class__.__name__}, next, order status changed, orderId: {order.ref}, old status: {order.getstatusname()}, new status: {bt.Order.Status[item_status]}")

                            # 对于已完成的订单 需要记录执行的size和价格
                            if item_status == bt.Order.Completed:
                                order.executed.size = item['qty']
                                order.executed.price = item['executePrice']
                                if item['openTime'] is not None:
                                    order.executed.dt = bt.date2num(datetime.fromtimestamp(item['openTime'] / 1000.0))

                                if item['closeTime'] is not None:
                                    order.created.dt = bt.date2num(datetime.fromtimestamp(item['closeTime'] / 1000.0))

                            order.status = item_status
                            self.orders[item['tradeId']] = order

                            # 只要是订单的状态发生了变化 放到notifs队列 backtrader框架会取走所有的notif 并通知给策略的notify_order
                            self.notifs.put(order.clone())
                else:
                    stdout_log(f"[CRITICAL], {self.__class__.__name__}, order query failed, url: {url}, payload: {payload}, response: {response}")

            # 获取所有的未完成的订单
            url = self.base_url + f"/orders/query/{self.name}/{self.id}"
            data = {
                "orderStatusList": ["pending", "working"]
            }
            payload = urlencode({"content": json.dumps(data)})
            if self.debug:
                stdout_log(f"{self.__class__.__name__}, next, order query payload: {payload}")
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            response = requests.post(url, headers=headers, data=payload).json()
            if self.debug:
                stdout_log(f"{self.__class__.__name__}, next, order query response: {response}")
            if response.get('code') == "200":
                self.pending_orders.clear()
                for item in response['results']:
                    order_id = item['tradeId']
                    exec_type = bt.Order.Market
                    if item['tradeType'] == "limit":
                        exec_type = bt.Order.Limit

                    owner = None
                    datafeed = None
                    existing_order = self.orders.get(order_id, None)
                    if existing_order is not None:
                        owner = existing_order.owner
                        datafeed = existing_order.data
                    p_order = None
                    if item['tradeSide'] == 'buy':
                        p_order = bt.order.BuyOrder(owner=owner,
                                                    data=datafeed,
                                                    size=item['qty'],
                                                    price=item['allocationPrice'],
                                                    pricelimit=item['allocationPrice'],
                                                    exectype=exec_type,
                                                    valid=None,
                                                    tradeid=0,
                                                    oco=None,
                                                    trailamount=None,
                                                    trailpercent=None,
                                                    simulated=True)
                    else:
                        p_order = bt.order.SellOrder(owner=owner,
                                                    data=datafeed,
                                                    size=item['qty'],
                                                    price=item['allocationPrice'],
                                                    pricelimit=item['allocationPrice'],
                                                    exectype=exec_type,
                                                    valid=None,
                                                    tradeid=0,
                                                    oco=None,
                                                    trailamount=None,
                                                    trailpercent=None,
                                                    simulated=True)
                    # Order对象在创建的时候 如果simulated传False 它要求必须有data 而在这里无法传递data
                    # 所以这里就在创建Order对象的时候simulated传True 创建完了之后将对象的simulated改为False
                    p_order.p.simulated = False
                    p_order.ref = order_id
                    p_order.status = bt.Order.Submitted
                    self.pending_orders.append(p_order)
            else:
                stdout_log(f"[CRITICAL], {self.__class__.__name__}, order query failed, url: {url}, payload: {payload}, response: {response}")

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
    
    def _convert_symbol(self, symbol):
        result = symbol
        if self.name == 'tv':
            if symbol == "HKEX:HSI1!":
                result = "CAPITALCOM:HK50"
        # elif self.name == 'futu':
        #     if symbol == "CAPITALCOM:HK50":
        #         result = "HKEX:HSI1!"
        return result