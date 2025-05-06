"""
    Check all Gts attributes, reorder attributes by increasing time and remove
    duplicated dates

    ----
    Developed at: ISTerre
    By: Lou MARILL
    Based on: PYACS module
"""


####################
def check_gts(self):
    """
    Check Gts object attributes

    Raises
    ------
    GtsTypeError
        If any |self| attribute does not have the right type.
    GtsValueError
        If any |self| attribute values do not have the right type.
        If |self.t0| values are not positive.
        If |self.outliers| values are negative or superior to
        |self.t0.shape[0]|.
    GtsDimensionError
        If any |self| attribute does not have the right dimensions.
    GtsError
        If there are no reference coordinates: |self.XYZ0| and |self.NEU0| are
        both None.
        
    See Also
    --------
    Gts class in [itsa.gts.Gts]

    """

    # Import
    import numpy as np
    from itsa.gts.errors import GtsTypeError, GtsDimensionError, GtsValueError
    
    # Mandatory attributes
    # |code|
    # str?
    if not isinstance(self.code, str):
        raise GtsTypeError('Gts |code| must be str: |type(self.code)=%s|.'
                           % type(self.code))
    # 4 letters?
    elif len(self.code) != 4:
        raise GtsValueError(('Gts |code| must have exactly 4 letters: '
                             '|len(self.code)=%d|.') % len(self.code))

    # |time|
    # np.ndarray?
    if not isinstance(self.time, np.ndarray):
        raise GtsTypeError(('Gts %s |time| must be np.ndarray: '
                            '|type(self.time)=%s|.')
                           % (self.code, type(self.time)))
    # enough data?
    if self.time.size < 2:
        raise GtsDimensionError(('Gts %s |time| must have at least 2 values '
                                 '(decimal year and modified Julian day): '
                                 '|self.time.size=%d|.')
                                % (self.code, self.time.size))
    # dimensions?
    if self.time.ndim == 1:
        self.time = self.time.reshape(1, -1)
    if self.time.ndim != 2:
        raise GtsDimensionError(('Gts %s |time| must be 2D np.ndarray: '
                                 '|self.time.ndim=%d|.')
                                % (self.code, self.time.ndim))
    # column number?
    if self.time.shape[1] != 2:
        raise GtsDimensionError(('Gts %s |time| must have exactly 2 columns '
                                 '(decimal years and modified Julian days): '
                                 '|self.time.shape[1]=%d|.')
                                % (self.code, self.time.shape[1]))
    # valid values?
    if self.time.dtype not in ['int', 'float']:
        raise GtsValueError(('Gts %s |time| must be int np.ndarray or '
                             'float np.ndarray: |self.time.dtype=%s|.')
                            % (self.code, self.time.dtype))
    # positive values?
    if (self.time < 0).any():
        raise GtsValueError('Gts %s |time| values must all be positive.'
                            % self.code)

    # |data|
    # np.ndarray?
    if not isinstance(self.data, np.ndarray):
        raise GtsTypeError(('Gts %s |data| must be np.ndarray: '
                            '|type(self.data)=%s|.')
                           % (self.code, type(self.data)))
    # enough data?
    if self.data.size < 9:
        raise GtsDimensionError(('Gts %s |data| must have at least 9 values '
                                 '(dN, dE, dU, Sn, Se, Su, Rne, Rnu and Reu): '
                                 '|self.data.size=%d|.')
                                % (self.code, self.data.size))
    # dimensions?
    if self.data.ndim == 1:
        self.data = self.data.reshape(1, -1)
    if self.data.ndim != 2:
        raise GtsDimensionError(('Gts %s |data| must be 2D np.ndarray: '
                                 '|self.data.ndim=%d|.')
                                % (self.code, self.data.ndim))
    # column number?
    if self.data.shape[1] != 9:
        raise GtsDimensionError(('Gts %s |data| must have exactly 9 columns '
                                 '(dN, dE, dU, Sn, Se, Su, Rne, Rnu and Reu): '
                                 '|self.data.shape[1]=%d|.')
                                % (self.code, self.data.shape[1]))
    # valid values?
    if self.data.dtype not in ['int', 'float']:
        raise GtsValueError(('Gts %s |data| must be int np.ndarray or float '
                             'np.ndarray: |self.data.dtype=%s|.')
                            % (self.code, self.data.dtype))

    # Consistency |time| and |data|
    # same length?
    if self.time.shape[0] != self.data.shape[0]:
        raise GtsDimensionError(('Gts %s |time| and |data| must have the same '
                                 'number of rows (|data| correspond to the '
                                 'coordinate data at the dates in |time|): '
                                 '|self.time.shape[0]=%d| and '
                                 '|self.data.shape[0]=%d|.')
                                % (self.code, self.time.shape[0],
                                   self.data.shape[0]))

    # Reference coordinates attributes
    # |t0|
    # np.ndarray?
    if not isinstance(self.t0, np.ndarray):
        raise GtsTypeError(('Gts %s |t0| must be 1D np.ndarray: '
                            '|type(self.t0)=%s|.')
                           % (self.code, type(self.t0)))
    # dimensions?
    if self.t0.ndim != 1:
        self.t0 = self.t0.reshape(-1)
    # value number?
    if self.t0.size != 2:
        raise GtsDimensionError(('Gts %s |t0| must have exactly 2 values '
                                 '(reference decimal year and modified Julian '
                                 'day): |self.t0.size=%d|.')
                                % (self.code, self.t0.size))
    # valid values?
    if self.t0.dtype not in ['int', 'float']:
        raise GtsValueError(('Gts %s |t0| must be int np.ndarray or float '
                             'np.ndarray: |self.t0.dtype=%s|.')
                            % (self.code, self.t0.dtype))
    # positive values?
    if (self.t0 < 0).any():
        raise GtsValueError(('Gts %s |t0| values must be positive: '
                             '|self.t0=%s|.') % (self.code, str(self.t0)))

    # |XYZ0|
    # np.ndarray?
    if not isinstance(self.XYZ0, np.ndarray):
        raise GtsTypeError(('Gts %s |XYZ0| must be np.ndarray: '
                            '|type(self.XYZ0)=%s|.')
                           % (self.code, type(self.XYZ0)))
    # dimensions?
    if self.XYZ0.ndim != 1:
        self.XYZ0 = self.XYZ0.reshape(-1)
    # value number?
    if self.XYZ0.size != 3:
        raise GtsDimensionError(('Gts %s |XYZ0| must have exactly 3 values '
                                 '(reference X, Y and Z): '
                                 '|self.XYZ0.size=%d|.')
                                % (self.code, self.XYZ0.size))
    # valid values?
    if self.XYZ0.dtype not in ['int', 'float']:
        raise GtsValueError(('Gts %s |XYZ0| must be int np.ndarray or float '
                             'np.ndarray: |self.XYZ0.dtype=%s|.')
                            % (self.code, self.XYZ0.dtype))

    # |NEU0|
    # np.ndarray?
    if not isinstance(self.NEU0, np.ndarray):
        raise GtsTypeError(('Gts %s |NEU0| must be np.ndarray: '
                            '|type(self.NEU0)=%s|.')
                           % (self.code, type(self.NEU0)))
    # dimensions?
    if self.NEU0.ndim != 1:
        self.NEU0 = self.NEU0.reshape(-1)
    # value number?
    if self.NEU0.size != 3:
        raise GtsDimensionError(('Gts %s |NEU0| must have exactly 3 values '
                                 '(reference N, E and U): '
                                 '|self.NEU0.size=%d|.')
                                % (self.code, self.NEU0.size))
    # valid values?
    if self.NEU0.dtype not in ['int', 'float']:
        raise GtsValueError(('Gts %s |NEU0| must be int np.ndarray or float '
                             'np.ndarray: |self.NEU0.dtype=%s|.')
                            % (self.code, self.NEU0.dtype))

    # |ref_frame|
    # str?
    if not isinstance(self.ref_frame, str):
        raise GtsTypeError(('Gts %s |ref_frame| must be str: '
                            '|type(self.ref_frame)=%s|.')
                           % (self.code, type(self.ref_frame)))

    # Optional attributes
    # |data_xyz|
    if self.data_xyz is not None:
        # np.ndarray?
        if not isinstance(self.data_xyz, np.ndarray):
            raise GtsTypeError(('Gts %s |data_xyz| must be None or np.ndarray:'
                                ' |type(self.data_xyz)=%s|.')
                               % (self.code, type(self.data_xyz)))
        # enough data?
        if self.data_xyz.size < 9:
            raise GtsDimensionError(('Gts %s |data_xyz| must be None or have '
                                     'at least 9 values (X, Y, Z, Sx, Sy, Sz, '
                                     'Rxy, Rxz and Ryz): '
                                     '|self.data_xyz.size=%d|.')
                                    % (self.code, self.data_xyz.size))
        # dimensions?
        if self.data_xyz.ndim == 1:
            self.data_xyz = self.data_xyz.reshape(1, -1)
        if self.data_xyz.ndim != 2:
            raise GtsDimensionError(('Gts %s |data_xyz| must be None or 2D '
                                     'np.ndarray: |self.data_xyz.ndim=%d|.')
                                    % (self.code, self.data_xyz.ndim))
        # column number?
        if self.data_xyz.shape[1] != 9:
            raise GtsDimensionError(('Gts %s |data_xyz| must be None or have '
                                     'exactly 9 columns (X, Y, Z, Sx, Sy, Sz, '
                                     'Rxy, Rxz and Ryz): '
                                     '|self.data_xyz.shape[1]=%d|.')
                                    % (self.code, self.data_xyz.shape[1]))
        # same length than |time|?
        if self.time.shape[0] != self.data_xyz.shape[0]:
            raise GtsDimensionError(('Gts %s |data_xyz| must be None or |time|'
                                     ' and |data_xyz| must have the same row '
                                     'number (|data_xyz| correspond to the '
                                     'coordinate data at the dates in |time|):'
                                     ' |self.time.shape[0]=%d| and '
                                     '|self.data_xyz.shape[0]=%d|.')
                                    % (self.code, self.time.shape[0],
                                       self.data_xyz.shape[0]))
        # valid values?
        if self.data_xyz.dtype not in ['int', 'float']:
            raise GtsValueError(('Gts %s |data_xyz| must be None, int '
                                 'np.ndarray or float np.ndarray: '
                                 '|self.data_xyz.dtype=%s|.')
                                 % (self.code, self.data_xyz.dtype))

    # |data_neu|
    if self.data_neu is not None:
        # np.ndarray?
        if not isinstance(self.data_neu, np.ndarray):
            raise GtsTypeError(('Gts %s |data_neu| must be None or np.ndarray:'
                                ' |type(self.data_neu)=%s|.')
                               % (self.code, type(self.data_neu)))
        # enough data?
        if self.data_neu.size < 3:
            raise GtsDimensionError(('Gts %s |data_neu| must be None or have '
                                     'at least 3 values (N, E and U): '
                                     '|self.data_neu.size=%d|.')
                                    % (self.code, self.data_neu.size))
        # dimensions?
        if self.data_neu.ndim == 1:
            self.data_neu = self.data_neu.reshape(1, -1)
        if self.data_neu.ndim != 2:
            raise GtsDimensionError(('Gts %s |data_neu| must be None or 2D '
                                     'np.ndarray: |self.data_neu.ndim=%d|.')
                                    % (self.code, self.data_neu.ndim))
        # column number?
        if self.data_neu.shape[1] != 3:
            raise GtsDimensionError(('Gts %s |data_neu| must be None or have '
                                     'exactly 3 columns (N, E and U): '
                                     '|self.data_neu.shape[1]=%d|.')
                                    % (self.code, self.data_neu.shape[1]))
        # same length than |time|?
        if self.time.shape[0] != self.data_neu.shape[0]:
            raise GtsDimensionError(('Gts %s |data_neu| must be None or |time|'
                                     ' and |data_neu| must have the same row '
                                     'number (|data_neu| correspond to the '
                                     'coordinate data at the dates in |time|):'
                                     ' |self.time.shape[0]=%d| and '
                                     '|self.data_neu.shape[0]=%d|.')
                                    % (self.code, self.time.shape[0],
                                       self.data_neu.shape[0]))
        # valid values?
        if self.data_neu.dtype not in ['int', 'float']:
            raise GtsValueError(('Gts %s |data_neu| must be None, int '
                                 'np.ndarray or float np.ndarray: '
                                 '|self.data_neu.dtype=%s|.')
                                % (self.code, self.data_neu.dtype))

    # Metadata attribute
    # |in_file|
    # str?
    if not isinstance(self.in_file, str):
        raise GtsTypeError(('Gts %s |in_file| must be str: '
                            '|type(self.in_file)=%s|.')
                           % (self.code, type(self.in_file)))
    # |process|
    # str?
    if not isinstance(self.process, str):
        raise GtsTypeError(('Gts %s |process| must be str: '
                            '|type(self.process)=%s|.')
                           % (self.code, type(self.process)))

    # Analysis attributes
    # |outliers|
    if self.outliers is not None:
        # np.array?
        if not isinstance(self.outliers, np.ndarray):
            raise GtsTypeError(('Gts %s |outliers| must be None or '
                                'np.ndarray: |type(self.outliers)=%s|.')
                               % (self.code, type(self.outliers)))
        # dimensions?
        self.outliers = self.outliers.reshape(-1)
        # int values?
        if self.outliers.dtype not in ['int', 'int64']:
            raise GtsValueError(('Gts %s |outliers| must be None or int '
                                 'np.ndarray: |self.outliers.dtype=%s|.')
                                % (self.code, self.outliers.dtype))
        # valid values?
        out_outliers = []
        for k in range(self.outliers.shape[0]):
            if self.outliers[k] not in range(self.time.shape[0]):
                out_outliers.append(k)
        if len(out_outliers) > 0:
            raise GtsValueError(('Gts %s |outliers| must be None or all '
                                 'values must be positive less than %d: '
                                 '|self.outliers[%s]=array(%s)|.')
                                % (self.code, self.time.shape[0], out_outliers,
                                   list(self.outliers[out_outliers])))

    # |velocity|
    if self.velocity is not None:
        # np.ndarray?
        if not isinstance(self.velocity, np.ndarray):
            raise GtsTypeError(('Gts %s |velocity| must be None or '
                                'np.ndarray: |type(self.velocity)=%s|.')
                               % (self.code, type(self.velocity)))
        # dimensions?
        if self.velocity.size != 3:
            raise GtsDimensionError(('Gts %s |velocity| must be None or have '
                                     'exactly 3 values (Vx, Vy and Vz): '
                                     '|self.velocity.size=%d|.')
                                    % (self.code, self.velocity.size))
        self.velocity = self.velocity.reshape(3)
        # valid values?
        if self.velocity.dtype not in ['int', 'float']:
            raise GtsValueError(('Gts %s |velocity| must be None, int '
                                 'np.ndarray or float np.ndarray: '
                                 '|self.velocity.dtype=%s|.')
                                % (self.code, self.velocity.dtype))
        
    # |jps|
    if self.jps is None:
        from itsa.jps.Jps import Jps
        self.jps = Jps(self.code)
    self.jps.check_jps()
        
    # |G|
    # initialised?
    if self.G is None:
        self.G = np.array([]).reshape(self.time.shape[0], 0)
        self.MOD = np.array([]).reshape(0, 6)
        self.GMOD_names = None
    # np.ndarray?
    if not isinstance(self.G, np.ndarray):
            raise GtsTypeError(('Gts %s |G| must be np.ndarray: '
                                '|type(self.G)=%s|.')
                               % (self.code, type(self.G)))
    # dimensions?
    if self.G.ndim != 2:
        raise GtsDimensionError(('Gts %s |G| must be 2D np.ndarray: '
                                 '|self.G.ndim=%d|.')
                                % (self.code, self.G.ndim))
    # same length than |time|?
    if self.time.shape[0] != self.G.shape[0]:
        raise GtsDimensionError(("Gts %s |G| and |time| must have the same "
                                 "number of rows (|G| correspond to the "
                                 "Green's functions at the dates in |time|): "
                                 "|self.time.shape[0]=%d| and "
                                 "|self.G.shape[0]=%d|.") 
                                % (self.code, self.time.shape[0],
                                   self.G.shape[0]))
    # valid values?
    if self.G.dtype not in ['int', 'float']:
        raise GtsValueError(('Gts %s |G| must be int np.ndarray or float '
                             'np.ndarray: |self.G.dtype=%s|.')
                            % (self.code, self.G.dtype))
        
    # |MOD|
    # np.ndarray?
    if not isinstance(self.MOD, np.ndarray):
        raise GtsTypeError(('Gts %s |MOD| must be np.ndarray: '
                            '|type(self.MOD)=%s|.')
                           % (self.code, type(self.MOD)))
    # dimensions?
    if self.MOD.ndim != 2:
        raise GtsDimensionError(('Gts %s |MOD| must be 2D np.ndarray: '
                                 '|self.MOD.ndim=%d|.')
                                % (self.code, self.MOD.ndim))
    # number of columns?
    if self.MOD.shape[1] != 6:
        raise GtsDimensionError(('Gts %s |MOD| must be np.ndarray with '
                                 'exactly 6 columns (N, E, U, err_N, err_E, '
                                 'err_U): |self.MOD.shape[1]=%d|.')
                                % (self.code, self.MOD.shape[1]))
    # number of rows?
    if self.MOD.shape[0] != self.G.shape[1]:
        raise GtsDimensionError(('Gts %s |MOD| must have the same number of '
                                 'rows than |G| number of columns (to allow '
                                 'matrix multiplication): '
                                 '|self.G.shape[1]=%d| and '
                                 '|self.MOD.shape[0]=%d|.')
                                % (self.code, self.G.shape[1],
                                   self.MOD.shape[0]))
    # valid values?
    if self.MOD.dtype not in ['int', 'float']:
        raise GtsValueError(('Gts %s |MOD| must be int np.ndarray or float '
                             'np.ndarray: |self.MOD.dtype=%s|.')
                            % (self.code, self.MOD.dtype))
        
    # |GMOD_names|
    if self.GMOD_names is not None:
        # np.ndarray?
        if not isinstance(self.GMOD_names, np.ndarray):
            raise GtsTypeError(('Gts %s |GMOD_names| must be np.ndarray: '
                                '|type(self.GMOD_names)=%s|.') 
                               % (self.code, type(self.GMOD_names)))
        # dimension?
        if self.GMOD_names.ndim != 1:
            raise GtsDimensionError(('Gts %s |GMOD_names| must be 1D '
                                     'np.ndarray: |self.GMID_names.ndim=%d|.')
                                    % (self.code, self.GMOD_names.ndim))
        # number of values?
        if self.GMOD_names.shape[0] != self.G.shape[1]:
            raise GtsDimensionError(('Gts %s |GMOD_names| must have the same '
                                     'number of values than the number of '
                                     'column of |G| (as |GMOD_names| '
                                     'correspond to the names of the columns):'
                                     ' |self.GMOD_names.shape[0]=%d| and '
                                     '|self.G.shape[1]=%d|.')
                                    % (self.code, self.GMOD_names.shape[0],
                                       self.G.shape[1]))
        # valid values?
        if (self.GMOD_names.size > 0 and self.GMOD_names.dtype != 'str'
            and 'U' not in str(self.GMOD_names.dtype)):
            raise GtsValueError(('Gts %s |GMOD_names| must be str np.ndarray: '
                                 '|self.GMOD_names.dtype=%s|.')
                                % (self.code, self.GMOD_names.dtype))
                                        
            
##################
def reorder(self):
    """
    Reorder Gts |time|, |data|, |data_xyz|, |data_neu| and |outliers| (if not
    None) by increasing time

    """

    # Check parameter
    self.check_gts()

    # Import
    import numpy as np
    from itsa.lib.index_dates import get_index_from_dates

    # Reorder required?
    if self.time.shape[0] > 1:
        diff = np.diff(self.time[:, 1])
        if np.min(diff) >= 0:
            return

        # Save outliers dates
        if self.outliers is not None:
            out_dates = self.time[self.outliers, 1]

        # Reorder
        sort_index = np.argsort(self.time[:, 1])
        self.select_data(sort_index, in_place=True)

        # Deal with outliers
        if self.outliers is not None:
            new_out = get_index_from_dates(self.time[:, 1], out_dates)
            self.outliers = new_out


#############################################
def remove_duplicated_dates(self, warn=True):
    """
    Remove duplicated dates from Gts

    Parameter
    ---------
    warn : bool, optional
        Print warning if true.
        The default is True.
        
    Raise
    -----
    WARNING
        If duplicated dates are removed.

    """

    # Import
    import numpy as np
    from itsa.lib.modif_vartype import adapt_bool
    from itsa.lib.index_dates import get_index_from_dates

    # Check and order by increasing time
    self.reorder()
    (warn, _) = adapt_bool(warn, True)

    # Duplicated dates?
    if self.time.shape[0] > 1:
        diff = np.diff(self.time[:, 1].astype(int))
        dupl_index = np.where(diff == 0)[0]
        if dupl_index.size == 0:
            return
        elif warn:
            print('[WARNING] from method [remove_duplicated_dates] in [%s]'
                  % __name__)
            print('\tDuplicated date found and removed!')
            print(('\tFor each duplicated date only the last associated '
                   'coordinates are kept!'))
            print()

        # Save outliers dates
        if self.outliers is not None:
            out_dates = self.time[self.outliers, 1]

        # Remove duplicated dates
        mask_dupl = np.ones(self.time.shape[0], dtype=bool)
        mask_dupl[dupl_index] = False
        self.select_data(mask_dupl, in_place=True)

        # Deal with outliers
        if self.outliers is not None:
            new_out = get_index_from_dates(self.time[:, 1], out_dates)
            self.outliers = new_out
    
