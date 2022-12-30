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
        

    def backtest_strategy(self, start=None):
        def buffer_all(i):
            return i.all()
        
        if start is None:
            start = max([self.macd.slowema_window, self.macd.signal_window])

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
                                .iloc[start:].sum()
            
        self.data['strat_returns'] = self.data['strat_returns'].cumsum()
        
        return performance


    def _find_optimum(self,range,to_modify, max_iterations=10, **kwargs):
        '''
        Method to find the optimum value, used in optimize_strat_params(). Not meant to be 
        called directly

        :param range: the range [a,b] over which the optimization will take place. First, it calculates
        the middle value c = (a+b)/2, then, given a function f, calculates f(a),f(b),f(c). The value whose
        function output is the lowest is discarded and the process is repeated with the remaining numbers
        :param to_modify: string which tells the method which variable is the one to be optimized
        :param max_iterations: the max number of iterations before the loop ends
        :**kwargs: used to feed custom data (such as variables that have already been optimized) to the 
        method
        '''
        f_ema = kwargs.get('fast_ema',self.macd.fastema_window)
        s_ema = kwargs.get('slow_ema',self.macd.slowema_window)
        signal = kwargs.get('signal', self.macd.signal_window)
        buffer = kwargs.get('buffer', self.buffer)
        round_numbers = kwargs.get('round_numbers', False)
        ppo_threshold = kwargs.get('ppo_threshold', self.ppo_threshold)
        fast_slow_ratio = (26/12)

        xlow, xhigh = min(range), max(range)
        for _ in range(max_iterations):
            xmid_start = (xlow+xhigh)/2
            if round_numbers:
                xmid = int(round(xmid_start))
            else:
                xmid = xmid_start
            xlist = [xlow,xmid,xhigh]
            xdict = {}
            for x in xlist:
                if to_modify == 'fast_ema':
                    f_ema = x
                    s_ema = int(round(f_ema*fast_slow_ratio))
                elif to_modify == 'signal':
                    signal = x
                elif to_modify == 'buffer':
                    buffer = x
                elif to_modify == 'ppo':
                    ppo_threshold = x   
                elif to_modify is None:
                    return
                
                macd = macd.MACD(s_ema,f_ema,signal)
                strat = strategy.macd_strategy.Macd_Strategy(self.symbol,
                                                             start=self.start,
                                                             end=self.end,
                                                             period=self.period,
                                                             macd_object=macd,
                                                             buffer=buffer,
                                                             method=self.method,
                                                             use_ppo=self.use_ppo,
                                                             ppo_threshold=ppo_threshold)  
                perf = strat.backtest_strategy()['strat_returns']
                xdict[x] = perf

            m = min(xdict.values())
            if xdict[xmid] == m:
                break
            xdict = {key:value for key,value in xdict if xdict[key] != m}
            xhigh = max(xdict.keys())
            xlow = min(xdict.keys())
        
        optimum_x = max(xdict, key=xdict.get)
        return optimum_x
            

    def optimize_strat_params(self,
                              fastema_range, 
                              signal_range,
                              buffer_range=None,
                              ppo_range=None,
                              max_iterations=10 ):
        '''
        Optimization method for the strategy. Uses a greedy approach through bisection.

        :param fastema_range: Mandatory range to be used for the Fast EMA optimization. The slow EMA
        will be calculated keeping the ratio that exists between the default values (12 and 26)
        :param signal_range: Mandatory. Range over which the signal will be optimized
        :param buffer_range: Optional. Range for the buffer
        :param ppo_range: Optional. Range for the ppo threshold. Does nothing if self.use_ppo is False
        :param max_iterations: Optional. How many times to iterate through bisection. The 
        iteration loop is coded to exit if the middle value is lower than both of the extremes regardless of this
        value. Default=10
        '''
        results = {}
        opt_f_ema= self.find_optimum(fastema_range, 
                                     to_modify='fast_ema', 
                                     fast_ema=self.macd.fastema_window)
        opt_s_ema = int(round(opt_f_ema*(26/12)))
       
        results['Fast EMA'] = opt_f_ema
        results['Slow EMA'] = opt_s_ema

        opt_signal = self._find_optimum(signal_range,
                                       to_modify='signal',
                                       fast_ema=opt_f_ema,
                                       slow_ema=opt_s_ema,)
        
        results['Signal'] = opt_signal

        if buffer_range is not None:
            opt_buffer = self._find_optimum(buffer_range,
                                            to_modify='buffer',
                                            fast_ema=opt_f_ema,
                                            slow_ema=opt_s_ema,
                                            signal=opt_signal)              
            results['Buffer'] = opt_buffer
        
        if ppo_range is not None and self.use_ppo:
            use_buffer = results['Buffer'] if 'Buffer' in results.keys() else self.buffer
            opt_ppo = self._find_optimum(ppo_range,
                                         to_modify='ppo',
                                         fast_ema=opt_f_ema,
                                         slow_ema=opt_s_ema,
                                         signal=opt_signal,
                                         buffer=use_buffer)
            results['PPO'] = opt_ppo

        return results
