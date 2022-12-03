from investing_companion.tickers import ticker
import yfinance as yf
import pandas as pd
import numpy as np
from investing_companion import indicators
from investing_companion.indicators import moving_averages, macd, bollinger, rsi

tsla = ticker.TickerAdditionalPricepoints('MSFT')
history = tsla.history('max')

bolbands = bollinger.BollingerBands(history['Close'])
sma = moving_averages.SimpleMovingAverage(history['Close'])
relstr = rsi.RelativeStrengthIndex(history['Close'])
mcd = macd.MACD(history['Close'])
buy = (mcd.df['MACD'] >= mcd.df['Signal'])
sell = (mcd.df['MACD'] < mcd.df['Signal'])

def backtest_strategy(buy_condlist, sell_condlist):
        history['b&h'] = np.log(history['Close']/history['Close'].shift(1))
        history['signal'] = np.where(buy_condlist, 1, 0)
        history['signal'] = np.where(sell_condlist, -1, history['signal'])
        history['position'] = history['signal'].replace(to_replace=0, method='ffill')
        history['position'].shift(1)
        history['returns'] = history['b&h'] * history['position']

        buy_hold_returns = history['b&h'].cumsum()[-1]
        strat_return = history['returns'].cumsum()[-1]

        return buy_hold_returns, strat_return

print(backtest_strategy(buy,sell))
