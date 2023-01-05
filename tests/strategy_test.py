from investing_companion.strategy import macd_strategy
from investing_companion.indicators import macd, rsi, bollinger, moving_averages
from investing_companion.tickers import ticker
import numpy as np
import pandas as pd

symbol = 'TSLA'
method = macd_strategy.Macd_Strategy.Method.PPO_ONLY
interval = [1,6]
max_iter = 20
n = 20