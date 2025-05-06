"""
    Check all Jps attributes, reorder attributes by increasing time and remove
    duplicated dates

    ----
    Developed at: ISTerre
    By: Lou MARILL
"""


####################
def check_jps(self):
    """
    Check Jps object attributes

    Raises
    ------
    JpsTypeError
        If any |self| attribute does not have the right type.
    JpsDimensionError
        If any |self| attribute does not have the right dimensions.
    JpsValueError
        If any |self| attribute values do not have the right type.
        If |self.code| does not have exactly 4 letters.
        If |self.dates| or |self.dur| values are not positives.
    JpsError
        If the number of rows is not the same for all attribute.

    See Also
    --------
    Jps class in [itsa.jps.Jps]

    """
    
    # Import
    import numpy as np
    from itsa.jps.errors import JpsError, JpsTypeError, JpsDimensionError
    from itsa.jps.errors import JpsValueError
    
    # |code|
    # str?
    if not isinstance(self.code, str):
        raise JpsTypeError('Jps |code| must be str: |type(self.code)=%s|.'
                           % type(self.code))
    # 4 letters?
    elif len(self.code) != 4:
        raise JpsValueError(('Jps |code| must have exactly 4 letters: '
                             '|len(self.code)=%d|.') % len(self.code))
    
    # |dates|
    # np.ndarray?
    if not isinstance(self.dates, np.ndarray):
        raise JpsTypeError(('Jps %s |dates| must be np.ndarray: '
                            '|type(self.dates)=%s|.')
                           % (self.code, type(self.dates)))
    # enough data?
    if self.dates.size == 1:
        raise JpsDimensionError(('Jps %s |dates| must be empty or have at '
                                 'least 2 values (decimal year and modified '
                                 'Julian day): |self.dates.size=1|.')
                                % self.code)
    # dimension?
    if self.dates.ndim == 1:
        self.dates = self.dates.reshape(1, -1)
    if self.dates.ndim != 2:
        raise JpsDimensionError(('Jps %s |dates| must be 2D np.ndarray: '
                                 '|self.dates.ndim=%d|.')
                                % (self.code, self.dates.ndim))
    # column number?
    if self.dates.shape[1] != 2:
        raise JpsDimensionError(('Jps %s |dates| must have exactly 2 columns '
                                 '(decimal years and modified Julian days): '
                                 '|self.dates.shape[1]=%d|.')
                                % (self.code, self.dates.shape[1]))
    # valid values?
    if self.dates.dtype not in ['int','float']:
        raise JpsValueError(('Jps %s |dates| values must be int or float: '
                             '|self.dates.dtype=%s|.')
                            % (self.code, self.dates.dtype))
    # positive values?
    if (self.dates < 0).any():
        raise JpsValueError('Jps %s |dates| values must all be positive.'
                            % self.code)
    
    # |type_ev|
    # np.ndarray?
    if not isinstance(self.type_ev, np.ndarray):
        raise JpsTypeError(('Jps %s |type_ev| must be np.ndarray: '
                            '|type(self.type_ev)=%s|.')
                           % (self.code, type(self.type_ev)))
    # dimension?
    if self.type_ev.ndim != 1:
        raise JpsDimensionError(('Jps %s |type_ev| must be 1D np.ndarray: '
                                 '|self.type_ev.ndim=%d|.')
                                % (self.code, self.type_ev.ndim))
    # valid values?
    if (self.type_ev.size > 0 and
        self.type_ev.dtype != 'str' and 'U' not in str(self.type_ev.dtype)):
        raise JpsValueError(('Jps %s |type_ev| values must be str: '
                             '|self.type_ev.dtype=%s|.')
                            % (self.code, self.type_ev.dtype))
    # row number?
    if self.type_ev.shape[0] != self.dates.shape[0]:
        raise JpsError(('Jps %s |dates| and |type_ev| must have the same '
                        'number of rows (|type_ev| correspond to the type of '
                        'the event occuring at |dates|): '
                        '|self.dates.shape[0]=%d| and '
                        '|self.type_ev.shape[0]=%d|.')
                       % (self.code, self.dates.shape[0],
                          self.type_ev.shape[0]))
     
    # |coords|
    # np.ndarray?
    if not isinstance(self.coords, np.ndarray):
        raise JpsTypeError(('Jps %s |coords| must be np.ndarray: '
                            '|type(self.coords)=%s|.')
                           % (self.code, type(self.coords)))
    # enough data?
    if self.coords.size > 0 and self.coords.size < 3:
        raise JpsDimensionError(('Jps %s |coords| must be empty or have at '
                                 'least 3 values (latitude, longitude and '
                                 'depth): |self.coords.size=%d|.')
                                % (self.code, self.coords.size))
    # dimension?
    if self.coords.ndim == 1:
        self.coords = self.coords.reshape(1, -1)
    if self.coords.ndim != 2:
        raise JpsDimensionError(('Jps %s |coords| must be 2D np.ndarray: '
                                 '|self.coords.ndim=%d|.')
                                % (self.code, self.coords.ndim))
    # column number?
    if self.coords.shape[1] != 3:
        raise JpsDimensionError(('Jps %s |coords| must have exactly 3 columns '
                                 '(latitude, longitude and depth): '
                                 '|self.coords.shape[1]=%d|.')
                                % (self.code, self.coords.shape[1]))
    # valid values?
    if self.coords.dtype not in ['int','float']:
        raise JpsValueError(('Jps %s |coords| values must be int or float '
                             'np.ndarray: |self.coords.dtype=%s|.')
                            % (self.code, self.coords.dtype))
    # row number?
    if self.coords.shape[0] != self.dates.shape[0]:
        raise JpsError(('Jps %s |dates| and |coords| must have the same '
                        'number of rows (|coords| correspond to the '
                        'coordinates of the event occuring at |dates|): '
                        '|self.dates.shape[0]=%d| and '
                        '|self.coords.shape[0]=%d|.')
                       % (self.code, self.dates.shape[0],
                          self.coords.shape[0]))
    
    # |mag|
    # np.ndarray?
    if not isinstance(self.mag, np.ndarray):
        raise JpsTypeError(('Jps %s |mag| must be np.ndarray: '
                            '|type(self.mag)=%s|.') 
                           % (self.code, type(self.mag)))
    # dimension?
    if self.mag.ndim != 1:
        raise JpsDimensionError(('Jps %s |mag| must be 1D np.ndarray: '
                                 '|self.mag.ndim=%d|.')
                                % (self.code, self.mag.ndim))
    # valid values?
    if self.mag.dtype not in ['int', 'float']:
        raise JpsValueError(('Jps %s |mag| values must be int or float '
                             'np.ndarray: |self.mag.dtype=%s|.')
                            % (self.code, self.mag.dtype))
    # row number?
    if self.mag.shape[0] != self.dates.shape[0]:
        raise JpsError(('Jps %s |dates| and |mag| must have the same number '
                        'of rows (|mag| correspond to the magnitude of the '
                        'event occuring at |dates|): |self.dates.shape[0]=%d| '
                        'and |self.mag.shape[0]=%d|.')
                       % (self.code, self.dates.shape[0], self.mag.shape[0]))
    # |dur|
    # np.ndarray?
    if not isinstance(self.dur, np.ndarray):
        raise JpsTypeError(('Jps %s |dur| must be np.ndarray: '
                            '|type(self.dur)=%s|.') 
                           % (self.code, type(self.dur)))
    # dimension?
    if self.dur.ndim != 1:
        raise JpsDimensionError(('Jps %s |dur| must be 1D np.ndarray: '
                                 '|self.dur.ndim=%d|.')
                                % (self.code, self.dur.ndim))
    # valid values?
    if self.dur.dtype != 'int':
        raise JpsValueError(('Jps %s |dur| values must be int: '
                             '|self.dur.dtype=%s|.')
                            % (self.code, self.dur.dtype))
    # positive values?
    if (self.dur < 0).any():
        raise JpsValueError('Jps %s |dur| values must all be positive.'
                            % self.code)
    # row number?
    if self.dur.shape[0] != self.dates.shape[0]:
        raise JpsError(('Jps %s |dates| and |dur| must have the same number '
                        'of rows (|dur| correspond to the durations of the '
                        'event occuring at |dates|): |self.dates.shape[0]=%d| '
                        'and |self.dur.shape[0]=%d|.')
                       % (self.code, self.dates.shape[0], self.dur.shape[0]))
        
    # Metadata
    # |mag_min|
    if not isinstance(self.mag_min, (int, float)):
        raise JpsTypeError(('Jps %s |mag_lim| must be int or float: '
                            '|type(self.mag_min)=%s|.')
                           % (self.code, type(self.mag_min)))
    # |mag_post|
    if not isinstance(self.mag_post, (int, float)):
        raise JpsTypeError(('Jps %s |mag_post| must be int or float: '
                            '|type(self.mag_post)=%s|.')
                           % (self.code, type(self.mag_post)))
    # |mag_spe|
    if (self.mag_spe is not None
        and not isinstance(self.mag_spe, (int, float))):
        raise JpsTypeError(('Jps %s |mag_spe| must be None, int or float: '
                            '|type(self.mag_spe)=%s|.')
                           % (self.code, type(self.mag_spe)))
    # |dco|
    if not isinstance(self.dco, (int, float)):
        raise JpsTypeError(('Jps %s |dco| must be int or float: '
                            '|type(self.dco)=%s|.')
                           % (self.code, type(self.dco)))
    # |dpost|
    if not isinstance(self.dpost, (int, float)):
        raise JpsTypeError(('Jps %s |dpost| must be int or float: '
                            '|type(self.dpost)=%s|.')
                           % (self.code, type(self.dpost)))
    # |dsse|
    if not isinstance(self.dsse, (int, float)):
        raise JpsTypeError(('Jps %s |dsse| must be int or float: '
                            '|type(self.dsse)=%s|.')
                           % (self.code, type(self.dsse)))
    # |dsw|
    if not isinstance(self.dsw, (int, float)):
        raise JpsTypeError(('Jps %s |dsw| must be int or float: '
                            '|type(self.dsw)=%s|.')
                           % (self.code, type(self.dsw)))
        
        
##################
def reorder(self):
    """
    Reorder Jps attributes by increasing time

    """
    
    # Check parameter
    self.check_jps()

    # Import
    import numpy as np

    # Enough data to reorder?
    if self.shape() > 1:
        
        # Reorder by time
        diff_dates = np.diff(self.dates[:, 1])
        if (diff_dates < 0).any():
            sort_dates = np.argsort(self.dates[:, 1].astype(int))
            self.select_ev(sort_dates, in_place=True)
        
        
#############################################
def remove_duplicated_dates(self, warn=True):
    """
    Remove duplicated dates from Jps

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
    
    # Check and order by increasing time
    self.reorder()
    (warn, _) = adapt_bool(warn, True)
    
    # Duplicated dates?
    if self.shape() > 1:
        diff = np.diff(self.dates[:, 1].astype(int))
        dupl_index = np.where(diff == 0)[0]
        if dupl_index.size == 0:
            return
        elif warn:
            print('[WARNING] from method [remove_duplicated_dates] in [%s]'
                  % __name__)
            print('\tDuplicated date found and removed!')
            print(('\tFor each duplicated date only the higher magnitude '
                   'event is kept!'))
            print()
            
        # Mask to remove duplicated dates
        mask_dupl = np.ones(self.dates.shape[0], dtype=bool)
        mask_dupl[dupl_index] = False
        
        # Keep all Jps events and remove duplicated dates from |self|
        jps_all = self.copy()
        self.select_ev(mask_dupl, in_place=True)
        
        # For all dates in |self|
        for d in range(self.shape()):
            # Look at all event at this date
            jps_d = jps_all.select_ev(jps_all.dates[:, 1]==self.dates[d, 1])
            if jps_d.shape() > 1:
                # Find higher magnitude event
                max_mag = jps_d.mag[np.argsort(jps_d.mag)[-1]]
                jps_d.select_ev(jps_d.mag==max_mag, in_place=True)
                if jps_d.shape() > 1:
                    # Find higher duration event (if same magnitude)
                    max_dur = jps_d.dur[np.argsort(jps_d.dur)[-1]]
                    jps_d.select_ev(jps_d.dur==max_dur, in_place=True)
                    if jps_d.shape() > 1:
                        # Find Antenna changes (if same magnitude and duration)
                        jps_d.select_ev(jps_d.type_ev=='A')
                # Keep caracteristic of select event
                # (higher magnitude, duration, or antenna)
                self.type_ev[d] = jps_d.type_ev[0]
                self.coords[d, :] = jps_d.coords[0, :]
                self.mag[d] = jps_d.mag[0]
                self.dur[d] = jps_d.dur[0]
        