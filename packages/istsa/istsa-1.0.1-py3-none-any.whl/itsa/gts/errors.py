"""
    Exception class for Geodetic time series (Gts)

    ----
    Developed at: ISTerre
    By: Lou MARILL
    Based on: PYACS module
"""

##########################
class GtsError(Exception):
    def __init__(self, message=''):
        self.message = message
        super().__init__(self.message)


#############################
class GtsTypeError(GtsError):
    pass


##################################
class GtsDimensionError(GtsError):
    pass


##############################
class GtsValueError(GtsError):
    pass