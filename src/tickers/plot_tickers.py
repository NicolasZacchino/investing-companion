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
    
    def reset_plot(self):
        self.plot = make_subplots(specs=[[{"secondary_y": True}]])

    def add_volume_plot(self):
        history = self.history(self.period)

        self.plot.add_trace(go.Scatter(x=history.index, y=history['Volume'],
        name='Volume'), secondary_y=True)
        self.plot.update_yaxes(range=[0,7000000000], secondary_y=True)
        self.plot.update_yaxes(visible=False, secondary_y=True)

    def add_candlestick_plot(self):
        history = self.history(self.period)

        self.plot.add_trace(go.Candlestick(x=history.index,
        open=history['Open'],
        high=history['High'],
        low=history['Low'],
        close=history['Close'],
        ))

    # def add_ema(self,window_size):
    #     history = self.history(self.period)
    #     ema_plot = indicators.exponential_moving_average(history['Close'], window_size)
    #     ema_name = str(window_size) + " day EMA"
    #     self.plot.add_trace(go.Scatter(x=history.index,
    #     y = ema_plot, marker_color='blue', name = ema_name))