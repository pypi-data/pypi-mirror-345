"""
    Linear algebra for Geodesy problems
    Functions to manipulate covariance and correlation matrices

    !!! Warning: You need to add the module 'itsa' to your Python path to use these functions

    ----
    Developed at: ISTerre
    By: Lou MARILL
    Based on: PYACS module
"""


############################
def corr2cov(corr, sigma_m):
    """
    From correlation to covariance matrix

    Parameters
    ----------
    corr : np.ndarray
        Correlation matrix.
    sigma_m : np.ndarray
        Vector of standard deviation: |sigma_m=sqrt(diag(Cov))|.

    Raises
    ------
    TypeError
        If any parameter does not have the right type.
    ValueError
        If |corr| is not 3x3 2D np.ndarray.
        If |sigma_m| does not have exactly 3 values.
        If |corr| or |sigma_m| values are not int nor float.

    Return
    ------
    np.ndarray
        Covariance matrix.

    """

    ###############################
    def _check_param(corr, sigma_m):
        """
        Raise error is one parameter is invalid
        """
        # Import
        import numpy as np

        # Check
        # |corr|
        if not isinstance(corr, np.ndarray):
            raise TypeError(('Correlation matrix must be np.ndarray: '
                             '|type(corr)=%s|.') % type(corr))
        if corr.shape not in [(3, 3)]:
            raise ValueError(('Correlation matrix must be 3x3 np.ndarray: '
                              '|corr.shape=%s|.') % str(corr.shape))
        if corr.dtype not in ['int', 'float']:
            raise ValueError(('Correlation marix must be int np.ndarray or '
                              'float np.ndarray: |corr.dtype=%s|.')
                             % corr.dtype)
        # |sigma_m|
        if not isinstance(sigma_m, np.ndarray):
            raise TypeError(('Standard deviation must be np.ndarray: '
                            '|type(sigma_m)=%s|.') % type(sigma_m))
        if sigma_m.size != 3:
            raise ValueError(('Standard deviation must have exactly 3 values: '
                              '|sigma_m.size=%d|.') % sigma_m.size)
        sigma_m = sigma_m.reshape(3)
        if sigma_m.dtype not in ['int', 'float']:
            raise ValueError(('Standart deviation must be int np.ndarray or '
                              'float np.ndarray: |sigma_m.dtype=%s|.')
                             % sigma_m.dtype)
    ###############################

    _check_param(corr, sigma_m)

    import numpy as np

    outer_v = np.outer(sigma_m, sigma_m)

    return corr*outer_v


##################
def cov2corr(Cov):
    """
    From covariance to correlation matrix

    Parameter
    ---------
    Cov : np.ndarray
        Covanriance matrix.

    Raises
    ------
    TypeError
        If |Cov| does not have the right type.
    ValueError
        If |Cov| is not 3x3 2D np.ndarray.
        If |Cov| values are not int nor float.

    Returns
    -------
    corr : np.ndarray
        Correlation matrix
    v : np.ndarray
        Strandard deviation vector.

    """

    ######################
    def _check_param(Cov):
        """
        Raise error if one parameter is invalid
        """
        # Import
        import numpy as np

        # Check
        # |Cov|
        if not isinstance(Cov, np.ndarray):
            raise TypeError(('Covariance matrix must be np.ndarray: '
                             '|type(Cov)=%s|.') % type(Cov))
        if Cov.shape not in [(3, 3)]:
            raise ValueError(('Covariance matrix must be 3x3 np.ndarray: '
                              '|Cov.shape=%s|.') % str(Cov.shape))
        if Cov.dtype not in ['int', 'float']:
            raise ValueError(('Covariance matrix must be int np.ndarray or '
                              'float np.ndarray: |Cov.dtype=%s|.') % Cov.dtype)
    ######################

    _check_param(Cov)

    import numpy as np

    v = np.sqrt(np.diag(Cov))
    outer_v = np.outer(v, v)
    corr = Cov/outer_v
    corr[Cov == 0] = 0

    return corr, v
