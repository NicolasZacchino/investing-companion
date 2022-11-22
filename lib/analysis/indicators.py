import pandas as pd
import yfinance as yf

def exponential_moving_average(prices, window_size = 20):
    """
    Calculates the exponential moving average of a given pandas series

    :param prices: the series to be used
    :param window_size: the range used in the calculation of the moving average (default = 20)

    :returns: a Pandas dataframe with the same index as the series and a column with the moving averages

    """
    ema_df = pd.DataFrame({f'EMA({window_size})': prices.ewm(span = window_size, 
    min_periods=window_size, adjust=False).mean()})
    return ema_df


def simple_moving_average(prices, window_size = 50):
    """
    Calculates the simple moving average of a given series
    :param prices: the series to be used
    :param window_size: the range used in the calculations of the moving average (default=50)

    :returns: a Pandas dataframe with the same index as the series and a column with the moving averages
    """
    sma_df = pd.DataFrame({f'SMA({window_size})' : prices.rolling(window_size, min_periods=window_size).mean()})
    return sma_df


def bollinger_bands(prices, sma_window = 20, stdev_window = 2):
    """
    Calculates the upper and the lower bollinger bands of a price series given the 
    moving average range and the amount of standard deviations 
    :param prices: the series to be used
    :param sma_window: the range used in the calculations of the moving average (default=20)
    :param stdev_window: How many standard deviations should be used in the calculation of the bands

    :returns: a Pandas dataframe with the same index as the series and columns for the lower and upper bollinger bands
    """
    sma = prices.rolling(sma_window).mean()
    stdev = prices.rolling(sma_window).std(ddof=0)
    upper_band = sma + stdev*stdev_window
    lower_band = sma - stdev*stdev_window

    bol_bands_df = pd.DataFrame({f'BB_upper{sma_window,stdev_window}': upper_band, 
    f'BB_lower{sma_window,stdev_window}': lower_band})
    
    return bol_bands_df

def relative_strength_index(prices_list, window_size=14):
    """
    Calculates de RSI (relative strength index) of a given series of prices with a given window size
    :param prices_hist: the series to be used
    :param window_size: the range used in the calculations of the moving average (default=14)

    :returns: a Pandas dataframe with the same index as the series and a column with the RSI value
    """
    prices= pd.DataFrame(prices_list)
    prices['diff'] = prices.diff(1)
    prices['upward'] = prices['diff'].clip(lower=0).round(2)
    prices['downward'] = prices['diff'].clip(upper=0).abs().round(2)
    
   

    prices['average_upward'] = prices['upward'].rolling(window_size,
    min_periods=window_size).mean()[:window_size+1]

    prices['average_downward'] = prices['downward'].rolling(window_size,
    min_periods=window_size).mean()[:window_size+1]

    #Calculating Wilder's Smoothing Mean (WSM)
    #Average gains
    for i, row in enumerate(prices['average_upward'].iloc[window_size+1:]):
        prices['average_upward'].iloc[i+window_size+1] =\
            (prices['average_upward'].iloc[i+window_size]*
            (window_size-1) +
            prices['upward'].iloc[i+window_size+1])\
                /window_size
    #Average Losses
    for i, row in enumerate(prices['average_downward'].iloc[window_size+1:]):
        prices['average_downward'].iloc[i+window_size+1] =\
            (prices['average_downward'].iloc[i+window_size]*
            (window_size-1) +
            prices['downward'].iloc[i+window_size+1])\
                /window_size

    prices['rs'] = prices['average_upward']/prices['average_downward']
    prices[f'RSI({window_size})'] = 100 - (100/(1.0+prices['rs'])) 

    rsi_df = pd.DataFrame(prices[f'RSI({window_size})'])
    return rsi_df

def macd(prices, macd_slowema_window = 26, macd_fastema_window = 12, signal_line_window = 9):
    """
    Calculates the Moving Average Convergence/Divergence (MACD) given a price series, 
    a window size for the slow EMA, a window size for the fast EMA, and a window size for the EMA used
    in the calculation of the signal line

    :param prices: the series to be used
    :param macd_slowema_window: the range used in the calculations of the moving average for the slow EMA (default=26)
    :param macd_fastema_window: the range used in the calculation of the fast EMA (default=12)
    :param signal_line_window: the range used in the calculation of the EMA for the signal line (default = 9)

    :returns: a Pandas dataframe with the same index as the series and columns for the MACD value and the signal line value
    """
    slow_ema = exponential_moving_average(prices, macd_slowema_window)
    fast_ema = exponential_moving_average(prices, macd_fastema_window)

    macd_line_df_column_name = f'MACD_line{macd_slowema_window, macd_fastema_window, signal_line_window}'
    
    macd_line_df = pd.DataFrame(fast_ema.values - slow_ema.values, 
    columns=[macd_line_df_column_name]).set_index(prices.index)
    
    signal_line_df = exponential_moving_average(macd_line_df[macd_line_df_column_name], signal_line_window)
    signal_line_df.rename(columns={signal_line_df.columns[0]: f'macd_sig{macd_slowema_window, macd_fastema_window, signal_line_window}'},
    inplace=True)
    
    macd_df = pd.concat([macd_line_df,signal_line_df], ignore_index=False, axis=1)
    
    return macd_df
    
 

