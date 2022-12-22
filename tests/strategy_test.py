from investing_companion.strategy import macd_strategy
from investing_companion.indicators import macd, rsi, bollinger, moving_averages
from investing_companion.tickers import ticker
import numpy as np
import pandas as pd

strat = macd_strategy.Macd_Strategy('TSLA')
perf = strat.backtest_strategy(macd_strategy.Macd_Strategy.Method.MIXED_CROSSOVER)
print(perf)
