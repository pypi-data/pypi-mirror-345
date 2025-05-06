"""
    Populate dN, dE and dU or XYZ from XYZ or dN, dE and dU

    ---
    Developed at: ISTerre
    By: Lou MARILL
    Based on: PYACS module
"""


##########################################
def xyz2dneu(self, corr=False, warn=True):
    """
    Populate dN, dE, dU (|data|) using XYZ (|data_xyz|)
    |XYZ0| and |NEU0| will also be set

    Parameters
    ----------
    corr : bool, optional
        Compute NEU STD and CORR (and populate |data|) if true.
        The default is False.
    warn : bool, optional
        Print warning if true.
        The default is True.
        
    Raise
    -----
    WARNING
        If |corr| is not bool: |corr| set to False.
        If NEU STD and CORR are set to np.nan: XYZ STD and CORR are not
                                               computed

    """

    ###################################
    def _check_param(self, corr, warn):
        """
        Raise error if one parameter is invalid and adapt some parameter values
        """
        # Import
        from itsa.lib.modif_vartype import adapt_bool

        # Check
        # |self|
        self.data = self.data_xyz  # check_gts need |self.data!=None|
        # Error from |self.data| come from error in |self.data_xyz|
        self.check_gts()

        # Adapt
        # |corr|
        (corr, warn_corr) = adapt_bool(corr)
        # |warn|
        (warn, _) = adapt_bool(warn, True)

        # Warning
        if warn and warn_corr:
            print('[WARNING] from method [xyz2dneu] in [%s]' % __name__)
            print(('\t|corr| parameter set to False because '
                   '|type(corr)!=bool|!'))
            print(('\tGts %s NEU STD and CORR are not computed (and set to '
                   'np.nan)!') % self.code)
            print()

        # Return
        return corr
    ###################################

    # Check parameters
    corr = _check_param(self, corr, warn)

    # Import
    import numpy as np
    from itsa.lib.coordinates import xyz2geo, mat_rot_general_to_local
    import warnings
    warnings.filterwarnings("error")

    # Compute rotation matrix
    (lon, lat, _) = xyz2geo(self.XYZ0[0], self.XYZ0[1], self.XYZ0[2])
    R = mat_rot_general_to_local(lon, lat)

    # Compute and populate dN, dE, dU coordinates
    # DXYZ
    DXYZ = self.data_xyz[:, :3]-self.XYZ0
    # DENU
    DENU = np.dot(R, DXYZ.T).T
    # Populate
    self.data = np.zeros(self.data_xyz.shape)*np.nan
    self.data[:, :3] = DENU[:, [1, 0, 2]]*1e3

    # Compute and populate NEU STD and CORR
    if corr:
        if not np.isnan(self.data_xyz[:, 3:]).all():
            # Import
            from itsa.lib.Glinalg import corr2cov, cov2corr

            for k in np.arange(self.data_xyz.shape[0]):
                # Read STD and CORR values for XYZ
                (_, _, _, Sx, Sy, Sz, Rxy, Rxz, Ryz) = self.data_xyz[k, :]
                # Create STD and CORR matrix for XYZ
                STD_XYZ = np.array([Sx, Sy, Sz])
                CORR_XYZ = np.array([[+1,  Rxy, Rxz],
                                     [Rxy,  1,  Ryz],
                                     [Rxz, Ryz, 1]])
                try:
                    # Compute COV for XYZ and ENU
                    COV_XYZ = corr2cov(CORR_XYZ, STD_XYZ)
                    COV_ENU = np.dot(np.dot(R, COV_XYZ), R.T)
                    # Compute CORR and STD for ENU
                    (CORR_ENU, STD_ENU) = cov2corr(COV_ENU)
                except:
                    pass
                else:
                    # Populate
                    self.data[k, 3:6] = STD_ENU[[1, 0, 2]]
                    self.data[k, 6:9] = CORR_ENU[[0, 1, 0], [1, 2, 2]]


##########################################
def dneu2xyz(self, corr=False, warn=True):
    """
    Populate XYZ (|data_xyz|) using dN, dE, dU (|data|)
    Require |XYZ0| to be set (|NEU0| will also be set)

    Parameters
    ----------
    corr : bool, optional
        Compute XYZ STD and CORR (and populate |data_xyz|) if true.
        The default is False.
    warn : bool, optional
        Print warning if true.
        The default is True.
    
    Raise
    -----
    WARNING
        If |corr| is not bool: |corr| set to False.
        If NEU STD and CORR are set to np.nan: XYZ STD and CORR are not
                                               computed

    """

    ###################################
    def _check_param(self, corr, warn):
        """
        Raise error if one parameter is invalid and adapt some parameter values
        """
        # Import
        from itsa.lib.modif_vartype import adapt_bool

        # Check
        # |self|
        self.check_gts()

        # Adapt
        # |corr|
        (corr, warn_corr) = adapt_bool(corr)
        # |warn|
        (warn, _) = adapt_bool(warn, True)

        # Warning
        if warn and warn_corr:
            print('[WARNING] from method [dneu2xyz] in [%s]' % __name__)
            print(('\t|corr| parameter set to False because '
                   '|type(corr)!=bool|!'))
            print(('\tGts %s XYZ STD and CORR are not computed (and set to '
                   'np.nan)!') % self.code)
            print()

        # Return
        return corr
    ###################################

    # Check parameters
    corr = _check_param(self, corr, warn)

    # Import
    import numpy as np
    from itsa.lib.coordinates import xyz2geo, mat_rot_local_to_general
    import warnings
    warnings.filterwarnings("error")

    # Compute rotation matrix
    (lon, lat, _) = xyz2geo(self.XYZ0[0], self.XYZ0[1], self.XYZ0[2])
    R = mat_rot_local_to_general(lon, lat)

    # Compute and populate XYZ coordinates
    # DENU
    DENU = np.copy(self.data[:, [1, 0, 2]]*1e-3)
    # DXYZ
    DXYZ = np.dot(R, DENU.T).T
    # Populate
    self.data_xyz = np.zeros(self.data.shape)*np.nan
    self.data_xyz[:, :3] = DXYZ+self.XYZ0

    # Compute and populate XYZ STD and CORR if asked
    if corr and not np.isnan(self.data[:, 3:]).all():
        # Import
        from itsa.lib.Glinalg import corr2cov, cov2corr

        for k in np.arange(self.data.shape[0]):
            # Read STD and CORR values for ENU
            (_, _, _, Sn, Se, Su, Rne, Rnu, Reu) = self.data[k, :]
            # Create STD and CORR matrix for ENU
            STD_ENU = np.array([Se, Sn, Su])
            CORR_ENU = np.array([[+1,  Rne, Reu],
                                 [Rne,  1,  Rnu],
                                 [Reu, Rnu, 1]])
            try:
                # Compute COV for ENU
                COV_ENU = corr2cov(CORR_ENU, STD_ENU)
                # Compute COV for XYZ
                COV_XYZ = np.dot(np.dot(R, COV_ENU), R.T)
                # Compute CORR and STD for XYZ
                (CORR_XYZ, STD_XYZ) = cov2corr(COV_XYZ)
            except:
                pass
            else:
                # Populate
                self.data_xyz[k, 3:6] = STD_XYZ
                self.data_xyz[k, 6:9] = CORR_XYZ[[0, 0, 1], [1, 2, 2]]
    
            
#############################
def change_ref(self, new_t0):
    """
    Change reference time and coordinates of given Gts

    Parameters
    ----------
    new_t0 : int or float
        Date of the new reference time, in modified julian day.

    Raises
    ------
    TypeError
        If |new_t0| has not the right type.
    ValueError
        If |new_t0| is not positive nor 0.
    GtsError
        If there is not data at the time |new_t0| in |self|.

    """
    
    ###############################
    def _check_param(self, new_t0):
        """
        Raise error if one parameter is invalid
        """
        # Import
        from itsa.lib.modif_vartype import nptype2pytype
        
        # Change type
        # |new_t0|
        new_t0 = nptype2pytype(new_t0)
        
        # Check
        # |self|
        self.check_gts()
        # |new_t0|
        if not isinstance(new_t0, (int, float)):
            raise TypeError('New t0 must be int or float: |type(new_t0)=%s|.'
                             % type(new_t0))
        if new_t0 < 0:
            raise ValueError('New t0 must be positive or 0: |new_t0=%g|.'
                             % new_t0)
    ###############################
    
    # Check parameters
    _check_param(self, new_t0)
    
    # Import
    import numpy as np
    from itsa.lib.index_dates import get_index_from_dates
    from itsa.gts.errors import GtsError
    
    # Find index of |new_t0|
    idx_t0 = get_index_from_dates(self.time[:, 1], new_t0)
    
    # Test if t0 is whithin |self.time|
    if idx_t0 < 0:
        raise GtsError('Gts %s has no data at |t0=%g|' % (self.code, self.t0))
    
    # Change |self.t0|
    if self.t0[1] != self.time[idx_t0, 1]:
        self.t0 = self.time[idx_t0, :]
        
        # Test if there is data at t0
        if np.isnan(self.data[idx_t0, :3]).any():
            raise GtsError('Gts %s has no data at |t0=%g|' % (self.code,
                                                              self.t0))
        
        # Change |self.XYZ0|
        if self.data_xyz is None:
            self.dneu2xyz(corr=True)
        self.XYZ0 = self.data_xyz[idx_t0, :3].reshape(-1)
        
        # Change |self.NEU0|
        if self.data_neu is not None:
            self.NEU0 = self.data_neu[idx_t0, :]
        else:      
            from itsa.lib.coordinates import xyz2geo
            (E0, N0, U0) = xyz2geo(self.XYZ0[0], self.XYZ0[1], self.XYZ0[2])
            self.NEU0 = np.array([N0, E0, U0])
        
        # Change |self.data|
        self.xyz2dneu(corr=True)
    
