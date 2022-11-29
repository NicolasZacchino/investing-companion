from investing_companion import indicators
import pandas as pd

class MACD(indicators.IndicatorBase):
    def __init__(self, base_df, slowema_window=26, fastema_window=12, signal_window=9, tag='MACD'):
        super().__init__(base_df, tag)
        self.slowema_window = slowema_window
        self.fastema_window = fastema_window
        self.signal_window = signal_window
        self.macd()

    def get_latest_value(self, key='All'):
        valid_keys = {'MACD','Signal','Histogram','All'}
        if key not in valid_keys:
            raise ValueError("Invalid key, must be one of %r (Case sensitive)" %valid_keys)
        if key == 'All':
            return self.df.iloc[-1].to_dict()
        return self.df[key].iat[-1]

    def macd(self):
        slow_ema = self.base_df.ewm(span = self.slowema_window, \
            min_periods=self.slowema_window, adjust=False).mean()
        
        fast_ema = self.base_df.ewm(span = self.fastema_window, \
            min_periods=self.fastema_window, adjust=False).mean()

        macd_line = fast_ema.subtract(slow_ema)

        signal_line = macd_line.ewm(span=self.signal_window, \
            min_periods=self.signal_window, adjust=False).mean()

        self.df = pd.DataFrame({'MACD': macd_line, 'Signal': signal_line, 'Histogram': macd_line-signal_line})

        