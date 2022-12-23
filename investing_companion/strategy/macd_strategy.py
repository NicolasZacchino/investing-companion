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
    :param method(Method Enum): Which method will be used in the strategy. Default= SIGNAL_CROSSOVER
    :param use_ppo(bool): If True, the strategy also considers a buy/sell signal if the PPO reaches a threshold.
    default = False. (Note that the PPO is always used for the PPO_ONLY method)
    :param ppo_threshold(float): the threshold that will be used for any method that uses the ppo. Default=2.5

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

        :PPO_ONLY: Only use the ppo threshold as a buy/sell signal
        '''
        SIGNAL_CROSSOVER = auto()
        ZERO_CROSSOVER = auto()
        MIXED_CROSSOVER = auto()
        PPO_ONLY = auto


    def __init__(self, symbol, start=None, end=None, period='max', 
                macd_object = macd.MACD(), buffer=1, method = Method.SIGNAL_CROSSOVER,
                use_ppo=False, ppo_threshold=2.5):
        super().__init__(symbol, start, end, period)
        self.macd = macd_object
        self.use_ppo = use_ppo
        self.ppo_threshold = ppo_threshold
        self.buffer = buffer
        self.method = method
        self.data = pd.concat([self.data, self.macd.build_df(self.data)], axis=1)
        

    def backtest_strategy(self):
        def buffer_all(i):
            return i.all()
        
        if self.method == self.Method.SIGNAL_CROSSOVER:
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


        elif self.method == self.Method.ZERO_CROSSOVER:
            #Buy if MACD goes from negative to postive. Sell otherwise
            buy_sig = (self.data[self.macd.macd_name] > 0)\
                       .rolling(self.buffer).apply(buffer_all).fillna(0).astype(bool)
            
            cross_buy_sig = (self.data[self.macd.macd_name].shift(self.buffer) <= 0)

            sell_sig = (self.data[self.macd.macd_name] < 0)\
                        .rolling(self.buffer).apply(buffer_all).fillna(0).astype(bool)
            
            cross_sell_sig = (self.data[self.macd.macd_name].shift(self.buffer) >= 0)
        
        elif self.method == self.Method.MIXED_CROSSOVER:
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
        
        elif self.method == self.Method.PPO_ONLY:
            buy_sig = (self.data[self.macd.ppo_name]) >= self.ppo_threshold
            cross_buy_sig = (self.data[self.macd.ppo_name].shift(self.buffer) <
                            self.ppo_threshold)
            
            sell_sig = (self.data[self.macd.ppo_name]) <= np.negative(self.ppo_threshold)
            cross_sell_sig = (self.data[self.macd.ppo_name].shift(self.buffer) >
                              np.negative(self.ppo_threshold))
        
        if self.use_ppo:
                buy_sig |= (self.data[self.macd.ppo_name]) >= self.ppo_threshold
                sell_sig |= (self.data[self.macd.ppo_name]) <= np.negative(self.ppo_threshold)

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


    def optimize_strat_params(self,
                              indic_optimization_range = 20, 
                              optimize_buffer=False, 
                              buffer_optimization_range = 2,
                              optimize_ppo=False,
                              ppo_optimization_range=4):
        '''
        Optimization method for the strategy. Uses a greedy approach through bisection

        :param indic_optimization_range: the range over which the indicator parameters will vary.
        for a range R, every parameter N will be optimized sequentially 
        used bisection over a [N-R/2; N+R/2] range. Default=20
        :param optimize_buffer: whether or not optimize the buffer after optimizing the indicator.
        Default=False
        :param buffer_optimization_range: for a buffer B and a range R, the buffer will be iterated over
        every B+Rn in [B; B+R]. This number is expected to be small because of this. Default=2
        :param optimize_ppo: whether or not to optimize the ppo threshold. Same approach as the 
        indicator parameters. Only does something if self.use_ppo=True or self.Method = Method.PPO_ONLY
        :param ppo_optimization_range: The range over which to optimize the threshold. Same approach as the
        indicator parameters.
        '''
        return
        

