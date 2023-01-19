from investing_companion.strategy import macd_strategy, bollinger_strategy, rsi_strategy, ma_strategy
from investing_companion.indicators import macd, rsi, bollinger, moving_averages
from investing_companion.tickers import ticker
import numpy as np
import pandas as pd
import yfinance as yf

def buffer_all(i):
    return i.all()

symbol = 'TSLA'
method = ma_strategy.Ma_Strategy.Method.PRICE_CROSSOVER
ind1 = moving_averages.ExponentialMovingAverage(window_size=5)
ind2 = moving_averages.ExponentialMovingAverage(window_size=20)
ind3 = moving_averages.ExponentialMovingAverage(window_size=50)

indlst = [ind1.ma_name,ind2.ma_name,ind3.ma_name]

strat = ma_strategy.Ma_Strategy(symbol, method=method, ma_objs=[ind1,ind2,ind3])
print(strat.backtest_strategy())

strat.data[['Close', *strat.ma_names, 'signal']].to_csv('file2.csv')