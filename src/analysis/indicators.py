import pandas as pd
import yfinance as yf

def simple_moving_average(prices, window_size=20):
    sma = prices.rolling(window_size).mean()
    return sma

def exponential_moving_average(prices, window_size=20):
    ema = prices.ewm(span=window_size, min_periods=1, adjust=False).mean()
    return ema

def bollinger_bands(sma, window_size=20):
    std = sma.rolling(window_size).std()
    upper_band = sma + 2*std
    lower_band = sma - 2*std
    return upper_band, lower_band

def relative_strength(prices, window_size=14):
    difference = prices.diff()
    increases = []
    decreases = []
    for i in range (len(difference)):
        if difference[i] < 0:
            increases.append(i)
            decreases.append(0)
        else:
            increases.append(0)
            decreases.append(i)

    increases_series = pd.Series(increases)
    decreases_series = pd.Series(decreases).abs()

    increases_ema = exponential_moving_average(increases_series, window_size)
    decreases_ema = exponential_moving_average(decreases_series, window_size)

    rs = increases_ema/decreases_ema
    rsi = 100 - (100/(1+rs))
    rsi_df = pd.DataFrame(rsi).rename(columns=
    {0:rsi}).set_index(prices.index)
    rsi_df.dropna()
    
    return rsi_df[3:]

def macd(prices, macd_slowema_window = 26, macd_fastema_window = 12, signal_line_window = 9):
    slow_ema = exponential_moving_average(prices,macd_slowema_window)
    fast_ema = exponential_moving_average(prices,macd_fastema_window)
    
    macd_line = fast_ema.substract(slow_ema)
    signal_line = exponential_moving_average(macd_line, signal_line_window)

    return macd_line, signal_line
    
 

