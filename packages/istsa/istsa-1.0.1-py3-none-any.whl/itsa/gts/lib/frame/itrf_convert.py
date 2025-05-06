"""
    Developed at: ISTerre
    By: Lou MARILL
"""

#%%###################
## GLOBAL VARIABLES ##
######################

import numpy as np

# From ITRF website: https://itrf.ign.fr/en/solutions/transformations
_itrf_possible = ['88', '89', '90', '91', '92', '93', '94','96', '97',
                  '2000', '2005', '2008', '2014', '2020']

_itrf_trans = {}
_itrf_trans['2014'] = {'2000': np.array([[-0.7, -1.2, 26.1, -2.12,
                                          0.00, 0.00, 0.00, 2010.0],
                                         [-0.1, -0.1,  1.9, -0.11,
                                          0.00, 0.00, 0.00, np.nan]]),
                       '2005': np.array([[-2.6, -1.0,  2.3, -0.92,
                                          0.00, 0.00, 0.00, 2010.0],
                                         [-0.3,  0.0,  0.1, -0.03,
                                          0.00, 0.00, 0.00, np.nan]]),
                       '2008': np.array([[-1.6, -1.9, -2.4,  0.02,
                                          0.00, 0.00, 0.00, 2010.0],
                                         [+0.0,  0.0,  0.1, -0.03,
                                          0.00, 0.00, 0.00, np.nan]])}

_itrf_trans['2020'] = {'2000': np.array([[+0.2, -0.8, 34.2, -2.25,
                                          0.00, 0.00, 0.00, 2015.0],
                                         [-0.1,  0.0,  1.7, -0.11,
                                          0.00, 0.00, 0.00, np.nan]]),
                       '2005': np.array([[-2.7, -0.1,  1.4, -0.65,
                                          0.00, 0.00, 0.00, 2015.0],
                                         [-0.3,  0.1, -0.1, -0.03,
                                          0.00, 0.00, 0.00, np.nan]]),
                       '2008': np.array([[-0.2, -1.0, -3.3,  0.29,
                                          0.00, 0.00, 0.00, 2015.0],
                                         [+0.0,  0.1, -0.1, -0.03,
                                          0.00, 0.00, 0.00, np.nan]]),
                       '2014': np.array([[+1.4,  0.9, -1.4,  0.42,
                                          0.00, 0.00, 0.00, 2015.0],
                                         [+0.0,  0.1, -0.2,  0.00,
                                          0.00, 0.00, 0.00, np.nan]])}


#%%##########
## METHODS ##
#############

#######################################################################
def itrf_convert(self, itrf_end='ITRF2014', in_place=False, warn=True):
    """
    Convert Gts reference frame from IGS or ITRF to another IGS or ITRF

    Parameters
    ----------
    itrf_end : str, optional
        Final ITRF/IGS reference frame.
        The default is 'ITRF2014'.
    in_place : bool, optional
        Change data directly in |self| if true.
        The default is False: create and return new Gts 
                              (|self| is not updated).
    warn : bool, optional
        Print warning if true.
        The default is True.

    Raises
    ------
    GtsValueError
        If |self.ref_frame| does not start by 'IGS' nor 'ITRF'.   
    TypeError
        If any parameter does not have the right type.
    ValueError
        If |itrf_end| does not start by 'IGS' nor 'ITRF'.
    KeyError
        If the conversion is not defined in GLOBAL VARIABLES.
    WARNING
        If |in_place| is not bool: |in_place| set to False.

    Return
    ------
    Gts
        Only if |in_place| is false.
        New Gts with data in |itrf_end| reference frame.

    """

    ##############################################
    def _check_param(self, itrf_end, in_place, warn):
        """
        Raise error if one parameter is invalid and adapt some parameter values
        """
        # Import
        from itsa.gts.errors import GtsValueError
        from itsa.lib.modif_vartype import adapt_bool

        # Check
        # |self|
        self.check_gts()
        # |self.ref_frame|
        if (self.ref_frame[:3].upper() != 'IGS' and 
            self.ref_frame[:4].upper() != 'ITRF'):
            raise GtsValueError(("Gts %s reference frame must be 'IGS' or "
                                 "'ITRF': |ref_frame='%s'|.")
                                % (self.code, self.ref_frame))
        # |itrf_end|
        if not isinstance(itrf_end, str):
            raise TypeError('Final frame must be str: |type(itrf_end)=%s|.'
                            % type(itrf_end))
        if itrf_end[:3].upper() != 'IGS' and itrf_end[:4].upper() != 'ITRF':
            raise ValueError(("Final frame must be IGS or ITRF and begin with "
                              "'IGS' or 'ITRF': |itrf_end|='%s'|.") % itrf_end)

        # Adapt
        # |self.data_xyz|
        if self.data_xyz is None:
            self.dneu2xyz(corr=True, warn=warn)
        # |in_place|
        (in_place, warn_place) = adapt_bool(in_place)
        # |warn|
        (warn, _) = adapt_bool(warn, True)

        # Warning
        if warn and warn_place:
            print('[WARNING] from method [itrf_convert] in [%s]' % __name__)
            print(('\t|in_place| parameter set to False because '
                   '|type(in_place)!=bool|!'))
            print('\tNew Gts %s is returned (and the old one is not updated)!'
                  % self.code)
            print()

        # Return
        return in_place, warn
    ##############################################

    # Check parameters
    (in_place, warn) = _check_param(self, itrf_end, in_place, warn)

    # Import
    import numpy as np

    # Year of the reference frames
    year_ini = _itrf_year(self.ref_frame)
    year_end = _itrf_year(itrf_end)

    # Test if initial and final reference frames are the same
    if year_ini == year_end:
        if not in_place:
            ts = self.copy()
            ts.ref_frame = itrf_end
            return ts
        else:
            self.ref_frame = itrf_end
            return

    # Look if value in program
    else:
        if int(year_end) > int(year_ini):
            year1, year2 = year_end, year_ini
        else:
            year1, year2 = year_ini, year_end

        if (year1 not in list(_itrf_trans.keys()) or 
            year2 not in list(_itrf_trans[year1].keys())):
            raise KeyError('Link between %s and %s not defined'
                           % (self.ref_frame, itrf_end))
        else:
            # Transpose coordinates
            # Read parameters
            (tx, ty, tz, d, rx, ry, rz, Epoch) = _itrf_trans[year1][year2].T
            if int(year_ini) > int(year_end):
                tx, ty, tz, d, rx, ry, rz = -tx, -ty, -tz, -d, -rx, -ry, -rz
            # Parameter over time
            def pot(p): return p[0]+p[1]*(self.time[:, 0]-Epoch[0])
            Tx = pot(tx)*1e-3
            Ty = pot(ty)*1e-3
            Tz = pot(tz)*1e-3
            D = pot(d)*1e-9
            Rx = np.radians(pot(rx)*3.6e-6)
            Ry = np.radians(pot(ry)*3.6e-6)
            Rz = np.radians(pot(rz)*3.6e-6)
            # Transpose
            if self.data_xyz is None:
                self.dneu2xyz(corr=True, warn=warn)
            data_xyz = self.data_xyz.copy()
            data_xyz[:, :3] = np.zeros(data_xyz[:, :3].shape)
            for k in range(self.data_xyz.shape[0]):
                T = np.array([Tx[k], Ty[k], Tz[k]])
                R = np.array([[+D[k], -Rz[k], Ry[k]],
                              [+Rz[k], D[k], -Rx[k]],
                              [-Ry[k], Rx[k], D[k]]])
                data_xyz[k, :3] = self.data_xyz[k, :3]+T+R@self.data_xyz[k, :3]

            # Create new Gts
            ts = self.copy(data=False, data_xyz=data_xyz, data_neu=False)
            ts.xyz2dneu()
            ts.data[:, 3:] = self.data[:, 3:]
            ts.ref_frame = itrf_end
            if self.data_neu is not None:
                from itsa.lib.coordinates import xyz2geo
                (E, N, U) = xyz2geo(ts.data_xyz[:, 0], ts.data_xyz[:, 1],
                                    ts.data_xyz[:, 2])
                data_neu = np.c_[N, E, U]
                ts.data_neu = data_neu
            else:
                data_neu = None
                
            # Change reference coordinates
            idx_nonan = np.unique(np.where(~np.isnan(ts.data))[0])
            ts.change_ref(ts.time[idx_nonan[0], 1])

    # Return
    if not in_place:
        return ts
    else:
        self.data = ts.data.copy()
        if ts.data_xyz is not None:
            self.data_xyz = ts.data_xyz.copy()
        self.ref_frame = itrf_end
        if ts.data_neu is not None:
            self.data_neu = ts.data_neu.copy()
        self.t0 = ts.t0.copy()
        self.XYZ0 = ts.XYZ0.copy()
        self.NEU0 = ts.NEU0.copy()


##########################
def _itrf_year(ref_frame):
    """
    Read the year of the ITRF or IGS reference frame

    Parameter
    ---------
    ref_frame : str
        Name of the reference frame.

    Raise
    -----
    ValueError
        If |ref_frame| does not exist in GLOBAL VARIABLE.

    Return
    ------
    year : str
        Year of the reference frame.

    """

    # Read year
    if ref_frame[:3].upper() == 'IGS':
        year = ref_frame[3:]
    else:
        year = ref_frame[4:]

    # Convert years in 0Y/1Y/2Y format to 20YY
    if year in ["00", "05", "08", "14", "20"]:
        year = f"20{year}"

    # Verify year
    if year not in _itrf_possible:
        raise ValueError(ref_frame
                         + (' reference frame unkown.\n'
                            'Existing years for ITRF: ')
                         + str(_itrf_possible))

    # Return
    return year
