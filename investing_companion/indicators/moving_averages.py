from investing_companion import indicators
import pandas as pd

class SimpleMovingAverage(indicators.IndicatorBase):
    '''
    The Class used to calculate the SMA indicator. Inherits from IndicatorBase.

    :param: base_df: The Dataframe which contains the data needed for SMA calculation
    :param: window_size: the window size for the SMA. Default=50
    :param tag: dentifier name for the instance. Not to be confused with the column names

    Methods:
    set_column_names()
    build_df()
    '''
    def __init__(self, window_size=50, tag='SMA'):
        super().__init__(tag)
        self.window_size=window_size
        self.set_column_names()


    def set_column_names(self):
        self.sma_name = f'SMA({self.window_size})'


    def build_df(self, base_df): 
        df = pd.DataFrame({self.sma_name: base_df.rolling(self.window_size, 
                                                     min_periods=self.window_size).mean()})

        return df


class ExponentialMovingAverage(indicators.IndicatorBase):
    '''
    The Class used to calculate the EMA indicator. Inherits from IndicatorBase.

    :param: base_df: The Dataframe which contains the data needed for EMA calculation
    :param: window_size: the window size for the SMA. Default=20
    :param tag: dentifier name for the instance. Not to be confused with the column names

    Methods:
    set_column_names()
    build_df()
    '''
    def __init__(self,window_size=20, tag='EMA'):
        super().__init__(tag)
        self.window_size = window_size
        self.set_column_names()


    def set_column_names(self):
        self.ema_name = f'EMA({self.window_size})'


    def build_df(self, base_df):
        df = pd.DataFrame({self.ema_name: base_df.ewm(span = self.window_size, 
                                                 min_periods=self.window_size, 
                                                 adjust=False).mean()})

        return df
