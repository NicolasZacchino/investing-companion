import pandas as pd

class IndicatorBase():
    '''
    Base class for the indicators. Shouldn't be used directly.
    
    :param base_df: the pandas dataframe that contains the data to be used in the calculation of 
    the indicator
    :param tag: string meant to identify the indicator. not to be confused with the column names

    Methods:
    set_parameters()
    '''
    def __init__(self,tag=str()):
        self.tag = tag

    def set_column_names(self):
        pass

    def set_parameters(self, *args, **kwargs):
        for key, val in kwargs.items():
            if key in self.__dict__:
                self.__setattr__(key, val)
        self.set_column_names()
