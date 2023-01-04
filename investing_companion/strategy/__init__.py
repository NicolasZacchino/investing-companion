import numpy as np
import yfinance as yf
from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    '''Base class for strategy implementation. S
    Shouldn't be instantiated directly.
    :param symbol(str): The ticker symbol, passed as a string
    :param start(str): the start date from which the dataframe will be built. Default=None
    :param end(str): the end date from which the dataframe will be built. Default=None
    :param period(str): the time period from which the dataframe will be built. Used if start or end are not set.
    default = 'max'
    
    Methods
    :retrieve_data()
    :prepare_data()
    :get_signal_column()
    :get_performance()
    :buffer_all() [static]
    :create_conditions() [Abstract]
    :backtest_strategy() [Abstract]
    :optimize_indic_parameters()[Abstract]
    '''
    def __init__(self, symbol, start=None, end=None, period='max'):
        self.symbol = symbol
        self.period = period
        self.start = start
        self.end = end
        self.retrieve_data(self.symbol, self.period, start=self.start, end=self.end)
        self.prepare_data()

    
    def retrieve_data(self, symbol, period, start=None, end=None):
        if start is not None and end is not None:
            self.data = yf.Ticker(symbol).history(start=start, end=end)
        else:
            self.data = yf.Ticker(symbol).history(period=period)


    def prepare_data(self):
        self.data['daily_returns'] = np.log(self.data['Close']/self.data['Close'].shift(1))
        self.data['bnh_returns'] = self.data['daily_returns'].cumsum()
        self.data.dropna(inplace=True)
    

    def get_signal_column(self,buy_cond,sell_cond):
        return np.select([buy_cond, sell_cond],[1, -1], 0)
    

    def get_performance(self, start=None):
        self.data['position'] = self.data['signal'].replace(to_replace=0, method='ffill')
        self.data['position'] = self.data['position'].shift()
        self.data['strat_returns'] = self.data['position'] * self.data['daily_returns']

        performance = self.data[['daily_returns','strat_returns']]\
                                .iloc[start:].sum()
            
        self.data['strat_returns'] = self.data['strat_returns'].cumsum()
        return performance


    @staticmethod
    def buffer_all(i):
        '''Function used to check for a condition over all the elements in the buffer'''
        return i.all()


    @abstractmethod
    def create_conditions(self):
        raise NotImplementedError()


    @abstractmethod
    def optimize_strat_params(self):
        raise NotImplementedError()
    

    @abstractmethod
    def backtest_strategy(self):
        raise NotImplementedError()


