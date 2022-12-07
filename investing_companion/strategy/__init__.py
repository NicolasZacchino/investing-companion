import pandas as pd
import numpy as np
from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    _BUY_SIGNAL = 1
    _SELL_SIGNAL = -1
    _NONE_SIGNAL = 0

    def __init__(self, buy_cond, sell_cond):
        self.buy_conds = buy_cond
        self.sell_conds = sell_cond

    def prepare_data(self, ticker):
        self.data = ticker.history('max')['Close']
        self.data['daily_returns'] = np.log(self.data['Close']/self.data['Close'].shift(1))
        self.data['bnh_returns'] = self.data['daily_returns'].cumsum()
        self.data.dropna()

    def backtest_strategy(self):
      
        #Set Buy and sell signals
        self.data['signal'] =np.select([self.buy_conds, self.sell_conds], 
                                       [self._BUY_SIGNAL, self._SELL_SIGNAL],
                                        self._NONE_SIGNAL)

        self.data['position'] = self.data['signal'].replace(to_replace=self._NONE_SIGNAL, method='ffill')
        self.data['position'] = self.data['position'].shift()

        self.data['strat_returns'] = self.data['position'] * self.data['daily_returns']

        performance = self.data[['daily_returns','strat_returns']]\
                                .iloc[:].sum()
        
        self.data['strat_returns'] = self.data['strat_returns'].cumsum()
        return performance

    @abstractmethod
    def optimize_strategy(self, *args, **kwargs):
        pass

    
    

    