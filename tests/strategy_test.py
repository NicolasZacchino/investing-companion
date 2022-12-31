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
strat = macd_strategy.Macd_Strategy(symbol,method=method,ppo_threshold=2.5, use_ppo=True)

perf = strat.backtest_strategy()
print(perf)


fastema_range = [8,20]
signal_range = [6, 12]
ppo_range = [1,5]

        