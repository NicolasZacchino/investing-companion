from investing_companion.indicators import bollinger
from investing_companion import strategy
import pandas as pd
import numpy as np
from enum import enum, auto

class Bollinger_Strategy(strategy.BaseStrategy):
    
    class Method(Enum):
        BAND_CROSSOVER_SIMPLE = auto()
        DOUBLE_BAND_CROSSOVER = auto()

    def __init__(self, symbol, start=None, end=None, period='max',
                 bollinger_obj=bollinger.BollingerBands(), 
                 method=Method.BAND_CROSSOVER_SIMPLE,
                 buffer=1):
        super().__init__(symbol, start, end, period)
        self.bol_band = bollinger_obj
        self.method = method
        self.buffer = buffer
        self.data = pd.concat([self.data, self.bol_band.build_df(self.data)], axis=1)
    
    def backtest_strategy(self):
        pass

    def optimize_strat_params(self):
        pass