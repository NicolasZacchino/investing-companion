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
    

    def backtest_strategy(self, ticker):
        strat_df = ticker.history('max')[['Close']]
        strat_df['b&h'] = np.log(strat_df['Close']/strat_df['Close'].shift(1))
        strat_df['signal'] =np.select([self.buy_conds, self.sell_conds], 
                                      [self._BUY_SIGNAL, self._SELL_SIGNAL],
                                      self._NONE_SIGNAL)

        strat_df['position'] = strat_df['signal'].replace(to_replace=self._NONE_SIGNAL, method='ffill')
        strat_df['position'].shift(1)
        strat_df['returns'] = strat_df['b&h'] * strat_df['position']

        buy_hold_returns = strat_df['b&h'].cumsum()[-1]
        strat_return = strat_df['returns'].cumsum()[-1]
        return buy_hold_returns, strat_return

    @abstractmethod
    def optimize_strategy(self, *args, **kwargs):
        pass

    
    

    