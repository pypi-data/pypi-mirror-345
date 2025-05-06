"""
    Functions for time based converstions

    Note: Leap seconds are not handled

    !!! Warning: All conversions not specifying |ut| or |uts| use 12h00mn00s
    as default
        - ut:   decimal fraction of the day
        - uts:  number of second since 00h00mn00s

    Warning2: !!! You need to add the module 'itsa' to your Python path to use
    these functions

    ----
    Developed at: ISTerre
    By: Lou MARILL
    Based on: PYACS module
"""

#%%##################
## GLOBAL VARIABLE ##
#####################

# Number of day by month for non-leap years
_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


#%%#############################
## CALENDAR DATES CONVERSIONS ##
################################

##############################
def cal2doy(day, month, year):
    """
    Convert calendar date to day or year (doy)

    Parameters
    ----------
    day : int, list or np.ndarray
        Day of the calendar date to convert.
    month : int, list or np.ndarray
        Month of the calendar date to convert.
    year : int, list or np.ndarray
        Year of the calendar date to convert.

    Return
    ------
    int or np.ndarray
        Doy of the year (doy) corresponding to the calendar date in parameters.

    Note
    ----
    If you use list or np.ndarray parameters, all the size need to be the same

    Examples
    --------
    In [1]: from itsa.lib.astrotime import cal2doy

    In [2]: cal2doy(3,3,1999)
    Out[2]: 62

    In [3]: cal2doy(3,3,[1999,2000])
    Out[3]: array([62, 63])

    In [4]: cal2doy(3,[3,2,1],[1999,2000,2001])
    Out[4]: array([62, 34,  3])

    In [5]: cal2doy([3,4,5],[3,2,1],[1999,2000,2001])
    Out[5]: array([62, 35,  5])

    """

    ###################################
    def _check_param(day, month, year):
        """
        Raise error is one parameter is invalid and adapt some parameter values
        """
        # Import
        from itsa.lib.modif_vartype import adapt_shape
        # Check
        _caltypeOK(day, month, year)
        # Adapt
        return adapt_shape([day, month, year])
    ###################################

    # Check parameters
    (day, month, year) = _check_param(day, month, year)

    # Import
    import numpy as np

    # Convert
    if isinstance(day, np.ndarray):
        doy = np.array(list(map(cal2doy, day, month, year)))
    else:
        # Check parameters
        _dayOK(day, month, year)
        # Adapt number of day by month according to leep year
        days = np.copy(_days)
        if leap_year(year):
            days[1] = 29
        # Find doy
        doy = day
        m = 0
        while m < month-1:  # |month-1| is for array indexing
            doy = doy + days[m]
            m += 1

    # Return
    return np.array(doy, dtype=int)+0


#####################################
def cal2mjd(day, month, year, ut=.5):
    """
    Convert calendar date to modified Julian day

    Parameters
    ----------
    day : int, list or np.ndarray
        Day of the calendar date to convert.
    month : int, list or np.ndarray
        Month of the calendar date to convert.
    year : int, list or np.ndarray
        Year of the calendar date to convert.
    ut : float, list or np.ndarray, optional
        Decimal fraction of the day: within [0.;1.[.
        The default is .5.

    Return
    ------
    mjd : int, float or np.ndarray
        Modified Julian day corresponding to the calendar date in parameters.

    Note
    ----
    Modified Julian day = Julian day - 2400000.5.

    Examples
    --------
    In [1]: from itsa.lib.astrotime import cal2mjd

    In [2]: cal2mjd(3,3,1999)
    Out[2]: 51240.5

    In [3]: cal2mjd(3,3,1999,.7)
    Out[3]: 51240.7

    In [4]: cal2mjd(3,3,[1999,2000])
    Out[4]: array([51240.5, 51606.5])

    In [5]: cal2mjd(3,[3,2,1],[1999,2000,2001])
    Out[5]: array([51240.5, 51577.5, 51912.5])

    In [6]: cal2mjd([3,4,5],[3,2,1],[1999,2000,2001],.25)
    Out[6]: array([51240.25, 51578.25, 51914.25])

    In [7]: cal2mjd([3,4,5],[3,2,1],[1999,2000,2001],[.7,.25,.6])
    Out[7]: array([51240.7 , 51578.25, 51914.6 ])

    """

    ######################################
    def _check_param(day, mont, year, ut):
        """
        Raise error if one parameter is invalid and adapt some parameter values
        """
        # Import
        from itsa.lib.modif_vartype import adapt_shape
        # Check
        _caltypeOK(day, month, year, ut)
        # Adapt
        return adapt_shape([day, month, year, ut])
    ######################################

    # Check parameters
    (day, month, year, ut) = _check_param(day, month, year, ut)

    # Import
    import numpy as np

    # Convert
    if isinstance(day, np.ndarray):
        mjd = np.array(list(map(cal2mjd, day, month, year, ut)))
    else:
        # Check parameters
        _dayOK(day, month, year)
        _utOK(ut)
        # Find mjd
        if month <= 2:
            m = month+9
            y = year-1
        else:
            m = month-3
            y = year

        c = y//100
        y = y-c*100
        x1 = 146097*c//4
        x2 = 1461*y//4
        x3 = (153*m+2)//5

        mjd = x1+x2+x3+day-678882+ut

    # Return
    return mjd


#########################################
def cal2decyear(day, month, year, ut=.5):
    """
    Convert calendar date to decimal year

    Parameters
    ----------
    day : int, list or np.ndarray
        Day of the calendar date to convert.
    month : int, list or np.ndarray
        Month of the calendar date to convert.
    year : int, list or np.ndarray
        Year of the calendar date to convert.
    ut : float, list or np.ndarray, optional
        Decimal fraction of the day: within [0.;1.[.
        The default is .5.

    Returns
    -------
    decyear : int, float or np.ndarray
        Decimal year corresponding to the calendar date in parameters.
        
    Notes
    -----
    - If you use list or np.ndarray parameters, all the size need to be the
    same.
    - Be aware that when ut is not provided, then the middle of the day is
    used.

    Examples
    --------
    In [1]: from itsa.lib.astrotime import cal2decyear

    In [2]: cal2decyear(3,6,2000)
    Out[2]: 2000.422131147541

    In [3]: cal2decyear(3,6,2000,.75)
    Out[3]: 2000.4228142076502

    In [4]: cal2decyear(3,6,[2000,1997])
    Out[4]: array([2000.42213115, 1997.42054795])

    In [5]: cal2decyear(3,[6,11],[2000,1997],.8)
    Out[5]: array([2000.42295082, 1997.84054795])

    In [6]: cal2decyear([3,20],[6,11],[2000,1997])
    Out[6]: array([2000.42213115, 1997.88630137])

    In [7]: cal2decyear([3,20],[6,11],[2000,1997],[.75,.8])
    Out[7]: array([2000.42281421, 1997.88712329])

    """

    # Check parameters
    _caltypeOK(day, month, year, ut)

    # Convert
    doy = cal2doy(day, month, year)
    decyear = doy2decyear(doy, year, ut=ut)

    # Return
    return decyear


#%%#########################
## DAY OF YEAR CONVERSION ##
############################

#######################
def doy2cal(doy, year):
    """
    Convert day of year (doy) to calendar date

    Parameters
    ----------
    doy : int, list or np.ndarray
        Day of year of the date to convert.
    year : int, list or np.ndarray
        Year of the date to convert.

    Returns
    -------
    day : int or np.ndarray
        Day corresponding to the day of year in parameter.
    month : int or np.ndarray
        Month corresponding to the day of year in parameter.
        
    Examples
    --------
    In [1]: from itsa.lib.astrotime import doy2cal

    In [2]: doy2cal(256,2000)
    Out[2]: (12, 9)

    In [3]: doy2cal(256,[2000,1999])
    Out[3]: (array([12, 13]),
             array([9, 9]))

    In [4]: doy2cal([256,106],[2000,1999])
    Out[4]: (array([12, 16]),
             array([9, 4]))

    """

    ############################
    def _check_param(doy, year):
        """
        Raise error if one parameter is invalid and adapt some parameter values
        """
        # Import
        from itsa.lib.modif_vartype import adapt_shape
        # Check
        _doytypeOK(doy, year)
        # Adapt
        return adapt_shape([doy, year])
    ############################

    # Check parameters
    (doy, year) = _check_param(doy, year)

    # Import
    import numpy as np

    # Convert
    if isinstance(doy, np.ndarray):
        (day, month) = np.array(list(map(doy2cal, doy, year))).T
    else:
        # Check parameters
        _doyOK(doy, year)  # Raise error if |doy| do not exist
        # Look number of days by month during |year|
        days = np.copy(_days)
        if leap_year(year):
            days[1] = 29
        # Find month
        month = 0
        end = days[month]
        while doy > end:
            month += 1
            end += days[month]
        # Find day
        end -= days[month]
        day = doy-end
        month += 1

    # Return
    return day, month


##############################
def doy2mjd(doy, year, ut=.5):
    """
    Convert doy of year (doy) to modified Julian day

    Parameters
    ----------
    doy : int, list or np.ndarray
        Day of year of the date to convert.
    year : int, list or np.ndarray
        Year of the date to convert.
    ut : float, list or np.ndarray, optional
        Decimal fraction of the day: within [0.;1.[.
        The default is .5.

    Return
    ------
    mjd : TYPE
        Modified Julian day corresponding to the date in parameters.

    Notes
    -----
    - Accounts for leap years with 366 days
    - Unless |ut| is specified, the returned decimal year is at 12h00mn00,
    that is |ut=0.5| by default

    Examples
    --------
    In [1]: from itsa.lib.astrotime import doy2mjd
    
    In [2]: doy2mjd(256,2000)
    Out[2]: 51799.5
    
    In [3]: doy2mjd(256,2000,0)
    Out[3]: 51799
    
    In [4]: doy2mjd(256,[2000,2019])
    Out[4]: array([51799.5, 58739.5])
    
    In [5]: doy2mjd([256,16],[2000,2019],.7)
    Out[5]: array([51799.7, 58499.7])
    
    In [6]: doy2mjd([256,16],[2000,1999],[0,.7])
    Out[6]: array([51799. , 58499.7])

    """

    # Check parameters
    _doytypeOK(doy, year, ut)

    # Convert
    (day, month) = doy2cal(doy, year)
    mjd = cal2mjd(day, month, year, ut)

    # Return
    return mjd


##################################
def doy2decyear(doy, year, ut=.5):
    """
    Convert day of year (doy) to decimal year

    Parameters
    ----------
    doy : int, list or np.ndarray
        Day of year of the date to convert.
    year : int, list or np.ndarray
        Year of the date to convert.
    ut : float, list or np.ndarray, optional
        Decimal fraction of the day: within [0.;1.[.
        The default is .5.

    Returns
    -------
    decyear: int, float or np.ndarray
        Decimal year corresponding to the date in parameters.
        
    Notes
    -----
    - Accounts for leap years with 366 days
    - Unless |ut| is specified, the returned decimal year is at 12h00mn00,
    that is |ut=0.5| by default

    Examples
    --------
    In [1]: from itsa.lib.astrotime import doy2decyear
    
    In [2]: doy2decyear(4,1999)
    Out[2]: 1999.009589041096
    
    In [3]: doy2decyear(4,1999,.25)
    Out[3]: 1999.0089041095891
    
    In [4]: doy2decyear(4,[1999,2000])
    Out[4]: array([1999.00958904, 2000.00956284])
    
    In [5]: doy2decyear([4,300],[1999,2000],.75)
    Out[5]: array([1999.01027397, 2000.81898907])
    
    In [6]: doy2decyear([4,300],[1999,2000],[.25,.25])
    Out[6]: array([1999.00890411, 2000.81898907])

    """

    ################################
    def _check_param(doy, year, ut):
        """
        Raise error if one parameter is invalid and adapt some parameter values
        """
        # Import
        from itsa.lib.modif_vartype import adapt_shape
        # Check
        _doytypeOK(doy, year, ut)
        # Adapt
        return adapt_shape([doy, year, ut])
    ################################

    # Check parameters
    (doy, year, ut) = _check_param(doy, year, ut)

    # Import
    import numpy as np

    # Convert
    if isinstance(doy, np.ndarray):
        decyear = np.array(list(map(doy2decyear, doy, year, ut)))

    else:
        # Check parameters
        _doyOK(doy, year)
        _utOK(ut)
        # Find decimal year
        nday = cal2doy(31, 12, year)
        doy += -1+ut
        decyear = year+doy/nday

    # Return
    return decyear


#%%##################################
## MODIFIED JULIAN DAY CONVERSIONS ##
#####################################

#################
def mjd2cal(mjd):
    """
    Convert mopdified julian day to calendar date

    Parameter
    ---------
    mjd : int, float, list or np.ndarray
        Modified julian day to convert.

    Returns
    -------
    day : int or np.ndarray
        Day corresponding to the modified julian day in parameter.
    month : int or np.ndarray
        Month corresponding to the modified julian day in parameter.
    year : int or np.ndarray
        Year corresponding to the modified julian day in parameter.
    ut : float or np.ndarray
        Decimal fraction of the day corresponding to the modified julian
        day in parameter.

    Examples
    --------
    In [1]: from itsa.lib.astrotime import mjd2cal
    
    In [2]: mjd2cal(49718.5)
    Out[2]: (1, 1, 1995, 0.5)
    
    In [3]: mjd2cal([49718.5,49818])
    Out[3]: (array([ 1, 11]),
             array([1, 4]),
             array([1995, 1995]),
             array([0.5, 0. ]))

    """

    ######################
    def _check_param(mjd):
        """
        Raise error is one parameter is invalid and adapt some parameter values
        """
        # Import
        import numpy as np
        # Check
        _mjdtypeOK(mjd)
        # Adapt
        if isinstance(mjd, list):
            mjd = np.array(mjd)
        return mjd
    ######################

    # Check parameters
    mjd = _check_param(mjd)

    # Import
    import numpy as np

    # Convert
    if isinstance(mjd, np.ndarray):
        (day, month, year, ut) = np.array(list(map(mjd2cal, mjd))).T
        day = day.astype(int)
        month = month.astype(int)
        year = year.astype(int)
    else:
        imjd = int(mjd)
        # Find decimal fraction of year
        ut = mjd-imjd
        # Do some rather cryptic calculations to find calendar date
        # |//| mean integer division
        jd = imjd + 2400001
        temp1 = 4*(jd+((6*(((4*jd-17918)//146097)))//4+1)//2-37)
        temp2 = 10*(((temp1-237) % 1461)//4)+5
        year = temp1//1461-4712
        month = ((temp2//306+2) % 12)+1
        day = (temp2 % 306)//10+1
        # Check results
        _dayOK(day, month, year)
        _utOK(ut)

    return day, month, year, ut


#################
def mjd2doy(mjd):
    """
    Convert modified julian day to day of year (doy) with year and decimal
    fraction of the day associated

    Parameter
    ---------
    mjd : int, float, list or np.ndarray
        Modified julian day to convert.

    Returns
    -------
    doy : int or np.ndarray
        Day of year corresponding to the modified julian day in parameter.
    year : int or np.ndarray
        Year of |doy|.
    ut : float or np.ndarray
        Decimal fraction of the day corresponding to the modified julian
        day in parameter.
        
    Examples
    --------
    In [1]: from itsa.lib.astrotime import mjd2doy

    In [2]: mjd2doy(49718.25)
    Out[2]: (1, 1995, 0.25)

    In [3]: mjd2doy([49718.25,49818.75])
    Out[3]: (array([  1, 101]),
             array([1995, 1995]),
             array([0.25, 0.75]))

    """

    # Check parameters
    _mjdtypeOK(mjd)

    # Convert
    (day, month, year, ut) = mjd2cal(mjd)
    doy = cal2doy(day, month, year)

    # Return
    return doy, year, ut


#####################
def mjd2decyear(mjd):
    """
    Convert modified julian day to decimal year

    Parameter
    ---------
    mjd : int, float, list or np.ndarray
        Modified julian day to convert.

    Return
    ------
    decyear : int, float or np.ndarray
        Decimal year corresponding to the modified julian date in parameter.
        
    Examples
    --------
    In [1]: from itsa.lib.astrotime import mjd2decyear

    In [2]: mjd2decyear(49718.5)
    Out[2]: 1995.0013698630137

    In [3]: mjd2decyear([49718.5,49818.75])
    Out[3]: array([1995.00136986, 1995.2760274 ])

    """

    # Check parameters
    _mjdtypeOK(mjd)

    # Convert
    (doy, year, ut) = mjd2doy(mjd)
    decyear = doy2decyear(doy, year, ut=ut)

    # Return
    return decyear


#%%##########################
## DECIMAL YEAR CONVERSION ##
#############################

#########################
def decyear2mjd(decyear):
    """
    Convert decimal year to modified Julian day

    Parameter
    ---------
    decyear : int, float, list or np.ndarray
        Decimal year of the date to convert.

    Return
    ------
    mjd : int, float or np.ndarray
        Modified Julian day corresponding to the date in parameter.
        
    Examples
    --------
    In [1]: from itsa.lib.astrotime import decyear2mjd

    In [2]: decyear2mjd(1999)
    Out[2]: 51179

    In [3]: decyear2mjd([1999,2000.5,2001.5])
    Out[3]: array([51179. , 51727. , 52092.5])

    """

    ##########################
    def _check_param(decyear):
        """
        Raise error is one parameter is invalid and adapt some parameter values
        """
        # Import
        import numpy as np
        # Check
        _decyeartypeOK(decyear)
        # Adapt
        if isinstance(decyear, list):
            decyear = np.array(decyear)
        return decyear
    ##########################

    # Check parameters
    decyear = _check_param(decyear)

    # Import
    import numpy as np

    # Convert
    year = np.array(decyear, dtype=int)+0
    frac_year = decyear-year

    if isinstance(year, np.ndarray):
        nday = leap_year(year)*366
        nday[nday == 0] = 365
    else:
        if leap_year(year):
            nday = 366
        else:
            nday = 365

    frac_doy = frac_year*nday
    doy = np.array(frac_doy, dtype=int)+1
    ut = frac_doy-(doy-1)
    mjd = doy2mjd(doy, year, ut)

    # Return
    return mjd


#########################
def decyear2cal(decyear):
    """
    Convert decimal year to calendar date

    Parameter
    ---------
    decyear : int, float, list or np.ndarray
        Decimal year of the date to convert.

    Returns
    -------
    day : int or np.ndarray
        Day corresponding to the day of year in parameter.
    month : int or np.ndarray
        Month corresponding to the day of year in parameter.
        
    Examples
    --------
    In [1]: from itsa.lib.astrotime import decyear2cal

    In [2]:decyear2cal(1999.5)
    Out[2]: (2, 7, 1999, 0.5)

    In [3]: decyear2cal([1999.25,2000.5,2001.5])
    Out[3]: (array([2, 2, 2]),
             array([4, 7, 7]),
             array([1999, 2000, 2001]),
             array([0.25, 0.  , 0.5 ]))
    
    """

    ##########################
    def _check_param(decyear):
        """
        Raise error is one parameter is invalid and adapt some parameter values
        """
        # Import
        import numpy as np
        # Check
        _decyeartypeOK(decyear)
        # Adapt
        if isinstance(decyear, list):
            decyear = np.array(decyear)
        return decyear
    ##########################

    # Check parameters
    decyear = _check_param(decyear)

    # Convert
    mjd = decyear2mjd(decyear)
    (day, month, year, ut) = mjd2cal(mjd)

    # Return
    return day, month, year, ut


#%%##########################################
## LEAP YEAR, HOUR/MIN/SECONDS CONVERSIONS ##
#############################################

####################
def leap_year(year):
    """
    Return True if |year| is a leap year (False otherwise)

    Parameter
    ---------
    year : int, float, list or np.ndarray
        Year to test.

    Return
    ------
    OK : bool or np.ndarray
        |year| is a leap year if true.
        
    Examples
    --------
    In [1]: from itsa.lib.astrotime import leap_year

    In [2]: leap_year(1999)
    Out[2]: False

    In [3]: leap_year([1999,2000,2001])
    Out[3]: array([False,  True, False])

    In [4]: leap_year([1999.3,2000.9,2001.1])
    Out[4]: array([False,  True, False])

    """

    #######################
    def _check_param(year):
        """
        Raise error if one parameter is invalid and adapt some parameter values
        """
        # Import
        import numpy as np
        # Check
        _yeartypeOK(year)
        # Adapt
        if isinstance(year, list):
            year = np.array(year)
        return year
    #######################

    # Check parameters
    year = _check_param(year)

    # Import
    import numpy as np

    # Find if |year| is a leep year
    if isinstance(year, np.ndarray):
        OK = np.array(list(map(leap_year, year)))
    else:
        year = int(year)
        OK = (year % 4 == 0 and year % 100 != 0) or year % 400 == 0

    # Return
    return OK


###############
def ut2hms(ut):
    """
    Convert decimal fraction of day to hours, minute, seconde

    Parameter
    ---------
    ut : float, list or np.ndarray
        Decimal fraction of the day: within [0.;1.[.

    Returns
    -------
    h : int or np.ndarray
        Hour corresponding to the decimal fraction given.
    m : int or np.ndarray
        Minute corresponding to the decimal fraction given.
    s : int or np.ndarray
        Second corresponding to the decimal fraction given.
        
    Examples
    --------
    In [1]: from itsa.lib.astrotime import ut2hms

    In [2]: ut2hms(.5)
    Out[2]: (12, 0, 0)

    In [3]: ut2hms([.5,.755])
    Out[3]: (array([12, 18]), array([0, 7]), array([ 0, 12]))

    """

    #####################
    def _check_param(ut):
        """
        Raise error is one parameter is invalid and adapt some parameter values
        """
        # Import
        import numpy as np
        # Check
        _uttypeOK(ut)
        # Adapt
        if isinstance(ut, list):
            ut = np.array(ut)
        return ut
    #####################

    # Check parameters
    ut = _check_param(ut)

    # Import
    import numpy as np

    # Convert |ut|
    if isinstance(ut, np.ndarray):
        (h, m, s) = np.array(list(map(ut2hms, ut))).T
    else:
        _utOK(ut)

        # decimal fraction of day to second of day (86400=60*60*24)
        nsec_ut = ut*86400
        int_sec = int(nsec_ut)

        h = int_sec//3600
        r = int_sec % 3600

        m = r//60
        s = r % 60

        if (nsec_ut-int_sec)*1e6 > 500000:
            s += 1

    return h, m, s


#%%###################
## INTERN FUNCTIONS ##
######################

##########################################
def _caltypeOK(day, month, year, ut=None):
    """
    Raise error if calendar date parameters have not the same type or shape

    Parameters
    ----------
    day : int, list or np.ndarray
        Day of the calendar date to test.
    month : int, list or np.ndarray
        Month of the calendar date to test.
    year : int, list or np.ndarray
        Year of the calendar date to test.
    ut : None, float, list or np.ndarray, optional
        Decimal fraction of the day to test.
        The default is None.

    Raises
    ------
    ValueError
        If any parameter is list and cannot be converted to np.ndarray.
        If any parameter is not 1D list nor array.
        If |day|, |month| or |year| values are not all int.
        If |ut| values are not float.
        If np.ndarray parameters do not have the same size.
    TypeError
        If any parameter does not have the right type.
        
    """
    # Import
    import numpy as np
    from itsa.lib.modif_vartype import list2ndarray, nptype2pytype

    # Change type
    # List to np.ndarray
    if isinstance(day, list):
        (day, err_day) = list2ndarray(day)
        if err_day:
            raise ValueError(('Day list must be convertible into np.ndarray '
                              '(or day can be int or np.ndarray): |day=%s|.')
                             % str(day))
    if isinstance(month, list):
        (month, err_month) = list2ndarray(month)
        if err_month:
            raise ValueError(('Month list must be convertible into np.ndarray '
                              '(or month can be int or np.ndarray): '
                              '|month=%s|.') % str(month))
    if isinstance(year, list):
        (year, err_year) = list2ndarray(year)
        if err_year:
            raise ValueError(('Year list must be convertible into np.ndarray '
                              '(or year can be int or np.ndarray): |year=%s|.')
                             % str(year))
    if isinstance(ut, list):
        (ut, err_ut) = list2ndarray(ut)
        if err_ut:
            raise ValueError(('Decimal fraction of day list must be '
                              'convertible into np.ndarray (or decimal '
                              'fraction of day can be int, float or '
                              'np.ndarray): |ut=%s|.') % str(ut))
    # Numpy type to Python type
    (day, month, year, ut) = nptype2pytype([day, month, year, ut])

    # Type errors
    if not isinstance(day, (int, np.ndarray)):
        raise TypeError('Day must be int, list or np.ndarray: |type(day)=%s|.'
                        % type(day))
    if not isinstance(month, (int, np.ndarray)):
        raise TypeError(('Month must be int, list or np.ndarray: '
                         '|type(month)=%s|.') % type(month))
    if not isinstance(year, (int, np.ndarray)):
        raise TypeError(('Year must be int, list or np.ndarray: '
                         '|type(year)=%s|.') % type(year))
    if ut is not None and not isinstance(ut, (float, np.ndarray)):
        raise TypeError(('Decimal fraction of day must be None, float, list '
                         'or np.ndarray: |type(ut)=%s|.') % type(ut))

    # Dimension and value errors
    # |day|
    if isinstance(day, np.ndarray):
        # 1D?
        if day.ndim != 1:
            raise ValueError(('Day must be int, 1D list or 1D np.array: '
                              '|day.ndim=%d|.') % day.ndim)
        # Same shape?
        if isinstance(month, np.ndarray) and month.shape != day.shape:
            raise ValueError(('Day and month must have the same shape: '
                              '|day.shape=%s| and |month.shape=%s|.')
                             % (day.shape, month.shape))
        if isinstance(year, np.ndarray) and year.shape != day.shape:
            raise ValueError(('Day and year must have the same shape: '
                              '|day.shape=%s| and |year.shape=%s|.')
                             % (day.shape, year.shape))
        if isinstance(ut, np.ndarray) and ut.shape != day.shape:
            raise ValueError(('Day and decimal fraction of day must have the '
                              'same shape: |day.shape=%s| and |ut.shape=%s|.')
                             % (day.shape, ut.shape))
        # Valid values?
        if day.dtype != 'int':
            raise ValueError(('Day must be int, list of int or int np.ndarray:'
                              ' |day.dtype=%s|.') % day.dtype)
    # |month|
    if isinstance(month, np.ndarray):
        # 1D?
        if month.ndim != 1:
            raise ValueError(('Month must be int, 1D list or 1D np.ndarray: '
                              '|month.ndim=%d|.') % month.ndim)
        # Same shape?
        if isinstance(year, np.ndarray) and year.shape != month.shape:
            raise ValueError(('Month and year must have the same shape: '
                              '|month.shape=%s| and |year.shape=%s|.')
                             % (month.shape, year.shape))
        if isinstance(ut, np.ndarray) and ut.shape != month.shape:
            raise ValueError(('Month and decimal fraction of day must have '
                              'the same shape: |month.shape=%s| and '
                              '|ut.shape=%s|.') % (month.shape, ut.shape))
        # Valid values?
        if month.dtype != 'int':
            raise ValueError(('Month must be int or list of int or int '
                              'np.ndarray: |month.dtype=%d|.') % month.dtype)
    # |year|
    if isinstance(year, np.ndarray):
        # 1D?
        if year.ndim != 1:
            raise ValueError(('Year must be int, 1D list or 1D np.ndarray: '
                              '|year.ndim=%d|.') % year.ndim)
        # Same shape?
        if isinstance(ut, np.ndarray) and ut.shape != year.shape:
            raise ValueError(('Year and decimal fraction of day must have the '
                              'same shape: |year.shape=%s| and |ut.shape=%s|.')
                             % (year.shape, ut.shape))
        # Valid values?
        if year.dtype != 'int':
            raise ValueError(('Year must be int, list of int or int '
                              'np.ndarray: |year.dtype=%s|.') % year.dtype)
    # |ut|
    if isinstance(ut, np.ndarray):
        # 1D?
        if ut.ndim != 1:
            raise ValueError(('Decimal fraction of day must be int, float, '
                              '1D list or 1D np.ndarray: |ut.ndim=%d|.')
                             % ut.ndim)
        # Valid values?
        if ut.dtype != 'float':
            raise ValueError(('Decimal fraction of day must be float, list '
                              'of float or float np.ndarray: |ut.dtype=%s|.')
                             % ut.dtype)


#############################
def _dayOK(day, month, year):
    """
    Raise error if the day/month/year parameters are invalid

    Parameters
    ----------
    day : int
        Day of the calendar date to test.
    month : int
        Month of the calendar date to test.
    year : int
        Year of the calendar date to test.

    Raise
    -----
    ValueError
        If |month| is negatif or above 12.
        If |day| is negatif or above the number of days of |month|.

    """
    # Import
    import numpy as np
    # Check |month|
    if month > 12 or month < 1:
        raise ValueError('Month out of range: |month=%d|' % month)
    # Check |day|
    days = np.copy(_days)
    if leap_year(year):
        days[1] = 29
    if day < 1 or day > days[month-1]:  # |month-1| is for array indexing
        raise ValueError(('Day of month out of range: '
                          '|(day,month,year)=(%d,%d,%d)|')
                         % (day, month, year))


##############
def _utOK(ut):
    """
    Raise error if the decimal fraction of day is not in [0;1[

    Parameter
    ---------
    ut : float
        Decimal fraction of the day to test.

    Raise
    -----
    ValueError
        If |ut| is not within [0.;1.[.

    """
    if ut < 0. or ut >= 1.:
        raise ValueError(('Decimal fraction of day out of range [0;1[: '
                          '|ut=%.2f|') % ut)


###################################
def _doytypeOK(doy, year, ut=None):
    """
    Raise error if day of year (doy) parameters have not the same type or shape

    Parameters
    ----------
    doy : int, list or np.ndarray
        Day of year of the date to test.
    year : int, list or np.ndarray
        Year of the date to test.
    ut : None, float, list or np.ndarray, optional
        Decimal fraction of the day to test.
        The default is None.

    Raises
    ------
    ValueError
        If any parameter is list and cannot be converted to np.ndarray.
        If any parameter is not 1D list nor array.
        If |doy| or |year| values are not all int.
        If |ut| values are not float.
        If np.ndarray parameters do not have the same size.
    TypeError
        If any parameter does not have the right type.
    
    """
    # Import
    import numpy as np
    from itsa.lib.modif_vartype import list2ndarray, nptype2pytype

    # Change type
    # List to np.ndarray
    if isinstance(doy, list):
        (doy, err_doy) = list2ndarray(doy)
        if err_doy:
            raise ValueError(('Day of year list must be convertible into '
                              'np.ndarray (or day of year can be int or '
                              'np.ndarray): |doy=%s|.') % str(doy))
    if isinstance(year, list):
        (year, err_year) = list2ndarray(year)
        if err_year:
            raise ValueError(('Year list must be convertible into np.ndarray '
                              '(or year can be int or np.ndarray): |year=%s|.')
                             % str(year))
    if isinstance(ut, list):
        (ut, err_ut) = list2ndarray(ut)
        if err_ut:
            raise ValueError(('Decimal fraction of day must be convertible '
                              'into np.ndarray (or decimal fraction of day can'
                              ' be int, float or np.ndarray): |ut=%s|.')
                             % str(ut))
    # Numpy type to Python type
    (doy, year, ut) = nptype2pytype([doy, year, ut])

    # Type errors
    if not isinstance(doy, (int, np.ndarray)):
        raise TypeError(('Day of year must be int, list or np.ndarray: '
                         '|type(doy)=%s|.') % type(doy))
    if not isinstance(year, (int, np.ndarray)):
        raise TypeError(('Year must be int, list or np.ndarray: '
                         '|type(year)=%s|.') % type(year))
    if ut is not None and not isinstance(ut, (float, np.ndarray)):
        raise TypeError(('Decimal fraction of day must be None, float, list '
                         'or np.ndarray: |type(ut)=%s|.') % type(ut))

    # Dimension and value errors
    # |doy|
    if isinstance(doy, np.ndarray):
        # 1D?
        if doy.ndim != 1:
            raise ValueError(('Day or year must be int, 1D list or 1D '
                              'np.ndarray: |doy.ndim=%d|.') % doy.ndim)
        # Same shape?
        if isinstance(year, np.ndarray) and year.shape != doy.shape:
            raise ValueError(('Day of year and year must have the same shape: '
                              '|doy.shape=%s| and |year.shape=%s|.')
                             % (doy.shape, year.shape))
        if isinstance(ut, np.ndarray) and ut.shape != doy.shape:
            raise ValueError(('Day of year and decimal fraction of day must '
                              'have the same shape: |doy.shape=%s| and '
                              '|ut.shape=%s|.') % (doy.shape, ut.shape))
        # Valid values?
        if doy.dtype != 'int':
            raise ValueError(('Day of year must be int, list of int or int '
                              'np.ndarray: |doy.dtype=%s|.') % doy.dtype)
    # |year|
    if isinstance(year, np.ndarray):
        # 1D?
        if year.ndim != 1:
            raise ValueError(('Year must be int, 1D list or 1D np.ndarray: '
                              '|year.ndim=%d|.') % year.ndim)
        # Same shape?
        if isinstance(ut, np.ndarray) and ut.shape != year.shape:
            raise ValueError(('Year and decimal fraction of day must have the '
                              'same shape: |year.shape=%s| and |ut.shape=%s|')
                             % (year.shape, ut.shape))
        # Valid values?
        if year.dtype != 'int':
            raise ValueError(('Year must be int, list of int or int '
                              'np.ndarray: |year.dtype=%s|.') % year.dtype)
    # |ut|
    if isinstance(ut, np.ndarray):
        # 1D?
        if ut.ndim != 1:
            raise ValueError(('Decimal fraction of day must be int, float, '
                              '1D list or 1D np.ndarray: |ut.ndim=%d|.')
                             % ut.ndim)
        # Valid values?
        if ut.dtype != 'float':
            raise ValueError(('Decimal fraction of day must be float, list of '
                              'float or float np.ndarray: |ut.dtype=%s|.')
                             % ut.dtype)


######################
def _doyOK(doy, year):
    """
    Raise error if |doy| (day of year) is invalid

    Parameters
    ----------
    doy : int
        Day of year of the date to test.
    year : int
        Year of the date to test.

    Raises
    ------
    ValueError
        If |doy| is negatif, under 1 or above 365 (or 366 if leap year).

    """
    if doy < 1 or doy > 366 or (doy > 365 and not leap_year(year)):
        raise ValueError('Day of year out of range: |(doy,year)=(%d,%d)|'
                         % (doy, year))


####################
def _mjdtypeOK(mjd):
    """
    Raise error if |mjd| is invalid

    Parameters
    ----------
    mjd : int, float, list or np.ndarray
        Modified julian day to test.

    Raises
    ------
    ValueError
        If |mjd| is list and cannot be converted to np.ndarray.
        If |mjd| values are not int nor float.
    TypeError
        If |mjd| does not have the right type.

    """
    # Import
    import numpy as np
    from itsa.lib.modif_vartype import list2ndarray, nptype2pytype

    # Change type
    # List to np.array
    if isinstance(mjd, list):
        (mjd, err_mjd) = list2ndarray(mjd)
        if err_mjd:
            raise ValueError(('Modified Julian day list must be convertible '
                              'into np.ndarray (or modified Julian day can be '
                              'int, float or np.ndarray): |mjd=%s|.')
                             % str(mjd))
    # Numpy type to Python type
    mjd = nptype2pytype(mjd)

    # Type errors
    if not isinstance(mjd, (int, float, np.ndarray)):
        raise TypeError(('Modified Julian day must be int, float, list or '
                         'np.ndarray: |type(mjd)=%s|.') % type(mjd))
    if isinstance(mjd, np.ndarray) and mjd.dtype not in ['int', 'float']:
        raise TypeError(('Modified Julian day must be int, float, list of int,'
                         ' list of float, int np.ndarray or float np.ndarray: '
                         '|mjd.dtype=%s|.') % mjd.dtype)

    # Dimension error
    if isinstance(mjd, np.ndarray) and mjd.ndim != 1:
        raise ValueError(('Modified Julian day must be int, float, 1D list or '
                          '1D np.ndarray: |mjd.ndim=%d|.') % mjd.ndim)


############################
def _decyeartypeOK(decyear):
    """
    Raise error if |decyear| is invalid

    Parameters
    ----------
    decyear : int, float, list or np.ndarray
        Decimal year of the date to test.
        
    Raises
    ------
    ValueError
        If |decyear| is list and cannot be converted to np.ndarray.
        If |decyear| values are not int nor float.
    TypeError
        If |decyear| does not have the right type.

    """
    # Import
    import numpy as np
    from itsa.lib.modif_vartype import list2ndarray, nptype2pytype

    # Change type
    # List to np.array
    if isinstance(decyear, list):
        (decyear, err_decyear) = list2ndarray(decyear)
        if err_decyear:
            raise ValueError(('Decimal year list must be convertible into '
                              'np.ndarray (or decimal year can be int, float '
                              'or np.ndarray): |decyear=%s|.') % str(decyear))
    # Numpy type to Python type
    decyear = nptype2pytype(decyear)

    # Type errors
    if not isinstance(decyear, (int, float, np.ndarray)):
        raise TypeError(('Decimal year must be int, float, list or np.ndarray:'
                         ' |type(decyear)=%s|.') % type(decyear))
    if (isinstance(decyear, np.ndarray) and
        decyear.dtype not in ['int', 'float']):
        raise TypeError(('Decimal year must be int, float, list of int, list '
                         'of float, int np.ndarray or float np.ndarray: '
                         '|decyear.dtype=%s|.') % decyear.dtype)

    # Dimension error
    if isinstance(decyear, np.ndarray) and decyear.ndim != 1:
        raise ValueError(('Decimal year must be int, float, 1D list or 1D '
                          'np.ndarray: |decyear.ndim=%d|.') % decyear.ndim)


######################
def _yeartypeOK(year):
    """
    Raise error if |year| is invalid

    Parameters
    ----------
    year : int, float, list or np.ndarray
        Year to test.
        
    Raises
    ------
    ValueError
        If |year| is list and cannot be converted to np.ndarray.
        If |year| values are not int nor float.
    TypeError
        If |year| does not have the right type.

    """
    # Import
    import numpy as np
    from itsa.lib.modif_vartype import list2ndarray, nptype2pytype

    # Change type
    # List to np.array
    if isinstance(year, list):
        (year, err_year) = list2ndarray(year)
        if err_year:
            raise ValueError(('Year list must be convertible into np.ndarray '
                              '(or decimal year can be int, float or '
                              'np.ndarray): |year=%s|.') % str(year))
    # Numpy type to Python type
    year = nptype2pytype(year)

    # Type errors
    if not isinstance(year, (int, float, np.ndarray)):
        raise TypeError(('Year must be int, float, list or np.ndarray: '
                         '|type(year)=%s|.') % type(year))
    if isinstance(year, np.ndarray) and year.dtype not in ['int', 'float']:
        raise TypeError(('Year must be int, float, list of int, list of float,'
                         ' int np.ndarray or float np.ndarray: '
                         '|year.dtype=%s|.') % year.dtype)

    # Dimension error
    if isinstance(year, np.ndarray) and year.ndim != 1:
        raise ValueError(('Year must be int, float, 1D list or 1D np.ndarray: '
                          '|year.ndim=%d|.') % year.ndim)


##################
def _uttypeOK(ut):
    """
    Raise error if |ut| is invalid

    Parameters
    ----------
    ut : float, list or np.ndarray
        Decimal fraction of day to test.
        
    Raises
    ------
    ValueError
        If |ut| is list and cannot be converted to np.ndarray.
        If |ut| values are not float.
    TypeError
        If |ut| does not have the right type.

    """
    # Import
    import numpy as np
    from itsa.lib.modif_vartype import list2ndarray, nptype2pytype

    # Change type
    # List to np.array
    if isinstance(ut, list):
        (ut, err_ut) = list2ndarray(ut)
        if err_ut:
            raise ValueError(('Decimal fraction of day must be convertible '
                              'into np.ndarray (or decimal fraction of day '
                              'can be float or np.ndarray): |ut=%s|.')
                             % str(ut))
    # Numpy type to Python type
    ut = nptype2pytype(ut)

    # Type errors
    if not isinstance(ut, (float, np.ndarray)):
        raise TypeError(('Decimal fraction of day must be float, list or '
                         'np.ndarray: |type(ut)=%s|.') % type(ut))
    if isinstance(ut, np.ndarray) and ut.dtype != 'float':
        raise TypeError(('Decimal fraction of day must be float, list of float'
                         ' or float np.ndarray: |ut.dtype=%s|.') % ut.dtype)

    # Dimension error
    if isinstance(ut, np.ndarray) and ut.ndim != 1:
        raise ValueError(('Decimal fraction of day must be float, 1D list or '
                          '1D np.ndarray: |ut.ndim=%d|.') % ut.ndim)
