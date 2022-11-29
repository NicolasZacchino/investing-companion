import pandas as pd
from abc import ABC, abstractmethod

class IndicatorBase(ABC):
    '''
    Base class for the indicators. Shouldn't be used directly.
    
    :param base_df: the pandas dataframe that contains the data to be used in the calculation of 
    the indicator
    :param tag: string meant to identify the indicator. not to be confused with the column names
    '''
    def __init__(self, base_df, tag=str()):
        self.base_df = base_df
        self.df = pd.DataFrame(index=base_df.index)
        self.tag = tag
   
    @abstractmethod
    def get_latest_value(self):
        #Since indicators might have more than 1 relevant number (ie: Bollinger's bands)
        #Child classes must implement this method themselves
        pass
    
    def get_dataframe(self):
        return self.df

    def get_tag(self):
        return self.tag
    
    def get_column_names(self):
        return self.df.columns
    
    def set_tag(self, new_tag):
        self.tag = new_tag

    def set_column_names(self, new_names):
        self.df.columns = new_names
