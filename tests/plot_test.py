from lib.tickers import tickerindicators
import yfinance as yf
import pandas as pd
from lib.analysis import indicators

tsla = yf.Ticker('TSLA')
hist = tsla.history('max')
testdict = {indicators.exponential_moving_average: [hist['Close'], 20],
indicators.relative_strength_index: [hist['Close'], 13], indicators.bollinger_bands: [hist['Close'], 20, 2]}
