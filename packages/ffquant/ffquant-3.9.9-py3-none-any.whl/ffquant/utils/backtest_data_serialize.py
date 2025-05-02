import os
import pickle
import backtrader as bt
from ffquant.utils.Logger import stdout_log
from pathlib import Path
import ffquant.utils.global_backtest_data as global_backtest_data
from datetime import datetime
import pytz

# 为什么需要wash order？ 因为backtrader的order是不可序列化的，所以需要把order_info转换成可序列化的dict
def wash_orders(orders, pickle_dict):
    washed_orders = dict()

    for symbol in orders.keys():
        symbol_orders = orders[symbol]
        symbol_washed_orders = []
        washed_orders[symbol] = symbol_washed_orders

        for item in symbol_orders:
            tmp_order_dict = dict()
            tmp_order_dict['datetime'] = item['datetime']
            tmp_order_dict['order_id'] = item['data'].ref
            tmp_order_dict['exec_type'] = "Market" if item['data'].exectype == bt.Order.Market else "Limit"
            tmp_order_dict['order_type'] = "Buy" if item['data'].ordtype == bt.Order.Buy else "Sell"
            order_status = ""
            if item['data'].status == bt.Order.Submitted:
                order_status = "Submitted"
            elif item['data'].status == bt.Order.Completed:
                order_status = "Completed"
            elif item['data'].status == bt.Order.Cancelled:
                order_status = "Cancelled"
            tmp_order_dict['order_status'] = order_status
            tmp_order_dict['execute_price'] = item['data'].executed.price
            tmp_order_dict['execute_size'] = abs(item['data'].executed.size)
            if item['data'].executed.dt is not None:
                tmp_order_dict['execute_time'] = bt.num2date(item['data'].executed.dt).astimezone().strftime("%Y-%m-%d %H:%M:%S")
            else:
                tmp_order_dict['execute_time'] = ""
            tmp_order_dict['create_price'] = item['data'].created.price
            tmp_order_dict['create_size'] = abs(item['data'].created.size)
            if item['data'].created.dt is not None:
                tmp_order_dict['create_time'] = bt.num2date(item['data'].created.dt).astimezone().strftime("%Y-%m-%d %H:%M:%S")
            else:
                tmp_order_dict['create_time'] = ""

            origin = item['data'].info["origin"]
            if origin is None or isinstance(origin, dict) or origin == "":
                origin = "Unknown"
            tmp_order_dict['origin'] = origin

            message = item['data'].info["message"]
            if message is None or isinstance(message, dict):
                message = ""
            tmp_order_dict['message'] = message

            tmp_order_dict['is_close_pos'] = item['data'].info["is_close_pos"] if item['data'].info["is_close_pos"] is not None and not isinstance(item['data'].info["is_close_pos"], dict) else False
            symbol_washed_orders.append(tmp_order_dict)
    
    pickle_dict['orders'] = washed_orders
    return pickle_dict

# 实时和回测都把数据序列化为pickle
def prepare_data_for_pickle(script_name, timeframe="Minutes", compression=1, riskfree_rate=0.01, commission=None, mult=None, use_local_dash_url=False, dash_port=None, version="1.0.3", debug=False):
    pickle_dict = {}
    pickle_dict["version"] = version
    pickle_dict["script_name"] = script_name
    pickle_dict["timeframe"] = timeframe
    pickle_dict["compression"] = compression
    pickle_dict["use_local_dash_url"] = use_local_dash_url
    pickle_dict["dash_port"] = dash_port
    pickle_dict["riskfree_rate"] = riskfree_rate
    pickle_dict["commission"] = commission
    pickle_dict["mult"] = mult
    pickle_dict["treturns"] = global_backtest_data.treturns
    pickle_dict["broker_values"] = global_backtest_data.broker_values
    pickle_dict["drawdowns"] = global_backtest_data.drawdowns
    pickle_dict["klines"] = global_backtest_data.klines
    pickle_dict["positions"] = global_backtest_data.positions
    pickle_dict["indcs"] = global_backtest_data.indcs

    # repack order info because it is not serializable
    pickle_dict = wash_orders(global_backtest_data.orders, pickle_dict)

    return pickle_dict

def serialize_backtest_data(script_name,
                            timeframe="Minutes",
                            compression=1,
                            riskfree_rate=0.01,
                            commission=None,
                            mult=None,
                            use_local_dash_url=False,
                            dash_port=None,
                            version="1.0.3",
                            backtest_data_dir=None,
                            debug=False):
    pickle_dict = prepare_data_for_pickle(
        script_name=script_name,
        timeframe=timeframe,
        compression=compression,
        riskfree_rate=riskfree_rate,
        commission=commission,
        mult=mult,
        use_local_dash_url=use_local_dash_url,
        dash_port=dash_port,
        version=version)

    pkl_data_dir = f"{Path.home()}/backtest_data/"
    if backtest_data_dir is not None:
        pkl_data_dir = backtest_data_dir

    if not os.path.exists(pkl_data_dir):
        os.makedirs(pkl_data_dir)

    klines = global_backtest_data.klines
    symbol = list(klines.keys())[0]
    symbol_klines = klines[symbol]
    start_dt_str = symbol_klines[0]['datetime'].replace(" ", "_").replace(":", "-")
    end_dt_str = symbol_klines[-1]['datetime'].replace(" ", "_").replace(":", "-")
    pkl_file_name = f"{script_name}_{start_dt_str}_to_{end_dt_str}_{version}_{datetime.now().timestamp() * 1000}.pkl"
    pkl_file_path = os.path.join(pkl_data_dir, pkl_file_name)

    if os.path.exists(pkl_file_path):
        os.remove(pkl_file_path)

    with open(pkl_file_path, 'wb') as pkl_file:
        pickle.dump(pickle_dict, pkl_file)

    return pkl_file_path
