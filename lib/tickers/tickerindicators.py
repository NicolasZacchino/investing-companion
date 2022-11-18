import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots
from ..analysis import indicators

class TickerWithIndicators(yf.Ticker):
    def __init__(self, ticker, session=None, period='max', indicators_params = None):
        super().__init__(ticker, session)
        self.period = period
        self.df = self.history(self.period)
        pass
    