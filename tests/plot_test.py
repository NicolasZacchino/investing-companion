from investing_companion.tickers import ticker
import yfinance as yf
import pandas as pd
import numpy as np
from investing_companion import indicators
from investing_companion.indicators import moving_averages, macd, bollinger, rsi

# tsla = ticker.TickerAdditionalPricepoints('TSLA')
# history = tsla.history('max')
# print(history['Close'])

class Parent():
    def __init__(self):
        pass

    def broadcast(self):
        print(self.to_print)

    def change_to_print(self,new_string):
        self.to_print = new_string

class Child(Parent):
    def __init__(self, to_print='Hello world'):
        super().__init__()
        self.to_print = to_print


a = Parent()
a.broadcast()
a.change_to_print('a')
a.broadcast()
        