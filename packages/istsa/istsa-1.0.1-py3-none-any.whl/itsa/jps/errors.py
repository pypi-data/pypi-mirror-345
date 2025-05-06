"""
    Exception class for Geodetic time series (Gts)

    ----
    Developed at: ISTerre
    By: Lou MARILL
"""

##########################
class JpsError(Exception):
    def __init__(self, message=''):
        self.message = message
        super().__init__(self.message)


#############################
class JpsTypeError(JpsError):
    pass

##################################


class JpsDimensionError(JpsError):
    pass

##############################


class JpsValueError(JpsError):
    pass