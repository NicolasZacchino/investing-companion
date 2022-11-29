from investing_companion.tickers import tickerindicators
import yfinance as yf
import pandas as pd
from investing_companion import indicators
from investing_companion.indicators import moving_averages, macd

tsla = tickerindicators.TickerWithIndicators('TSLA')

hist = tsla.history('max')


mcd = macd.MACD(hist['Close'])
print(mcd.get_latest_value('MACD'))