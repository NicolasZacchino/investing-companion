import pandas as pd

class IndicatorBase():
    '''
    Base class for the indicators. Shouldn't be used directly.
    
    :param base_df: the pandas dataframe that contains the data to be used in the calculation of 
    the indicator
    :param tag: string meant to identify the indicator. not to be confused with the column names

    Methods:
    get_dataframe()
    get_tag()
    get_column_names()
    get_column_last_value()
    set_tag()
    set_column_name()
    '''
    def __init__(self, base_df, tag=str()):
        self.base_df = base_df
        self.df = pd.DataFrame(index=base_df.index)
        self.tag = tag
    
    def get_dataframe(self):
        return self.df

    def get_tag(self):
        return self.tag
    
    def get_column_names(self):
        return self.df.columns
    
    def get_column_last_value(self,which_column):
        return self.df[which_column].iat[-1]
    
    def set_tag(self, new_tag):
        self.tag = new_tag

    def set_column_name(self,which_column,new_name):
        self.df.rename({which_column: new_name},axis='columns',inplace=True)