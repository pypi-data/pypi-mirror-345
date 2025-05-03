import backtrader as bt
import threading
from ffquant.plot.dash_graph import show_perf_graph, update_task_field
from ffquant.observers.MyBkr import MyBkr
from ffquant.observers.MyBuySell import MyBuySell
from ffquant.observers.MyDrawDown import MyDrawDown
from ffquant.observers.MyTimeReturn import MyTimeReturn
from ffquant.analyzers.OrderAnalyzer import OrderAnalyzer
import inspect
import os
from ffquant.utils.backtest_data_serialize import prepare_data_for_pickle
import time
from ffquant.utils.Logger import stdout_log
import ffquant.utils.global_backtest_data as global_backtest_data
from ffquant.plot.dash_graph import get_order_pnl_stats, get_return_and_sharpe
from tabulate import tabulate
import numpy as np

__ALL__ = ['run_and_show_performance']

# 做了两件事 1、执行cerebro.run() 2、计算性能数据 并调用Dash进行展示
# riskfree_rate 无风险利率
# use_local_dash_url为true时 打开性能界面时使用的是本地ip 如果False 使用的是域名
# backtest_data_dir 指定存储回测数据的目录
# task_id是搭配backtest_manage工程而使用的 指的是建立的回测任务的id
def run_and_show_performance(
        cerebro,
        script_name=None,
        riskfree_rate = 0.01,
        use_local_dash_url=False,
        dash_port=None,
        backtest_data_dir=None,
        task_id=None,
        debug=False):
    if hasattr(cerebro, 'runstrats'):
        raise Exception('Cerebro already run. Cannot run again')

    # 一般是用策略的脚本名
    if script_name is None or script_name == '':
        frame = inspect.stack()[1]
        caller_file_path = frame.filename
        script_name = os.path.basename(caller_file_path)
        if script_name.endswith('.py'):
            script_name = script_name[:-3]

    commission = None
    mult = None
    if len(cerebro.datas) > 0:
        data = cerebro.datas[0]
        commission = cerebro.broker.getcommissioninfo(data).p.commission
        mult = cerebro.broker.getcommissioninfo(data).p.mult

    # 这里是为了记录策略执行过程中的各种基础数据 方便后面的性能计算
    add_observers(cerebro, debug)

    # 这里用Analyzer而不是Observer是因为只有Analyzer才有notify_order回调方法 这里是为了记录订单的执行信息
    add_analyzers(cerebro, debug)

    is_live_trade = False
    for data in cerebro.datas:
        if data.islive():
            is_live_trade = True

    # 准备timeframe和compression信息 用于保存到pkl文件中
    timeframe = "Minutes"
    compression = 1
    if len(cerebro.datas) > 0 and cerebro.datas[0].p.timeframe == bt.TimeFrame.Seconds:
        timeframe = "Seconds"
        compression = cerebro.datas[0].p.compression

    # 回测是run完就show 所以单线程就行 但是实时的话需要一边run 一边show 所以需要多线程
    if is_live_trade:
        threading.Thread(target=lambda: cerebro.run(), daemon=True).start()
        for i in range(10):
            stdout_log(f"{10 - i} seconds before showing perf graph...")
            time.sleep(1)
        backtest_data = prepare_data_for_pickle(
            script_name=script_name,
            timeframe=timeframe,
            compression=compression,
            riskfree_rate=riskfree_rate,
            commission=commission,
            mult=mult,
            use_local_dash_url=use_local_dash_url,
            dash_port=dash_port,
            debug=debug)
        show_perf_graph(backtest_data, is_live=is_live_trade, backtest_data_dir=backtest_data_dir, task_id=task_id, debug=debug)
    else:
        # 这里禁止preload模式 是为了让MyFeed和MyLiveFeed的逻辑尽可能保持一致 让他们的next方法都被调用
        cerebro.p.preload = False

        cerebro.run()

        if task_id is not None:
            for runstrat in cerebro.runstrats:
                if len(runstrat) > 0 and runstrat[0].logger is not None:
                    strat_log_path = runstrat[0].logger.log_filepath
                    update_task_field(task_id, 'strat_log_path', strat_log_path)
                    break

        backtest_data = prepare_data_for_pickle(
            script_name=script_name,
            timeframe=timeframe,
            compression=compression,
            riskfree_rate=riskfree_rate,
            commission=commission,
            mult=mult,
            use_local_dash_url=use_local_dash_url,
            dash_port=dash_port,
            debug=debug)
        show_perf_graph(backtest_data, is_live=is_live_trade, backtest_data_dir=backtest_data_dir, task_id=task_id, debug=debug)

def optrun_and_show_table(cerebro, strategy, *args, **kwargs):

    frame = inspect.stack()[1]
    caller_file_path = frame.filename
    script_name = os.path.basename(caller_file_path)
    if script_name.endswith('.py'):
        script_name = script_name[:-3]

    # 这里是为了记录策略执行过程中的各种基础数据 方便后面的性能计算
    add_observers(cerebro)

    # 这里用Analyzer而不是Observer是因为只有Analyzer才有notify_order回调方法 这里是为了记录订单的执行信息
    add_analyzers(cerebro)

    # 这里禁止preload模式 是为了让MyFeed和MyLiveFeed的逻辑尽可能保持一致 让他们的next方法都被调用
    cerebro.p.preload = False

    opt_param_keys = []
    for key, value in kwargs.items():
        if isinstance(value, list) or isinstance(value, np.ndarray) and len(value) > 0:
            opt_param_keys.append(key)

    global_backtest_data.opt_param_keys = opt_param_keys

    cerebro.optstrategy(strategy, **kwargs)
    cerebro.run(maxcpus=1)

    headers = []
    
    for key in opt_param_keys:
        headers.append(f"Param:{key}")
    headers = headers + ["order_count", "return_rate", "sharpe", "reward_risk_ratio", "win_rate", "max_drawdown"]

    table_data = []
    for opt_result in global_backtest_data.opt_results:
        row_data = []

        opt_params = opt_result['opt_params']
        for key in opt_params.keys():
            v = opt_params[key]
            if isinstance(v, float):
                v = round(v, 8)
            row_data.append(v)

        backtest_data = opt_result['backtest_data']
        orders = backtest_data["orders"]
        completed_order_num = 0
        for symbol in orders.keys():
            completed_order_num += len([item for item in orders[symbol] if item['order_status'] == "Completed"])
        row_data.append(completed_order_num)

        broker_values = backtest_data["broker_values"]
        return_rate = None
        if len(broker_values) > 0:
            return_rate = broker_values[-1]["value"] / broker_values[0]["value"] - 1
        row_data.append(return_rate)

        _, _, _, sharpe = get_return_and_sharpe(backtest_data)
        row_data.append(sharpe)

        positions = backtest_data["positions"]
        reward_risk_ratio, win_rate, _ = get_order_pnl_stats(
            orders=orders,
            positions=positions)
        row_data.append(reward_risk_ratio)
        row_data.append(win_rate)

        drawdowns = backtest_data["drawdowns"]
        max_drawdown = f"{max([item['drawdown'] for item in drawdowns]) / 100.0}"
        row_data.append(max_drawdown)

        table_data.append(row_data)
    print(tabulate(table_data, headers=headers, tablefmt="pretty", floatfmt=".8f"))

def add_observers(cerebro, debug=False):
    cerebro.addobserver(MyBkr)
    cerebro.addobserver(MyBuySell)
    cerebro.addobserver(MyDrawDown)

    if len(cerebro.datas) > 0:
        timeframe = cerebro.datas[0].p.timeframe
        compression = cerebro.datas[0].p.compression
        cerebro.addobserver(
            MyTimeReturn,
            timeframe=timeframe,
            compression=compression
        )

def add_analyzers(cerebro, debug=False):
    cerebro.addanalyzer(OrderAnalyzer)