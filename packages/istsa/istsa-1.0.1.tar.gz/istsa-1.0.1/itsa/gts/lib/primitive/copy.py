"""
    Developed at: ISTerre
    By: Lou MARILL
    Based on: PYACS module
"""


###################################################################
def copy(self, data=True, data_xyz=True, data_neu=True, warn=True):
    """
    Copy Geodetic time series (Gts)

    Parameters
    ----------
    data : bool or None or np.ndarray, optional
        New dN, dE, dU coordinates for the new Gts |ts|.
        The default is True: |ts.data=self.data|.
    data_xyz : bool or None or np.ndarray, optional
        New NEU coordinates for |ts|.
        The default is True: |ts.data_xyz=self.data_xyz|.
    data_neu : bool or None or np.ndarray, optional
        New NEU coordinates for |ts|.
        The default is True: |ts.data_neu=self.data_neu|.
    warn : bool, optional
        Print warning if true.
        The default is True.
        
    Raise
    -----
    WARNING
        If any parameter does not have the right type: parameter set to False.

    Returns
    -------
    ts : Gts
        New Gts from |self|.
        
    Notes
    -----
    - All the parameter (except |self|) can be defined by the wanted new value
    in the new Gts
    - If a parameter is True: the data associated to the parameter are
    identical in both Gts
    - If a parameter is False: the data associated to the parameter is None in
    the new Gts

    """

    #######################################################
    def _check_param(self, data, data_xyz, data_neu, warn):
        """
        Raise error if one parameter is invalid and adapt some parameter values
        """
        # Import
        import numpy as np
        from itsa.lib.modif_vartype import adapt_bool

        # Check
        # |self|
        self.check_gts()

        # Adapt
        warn_data, warn_xyz, warn_neu = False, False, False
        # |data|
        if data is not None and not isinstance(data, np.ndarray):
            (data, warn_data) = adapt_bool(data)
        # |data_xyz|
        if data_xyz is not None and not isinstance(data_xyz, np.ndarray):
            (data_xyz, warn_xyz) = adapt_bool(data_xyz)
        # |data|
        if data_neu is not None and not isinstance(data_neu, np.ndarray):
            (data_neu, warn_neu) = adapt_bool(data_neu)
        # |warn|
        (warn, _) = adapt_bool(warn, True)

        # Warnings
        if warn and (warn_data or warn_xyz or warn_neu):
            print('[WARNING] from method [copy] in [%s]' % __name__)
            if warn_data:
                print(('\t|data| parameter set to False because |data!=None|, '
                       '|type(data)!=np.ndarray)| and |type(data)!=bool|!'))
                print('\tNew Gts %s |data| is set to None!' % self.code)
                print()
            if warn_xyz:
                print(('\t|data_xyz| parameter set to False because '
                       '|data_xyz!=None|, |type(data_xyz)!=np.ndarray)| and '
                       '|type(data_xyz)!=bool|!'))
                print('\tNew Gts %s |data_xyz| is set to None!' % self.code)
                print()
            if warn_neu:
                print(('\t|data_neu| parameter set to False because '
                       '|data_neu!=None|, |type(data_neu)!=np.ndarray)| and '
                       '|type(data_neu)!=bool|!'))
                print('\tNew Gts %s |data_neu| is set to None!' % self.code)
                print()

        # Return
        return data, data_xyz, data_neu
    #######################################################

    # Check parameters
    (data, data_xyz, data_neu) = _check_param(self, data, data_xyz, data_neu,
                                              warn)

    # Import
    from copy import deepcopy

    # Copy
    ts = deepcopy(self)

    # Change data
    if isinstance(data, bool):
        if not data:
            ts.data = None
    else:
        ts.data = data

    if isinstance(data_xyz, bool):
        if not data_xyz:
            ts.data_xyz = None
    else:
        ts.data_xyz = data_xyz

    if isinstance(data_neu, bool):
        if not data_neu:
            ts.data_neu = None
    else:
        ts.data_neu = data_neu

    # Return
    return ts
