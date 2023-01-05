from investing_companion.indicators import bollinger
from investing_companion import strategy
import pandas as pd
import numpy as np
from enum import enum, auto

class Bollinger_Strategy(strategy.BaseStrategy):
    '''
    Bollinger bands-based strategy. Inherits from BaseStrategy

    :Methods:
    create_conditions()
    backtest_strategy()
    _find_optimum()
    optimize_strat_params()
    '''
    class Method(Enum):
        BAND_CROSSOVER_SIMPLE = auto()
        DOUBLE_BAND_TEST = auto()


    def __init__(self, symbol, start=None, end=None, period='max',
                 bollinger_obj=bollinger.BollingerBands(), 
                 method=Method.BAND_CROSSOVER_SIMPLE,
                 buffer=1):
        """Constructor for the Bollinger-based strategy

        Args:
            symbol (String): Base Ticker to be used
            start (string, optional): start date for the retrieval of the data from symbol. Defaults to None.
            end (string, optional): end date for the retrieval of the data. Defaults to None.
            period (str, optional): time period (ie '1y') used 
            if either start or end are None. Defaults to 'max'. 
            bollinger_obj (bollinger.BollingerBands(), optional): the B_bands to be used. 
            Defaults to a bollinger object with default values.
            method (optional): Method to use. Defaults to Method.BAND_CROSSOVER_SIMPLE.
            buffer (int, optional): How many days should a condition hold true for a signal to be
            emitted. Defaults to 1.
        """        
        super().__init__(symbol, start, end, period)
        self.bol_band = bollinger_obj
        self.method = method
        self.buffer = buffer
        self.data = pd.concat([self.data, self.bol_band.build_df(self.data)], axis=1)
        self.create_conditions()
    

    def create_conditions(self):
        if self.method == Method.BAND_CROSSOVER_SIMPLE:
            #Sell if the Price breaks the upper band. Buy if it breaks the upper one
            buy_sig = (self.data['Close'] < self.data[self.bol_band.lower_band_name])\
                      .rolling(self.buffer).apply(self.buffer_all).fillna(0).astype(bool)
            
            cross_buy_sig = (self.data['Close'].shift(self.buffer) >= 
                             self.data[self.bol_band.lower_band_name].shift(self.buffer-1))
            
            sell_sig = (self.data['Close'] > self.data[self.bol_band.upper_band_name])\
                      .rolling(self.buffer).apply(self.buffer_all).fillna(0).astype(bool)
            
            cross_sell_sig = (self.data['Close'].shift(self.buffer) <= 
                             self.data[self.bol_band.upper_band_name].shift(self.buffer-1))
        
        if self.method == Method.DOUBLE_BAND_TEST:
            #Sell if the Price breaks the upper band and has also done so in the last self.buffer periods.
            #Buy if it breaks the lower band and also broke it in the last self.buffer periods
            buy_sig = ((self.data['Close'] < self.data[self.bol_band.lower_band_name]) &\
                       (self.data['Close'].shift() >= self.data[self.bol_band.lower_band_name]))\
                       .rolling(self.buffer).sum() >= 2
            cross_buy_sig = True

            sell_sig = ((self.data['Close'] > self.data[self.bol_band.upper_band_name]) &\
                       (self.data['Close'].shift() <= self.data[self.bol_band.upper_band_name]))\
                       .rolling(self.buffer).sum() >= 2
            cross_sell_sig = True
        
        self.buy_cond = buy_sig & cross_buy_sig
        self.sell_cond = sell_sig & cross_sell_sig


    def backtest_strategy(self):
        start = self.bol_band.window_size
        self.data['signal'] = self.get_signal_column(self.buy_cond, self.sell_cond)
        return self.get_performance(start=start)


    def _find_optimum(self,range_to_use,to_modify, max_iterations=5, **kwargs):
        '''
        Method to find the optimum value, used in optimize_strat_params(). Not meant to be 
        called directly

        :param range_to_use: the range_to_use [a,b] over which the optimization will take place. First, it calculates
        the middle value c = (a+b)/2, then, given a function f, calculates f(a),f(b),f(c). The value whose
        function output is the lowest is discarded and the process is repeated with the remaining numbers
        :param to_modify: string which tells the method which variable is the one to be optimized
        :param max_iterations: the max number of iterations before the loop ends
        :**kwargs: used to feed custom data (such as variables that have already been optimized) to the 
        method
        '''
        ema_window = kwargs.get('ema',self.bol_band.window_size)
        std_dev = kwargs.get('std_dev',self.bol_band.std_deviations)
        buffer = kwargs.get('buffer', self.buffer)
        round_numbers = kwargs.get('round_numbers', False)

        xlow, xhigh = min(range_to_use), max(range_to_use)
        for _ in trange(max_iterations):
            xmid_start = (xlow+xhigh)/2
            if round_numbers:
                xmid = int(round(xmid_start))
            else:
                xmid = xmid_start
            xlist = [xlow,xmid,xhigh]
            xdict = {}
            for x in xlist:
                if to_modify == 'ema':
                    ema_window = x
                elif to_modify == 'std_dev':
                    std_dev = x
                elif to_modify == 'buffer':
                    buffer = x 
                else: return
                
                b_band = bollinger.BollingerBands(window_size=ema_window,
                                                  std_deviations=std_dev)
                strat = strategy.bollinger_strategy.Bollinger_Strategy(self.symbol,
                                                                       start=self.start,
                                                                       end=self.end,
                                                                       period=self.period,
                                                                       bollinger_obj=b_band,
                                                                       buffer=buffer,
                                                                       method=self.method,)
                perf = strat.backtest_strategy()['strat_returns']
                xdict[x] = perf

            m = min(xdict.values())
            if xdict[xmid] == m:
                print('concavity found, breaking loop')
                break
            xdict = {key:value for key,value in xdict.items() if xdict[key] != m}
            xhigh = max(xdict.keys())
            xlow = min(xdict.keys())
        
        optimum_x = max(xdict, key=xdict.get)
        return optimum_x


    def optimize_strat_params(self,
                              ema_range,
                              max_iterations=5,
                              std_range=None,
                              buffer_range=None):
        """Optimizes the parameters of the strategy. Uses a greedy approach through 
        bisection and optimizes in sequence (ema->std->buffer)

        Args:
            ema_range (list[int]): the range to be used in the ema optimization
            max_iterations (int, optional): max number of iteration loops. Defaults to 5.
            std_range (list[int], optional): range for the standard deviations. Defaults to None.
            buffer_range (list[int], optional): range for the buffer. Defaults to None.

        Returns:
            dictionary: a dictionary with the values of all the optimized values
        """              
        results = {}
        results['EMA'] = self._find_optimum(ema_range, 
                                            'ema',
                                            max_iterations=max_iterations,
                                            round_numbers=True)
        
        if std_range is not None:
            results['std_dev'] = self._find_optimum(std_range, 
                                                    'std_dev',
                                                    ema=results['EMA'],
                                                    max_iterations=max_iterations,
                                                    round_numbers=True)
        
        if buffer_range is not None:
            std = results['std_dev'] if 'std_dev' in results.keys() else self.bol_band.std_deviations
            results['buffer'] = self._find_optimum(buffer_range, 
                                                   'buffer',
                                                   ema=results['EMA'],
                                                   std_dev=std,
                                                   max_iterations=max_iterations,
                                                   round_numbers=True)

        return results