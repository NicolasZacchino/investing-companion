from investing_companion import indicators
import pandas as pd

class MACD(indicators.IndicatorBase):
    '''
    The Class used to calculate the MACD indicator. Inherits from IndicatorBase.

    :param: base_df: The Dataframe which contains the data needed for MACD calculation
    :param: slowema_window: the window size for the slow EMA. Default=26
    :param: fastema_window: the window size for the fast EMA. Default=12
    :param signal_window: the window size for the signal line. Default=9
    :param tag: dentifier name for the instance. Not to be confused with the column names

    Methods:
    get_latest_value()
    macd()
    '''
    def __init__(self,base_df, 
                 slowema_window=26, 
                 fastema_window=12, 
                 signal_window=9, 
                 tag='MACD'):

        super().__init__(base_df, tag)
        self.slowema_window = slowema_window
        self.fastema_window = fastema_window
        self.signal_window = signal_window
        self.macd()

    def macd(self):
        slow_ema = self.base_df.ewm(span=self.slowema_window,
                                    min_periods=self.slowema_window, 
                                    adjust=False).mean()
        
        fast_ema = self.base_df.ewm(span = self.fastema_window,
                                    min_periods=self.fastema_window, 
                                    adjust=False).mean()

        macd_line = fast_ema.subtract(slow_ema)

        signal_line = macd_line.ewm(span=self.signal_window,
                                    min_periods=self.signal_window, 
                                    adjust=False).mean()

        self.df = pd.DataFrame({'MACD': macd_line,
                                'Signal': signal_line, 
                                'Histogram': macd_line-signal_line})

        