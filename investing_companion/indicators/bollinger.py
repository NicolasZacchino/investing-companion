from investing_companion import indicators

class BollingerBands(indicators.IndicatorBase):
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

    def get_latest_value(self, key='All'):
        valid_keys = {'Upper','Lower','All'}
        if key not in valid_keys:
            raise ValueError("Invalid key, must be one of %r (Case sensitive)" %valid_keys)
        if key == 'All':
            return self.df.iloc[-1].to_dict()
        return self.df[key].iat[-1]