import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class TickerPlot(yf.Ticker):
    def __init__(self, ticker, session=None, period='max'):
        super().__init__(ticker, session)
        self.period = period
        self.plot = make_subplots(specs=[[{"secondary_y": True}]])

    def show_plot(self):
        self.plot.show()

    def add_volume_plot(self):
        history = self.history(self.period)

        self.plot.add_trace(go.Scatter(x=history.index, y=history['Volume'],
        name='Volume'), secondary_y=True)
        self.plot.update_yaxes(range=[0,7000000000], secondary_y=True)
        self.plot.update_yaxes(visible=False, secondary_y=True)

    def add_candlestick_plot(self):
        pass