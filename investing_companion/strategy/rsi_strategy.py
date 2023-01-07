from investing_companion.indicators import rsi
from investing_companion import strategy
import pandas as pd
import numpy as np
from enum import Enum, auto

class RSI_Strategy(strategy.BaseStrategy):
    '''
    RSI-based strategy. Inherits from BaseStrategy

    :Methods:
    create_conditions()
    backtest_strategy()
    _find_optimum()
    optimize_strat_params()
    create_trend_columns()
    '''
    class Method(Enum):
        DEFAULT = auto()
        TREND_RANGES = auto()
        TREND_RANGES_SAFE = auto()
    

    def __init__(self, symbol, start=None, end=None, period='max',
                 rsi_obj=rsi.RelativeStrengthIndex(), buffer=1, method=Method.DEFAULT,
                 overbought_threshold=70, oversold_threshold=30,
                 uptrend_start=40, downtrend_start=60,
                 uptrend_support_high=50,
                 downtrend_resist_low=50,):
        """Class constructor

        Args:
            symbol (string): The ticker to be used
            start (string, optional): start date for the retrieval of the data from symbol. Defaults to None.
            end (string, optional): end date for the retrieval of the data. Defaults to None.
            period (str, optional): time period (ie '1y') used. Defaults to 'max'
            rsi_obj (_type_, optional): the RSI object to use. Defaults to an object with default values.
            buffer (int, optional): How many days should a condition hold true for a signal to be
            emitted. Defaults to 1.
            method (Method(enum), optional): Method to use. Defaults to Method.DEFAULT.
            overbought_threshold (int, optional): RSI value over which the stock is considered 
            overbought. Defaults to 70.
            oversold_threshold (int, optional):  RSI value over which the stock is considered 
            oversold. Defaults to 30.
            uptrend_start (int, optional): RSI value over which the stock is considered
            to be in an uptrend. Can have some overlap with downtrend_start. Defaults to 40.
            downtrend_start (int, optional): RSI value under which the stock is considered
            to be in a downtrend. Can have some overlap with uptrend_start. Defaults to 60.
            uptrend_support_high (int, optional): the upper value of the support band
            for an uptrend (the lower one is considered the start point. This value is 
            expected to be higher than that). Defaults to 50.
            downtrend_resist_low (int, optional): the lower value for the resistance
            band for a downtrend (the upper one is the start point. This value is expected
            to be lower than that). Defaults to 50.
        """        
        super().__init__(symbol, start, end, period)
        self.rel_str = rsi_obj
        self.buffer = buffer
        self.method = method
        self.overbought_threshold = overbought_threshold
        self.oversold_threshold = oversold_threshold
        self.uptrend_start = uptrend_start
        self.downtrend_start = downtrend_start
        self.uptrend_support_high = uptrend_support_high
        self.downtrend_resist_low = downtrend_resist_low
        self.data = pd.concat([self.data, self.rel_str.build_df(self.data)], axis=1)
        self.create_conditions()


    def create_trend_columns(self):
        """Creates a Pandas series where the value is 1 if the stock is in an uptrend and 
        -1 if it is in a downtrend. This is calculated using the values provided on initialization
        and the previous values of the series itself to account for overlap in ranges.

        Returns:
            Pandas Series
        """        
        df = pd.DataFame()
        uptrend = self.data[self.rel_str.rsi_name] >= self.uptrend_start
        downtrend = self.data[self.rel_str.rsi_name] <= self.downtrend_start
        df['zone'] = np.select([uptrend&downtrend, uptrend, downtrend],[0,1,-1], 0)
        df['trend'] = df['zone'].replace(to_replace=0, method='ffill')

        return df['trend']


    def create_conditions(self):
        if self.method == self.Method.DEFAULT:
            #Buy when rsi reaches the oversold threshold and remains oversold for self.buffer periods
            #Sell when the rsi reaches the overbought threshold and remains overbought for self.buffer periods
            buy_sig = (self.data[self.rel_str.rsi_name] < self.oversold_threshold)\
                      .rolling(self.buffer).apply(self.buffer_all).fillna(0).astype(bool)

            cross_buy_sig = (self.data[self.rel_str.rsi_name].shift(self.buffer) >= self.oversold_threshold)

            sell_sig = (self.data[self.rel_str.rsi_name] > self.overbought_threshold)\
                      .rolling(self.buffer).apply(self.buffer_all).fillna(0).astype(bool)

            cross_sell_sig = (self.data[self.rel_str.rsi_name].shift(self.buffer) <= 
                              self.overbought_threshold)

        if self.method == self.Method.TREND_RANGES or self.method == self.Method.TREND_RANGES_SAFE:
            #Buy when the RSI, being in an uptrend (as determined by the DataFrame returned by 
            # create_trend_columns()) recognizes the resistance band defined by 
            # [self.uptrend_start, self.uptrend_support_high]
            #Sell when this resistance is broken (trend reversal)
            self.data['trend'] = self.create_trend_columns()

            buy_sig=(self.data[self.rel_str.rsi_name] > self.uptrend_support_high)\
                    .rolling(self.buffer).apply(self.buffer_all).fillna(0).astype(bool) &\
                    (self.data['trend'].eq(1))

            cross_buy_sig = (self.data[self.rel_str.rsi_name].shift(self.buffer) <
                             self.uptrend_support_high)
            
            sell_sig = (self.data['trend'].eq(-1)).rolling(self.buffer).apply(self.buffer_all).fillna(0)\
                       .astype(bool)
            
            cross_sell_sig = (self.data['trend'].shift(self.buffer).eq(1))

            if self.method == self.Method.TREND_RANGES:
                #We also consider a buy signal if there is a trend reversal (self.data['trend']
                # goes from -1 to 1)
                buy_sig |= (self.data['trend'].eq(1)).rolling(self.buffer).apply(self.buffer_all).fillna(0)\
                           .astype(bool)

                cross_buy_sig |= (self.data['trend'].shift(self.buffer)).eq(-1)

        self.buy_cond = buy_sig & cross_buy_sig
        self.sell_cond = sell_sig & cross_sell_sig


    def backtest_strategy(self):
        start = self.rel_str.window_size
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
        rsi_window = kwargs.get('rsi_window',self.rel_str.window_size)
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
                if to_modify == 'rsi_window':
                    rsi_window = x
                elif to_modify == 'buffer':
                    buffer = x 
                elif to_modify is None:
                    return
                
                relstr = rsi.RelativeStrengthIndex(rsi_window)
                strat = strategy.rsi_strategy.RSI_Strategy(self.symbol,
                                                           start=self.start,
                                                           end=self.end,
                                                           period=self.period,
                                                           rsi_obj=relstr,
                                                           buffer=buffer,
                                                           method=self.method,
                                                           overbought_threshold=self.overbought_threshold,
                                                           oversold_threshold=self.oversold_threshold,
                                                           uptrend_start=self.uptrend_start,
                                                           downtrend_start=self.downtrend_start,
                                                           uptrend_support_high=self.uptrend_support_high,
                                                           downtrend_resist_low=self.downtrend_resist_low)  
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
                              rsi_range,
                              buffer_range=None,
                              max_iterations=5):
        results = {}

        results['Window'] = self._find_optimum(rsi_range, 'rsi_window', round_numbers=True)
        if buffer_range is not None:
            results['buffer'] = self._find_optimum(buffer_range, 
                                                   'buffer', 
                                                   rsi_window=results['Window'],
                                                   round_numbers=False)
        return results