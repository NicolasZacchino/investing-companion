from lib.tickers import tickerindicators
import yfinance as yf
import pandas as pd
from lib.analysis import indicators

tsla = yf.Ticker('TSLA')
hist = tsla.history('max')
rsi = indicators.macd(hist['Close'])
print(type(hist['Close']))