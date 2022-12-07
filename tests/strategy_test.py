'''
Example of the Strategy implementation. Given a list of Tickers, we create the price history dataframe
for each one of them, then we create instances of the indicators we are going to use and call the
prepare_data function in strategy, which returns a df resulting from the concatenation of the price
history, and the indicators applied to those prices. 

Next, we set the buy and sell conditions. In this case we consider it a buy signal when the 5-day SMA
croses above the 50-day one (we require that day X SMA-5 closes above day X SMA-50 *AND* that 
day (X-1) SMA-5 closed below day X SMA-50). We then call the backtest_strategy function, which process
those conditions and declare buy and sell signals along with short and long positions and give us 
the logarithmic return of our strategy compared to simply buying and holding onto a stock.
The mean logarithmic return for each of these two approaches is then calculated

Some caveats and notes:
-consider using yf.Ticker() if you are not going to make use of the additional price points, as it 
should be faster (since it doesn't perform needless calculations)
-the longer the time period and the more tickers to backtest, the longer the program will take to run.
consider using a narrower time range
-On the topic of time range: 'max' can include data that goes as far bacl as the late 90s. Such old 
data may no longer be representative for the current circumstances and may skew the results (on top of,
again, take longer to calculate))
'''

from investing_companion import strategy
from investing_companion.indicators import macd, rsi, bollinger, moving_averages
from investing_companion.tickers import ticker
import numpy as np

tickerlist = ['TSLA','AMZN','AMD','NVDA','T','META','MSFT','GOLD','AAPL','GOOG','NFLX']

bnhlist = []
stratlist =[]
for tick in tickerlist:
    t = ticker.TickerAdditionalPricepoints(tick)
    hist = t.history('max')['Close']
    sma5 = moving_averages.SimpleMovingAverage(5)
    sma50 = moving_averages.SimpleMovingAverage()

    df = strategy.prepare_data(hist,[sma5,sma50])
    
    buy_cond = (df[sma50.sma_name] < df[sma5.sma_name]) & (df[sma50.sma_name].shift(1)  >= df[sma5.sma_name])
    sell_cond = (df[sma50.sma_name] > df[sma5.sma_name]) & (df[sma50.sma_name].shift(1) <= df[sma5.sma_name])

    perf = strategy.backtest_strategy(df, buy_cond,sell_cond)
    bnhlist.append(perf['daily_returns'])
    stratlist.append(perf['strat_returns'])

bnh_mean = np.mean(bnhlist)
strat_mean = np.mean(stratlist)

print({'b&h mean return': bnh_mean,
       'strat mean return': strat_mean})