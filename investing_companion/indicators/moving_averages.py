from investing_companion import indicators

class SimpleMovingAverage(indicators.IndicatorBase):
    '''
    The Class used to calculate the SMA indicator. Inherits from IndicatorBase.

    :param: base_df: The Dataframe which contains the data needed for SMA calculation
    :param: window_size: the window size for the SMA. Default=50
    :param tag: dentifier name for the instance. Not to be confused with the column names

    Methods:
    get_latest_value()
    sma()
    '''
    def __init__(self, base_df, window_size=50, tag='SMA'):
        super().__init__(base_df, tag)
        self.window_size=window_size
        self.sma()
    
    def get_latest_value(self):
        return self.df.iat[-1,0]
        
    def sma(self):
        self.df['SMA'] = self.base_df.rolling(self.window_size, min_periods=self.window_size).mean()


class ExponentialMovingAverage(indicators.IndicatorBase):
    '''
    The Class used to calculate the EMA indicator. Inherits from IndicatorBase.

    :param: base_df: The Dataframe which contains the data needed for EMA calculation
    :param: window_size: the window size for the SMA. Default=20
    :param tag: dentifier name for the instance. Not to be confused with the column names

    Methods:
    get_latest_value()
    ema()
    '''
    def __init__(self, base_df,window_size=20, name='EMA'):
        super().__init__(base_df, name)
        self.window_size = window_size
        self.ema()

    def get_latest_value(self):
        return self.df.iat[-1,0]

    def ema(self):
        self.df['EMA'] = self.df.ewm(span = self.window_size, 
    min_periods=self.window_size, adjust=False).mean()