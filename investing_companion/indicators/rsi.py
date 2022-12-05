from investing_companion import indicators
import pandas as pd

class RelativeStrengthIndex(indicators.IndicatorBase):
    '''
    The Class used to calculate the RSI indicator. Inherits from IndicatorBase.

    :param: base_df: The Dataframe which contains the data needed for RSI calculation
    :param: window_size: the window size for the RSI. Default=14
    :param tag: dentifier name for the instance. Not to be confused with the column names

    Methods:
    rsi()
    '''
    def __init__(self, base_df, window_size=14, tag='RSI'):
        super().__init__(base_df, tag)
        self.window_size = window_size
        self.rsi()
      
    def rsi(self):
        self.df['diff'] = self.base_df.diff(1)
        self.df['upward'] = self.df['diff'].clip(lower=0).round(2)
        self.df['downward'] = self.df['diff'].clip(upper=0).abs().round(2)
        
    

        self.df['average_upward'] = self.df['upward'].rolling(self.window_size,
                                                              min_periods=self.window_size)\
                                                              .mean()[:self.window_size+1]

        self.df['average_downward'] = self.df['downward'].rolling(self.window_size,
                                                                  min_periods=self.window_size)\
                                                                  .mean()[:self.window_size+1]

        #Calculating Wilder's Smoothing Mean (WSM)
        #Average gains
        for i, row in enumerate(self.df['average_upward'].iloc[self.window_size+1:]):
            self.df['average_upward'].iloc[i+self.window_size+1] =\
                (self.df['average_upward'].iloc[i+self.window_size]*
                (self.window_size-1) +
                self.df['upward'].iloc[i+self.window_size+1])\
                    /self.window_size
        #Average Losses
        for i, row in enumerate(self.df['average_downward'].iloc[self.window_size+1:]):
            self.df['average_downward'].iloc[i+self.window_size+1] =\
                (self.df['average_downward'].iloc[i+self.window_size]*
                (self.window_size-1) +
                self.df['downward'].iloc[i+self.window_size+1])\
                    /self.window_size

        self.df['rs'] = self.df['average_upward']/self.df['average_downward']
        self.df['RSI'] = 100 - (100/(1.0+self.df['rs'])) 
        self.df = self.df[['RSI']]