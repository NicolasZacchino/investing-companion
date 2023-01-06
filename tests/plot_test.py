from investing_companion.tickers import ticker
import yfinance as yf
import pandas as pd
import numpy as np
from investing_companion import indicators
from investing_companion.indicators import moving_averages, macd, bollinger, rsi

tsla = yf.Ticker('TSLA')
hist = tsla.history('max')
rel = rsi.RelativeStrengthIndex()
df = rel.build_df(hist)

uptrend_range = [40,90]
downtrend_range = [10,60]

uptrend = df[rel.rsi_name].between(uptrend_range[0],uptrend_range[1])
downtrend = df[rel.rsi_name].between(downtrend_range[0],downtrend_range[1])

df['zone'] = np.select([uptrend&downtrend, uptrend, downtrend],[0,1,-1], default=0)
df['trend'] = df['zone'].replace(to_replace=0, method='ffill')       

print(df.to_string())