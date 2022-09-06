import pandas as pd

def simple_moving_average(set, window_size=20):
    series = pd.Series(set)
    rolling_window = series.rolling(window_size)

    moving_average = rolling_window.mean()
    moving_average_list = moving_average.tolist()
    moving_average_list_final = moving_average_list[window_size-1:]

    return moving_average_list_final

def exponential_moving_average(set, window_size=20):
    series = pd.Series(set)
    ema = series.ewm(span=window_size, min_periods=1, adjust=False).mean()
    return ema