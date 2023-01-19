from investing_companion.indicators import moving_averages
from investing_companion import strategy
from enum import Enum, auto
import pandas as pd 
import numpy as np

class Ma_Strategy(strategy.BaseStrategy):
    """MA-based strategy. Inherits from BaseStrategy

    Methods:
    create_conditions()
    backtest_strategy()
    optimize_strat_params() [raises NotImplementedError. see docstring]
    """    
    class Method(Enum):
        PRICE_CROSSOVER = auto()
        IND_ORDERED = auto()

    def __init__(self, symbol, start=None, end=None,
                 period='max', ma_objs=None,
                 method=Method.PRICE_CROSSOVER,
                 buffer=1):
        """Constructor for the MA-based strategy

        Args:
            symbol (String): Base Ticker to be used
            start (string, optional): start date for the retrieval of the data from symbol. Defaults to None.
            end (string, optional): end date for the retrieval of the data. Defaults to None.
            period (str, optional): time period (ie '1y') used 
            if either start or end are None. Defaults to 'max'. 
            ma_objs (list[moving_averages], optional): list with MA objects to be used for the strategy. 
            Defaults to None.
            method (Method(enum), optional): Method to use. Defaults to Method.PRICE_CROSSOVER.
            buffer (int, optional): How many days should a condition hold true for a signal to be
            emitted. Defaults to 1.
        """        
        super().__init__(symbol,start,end,period)
        self.ma_objs = [moving_averages.SimpleMovingAverage()] if ma_objs is None else ma_objs
        self.ma_objs.sort(key=lambda x: x.window_size)
        self.ma_names = [m.ma_name for m in self.ma_objs]
        self.buffer = buffer
        self.method = method
        self.data = pd.concat([self.data, *[m.build_df(self.data) for m in self.ma_objs]], axis=1)
        self.create_conditions()


    def create_conditions(self):
        if self.method == self.Method.IND_ORDERED:
            #buy when the MAs become ordered in such a way that the faster MAs are above and
            #the slower ones below. Sell when this stops being True
            dif = np.sign(self.data[self.ma_names].diff(-1, axis='columns')).iloc[:,:-1]

            buy_sig = dif.eq(1).all(axis='columns').rolling(self.buffer).apply(self.buffer_all)\
                      .fillna(0).astype(bool)
            cross_buy_sig = dif.shift(self.buffer).ne(1).any(axis='columns').fillna(0).astype(bool)

            sell_sig = dif.eq(-1).all(axis='columns').rolling(self.buffer).apply(self.buffer_all)\
                       .fillna(0).astype(bool)
            cross_sell_sig = dif.shift(self.buffer).ne(-1).any(axis='columns').fillna(0).astype(bool)
        
        if self.method == self.Method.PRICE_CROSSOVER:
            not_null_cond = (self.data[[*self.ma_names]].notnull()).all(axis=1)
            #buy the moment the price is above all the provided indicators. Sell otherwise
            buy_sig = (self.data[['Close', *self.ma_names]].idxmax(axis=1) == 'Close')\
                      .rolling(self.buffer)\
                      .apply(self.buffer_all)\
                      .astype(bool)
                      

            cross_buy_sig = (self.data[['Close', *self.ma_names]].shift(self.buffer).idxmin(axis=1) == 'Close')\
                            .astype(bool)

            sell_sig = (self.data[['Close', *self.ma_names]].idxmin(axis=1) == 'Close')\
                       .rolling(self.buffer)\
                       .apply(self.buffer_all)\
                       .astype(bool)

            cross_sell_sig = (self.data[['Close', *self.ma_names]].shift(self.buffer).idxmax(axis=1) == 'Close')\
                             .astype(bool)

        self.buy_cond = buy_sig & cross_buy_sig & not_null_cond
        self.sell_cond = sell_sig & cross_sell_sig & not_null_cond


    def backtest_strategy(self):
        start = max(self.ma_objs, key=lambda x: x.window_size)
        self.data['signal'] = self.get_signal_column(self.buy_cond,self.sell_cond)
        return self._get_performance(start=start.window_size)


    def optimize_strat_params(self):
        '''Probably too complex to implement efficiently'''
        raise NotImplementedError()