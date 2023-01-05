from investing_companion import indicators
import pandas as pd

class SimpleMovingAverage(indicators.IndicatorBase):
    '''
    The Class used to calculate the SMA indicator. Inherits from IndicatorBase.

    Methods:
    :set_column_names()
    :build_df()
    '''
    def __init__(self, window_size=50,price_point='Close', tag='SMA'):
        '''
        Class constructor. Calls set_column_names after initialising attributes.
        :param: window_size(int): the window size for the RSI. Default=14
        :param tag(str): dentifier name for the instance. Not to be confused with the column names
        :param price_point(str): The price point (Open, Close, High, etc) from which to calculate the indicator
        '''
        super().__init__(price_point,tag)
        self.window_size=window_size
        self.set_column_names()


    def __str__(self):
        return f'SMA{(self.window_size)} (Evaluated on: {self.price_point})'


    def set_column_names(self):
        self.sma_name = f'SMA({self.window_size})'


    def build_df(self, base_df, price_point='Close'): 
        df = pd.DataFrame({self.sma_name: base_df[price_point].rolling(self.window_size, 
                                                                       min_periods=self.window_size)
                                                                       .mean()})
        return df


class ExponentialMovingAverage(indicators.IndicatorBase):
    '''
    The Class used to calculate the EMA indicator. Inherits from IndicatorBase.

    Methods:
    :set_column_names()
    :build_df()
    '''
    def __init__(self,window_size=20,price_point='Close', tag='EMA'):
        '''
        Class constructor. Calls set_column_names after initialising attributes.
        :param: window_size(int): the window size for the SMA. Default=20
        :param tag(str): dentifier name for the instance. Not to be confused with the column names

        '''
        super().__init__(price_point,tag)
        self.window_size = window_size
        self.set_column_names()


    def __str__(self) -> str:
        return f'EMA{(self.window_size)} (Evaluated on: {self.price_point})'


    def set_column_names(self):
        self.ema_name = f'EMA({self.window_size})'


    def build_df(self, base_df):
        df = pd.DataFrame({self.ema_name: base_df[self.price_point].ewm(span = self.window_size, 
                                                                        min_periods=self.window_size, 
                                                                        adjust=False).mean()})
        return df
