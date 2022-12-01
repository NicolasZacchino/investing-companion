from investing_companion import indicators

class BollingerBands(indicators.IndicatorBase):
    '''
    Class for the Bollinger bands indicator. Inherits from IndicatorBase
    :param base_df: the Dataframe containing the necessary data to calculate the bands
    :param window_size: the size of the window used in the SMA calculation. Default=20
    :param std_deviations: The amount of standard deviations used to determine the bands. Default=2
    :param tag: Identifier name for the instance. Not to be confused with the column names

    Methods:
    bol_bands()
    '''
    def __init__(self, base_df, window_size = 20, std_deviations=2, tag='Boll_Bands'):
        super().__init__(base_df, tag)
        self.window_size = window_size
        self.std_deviations = std_deviations
        self.bol_bands()
        
    
    def bol_bands(self):
        sma = self.base_df.rolling(self.window_size, min_periods=self.window_size).mean()
        stdev = self.base_df.rolling(self.window_size, min_periods=self.window_size).std(ddof=0)
        upper_band = sma + stdev*self.std_deviations
        lower_band = sma - stdev*self.std_deviations

        self.df['BB_Upper'] = upper_band
        self.df['BB_Lower'] = lower_band