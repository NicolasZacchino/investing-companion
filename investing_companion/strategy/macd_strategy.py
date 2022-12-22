from investing_companion.indicators import macd
from investing_companion import strategy
import pandas as pd
import numpy as np
from enum import Enum, auto

class Macd_Strategy(strategy.BaseStrategy):
    '''MACD-based strategy class. Inherits from BaseStrategy

    :param symbol(str): The ticker symbol, passed as a string
    :param start(str): the start date from which the dataframe will be built. Default=None
    :param end(str): the end date from which the dataframe will be built. Default=None
    :param period(str): the time period from which the dataframe will be built. Used if start or end are not set.
    default = 'max'
    :param macd_object(indicators.macd.MACD) = the macd indicator object to be used in the strategy. Defaults to a macd object
    with default parameters
    :param buffer(int): the amount of days a condition needs to hold true in order to raise a signal.
    see the Method nested class for further explanation. Default=1
    :param use_ppo(bool): If True, the strategy also considers a buy/sell signal if the PPO reaches a threshold.
    default = False
    :param ppo_threshold(float): the threshold that will be used for the ppo strategy. Does nothing if 
    use_ppo is set to False. Default=2.5

    Methods:
    :backtest_strategy()
    :optimize_indic_params()

    '''
    class Method(Enum):
        '''Enum to determine the criteria for buy and sell signals.

        :SIGNAL_CROSSOVER: Buy when the MACD becomes greater than the signal and remains so 
        for self.buffer periods. Sell when the opposite happens

        :ZERO_CROSSOVER: Buy when the MACD becomes positive and remains so for self.buffer periods.
        Sell when the opposite happens.

        :MIXED_CROSSOVER: Buy when the MACD becomes greater than the signal, and has remained greater
        than the signal for the previous self.buffer periods
        '''
        SIGNAL_CROSSOVER = auto()
        ZERO_CROSSOVER = auto()
        MIXED_CROSSOVER = auto()


    def __init__(self, symbol, start=None, end=None, period='max', 
                macd_object = macd.MACD(), buffer=1, use_ppo=False, ppo_threshold=2.5):
        super().__init__(symbol, start, end, period)
        self.macd = macd_object
        self.use_ppo = use_ppo
        self.ppo_threshold = ppo_threshold
        self.buffer = buffer
        self.data = pd.concat([self.data, self.macd.build_df(self.data)], axis=1)
        

    def backtest_strategy(self, method):

        def buffer_all(i):
            return i.all()
        
        if method == self.Method.SIGNAL_CROSSOVER:
        #buy if macd>signal for self.buffer periods. Sell if the opposite happens
        #In all cases we check if a crossing has happened with .shift()
            buy_sig = (self.data[self.macd.macd_name] > 
                      self.data[self.macd.signal_name])\
                      .rolling(self.buffer).apply(buffer_all).fillna(0).astype(bool)

            cross_buy_sig = (self.data[self.macd.macd_name].shift(self.buffer) <= 
                             self.data[self.macd.signal_name].shift(self.buffer-1))
           
            sell_sig = (self.data[self.macd.macd_name] < 
                        self.data[self.macd.signal_name])\
                        .rolling(self.buffer).apply(buffer_all).fillna(0).astype(bool)
                       
            cross_sell_sig = (self.data[self.macd.macd_name].shift(self.buffer) >=
                              self.data[self.macd.signal_name].shift(self.buffer-1))


        elif method == self.Method.ZERO_CROSSOVER:
            #Buy if MACD goes from negative to postive. Sell otherwise
            buy_sig = (self.data[self.macd.macd_name] > 0)\
                       .rolling(self.buffer).apply(buffer_all).fillna(0).astype(bool)
            
            cross_buy_sig = (self.data[self.macd.macd_name].shift(self.buffer) <= 0)

            sell_sig = (self.data[self.macd.macd_name] < 0)\
                        .rolling(self.buffer).apply(buffer_all).fillna(0).astype(bool)
            
            cross_sell_sig = (self.data[self.macd.macd_name].shift(self.buffer) >= 0)
        
        elif method == self.Method.MIXED_CROSSOVER:
            #Buy if MACD goes from negative to positive and it has remained greater than the signal
            #for self.buffer periods. Sell otherwise
            buy_sig = (self.data[self.macd.macd_name] > 0)

            buy_sig&= (self.data[self.macd.macd_name] >= 
                      self.data[self.macd.signal_name])\
                      .rolling(self.buffer).apply(buffer_all).fillna(0)
            
            cross_buy_sig = (self.data[self.macd.macd_name].shift() <= 0)
            
            sell_sig = (self.data[self.macd.macd_name] < 0)
            
            sell_sig &= (self.data[self.macd.macd_name] <= 
                        self.data[self.macd.signal_name])\
                        .rolling(self.buffer).apply(buffer_all).fillna(0).astype(bool)
            
            cross_sell_sig = (self.data[self.macd.macd_name].shift() >= 0)
        
        if self.use_ppo:
                buy_sig |= (self.data[self.macd.ppo_name].abs()) >= self.ppo_threshold
                sell_sig |= (self.data[self.macd.ppo_name].abs()) >= self.ppo_threshold

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
        

