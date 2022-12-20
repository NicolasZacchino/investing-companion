from investing_companion.indicators import macd
from investing_companion import strategy
import pandas as pd
import numpy as np
from enum import Enum, auto

class Macd_Strategy(strategy.BaseStrategy):
    class Method(Enum):
        SIGNAL_CROSSOVER = auto()
        ZERO_CROSSOVER = auto()
        MIXED_CROSSOVER = auto()

    def buffer_func(i):
        return i.all()


    def __init__(self, symbol, start=None, end=None, period='max', 
                macd_object = macd.MACD(), buffer=1, use_ppo=False, ppo_threshold=2):
        super().__init__(symbol, start, end, period)
        self.macd = macd_object
        self.use_ppo = use_ppo
        self.ppo_threshold = ppo_threshold
        self.buffer = buffer
        self.data = pd.concat([self.data, self.macd.build_df(self.data)], axis=1)
        

    def backtest_strategy(self, method):
        if method == self.Method.SIGNAL_CROSSOVER:
            buy_sig = (self.data[self.macd.macd_name] > 
                      self.data[self.macd.signal_name])\
                      .rolling(self.buffer).apply(self.buffer_func).astype(bool)

            cross_buy_sig = (self.data[self.macd.macd_name].shift(self.buffer+1) <= 
                             self.data[self.macd.signal_name])
           
            sell_sig = (self.data[self.macd.macd_name] < 
                        self.data[self.macd.signal_name])\
                        .rolling(self.buffer).apply(self.buffer_func).astype(bool)
                       
            cross_sell_sig = (self.data[self.macd.macd_name].shift(self.buffer+1) >=
                              self.data[self.macd.signal_name])

            if self.use_ppo:
                buy_sig &= (self.data[self.macd.ppo_name].abs()) >= self.ppo_threshold
                sell_sig &= (self.data[self.macd.ppo_name].abs()) >= self.ppo_threshold

        elif method == self.Method.ZERO_CROSSOVER:
            buy_sig = (self.data[self.macd.macd_name] > 0)\
                       .rolling(self.buffer).apply(self.buffer_func).astype(bool)
            
            cross_buy_sig = (self.data[self.macd.macd_name].shift(self.buffer+1) <= 0)

            sell_sig = (self.data[self.macd.macd_name] < 0)\
                        .rolling(self.buffer).apply(self.buffer_func).astype(bool)
            
            cross_sell_sig = (self.data[self.macd.macd_name].shift(self.buffer+1) >= 0)
        
        elif method == self.Method.MIXED_CROSSOVER:
            #TODO
            pass

        buy_cond = buy_sig & cross_buy_sig
        sell_cond = sell_sig & cross_sell_sig

        self.data['signal'] =np.select([buy_cond, sell_cond],[1, -1], 0)

        self.data['position'] = self.data['signal'].replace(to_replace=0, method='ffill')
        self.data['position'] = self.data['position'].shift()
        self.data['strat_returns'] = self.data['position'] * self.data['daily_returns']

        performance = self.data[['daily_returns','strat_returns']]\
                                .iloc[:].sum()
            
        self.data['strat_returns'] = self.data['strat_returns'].cumsum()
        
        return performance


    def optimize_indic_parameters(self):
        return super().optimize_indic_parameters()
        

