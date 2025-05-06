"""
    Read Jps catalog text file and fill Jps object

    ----
    Developed at: ISTerre
    By: Lou MARILL
"""


#######################################
def read(self, tsdir='.', tsfile=None):
    """
    Read Jps catalog file to populate given Jps object

    Parameters
    ----------
    tsdir : str, optional
        Directory of the Jps catalog file to be readed.
        The default is '.'.
    tsfile : str, optional
        Jps catalog file to be readed
        The default is None: |read| look for '|self.code|*.txt' file.

    Raises
    ------
    TypeError
        If any parameter does not have the right type.
    FileNotFoundError
        If there is no '|code|*.txt' file in |tsdir|.

    """
    
    ######################################
    def _check_param(self, tsdir, tsfile):
        # |self|
        self.check_jps()
        # |tsdir|
        if not isinstance(tsdir, str):
            raise TypeError(('Directory must be str: '
                             '|type(tsdir)=%s|.') % type(tsdir))
        # |tsfile|
        if tsfile is not None and not isinstance(tsfile, str):
            raise TypeError('File must be str: |type(tsfile)=%s|.'
                            % type(tsfile))
    ######################################
    
    # Check parameters
    _check_param(self, tsdir, tsfile)
    
    # Import
    import os
    import numpy as np
    from linecache import getline
    from itsa.lib.astrotime import mjd2decyear
    
    # Name of the file - if not provided, tries to guess
    if tsfile is None:
        from glob import glob
        txt_file = glob(tsdir+os.sep+self.code.upper()+'*.txt')
        if len(txt_file) == 0:
            raise FileNotFoundError('No file %s/%s*.txt was found.'
                                    % (tsdir, self.code.upper()))
        txt_file = txt_file[0]
    else:
        txt_file = tsdir+os.sep+tsfile
            
    # Populate data
    # Read data
    data = np.genfromtxt(txt_file, skip_header=22, dtype=str)
    # Ensure 2D array
    if data.ndim == 1:
        data = data.reshape(-1, 1)
    # Part data matrix
    mjd = data[:, 2].astype(float)
    type_ev = data[:, 3]
    coords = data[:, 4:7].astype(float)
    mag = data[:, 7].astype(float)
    dur = data[:, 8].astype(float)
    
    # Make time array
    dates = np.c_[mjd2decyear(np.round(mjd, 1)), np.round(mjd, 1)]
    self.add_ev(dates, type_ev, coords, mag, dur)
        
    # Populate metadata
    # Read influence radius parameter
    # Co- and post-seismic
    d11 = getline(txt_file, 3).split(':')[2:]
    d12 = np.array(list(map(lambda x: x.split(',')[0], d11)), dtype=float)
    self.dco = d12[0]
    self.dpost = d12[1]
    # SSE and swarm
    d21 = getline(txt_file, 4).split(':')[1:]
    d22 = np.array(list(map(lambda x: x.split(',')[0], d21)), dtype=float)
    self.dsse = d22[0]
    self.dsw = d22[1]
    # Read magnitudes
    mag1 = getline(txt_file, 8).split(':')[1:]
    mag2 = np.array(list(map(lambda x: x.split(',')[0], mag1)), dtype=float)
    self.mag_min = mag2[0]
    self.mag_post = mag2[1]
    if len(mag2) > 2:
        self.mag_spe = mag2[2]
    

##################################################################
def add_ev(self, dates, type_ev, coords=None, mag=None, dur=None):
    """
    Add seismic or aseismic events to |jps| catalog of Gts

    Parameters
    ----------
    dates : list or np.ndarray
        Dates of the events to add.
    type_ev : str, list or np.ndarray
        Type of the events to add.
    coords : None, list or np.ndarray, optional
        Coordinates of the events to add.
        The default is None: set to 0 for all events.
    mag : None, int, float, list or np.ndarray, optional
        Magnitude of the events to add.
        The default is None: set to 0 for all events.
    dur : None, int, list or np.ndarray, optional
        Duration of the events to add.
        The default is None: set to 0 for all events.

    Raises
    ------
    ValueError
        If any parameter is list and cannot be converted to np.ndarray.
        If |dates| or |coords| is not list of lists nor 2D np.ndarray.
        If |dates| is not list of 2-value lists nor 2-column np.ndarray.
        If |dates|, |coords| or |mag| values are not int nor float.
        If |type_ev|, |mag| or |dur| is list or np.ndarray, but not 1D.
        If |type_ev| values are not str.
        If |coords| is not list of 3-value lists nor 3-column np.ndarray.
        If |dur| values are not int.
        If |coords|, |mag| or |dur| is not None and does not have the same
        number of rows than |dates|.
    TypeError
        If any parameter does not have the right type.

    Note
    ----
    If |coords|, |mag| and/or |dur| are not None, they number of rows must be
    the same than |dates|. 

    """

    #########################################################
    def _check_param(self, dates, type_ev, coords, mag, dur):
        """
        Raise error if one parameter is invalid and adapt some parameter values
        """
        # Import
        import numpy as np
        from itsa.lib.modif_vartype import list2ndarray, nptype2pytype
        
        # Change type
        # |dates|
        if isinstance(dates, list):
            (dates, err_dates) = list2ndarray(dates)
            if err_dates:
                raise ValueError(('Dates list must be convertible into '
                                  'np.ndarray: |dates=%s|.') % str(dates))
        # |dtype_ev|
        if isinstance(type_ev, list):
            (type_ev, err_type) = list2ndarray(type_ev)
            if err_type:
                raise ValueError(("Event's type list must be convertible into "
                                  "np.ndarray: |type_ev=%s|.") % str(type_ev))
        # |coords|
        if isinstance(coords, list):
            (coords, err_coords) = list2ndarray(coords)
            if err_coords:
                raise ValueError(('Coordinates list must be convertible into '
                                  'np.ndarray: |coords=%s|.') % str(coords))
        # |mag|
        if isinstance(mag, list):
            (mag, err_mag) = list2ndarray(mag)
            if err_mag:
                raise ValueError(('Magnitudes list must be convertible into '
                                  'np.ndarray: |mag=%s|.') % str(mag))
        # |dur|
        if isinstance(dur, list):
            (dur, err_dur) = list2ndarray(dur)
            if err_dur:
                raise ValueError(('Durations list must be convertible into '
                                  'np.ndarray: |dur=%s|.') % str(dur))
        #|type_ev|, |mag| and |dur|
        [type_ev, mag, dur] = nptype2pytype([type_ev, mag, dur])

        # Check
        # |self|
        self.check_jps()
        # |dates|
        if not isinstance(dates, np.ndarray):
            raise TypeError(('Dates must be list or np.ndarray: '
                             '|type(dates)=%s|.') %type(dates))
        if dates.ndim == 1:
            dates = dates.reshape(1,-1)
        if dates.ndim != 2:
            raise ValueError(('Dates must be list of lists or 2D np.ndarray: '
                              '|dates.ndim=%d|.') % dates.ndim)
        if dates.shape[1] != 2:
            raise ValueError(('Dates must be list of 2-value lists or 2-column'
                              ' np.ndarray: |dates.shape[1]=%d|.')
                             % dates.shape[1])
        if dates.dtype not in ['int', 'float']:
            raise ValueError(('Dates must be list of int, list of float, '
                              'int np.ndarray or float np.ndarray:'
                              '|dates.dtype=%s|.') % dates.dtype)
        # |type_ev|
        if not isinstance(type_ev, (str, np.ndarray)):
            raise TypeError(("Event's type must be str, list or np.ndarray: "
                             "|type(type_ev)=%s|.") % type(type_ev))
        if isinstance(type_ev, np.ndarray):
            if type_ev.ndim != 1:
                raise ValueError(("Event's type must be str, 1D list or 1D "
                                  "np.ndarray: |type_ev.ndim=%d|.")
                                 % type_ev.ndim)
            if type_ev.dtype != 'str' and 'U' not in str(type_ev.dtype):
                raise ValueError(("Event's type must be str, list of str or "
                                  "str np.ndarray: |type_ev.dtype=%s|.")
                                 % type_ev.dtype)
        # |coords|
        if coords is not None:
            if not isinstance(coords, np.ndarray):
                raise TypeError(('Coordinates must be list or np.ndarray: '
                                 '|type(coords)=%s|.') % type(coords))
            if coords.ndim == 1:
                coords = coords.reshape(1,-1)
            if coords.ndim != 2:
                raise ValueError(('Coordinates must be list of lists or 2D '
                                  'np.ndarray: |coords.ndim=%d|.')
                                 % coords.ndim)
            if coords.shape[1] != 3:
                raise ValueError(('Coordinates must be list of 3-value lists '
                                  'or 3-column np.ndarray: '
                                  '|coords.shape[1]=%d|.') % coords.shape[1])
            if coords.dtype not in ['int', 'float']:
                raise ValueError(('Coordinates must be list of int, list of '
                                  'float, int np.ndarray or float np.ndarray: '
                                  '|coords.dtype=%s|.') % coords.dtype)
            if coords.shape[0] != dates.shape[0]:
                raise ValueError(('As |coords| is not None: Dates and '
                                  'coordinates must have the same number of '
                                  'rows: |coords.shape[0]=%d| and '
                                  '|dates.shape[0]=%d|.')
                                 % (coords.shape[0],dates.shape[0]))
        # |mag|
        if mag is not None:
            if not isinstance(mag, (int, float, np.ndarray)):
                raise TypeError(('Magnitudes must be int, float, list or '
                                 'np.ndarray: |type(mag)=%s|.')
                                % type(mag))
            if isinstance(mag, np.ndarray):
                if mag.ndim != 1:
                    raise ValueError(('Magnitudes must be int, float, list or '
                                      '1D np.ndarray: |mag.ndim=%d|.')
                                     % mag.ndim)
                if mag.dtype not in ['int', 'float']:
                    raise ValueError(('Magnitudes must be int, float, list of '
                                      'int, list of float, int np.ndarray or '
                                      'float np.ndarray: |mag.dtype=%s|.')
                                     % mag.dtype)
                if mag.shape[0] != dates.shape[0]:
                    raise ValueError(('As |mag| is not None: Dates and '
                                      'magnitudes must have the same number '
                                      'of rows: |mag.shape[0]=%d| and '
                                      '|dates.shape[0]=%d|.')
                                     % (mag.shape[0],dates.shape[0]))
        # |dur|
        if dur is not None:
            if not isinstance(dur, (int, float, np.ndarray)):
                raise TypeError(('Durations must be int,float, list or '
                                 'np.ndarray: |type(mag)=%s|.') % type(dur))
            if isinstance(dur, np.ndarray):
                if dur.ndim != 1:
                    raise ValueError(('Durations must be int, float, list or '
                                      '1D np.ndarray: |dur.ndim=%d|.')
                                     % dur.ndim)
                if dur.dtype not in ['int', 'float']:
                    raise ValueError(('Durations must be int; float, list of '
                                      'int, list of float, int np.ndarray or '
                                      'float np.ndarray: |dur.dtype=%s|.')
                                     % dur.dtype)
                if dur.shape[0] != dates.shape[0]:
                    raise ValueError(('As |dur| is not None: Dates and '
                                      'durations must have the same number of '
                                      'rows: |dur.shape[0]=%d| and '
                                      '|dates.shape[0]=%d|.')
                                     % (dur.shape[0],dates.shape[0]))
                    
        # Return
        return dates, type_ev, coords, mag, dur
    #########################################################

    # Check parameters
    (dates, type_ev, coords, mag, dur) = _check_param(self, dates, type_ev,
                                                      coords, mag, dur)

    # Import
    import numpy as np

    # Populate |jps|
    # |dates|
    self.dates = np.vstack((self.dates, dates))
    # |type_ev|
    if isinstance(type_ev, str):
        type_ev = np.repeat(type_ev, dates.shape[0])
    self.type_ev = np.hstack((self.type_ev, type_ev))
    # |coords|
    if coords is None:
        coords = np.zeros((dates.shape[0], 3))
    self.coords = np.vstack((self.coords, coords))
    # |mag|
    if mag is None:
        mag = np.zeros(dates.shape[0])
    self.mag = np.hstack((self.mag, mag))
    # |dur|
    if dur is None:
        dur = np.zeros(dates.shape[0])
    dur = np.round(dur).astype(int)
    self.dur = np.hstack((self.dur, dur))
