from investing_companion import strategy
from investing_companion.indicators import macd, rsi
from investing_companion.tickers import ticker

tsla = ticker.TickerAdditionalPricepoints('TSLA')
hist = tsla.history('max')['Close']
mcd = macd.MACD()
relstr = rsi.RelativeStrengthIndex()
df = relstr.build_df(hist)
print(df)
