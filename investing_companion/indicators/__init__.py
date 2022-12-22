
class IndicatorBase():
    '''
    Base class for the indicators. Shouldn't be used directly.

    :param price_point(str): The price point (Open, Close, High, etc) from which to calculate the indicator
    :param tag(str): string meant to identify the indicator. not to be confused with the column names

    Methods:
    :set_parameters(): When seeking to change the column names, call this one instead of modifying
    the instance variable directly as it also calls set_column_names()
    :set_column_names(): To be implemented by the child classes
    '''
    def __init__(self,price_point='Close',tag=str()):
        self.tag = tag
        self.price_point = price_point

    def set_column_names(self):
        pass

    def set_parameters(self, *args, **kwargs):
        for key, val in kwargs.items():
            if key in self.__dict__:
                self.__setattr__(key, val)
        self.set_column_names()
