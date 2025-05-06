"""
    Developed at: ISTerre
    By: Lou MARILL
    Based on: PYACS module
"""


#################################################################
def remove_velocity(self, Vn, Ve, Vu, in_place=False, warn=True):
    """
    Remove velocity from Gts

    Parameters
    ----------
    Vn : int or float
        North velocity, in milimeter.
    Ve : int or float
        East velocity; in milimeter.
    Vu : int or float
        Vertical velocity, in milimeter.
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
        

    Returns
    -------
    ts: Gts
        Only if |in_place| is false.
        New Gts with given velocity removed from all coordinates.

    """

    ###################################################
    def _check_param(self, Vn, Ve, Vu, in_place, warn):
        """
        Raise error is one parameter is invalid and adapt some parameter values
        """
        # Import
        from itsa.lib.modif_vartype import nptype2pytype, adapt_bool

        # Change type
        (Vn, Ve, Vu) = nptype2pytype([Vn, Ve, Vu])

        # Check
        # |self|
        self.check_gts()
        # |Vn|
        if not isinstance(Vn, (int, float)):
            raise TypeError(('North velocity must be int or float: '
                             '|type(Vn)=%s|.') % type(Vn))
        # |Ve|
        if not isinstance(Ve, (int, float)):
            raise TypeError(('East velocity must be int or float: '
                             '|type(Ve)=%s|.') % type(Ve))
        # |Vn|
        if not isinstance(Vu, (int, float)):
            raise TypeError(('Vertical velocity must be int or float: '
                             '|type(Vu)=%s|.') % type(Vu))

        # Adapt
        # |in_place|
        (in_place, warn_place) = adapt_bool(in_place)
        # |warn|
        (warn, _) = adapt_bool(warn, True)

        # Warning
        if warn and warn_place:
            print('[WARNING] from method [remove_velocity] in [%s]' % __name__)
            print(('\t|in_place| parameter set to False because '
                   '|type(in_place)!=bool|!'))
            print('\tNew Gts %s is returned (and old one is not updated)!' 
                  % self.code)
            print()

        # Return
        return in_place, warn
    ###################################################

    # Check parameters
    (in_place, warn) = _check_param(self, Vn, Ve, Vu, in_place, warn)

    # Import
    import numpy as np

    # Create new data
    vel_neu = np.array([[Vn, Ve, Vu]])
    data = self.data.copy()
    data[:, :3] = self.data[:, :3] \
                  - np.dot(self.time[:, 0].reshape(-1, 1)-self.t0[0], vel_neu)

    # Create new ts
    ts = self.copy(data=data, data_xyz=False, data_neu=False)
    ts.velocity = vel_neu
    # data_xyz
    if self.data_xyz is not None:
        ts.dneu2xyz(corr=True, warn=warn)
    # data_neu
    if self.data_neu is not None:
        from itsa.lib.coordinates import xyz2geo
        E, N, U = xyz2geo(ts.data_xyz[:, 0],ts.data_xyz[:, 1],
                          ts.data_xyz[:, 2])
        ts.data_neu = np.c_[N, E, U]
        
    # Change reference coordinates
    idx_nonan = np.unique(np.where(~np.isnan(ts.data))[0])
    ts.change_ref(ts.time[idx_nonan[0], 1])

    # Change |self|
    if not in_place:
        return ts
    else:
        self.data = data
        self.velocity = vel_neu
        if self.data_xyz is not None:
            self.data_xyz = ts.data_xyz.copy()
        if self.data_neu is not None:
            self.data_neu = ts.data_neu.cipy()
        self.change_ref(ts.time[idx_nonan[0], 1])
