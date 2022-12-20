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

    @abstractmethod
    def optimize_indic_parameters(self):
        pass


