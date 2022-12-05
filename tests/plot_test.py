from investing_companion.tickers import ticker
import yfinance as yf
import pandas as pd
import numpy as np
from investing_companion import indicators
from investing_companion.indicators import moving_averages, macd, bollinger, rsi

tsla = ticker.TickerAdditionalPricepoints('TSLA')
history = tsla.history('max')

