from investing_companion.tickers import ticker
import yfinance as yf
import pandas as pd
import numpy as np
from investing_companion import indicators
from investing_companion.indicators import moving_averages, macd, bollinger

tsla = ticker.TickerAdditionalPricepoints('TSLA')
print(tsla.history('max'))