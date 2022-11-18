import pandas as pd
import yfinance as yf

def exponential_moving_average(prices, window_size = 20):
    ema_df = pd.DataFrame({f'EMA({window_size})': prices.ewm(span = window_size, 
    min_periods=1, adjust=False).mean()})
    return ema_df


def simple_moving_average(prices, window_size = 50):
    sma_df = pd.DataFrame({f'SMA({window_size}' : prices.rolling(window_size).mean()})
    return sma_df


def bollinger_bands(prices, sma_window = 20, stdev_window = 2):
    sma = prices.rolling(sma_window).mean()
    stdev = sma.std()
    upper_band = sma + stdev*stdev_window
    lower_band = sma - stdev*stdev_window

    bol_bands_df = pd.DataFrame({f'BB_upper{sma_window,stdev_window}': upper_band, 
    f'BB_lower{sma_window,stdev_window}': lower_band})
    
    return bol_bands_df

def relative_strength_index(prices, window_size=14):
    
    up_moves = []
    down_moves = []
    difference = prices.diff()

    for i in range(len(difference)):
        if difference[i] < 0:
            up_moves.append(i)
            down_moves.append(0)
        else:
            up_moves.append(0)
            down_moves.append(i)
    
    up_moves_series = pd.Series(up_moves)
    down_moves_series = pd.Series(down_moves).abs()

    up_moves_ema = exponential_moving_average(up_moves_series, window_size)
    down_moves_ema = exponential_moving_average(down_moves_series, window_size)
    rs = up_moves_ema/down_moves_ema
    rsi = 100 - (100/(1+rs))
    rsi_df = pd.DataFrame(rsi).rename(columns={rsi.columns[0]: f'RSI({window_size})'}, 
    inplace=False).set_index(prices.index) 

    return rsi_df

def macd(prices, macd_slowema_window = 26, macd_fastema_window = 12, signal_line_window = 9):
    slow_ema = exponential_moving_average(prices, macd_slowema_window)
    fast_ema = exponential_moving_average(prices, macd_fastema_window)

    macd_line_df_column_name = f'MACD_line{macd_slowema_window, macd_fastema_window, signal_line_window}'
    
    macd_line_df = pd.DataFrame(slow_ema.values - fast_ema.values, 
    columns=[macd_line_df_column_name]).set_index(prices.index)
    
    signal_line_df = exponential_moving_average(macd_line_df[macd_line_df_column_name], signal_line_window)
    signal_line_df.rename(columns={signal_line_df.columns[0]: f'macd_sig{macd_slowema_window, macd_fastema_window, signal_line_window}'},
    inplace=True)
    
    macd_df = pd.concat([macd_line_df,signal_line_df], ignore_index=False, axis=1)
    
    return macd_df
    
 

