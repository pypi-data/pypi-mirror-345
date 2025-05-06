"""
    Change of Gtss time vector

    ----
    Developed at: ISTerre
    By: Lou MARILL
"""


###############################################################################
def continuous_time(self, step=1, ini_time=None, fin_time=None, in_place=False,
                    warn=True):
    """
    Change Gts |time| into countinuous time vector with step of |step|

    Parameters
    ----------
    step : int, optional
        Step of the new time vector, in days.
        The default is 1.
    ini_time : None, int or float, optional
        Initial time for the new time vector, in decimal year.
        The default is None: the first value of |self.time| is taken.
    fin_time : None, int or float, optional
        Final time for the new time vector, in decimal year.
        The default is None: the last value of |self.time| is taken.
    in_place : bool, optional
        Change data directly in |self| if true.
        The default is False: create and return new Gts 
                              (|self| is not updated).
    warn : bool, optional
        Print warning if true.
        The default is True.

    Raises
    ------
    TypeError
        If any parameter does not have the right type.
    WARNING
        If |in_place| is not bool: |in_place| is set to False.

    Return
    ------
    ts: Gts
        Only if |in_place| is false.
        New Gts with continuous time vector.

    Note
    ----
    Attribute |G| and |MOD| are reinitialised.

    """

    #################################################################
    def _check_param(self, step, ini_time, fin_time, in_place, warn):
        """
        Raise error if one parameter is invalid and adapt some parameter values
        """
        # Import
        from itsa.lib.modif_vartype import adapt_bool

        # Check
        # |self|
        self.check_gts()
        # |setp|
        if not isinstance(step, int):
            raise TypeError('Step must be int: |type(step)=%s|.' % type(step))
        # |ini_time|
        if ini_time is not None and not isinstance(ini_time, (int, float)):
            raise TypeError(('Initial time must be None, int or float: '
                             'type(ini_time)=%s|.') % type(ini_time))
        # |fin_time|
        if fin_time is not None and not isinstance(fin_time, (int, float)):
            raise TypeError(('Final time must be None, int or float: '
                             '|type(fin_time)=%s|.') % type(fin_time))

        # Adapt
        # |in_place|
        (in_place, warn_place) = adapt_bool(in_place)
        # |warn|
        (warn, _) = adapt_bool(warn, True)

        # Warning
        if warn and warn_place:
            print('[WARNING] from method [countinuous_time] in [%s]:'
                  % __name__)
            print(('\t|in_place| parameter set to False because '
                   '|type(in_place)!=bool|!'))
            print('\tNew Gts %s is returned (and the old one is not updated)!'
                  % self.code)
            print()

        return in_place, warn
    #################################################################

    # Check parameters
    (in_place, warn) = _check_param(self, step, ini_time, fin_time, in_place,
                                    warn)

    # Import
    import numpy as np
    from itsa.lib.astrotime import decyear2mjd, mjd2decyear
    from itsa.lib.index_dates import get_index_from_dates

    # Sort time vector and remove duplicated dates
    self.remove_duplicated_dates(warn=warn)

    # Initial and final dates
    if ini_time is None:
        ini_time = int(self.time[0, 1])
    else:
        ini_time = int(decyear2mjd(ini_time))

    if fin_time is None:
        fin_time = int(self.time[-1, 1])
    else:
        fin_time = int(decyear2mjd(fin_time))

    # New Gts
    ts = self.copy(data=False, data_xyz=False, data_neu=False)

    # New time vector
    if ini_time != fin_time:
        mjd = np.array([t for t in range(ini_time, fin_time+1, step)])+.5
    else:
        mjd = np.array([ini_time])+.5
    ts.time = np.c_[mjd2decyear(mjd), mjd]

    # Get index for Gts data
    idx_ts = get_index_from_dates(ts.time[:, 1], self.time[:, 1])
    nan_idx = np.where(idx_ts<0)[0]
    if nan_idx.size > 0:
        idx_ts = np.delete(idx_ts, nan_idx).astype(int)
        idx_self = get_index_from_dates(self.time[:, 1], ts.time[:, 1])
        idx_self = np.delete(idx_self,
                             np.where(idx_self<0)[0]).astype(int)
    else:
        idx_self = np.array([idx for idx in range(self.data.shape[0])])

    # Populate |ts|
    # |data|
    ts.data = np.ones((ts.time.shape[0], self.data.shape[1]))*np.nan
    ts.data[idx_ts, :] = self.data[idx_self, :]
    # |data_xyz|
    if self.data_xyz is not None:
        ts.data_xyz = np.ones((ts.time.shape[0],
                               self.data_xyz.shape[1]))*np.nan
        ts.data_xyz[idx_ts, :] = self.data_xyz[idx_self, :]
    # |data_neu|
    if self.data_neu is not None:
        ts.data_neu = np.ones((ts.time.shape[0],
                               self.data_neu.shape[1]))*np.nan
        ts.data_neu[idx_ts, :] = self.data_neu[idx_self, :]

    # Remove |G| and |MOD|
    ts.G = None
    ts.MOD = None

    # Return
    if not in_place:
        return ts
    else:
        self.time = ts.time.copy()
        self.data = ts.data.copy()
        if self.data_xyz is not None:
            self.data_xyz = ts.data_xyz.copy()
        if self.data_neu is not None:
            self.data_neu = ts.data_neu.copy()
        self.G = None
        self.MOD = None


################################################
def nonan_time(self, in_place=False, warn=True):
    """
    Change Gts |time| into time vector with no NaN value into |data|

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
        If |in_place| is not bool: |in_place| is set to False.

    Return
    ------
    ts : Gts
        Only if |in_place| is false.
        New Gts without np.nan in any coordinates.

    """

    #######################################
    def _check_param(self, in_place, warn):
        """
        Raise error if one parameter is invalid and adapt some parameter values
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

        # Warning
        if warn and warn_place:
            print('[WARNING] from method [nonan_time] in [%s]' % __name__)
            print(('\t|in_place| parameter set to False because '
                   '|type(in_place)!=bool|!'))
            print('\tNew Gts %s is returned (and the old one is not updated)!'
                  % self.code)
            print()

        return in_place
    #######################################

    # Check parameters
    in_place = _check_param(self, in_place, warn)

    # Import
    import numpy as np

    # Find NaN
    idx_nonan = np.unique(np.where(~np.isnan(self.data))[0])

    # Return
    return self.select_data(idx_nonan, in_place=in_place)
