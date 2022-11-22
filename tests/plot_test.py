from lib.tickers import tickerindicators
import yfinance as yf
import pandas as pd
from lib.analysis import indicators

tsla = tickerindicators.TickerWithIndicators('TSLA')
hist = tsla.history(tsla.period)

rsi = indicators.relative_strength_index(hist['Close'])