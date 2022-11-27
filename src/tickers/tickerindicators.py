import yfinance as yf
import pandas as pd
from ..analysis import indicators

class TickerWithIndicators(yf.Ticker):
    """
    Child class of the yf.Ticker class. Intended to add additional functionality
    over its parent class (mainly indicators)

    Methods:
    indicators_history()
    additional_pricepoints()
    """
    def __init__(self, ticker, session=None):
        super().__init__(ticker, session)

    def indicators_history(self, price_point='Close', sma_params=[50], ema_params=[20],bollinger_params=[20,2],
    rsi_params=[14],macd_params=[26,12,9], period='max'):
        """
        Creates a Pandas Dataframe with the most commonly used indicators
        (SMA, EMa, Bollinger bands, RSI, MACD)

        :param price_point: Which price point should be used. Valid inputs = 'Close', 'Open',
        'High', 'Low', 'HL2', 'HLC3', 'HLCC4', 'OHLC4'. (Default = 'Close)
        :param sma_params: list with the numeric parameters for the SMA. (Default = [50])
        :param ema_params: list with the numeric parameters for the EMA. (Default = [20])
        :param bollinger_params: list with the numeric parameters for the bollinger bands
        (Default = [20,2])
        :param rsi_params: list with the numeric parameters for the RSI (Default = [14])
        :params macd_params: list with the numeric parameters for the MACD (Default = [26,12,9])
        :params period: how far back in time the dataframe should go. same valid
        values as yf.Ticker.history() method (default 'max')

        :returns: a Pandas Dataframe with columns containing the indicator values and the corresponding
        date in the index
        """
        valid_fields = {'standard': ['Open','High','Low','Close'],
        'calculated': ['HL2','HLC3','HLCC4','OHLC4']}

        #Checking if the user introduced a valid price point
        if price_point not in valid_fields['calculated'] and price_point not in valid_fields['standard']:
            raise ValueError("Invalid price action field. Must be one of %r" %valid_fields)
        
        #If the user intoduced a pricepoint not available in history, it has to be calculated
        #with the corresponding additional_pricepoints() method
        if price_point in valid_fields['standard']:
            base_prices=self.history(period)[price_point]
        if price_point in valid_fields['calculated']:
            base_prices= self.additional_pricepoints(period)[price_point]

        sma_df = indicators.simple_moving_average(base_prices,*sma_params)
        ema_df = indicators.exponential_moving_average(base_prices, *ema_params)
        boll_df = indicators.bollinger_bands(base_prices, *bollinger_params)
        rsi_df = indicators.relative_strength_index(base_prices, *rsi_params)
        macd_df = indicators.macd(base_prices, *macd_params)
        
        df = pd.concat([sma_df,ema_df,boll_df,rsi_df,macd_df], axis=1)
        return df

    def additional_pricepoints(self, period):
        """
        Returns a Pandas dataframe with additional pricepoints, calculated from the 
        more commonly used Open, High, Low, and Close

        :param period: a string that states how far back in time the dataframe should go.
        Same valid values as the yf.Ticker.history() method

        returns: a Pandas dataframe with the HL2, HLC3, HLCC4 and OHLC4 price points
        """
        history = self.history(period)
        
        price_open = history['Open']
        price_close = history['Close']
        price_high = history['High']
        price_low = history['Low']

        HL2 = (price_high+price_low)/2
        HLC3 = (price_high+price_low+price_close)/3
        HLCC4 = (price_high+price_low+price_close*2)/4
        OHLC4 = (price_high+price_low+price_close+price_open)/4

        df = pd.concat([HL2.rename('HL2'),
        HLC3.rename('HLC3'),
        HLCC4.rename('HLCC4'),
        OHLC4.rename('OHLC4')],
        axis=1)

        return df
