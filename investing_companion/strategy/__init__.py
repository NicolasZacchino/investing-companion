import numpy as np
import yfinance as yf
from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    def __init__(self, symbol, start=None, end=None, period='max'):
        self.symbol = symbol
        self.period = period
        self.start = start
        self.end = end
        self.retrieve_data(self.symbol, self.period, start=self.start, end=self.end)
        self.prepare_data()

    
    def retrieve_data(self, symbol, period, start=None, end=None):
        if start is not None and end is not None:
            self.data = yf.download(symbol, start=start, end=end)
        else:
            self.data = yf.download(symbol, period=period)


    def prepare_data(self):
        self.data['daily_returns'] = np.log(self.data['Close']/self.data['Close'].shift(1))
        self.data['bnh_returns'] = self.data['daily_returns'].cumsum()
        self.data.dropna(inplace=True)

    @abstractmethod
    def backtest_strategy(self):
        pass

    # def backtest_strategy(data, buy_conds, sell_conds):   
    #         #Set Buy and sell signals
    #         data['signal'] =np.select([buy_conds, sell_conds], 
    #                                     [Signal.BUY.value, Signal.SELL.value],
    #                                         Signal.NONE.value)

    #         data['position'] = data['signal'].replace(to_replace=Signal.NONE.value, method='ffill')
    #         data['position'] = data['position'].shift()
    #         data['strat_returns'] = data['position'] * data['daily_returns']

    #         performance = data[['daily_returns','strat_returns']]\
    #                                 .iloc[:].sum()
            
    #         data['strat_returns'] = data['strat_returns'].cumsum()
    #         return performance

    @abstractmethod
    def optimize_indic_parameters(self):
        pass


