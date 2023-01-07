from investing_companion.tickers import ticker
import yfinance as yf
import timeit
import pandas as pd
import numpy as np
from investing_companion import indicators
from investing_companion.indicators import moving_averages, macd, bollinger, rsi

def buffer_all(i):
    return i.all()
buffer=3

tsla = yf.Ticker('TSLA')
hist = tsla.history('max')
ma_objs = [moving_averages.ExponentialMovingAverage(window_size=5), moving_averages.ExponentialMovingAverage(window_size=20),moving_averages.ExponentialMovingAverage(window_size=50)]
ma_names = [m.ma_name for m in ma_objs]

ma_df = pd.concat([m.build_df(hist) for m in ma_objs], axis=1)

df = hist[['Close']]

df2 = pd.concat([df, ma_df], axis=1)

df3 = (df2.dropna().idxmax(axis=1) == 'Close').rolling(buffer).apply(buffer_all).fillna(0).astype(bool)
print(df3.to_string())

