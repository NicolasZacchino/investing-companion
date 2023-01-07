from investing_companion.indicators import moving_averages
from investing_companion import strategy
from enum import Enum, auto
import pandas as pd 
import numpy as np


class Ma_Strategy(strategy.BaseStrategy):
    class Method(Enum):
        PRICE_CROSSOVER = auto()
        IND_ORDERED = auto()

    def __init__(self, symbol, start=None, end=None,
                 period='max', ma_objs=None,
                 method=Method.PRICE_CROSSOVER,
                 buffer=1):
        super().__init__(symbol,start,end,period)
        self.ma_objs = [moving_averages.SimpleMovingAverage()] if ma_objs is None else ma_objs
        self.ma_objs.sort(key=lambda x: x.window_size)
        self.ma_names = [m.ma_name for m in self.ma_objs]
        self.buffer = buffer
        self.method = method
        self.data = pd.concat([self.data, *[m.build_df(self.symbol) for m in self.ma_objs]], axis=1)
        self.create_conditions()


    def create_conditions(self):
        if self.method == self.Method.IND_ORDERED:
            #buy when the MAs become ordered in such a way that the faster MAs are above and
            #the slower ones below. Sell when this stops being True
            dif = np.sign(self.data[self.ma_names].diff(-1, axis='columns')).iloc[:,:-1]

            buy_sig = dif.eq(1).all(axis='columns').rolling(self.buffer).apply(buffer_all)\
                      .fillna(0).astype(bool)
            cross_buy_sig = dif.shift(self.buffer).ne(1).any(axis='columns').fillna(0).astype(bool)

            sell_sig = dif.eq(-1).all(axis='columns').rolling(self.buffer).apply(buffer_all)\
                       .fillna(0).astype(bool)
            cross_sell_sig = dif.shift(self.buffer).ne(-1).any(axis='columns').fillna(0).astype(bool)
        
        if self.method == self.Method().PRICE_CROSSOVER:
            #buy the moment the price is above all the provided indicators. Sell otherwise
            buy_sig = (self.data.idxmax(axis=1) == 'Close').rolling(self.buffer).apply(buffer_all)\
                      .fillna(0).astype(bool)
            cross_buy_sig = (self.data.shift(self.buffer).idxmin(axis=1) == 'Close').fillna(0).astype(bool)

            sell_sig = (self.data.idxmin(axis=1) == 'Close').rolling(self.buffer).apply(buffer_all)\
                        .fillna(0).astype(bool)
            cross_sell_sig = (self.data.shift(self.buffer).idxmax(axis=1) == 'Close').fillna(0).astype(bool)

        self.buy_cond = buy_sig & cross_buy_sig
        self.sell_cond = sell_sig & cross_sell_sig


    def backtest_strategy(self):
        start = max(self.ma_objs, key=lambda x: x.window_size)
        self.data['signal'] = self.get_signal_column(self.buy_cond,self.sell_cond)
        return self.get_performance(start=start)


    def optimize_strat_params(self):
        '''Probably too complex to implement efficiently'''
        raise NotImplementedError()