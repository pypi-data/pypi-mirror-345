"""
    Functions to modified parameter type and/or shape

    Warning: !!! You need to add the module 'itsa' to your Python path to use
    these functions

    ----
    Developed at: ISTerre
    By: Lou MARILL
"""


#####################
def nptype2pytype(L):
    """
    Change numpy type to Python type if there is only one value
    Used when only some type are accepted to avoid issues with numpy type

    Parameter
    ---------
    L
        Change the type of all arguments in |L| if |L| is list.
        Change the type of |L| otherwise.

    Return
    ------
    L
        List or |L| with changed type (if change needed).

    Examples
    --------
    In [1]: from itsa.lib.modif_vartype import nptype2pytype

    In [2]: import numpy as np

    In [3]: x = np.array([3])[0]

    In [4]: (x,type(x))
    Out[4]: (3, numpy.int64)

    In [5]: x = nptype2pytype(x)

    In [6]: (x,type(x))
    Out[6]: (3,int)

    In [7]: XYZ = np.array([3,4,5.])

    In [8]: (x,y,z) = XYZ

    In [9]: ([x,type(x)],[y,type(y)],[z,type(z)])
    Out[9]: ([3.0, numpy.float64], [4.0, numpy.float64], [5.0, numpy.float64])

    In [10]: (x,y,z) = nptype2pytype(list(XYZ))

    In [11]: ([x,type(x)],[y,type(y)],[z,type(z)])
    Out[11]: ([3.0, float], [4.0, float], [5.0, float])

    In [12]: XYZ = np.array([(3,4,5.)],dtype='i,i,f')

    In [13]: (x,y,z) = XYZ[0]

    In [14]: ([x,type(x)],[y,type(y)],[z,type(z)])
    Out[14]: ([3, numpy.int32], [4, numpy.int32], [5.0, numpy.float32])

    In [15]: (x,y,z) = nptype2pytype(list(XYZ[0]))

    In [16]: ([x,type(x)],[y,type(y)],[z,type(z)])
    Out[16]: ([3, int], [4, int], [5.0, float])
    
    """


    if not isinstance(L, list):
        if 'numpy' in str(type(L)):
            try:
                L = L.item()
            except:
                pass
    else:
        for var in range(len(L)):
            if 'numpy' in str(type(L[var])):
                try:
                    L[var] = L[var].item()
                except:
                    pass
    return L


###################
def adapt_shape(L):
    """
    Make int and float arguments of list, np.ndarray of the same shape
    If no list nor np.ndarray if found among arguments, no changes are made
    
    Parameter
    ---------
    L : list
        List of variables to adapt.

    Return
    ------
    L : list
        List of the variable adapted.
        
    Notes
    -----
    - If |L| is not list: no changes are made.
    - If several np.ndarray are in arguments: int and float in arguments will
    be changed to np.ndarray with the same shape of the first np.ndarray found.

    Example
    -------
    In [1]: from itsa.lib.modif_vartype import adapt_shape

    In [2]: x, y, z = 1, [3, 4], np.array([4])[0]

    In [3]: x, y, z
    Out[3]: (1, [3, 4], 4)

    In [4]: (x, y, z) = adapt_shape([x, y, z])

    In [5]: x, y, z
    Out[5]: (array([1, 1]), array([3, 4]), array([4, 4]))

    In [6]: adapt_shape([1, [3, 4], [4]])
    Out[6]: [array([1, 1]), array([3, 4]), array([4, 4])]

    In [7]: adapt_shape([1, [3, 4], [4, 5]])
    Out[7]: [array([1, 1]), array([3, 4]), array([4, 5])]

    In [8]: adapt_shape([1, [3, 4], [4, 5, 6]])
    Out[8]: [array([1, 1]), array([3, 4]), array([4, 5, 6])]

    In [9]: adapt_shape([1, [3, 4, 5], [4, 5]])
    Out[9]: [array([1, 1, 1]), array([3, 4, 5]), array([4, 5])]

    """

    if isinstance(L, list):
        # Import
        import numpy as np

        # Change list into np.ndarray
        for var in range(len(L)):
            if isinstance(L[var], list):
                L[var] = np.array(L[var])
            L[var] = nptype2pytype(L[var])

        # Adapt int and float into np.ndarray
        for var in range(len(L)):
            if isinstance(L[var], np.ndarray):
                for var2 in range(len(L)):
                    if isinstance(L[var2], (int, float)):
                        L[var2] = np.ones(L[var].shape, dtype=int)*L[var2]

    # Return
    return L


#################################
def adapt_bool(B, default=False):
    """
    Make variable False if not boolean variable

    Parameters
    ----------
    B : bool
        Variable to adapt.
    default : bool, optional
        Default value to give B if needed to adapt.
        The default is False.

    Returns
    -------
    B : bool
        |B| if |B| was already bool and |default| otherwise.
    bool
        True if |B| was already bool and False otherwise.

    """
    if not isinstance(B, (bool, int)) or (B != 0 and B != 1):
        return default, True
    return B, False


####################
def list2ndarray(L):
    """
    Change list into np.ndarray

    Parameters
    ----------
    L : list
        List to convert to np.ndarray.

    Returns
    -------
    L : list or np.ndarray
        |L| in list if the conversion was not possible.
        |L| in np.ndarray otherwise.
    err_warn : bool
        True if |L| still list and False otherwise.

    """
    import numpy as np
    from warnings import filterwarnings
    filterwarnings('error')

    if isinstance(L, list):
        err_warn = False
        try:
            L = np.array(L)
        except np.VisibleDeprecationWarning:
            err_warn = True
    else:
        err_warn = True

    return L, err_warn
