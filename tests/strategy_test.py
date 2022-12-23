from investing_companion.strategy import macd_strategy
from investing_companion.indicators import macd, rsi, bollinger, moving_averages
from investing_companion.tickers import ticker
import numpy as np
import pandas as pd

symbol = 'TSLA'
method = macd_strategy.Macd_Strategy.Method.PPO_ONLY
interval = [1,6]
max_iter = 20
n = 20
strat = macd_strategy.Macd_Strategy(symbol,method=method,ppo_threshold=2.5)
perf = strat.backtest_strategy()
print(perf)
while n < 20:
    xlow, xhigh = interval[0], interval[1]
    xmid = (xlow+xhigh)/2
    
    xlist = [xlow,xmid,xhigh]
    reslist = {}
    for x in xlist:
        strat = macd_strategy.Macd_Strategy(symbol,ppo_threshold=x)
        perf = strat.backtest_strategy(method)['strat_returns']
        reslist[x] = perf
    
    m = min(reslist.values())
    print(reslist)
    reslist = {key:value for key,value in reslist.items() if reslist[key] != m}
    interval[0] = min(reslist.keys())
    interval[1] = max(reslist.keys())
    n += 1

        