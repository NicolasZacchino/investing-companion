import yfinance as yf
import pandas as pd

class TickerAdditionalPricepoints(yf.Ticker):
    """
    Child class of the yf.Ticker class. Extends its history() method to include
    additional pricepoints that are commonly used (HL2, HLC3, HLCC4, OHLC 4)

    Methods:
    history()
    """
    def __init__(self, ticker, session=None):
        super().__init__(ticker, session)

    
    def history(self, *args, **kwargs):
        """
        Returns a Pandas dataframe with additional pricepoints, calculated from the 
        more commonly used Open, High, Low, and Close. Extends yf.Ticker.history()
        """
        df = super().history(*args, **kwargs)
        
        price_open = df['Open']
        price_close = df['Close']
        price_high = df['High']
        price_low = df['Low']

        HL2 = (price_high+price_low)/2
        HLC3 = (price_high+price_low+price_close)/3
        HLCC4 = (price_high+price_low+price_close*2)/4
        OHLC4 = (price_high+price_low+price_close+price_open)/4

        df = pd.concat([df,
                        HL2.rename('HL2'),
                        HLC3.rename('HLC3'),
                        HLCC4.rename('HLCC4'),
                        OHLC4.rename('OHLC4')],
        axis=1)

        return df
