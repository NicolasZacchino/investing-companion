from investing_companion import strategy
from investing_companion.indicators import macd
from investing_companion.tickers import ticker

tsla = ticker.TickerAdditionalPricepoints('TSLA')
hist = tsla.history('max')

mcd = macd.MACD(hist['Close'])

buy_conds = (mcd.df['MACD'] > mcd.df['Signal']) & (mcd.df['MACD'].shift(1) <= mcd.df['Signal'])
sell_conds = (mcd.df['MACD'] <= mcd.df['Signal']) & (mcd.df['MACD'].shift(1) >= mcd.df['Signal'])


strat = strategy.BaseStrategy(buy_conds, sell_conds)
b_h_ret, strat_ret = strat.backtest_strategy(tsla)
print(b_h_ret, strat_ret)