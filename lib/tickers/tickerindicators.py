import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots
from ..analysis import indicators

class TickerWithIndicators(yf.Ticker):

    def __init__(self, ticker, session=None):
        super().__init__(ticker, session)

    def indicators_history(self, field='Close', sma_params=[50], ema_params=[20],bollinger_params=[20,2],
    rsi_params=[14],macd_params=[26,12,9]):
        """
        Creates a Pandas Dataframe with the most commonly used indicators
        (SMA, EMa, Bollinger bands, RSI, MACD)

        :param field: Which price point should be used. Valid inputs = 'Close', 'Open',
        'High', 'Low'. (Default = 'Close)
        :param sma_params: list with the numeric parameters for the SMA. (Default = [50])
        :param ema_params: list with the numeric parameters for the EMA. (Default = [20])
        :param bollinger_params: list with the numeric parameters for the bollinger bands
        (Default = [20,2])
        :param rsi_params: list with the numeric parameters for the RSI (Default = [14])
        :params macd_params: list with the numeric parameters for the MACD (Default = [26,12,9])

        :returns: a Pandas Dataframe with columns containing the indicator values and the corresponding
        date in the index
        """
        valid_fields = {'Open', 'Close', 'High', 'Low'}
        #TODO: Implement HL2, HLC3, HLCC4, OHLC4
        if field not in valid_fields:
            raise ValueError("Invalid price action field. Must be one of %r" %valid_fields)

        base_prices=self.history('max')[field]
        sma_df = indicators.simple_moving_average(base_prices,*sma_params)
        ema_df = indicators.exponential_moving_average(base_prices, *ema_params)
        boll_df = indicators.bollinger_bands(base_prices, *bollinger_params)
        rsi_df = indicators.relative_strength_index(base_prices, *rsi_params)
        macd_df = indicators.macd(base_prices, *macd_params)
        
        df = pd.concat([sma_df,ema_df,boll_df,rsi_df,macd_df], axis=1)
        return df
