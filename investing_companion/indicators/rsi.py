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
        prices = pd.DataFrame(self.base_df)
        prices['diff'] = prices.diff(1)
        prices['upward'] = prices['diff'].clip(lower=0).round(2)
        prices['downward'] = prices['diff'].clip(upper=0).abs().round(2)
        
    

        prices['average_upward'] = prices['upward'].rolling(self.window_size,
                                                            min_periods=self.window_size)\
                                                            .mean()[:self.window_size+1]

        prices['average_downward'] = prices['downward'].rolling(self.window_size,
                                                                min_periods=self.window_size)\
                                                                .mean()[:self.window_size+1]

        #Calculating Wilder's Smoothing Mean (WSM)
        #Average gains
        for i, row in enumerate(prices['average_upward'].iloc[self.window_size+1:]):
            prices['average_upward'].iloc[i+self.window_size+1] =\
                (prices['average_upward'].iloc[i+self.window_size]*
                (self.window_size-1) +
                prices['upward'].iloc[i+self.window_size+1])\
                    /self.window_size
        #Average Losses
        for i, row in enumerate(prices['average_downward'].iloc[self.window_size+1:]):
            prices['average_downward'].iloc[i+self.window_size+1] =\
                (prices['average_downward'].iloc[i+self.window_size]*
                (self.window_size-1) +
                prices['downward'].iloc[i+self.window_size+1])\
                    /self.window_size

        prices['rs'] = prices['average_upward']/prices['average_downward']
        self.df['RSI'] = 100 - (100/(1.0+prices['rs'])) 