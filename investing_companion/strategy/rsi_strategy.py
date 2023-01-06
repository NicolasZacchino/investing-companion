from investing_companion.indicators import rsi
from investing_companion import strategy
import pandas as pd
import numpy as np
from enum import enum, auto

class RSI_Strategy(strategy.BaseStrategy):
    class Method(enum):
        DEFAULT = auto()
        TREND_RANGES = auto()
    
    def __init__(self, symbol, start=None, end=None, period='max',
                 rsi_obj=rsi.RelativeStrengthIndex(), buffer=1, method=Method.DEFAULT,
                 overbought_threshold=70, oversold_threshold=30,
                 uptrend_range=None, downtrend_range=None,
                 show_trend_column=False):
        super().__init__(symbol, start, end, period)
        self.rel_str = rsi_obj
        self.buffer = buffer
        self.method = method
        self.overbought_threshold = overbought_threshold
        self.oversold_threshold = oversold_threshold
        self.uptrend_range = [40,90] if uptrend_range is None else uptrend_range
        self.downtrend_range = [10,60] if downtrend_range is None else downtrend_range
        self.data = pd.concat([self.data, self.rel_str.build_df(self.data)], axis=1)
        self.create_conditions()

    def create_trend_columns(self):
        df = pd.DataFame()
        uptrend = self.data[self.rel_str.rsi_name].between(self.uptrend_range[0], self.uptrend_range[1])
        downtrend = self.data[self.rel_str.rsi_name].between(self.downtrend_range[0], self.downtrend_range[1])
        
        df['zone'] = np.select([uptrend&downtrend, uptrend, downtrend],[0,1,-1], default=0)
        df['trend'] = df['zone'].replace(to_replace=0, method='ffill')

        return df['trend']

    def create_conditions(self):
        pass

    def backtest_strategy(self):
        pass

    def optimize_strat_params(self):
        pass