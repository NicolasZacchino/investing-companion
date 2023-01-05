from investing_companion import indicators
import pandas as pd

class MACD(indicators.IndicatorBase):
    '''
    The Class used to calculate the MACD indicator. Inherits from IndicatorBase.

    Methods:
    :build_df()
    :set_column_names()
    '''
    def __init__(self, 
                 slowema_window=26, 
                 fastema_window=12, 
                 signal_window=9, 
                 price_point='Close',
                 tag='MACD',
                 ):
        '''
        Class constructor.Calls set_column_names after initializing attributes.

        :param: slowema_window(int): the window size for the slow EMA. Default=26
        :param: fastema_window(int): the window size for the fast EMA. Default=12
        :param signal_window(int): the window size for the signal line. Default=9
        :param tag(str): dentifier name for the instance. Not to be confused with the column names
        :param price_point(str): The price point (Open, Close, High, etc) from which to calculate the indicator
        '''
        super().__init__(price_point,tag)
        self.slowema_window = slowema_window
        self.fastema_window = fastema_window
        self.signal_window = signal_window
        self.set_column_names()


    def __str__(self):
        return f'MACD {(self.fastema_window, self.slowema_window, self.signal_window)}'


    def set_column_names(self):
        self.macd_name = f'MACD{(self.slowema_window, self.fastema_window, self.signal_window)}'
        self.signal_name = f'MACD Signal{(self.slowema_window, self.fastema_window, self.signal_window)}'
        self.histogram_name = f'MACD Hist.{(self.slowema_window, self.fastema_window, self.signal_window)}'
        self.ppo_name = f'MACD%{(self.slowema_window, self.fastema_window, self.signal_window)}'
        

    def build_df(self, base_df):
        slow_ema = base_df[self.price_point].ewm(span=self.slowema_window,
                                    min_periods=self.slowema_window, 
                                    adjust=False).mean()
        
        fast_ema = base_df[self.price_point].ewm(span = self.fastema_window,
                                    min_periods=self.fastema_window, 
                                    adjust=False).mean()

        macd_line = fast_ema.subtract(slow_ema)

        ppo_value = (fast_ema.subtract(slow_ema)).div(slow_ema).multiply(100)

        signal_line = macd_line.ewm(span=self.signal_window,
                                    min_periods=self.signal_window, 
                                    adjust=False).mean()

        df = pd.DataFrame({self.macd_name: macd_line,
                           self.ppo_name : ppo_value,
                           self.signal_name: signal_line, 
                           self.histogram_name: macd_line-signal_line})
        return df

        