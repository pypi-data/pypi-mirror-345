"""
    Functions to find and remove outliers

    ----
    Developed at: ISTerre
    By: Lou MARILL
    Based on: PYACS package
"""


#################################################################
def find_outliers(self, threshold=5, window_len=61, periods=None,
                  excluded_periods=None, warn=True):
    """
    Populate |outliers| by a sliding window method

    Parameters
    ----------
    threshold : int or float, optional
        Value multiplied by the Median Absolution Deviation (MAD) of the window
        to create the final threshold.
        Advise: Take |threshold >= 5|
        The default is 5.
    window_len : int, optional
        Length of the sliding window.
        The default is 61.
    periods : None, list or np.ndarray, optional
        Time period to look at outliers.
        The default is None: look at the full time series.
    excluded_periods : None, list or np.ndarray, optional
        Time periods to exclude for the outlier search.
        The default is None: do not exclude any period.
    warn : bool, optional
        Print warning if true.
        The default is True.

    Raises
    ------
    ValueError
        If |periods| or |excluded_periods| is list and cannot be converted to
        np.ndarray.
        If |threshold| or |window_len| is negatif.
        If |periods| or |excluded_periods| is not a 2-column 2D np.ndarray
        (after conversion if given as list)
        If |periods| or |excluded_periods| values are not int nor float
    TypeError
        If any parameter does not have the right type.
    WARNING
        If both |periods| and |excluded_periods| are given: periods in 
        |excluded_periods| will be excluded even if they are in |periods|.

    !!! Warning
    -----------
    - The time periods (included or excluded) need to be defnied with decimal
    years
    - The function assume that ts.time is continue (with NaN value in |data|
                                                    when there are no data) 

    """

    ########################################################################
    def _check_param(self, threshold, window_len, periods, excluded_periods,
                     warn):
        """
        Raise error if one parameter is invalid and adapt some parameter values
        """
        # Import
        import numpy as np
        from itsa.lib.modif_vartype import list2ndarray, adapt_bool

        # Change type
        # |periods|
        if isinstance(periods, list):
            (periods, err_periods) = list2ndarray(periods)
            if err_periods:
                raise ValueError(('Periods list must be convertible into '
                                  'np.ndarray: |periods=%s|.') % str(periods))
        # |excluded_periods|
        if isinstance(excluded_periods, list):
            (excluded_periods, err_excluded) = list2ndarray(excluded_periods)
            if err_excluded:
                raise ValueError(('Excluded periods list must be convertible '
                                  'into np.ndarray: |excluded_periods=%s|.')
                                 % str(excluded_periods))

        # Check
        # |self|
        self.check_gts()
        # |threshold|
        if not isinstance(threshold, (int, float)):
            raise TypeError(('Threshold must be int or float: '
                             '|type(threshold)=%s|.') % type(threshold))
        if threshold < 0:
            raise ValueError('Threshold must be positive: |threshold=%f|.'
                             % threshold)
        # |window_len|
        if (not isinstance(window_len, (int, float)) or
            (isinstance(window_len, float) and window_len != int(window_len))):
            raise TypeError('Window length must be int: |type(window_len)=%s|.'
                            % type(window_len))
        if window_len < 0:
            raise ValueError('Window length must be positive: |window_len=%d|.'
                             % int(window_len))
        # |periods|
        if periods is not None:
            if not isinstance(periods, np.ndarray):
                raise TypeError(('Periods must be None, list or np.ndarray: '
                                 '|type(periods)=%s|.') % type(periods))
            if ((periods.ndim == 1 and periods.shape[0] != 2) or 
                (periods.ndim == 2 and periods.shape[1] != 2) or 
                periods.ndim > 2):
                raise ValueError(('Periods must have only 2 values (list or 1D'
                                  ' np.ndarray) or be a list of 2-value lists '
                                  'or a 2-column 2D np.ndarray: '
                                  '|periods.shape=%s|.') % str(periods.shape))
            if periods.dtype not in ['int', 'float']:
                raise ValueError(('Periods limit must be int of float: '
                                  '|periods.dtype=%s|.') % periods.dtype)
        # |excluded_periods|
        if excluded_periods is not None:
            if not isinstance(excluded_periods, np.ndarray):
                raise TypeError(('Excluded periods must be None, list or '
                                 'np.ndarray: |type(excluded_periods)=%s|.')
                                % type(excluded_periods))
            if ((excluded_periods.ndim == 1 and excluded_periods.shape[0] != 2)
                or (excluded_periods.ndim == 2 and
                    excluded_periods.shape[1] != 2)
                or excluded_periods.ndim > 2):
                raise ValueError(('Excluded periods must have only 2 values '
                                  '(list or 1D np.ndarray) or be a list of '
                                  '2-value lists or a 2-column 2D np.ndarray: '
                                  '|excluded_periods.shape=%s|.')
                                 % str(excluded_periods.shape))
            if excluded_periods.dtype not in ['int', 'float']:
                raise ValueError(('Excluded periods limit must be int of '
                                  'float: |excluded_periods.dtype=%s|.')
                                 % excluded_periods.dtype)

        # Adapt
        # |window_len|
        window_len = int(window_len)
        if window_len > self.time.shape[0]:
            window_len = self.time.shape[0]
        # |periods|
        if periods is not None:
            if periods.ndim == 1:
                periods = periods.reshape(-1, 2)
            periods = list(periods)
        # |excluded_periods|
        if excluded_periods is not None:
            if excluded_periods.ndim == 1:
                excluded_periods = excluded_periods.reshape(-1, 2)
            excluded_periods = list(excluded_periods)
        # |warn|
        (warn, _) = adapt_bool(warn, True)

        # Warning
        if warn and periods is not None and excluded_periods is not None:
            print('[WARNING] from method [find_outliers] in [%s]' % __name__)
            print('\t|periods| and |excluded_periods| provided!')
            print(('\tPeriods in |excluded_periods| will be excluded even if '
                   'there are in |periods|!'))
            print()

        # Return
        return window_len, periods, excluded_periods
    ########################################################################

    # Check parameters
    (window_len, periods, excluded_periods) = _check_param(self, threshold,
                                                           window_len, periods,
                                                           excluded_periods,
                                                           warn)

    # Import
    import numpy as np

    # Reorder
    self.reorder()

    # Copy |data|
    data = self.data[:, :3].copy()

    # Account for previous outliers
    if self.outliers is not None:
        data[self.outliers, :] = np.nan

    # Exclude periods
    # Exclude periods out of |periods|
    if periods:
        excluded = np.ones(self.time.shape[0], dtype=bool)
        for period in periods:
            excluded[(self.time[:, 0] >= period[0]) & 
                     (self.time[:, 0] <= period[1])] = False
        data[excluded, :3] = np.nan
    # Exclude periods in |excluded_periods|
    if excluded_periods:
        excluded = np.zeros(self.time.shape[0], dtype=bool)
        for period in excluded_periods:
            excluded[(self.time[:, 0] >= period[0]) & 
                     (self.time[:, 0] <= period[1])] = True
        data[excluded, :3] = np.nan

    # Find outlier indexes
    idx_out = []
    for i in range(data.shape[0]-window_len):
        # Sliding window
        window = data[i:i+window_len, :]
        if (not np.isnan(window).all() and
            not np.isnan(window[window_len//2, :]).all()):
            residuals = np.abs(window-np.nanmedian(window, axis=0))
            MAD = np.nanmedian(residuals, axis=0)
            if (residuals[window_len//2, :] > threshold*MAD).any():
                idx_out.append(i+window_len//2)
    # First data
    window = data[:window_len, :]
    if (not np.isnan(window).all() and
        not np.isnan(window[:window_len//2, :]).all()):
        residuals = np.abs(window-np.nanmedian(window, axis=0))
        MAD = np.nanmedian(residuals, axis=0)
        idx_out += list(np.unique(np.where(
            residuals[:window_len//2, :] > threshold*MAD)[0])
            )
    # Last data
    window = data[-window_len:, :]
    if (not np.isnan(window).all() and
        not np.isnan(window[window_len//2+1:, :]).all()):
        residuals = np.abs(window-np.nanmedian(window, axis=0))
        MAD = np.nanmedian(residuals, axis=0)
        idx_out += list(np.unique(np.where(
                        residuals[window_len//2+1:, :] > threshold*MAD)[0])
                        + data.shape[0]-window_len+1)

    # Populate |outliers|
    if len(idx_out) > 0:
        if self.outliers is None:
            self.outliers = np.sort(idx_out)
        # If |outliers| already exists
        else:
            self.outliers = np.sort(np.unique(idx_out+list(self.outliers)))


#####################################################
def remove_outliers(self, in_place=False, warn=True):
    """
    Remove outliers provided in |outliers|

    Parameters
    ----------
    in_place : bool, optional
        Change data directly in |self| if true.
        The default is False: create and return new Gts 
                              (|self| is not updated).
    warn : bool, optional
        Print warnings if true.
        The default is True.
    
    Raise
    -----
    WARNING
        If |self.outliers=None|: no outliers removed (as None given).
        If |in_place| is not bool: |in_place| is set to False.

    Return
    ------
    ts : Gts
        Only if |in_place| is false.
        New Gts with outliers removed.

    """

    #####################################
    def _check_param(self, in_place, warn):
        """
        Raise error is one parameter is invalid and adapt some parameter values
        """
        # Import
        from itsa.lib.modif_vartype import adapt_bool

        # Check
        # |self|
        self.check_gts()

        # Adapt
        # |in_place|
        (in_place, warn_place) = adapt_bool(in_place)
        # |warn|
        (warn, _) = adapt_bool(warn, True)

        # Warnings
        if warn and (self.outliers is None or warn_place):
            print('[WARNING] from method [remove_outliers] in [%s]' % __name__)
            if self.outliers is None:
                print('\tNo outliers provided: |self.outliers=None|!')
                print('\tNo outliers removed from Gts %s!' % self.code)
                print()
            if warn_place:
                print(('\t|in_place| parameter set to False because '
                       '|type(in_place)!=bool|!'))
                print('\tNew Gts %s is returned (and old one is not updated).'
                      % self.code)
                print()

        # Return
        return in_place
    #####################################

    # Check parameters
    in_place = _check_param(self, in_place, warn)

    if self.outliers is not None:
        # Import
        import numpy as np

        # Copie data and remove outliers from copied data
        # dN, dE, dU
        data = self.data.copy()
        data[self.outliers, :] = np.nan
        # XYZ
        if self.data_xyz is not None:
            data_xyz = self.data_xyz.copy()
            data_xyz[self.outliers, :] = np.nan
        else:
            data_xyz = None
        # NEU
        if self.data_neu is not None:
            data_neu = self.data_neu.copy()
            data_neu[self.outliers, :] = np.nan
        else:
            data_neu = None

        # Create new Gts
        ts = self.copy(data, data_xyz, data_neu)
        ts.outliers = None

        # Change |self|
        if in_place:
            self.data = data
            self.data_xyz = data_xyz
            self.data_neu = data_neu
            self.outliers = None
    else:
        ts = self.copy()

    # Return
    if not in_place:
        return ts
