from investing_companion.tickers import tickerindicators
import yfinance as yf
import pandas as pd
import numpy as np
from investing_companion import indicators
from investing_companion.indicators import moving_averages, macd, bollinger

tsla = tickerindicators.TickerWithIndicators('TSLA')
hist = tsla.history('max')
bolb = bollinger.BollingerBands(hist['Close'])

conditions = [bolb.df['BB_Upper'] <= hist['Close'], 
              bolb.df['BB_Lower'] >= hist['Close']]

choices = ['Buy','Sell']

hist['Signal'] = np.select(conditions, choices, 0)