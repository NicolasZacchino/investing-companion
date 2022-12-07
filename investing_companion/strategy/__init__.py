import pandas as pd
import numpy as np
from enum import Enum

class Signal(Enum):
    BUY = 1
    SELL = -1
    NONE = 0

def prepare_data(ticker_df, indicator_list):
    df_list = [ind.build_df(ticker_df) for ind in indicator_list]
    df_list.insert(0,ticker_df)
    data = pd.concat(df_list, axis=1)
    data = pd.concat(df_list,axis=1)
    data['daily_returns'] = np.log(data['Close']/data['Close'].shift(1))
    data['bnh_returns'] = data['daily_returns'].cumsum()
    data.dropna()

    return data


def backtest_strategy(data, buy_conds, sell_conds):   
    #Set Buy and sell signals
    data['signal'] =np.select([buy_conds, sell_conds], 
                                   [Signal.BUY.value, Signal.SELL.value],
                                    Signal.NONE.value)

    data['position'] = data['signal'].replace(to_replace=Signal.NONE.value, method='ffill')
    data['position'] = data['position'].shift()
    data['strat_returns'] = data['position'] * data['daily_returns']

    performance = data[['daily_returns','strat_returns']]\
                            .iloc[:].sum()
    
    data['strat_returns'] = data['strat_returns'].cumsum()
    return performance


def optimize_indic_parameters(window, *args, **kwargs):
    pass


