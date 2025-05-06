"""
    Warning: !!! You need to add the module 'itsa' to your Python path to use
    these functions

    ----
    Developped at: ISTerre
    By: Lou MARILL
    Based on: PYACS module for |get_index_from_dates|
"""

#########################################################################
def get_index_from_dates(time, dates, type_time='mjd', type_dates='mjd'):
    """
    Return list of index in |time| corresponding to given dates

    Parameters
    ----------
    time : list or np.ndarray
        Time vector in which we search dates index, in |type_time|.
    dates : int, float, list or np.ndarray
        Dates for which we want time index, in |type_dates|.
    type_time : 'mjd', 'decyear', 'cal' or 'doy', optional
        Type of dates in |time|:
            'mjd': Modified Julian day,
            'decyear': Decimal year,
            'cal': Calendar date (|time| must have 3 columns:
                                  day, month, year),
            'doy': Day of year and associated year (|time| must have 2 columns:
                                                    doy, year).
        The default is 'mjd'.
    type_dates : 'mjd', 'decyear', 'cal' or 'doy', optional
        Type of dates in |dates|.
        The default is 'mjd'.

    Raises
    ------
    ValueError
        If |time| or |dates| is list and cannot be converted to np.ndarray.
        If |type_time| or |type_dates| is not 'mjd', 'decyear', 'cal' nor
        'doy'.
        If |time| or |dates| values are not int nor float.
        If |type_time| does not have the right dimension according to 
        |type_time|.
        If |type_dates| does not have the right dimension according to 
        |type_dates|.
    TypeError
        If any parameter does not have the right type.

    Returns
    -------
    np.ndarray
        1D matrix with the time index for the given dates.

    """

    #####################################################
    def _check_param(time, dates, type_time, type_dates):
        """
        Raise error if one parameter is invalid and adapt some parameter values
        """
        # Import
        import numpy as np
        from itsa.lib.modif_vartype import list2ndarray, nptype2pytype

        # Change type
        # |time|
        if isinstance(time, list):
            (time, err_time) = list2ndarray(time)
            if err_time:
                raise ValueError(('Time list must be convertible into '
                                  'np.ndarray: |time=%s|.') % str(time))
        # |dates|
        if isinstance(dates, list):
            (dates, err_dates) = list2ndarray(dates)
            if err_dates:
                raise ValueError(('Dates list must be convertible into '
                                  'np.ndarray: |dates=%s|.') % str(dates))
        dates = nptype2pytype(dates)

        # Check
        # |type_time|
        if not isinstance(type_time, str):
            raise TypeError(('Type of dates in |time| must be str: '
                             '|type(type_time)=%s|.') % type(type_time))
        if type_time not in ['mjd', 'decyear', 'cal', 'doy']:
            raise ValueError(("Type of dates in |time| must be 'mjd' "
                              "(modified Julian day), 'decyear' "
                              "(decimal year), 'cal' (calendar date) or "
                              "'doy' (day of year): |type_time='%s'|.")
                             % type_time)
        # |time|
        if not isinstance(time, np.ndarray):
            raise TypeError('Time must be list or np.ndarray: |type(time)=%s|.'
                            % type(time))
        if type_time in ['mjd', 'decyear']:
            if time.ndim != 1:
                raise ValueError(("Time must be 1D list or 1D np.ndarray "
                                  "because |type_time='%s'|: |time.ndim=%d|.")
                                 % (type_time, time.ndim))
            if time.dtype not in ['int', 'float']:
                raise ValueError(("Time must be list of int, list of float, "
                                  "int np.ndarray or float np.ndarray because "
                                  "|type_time='%s'|: |time.dtype=%s|.")
                                 % (type_time, time.dtype))
        if type_time in ['cal', 'doy']:
            if time.ndim != 2:
                raise ValueError(("Time must be list of lists or 2D np.ndarray"
                                  " because |type_time='%s'|: |time.ndim=%d|.")
                                 % (type_time, time.ndim))
            if time.dtype not in ['int']:
                raise ValueError(("Time must be list of int or int "
                                  "np.ndarray because |type_time='%s'|: "
                                  "|time.dtype=%s|.") % (type_time,time.dtype))
            if type_time == 'cal' and time.shape[1] != 3:
                raise ValueError(("Time must be list of 3-value lists or "
                                  "np.ndarray with 3 colums because "
                                  "|type_time='%s'|: |time.shape[1]=%d|.")
                                 % (type_time, time.shape[1]))
            if type_time == 'doy' and time.shape[1] != 2:
                raise ValueError(("Time must be list of 2-value lists or "
                                  "np.ndarray with 2 colomns because "
                                  "|type_time='%s'|: |time.shape[1]=%d|.")
                                 % (type_time, time.shape[1]))
        # |type_dates|
        if not isinstance(type_dates, str):
            raise TypeError(('Type of dates in |dates| must be str: '
                             '|type(type_dates)=%s|.') % type(type_dates))
        if type_dates not in ['mjd', 'decyear', 'cal', 'doy']:
            raise ValueError(("Type of dates in |dates| must be 'mjd' "
                              "(modified Julian day), 'decyear' "
                              "(decimal year), 'cal' (calendar date) or 'doy' "
                              "(day of year): |type_dates='%s'|.")
                             % type_dates)
        # |dates|
        if not isinstance(dates, (int, float, np.ndarray)):
            raise TypeError(('Dates must be int, float, list or np.ndarray: '
                             '|type(dates)=%s|.') % type(dates))
        if type_dates in ['mjd', 'decyear']:
            if isinstance(dates, (int, float)):
                dates = np.array(dates)
            if dates.size == 1:
                dates = dates.reshape(-1)
            if dates.ndim != 1:
                raise ValueError(("Dates must be int, float, 1D list or 1D "
                                  "np.ndarray because |type_dates='%s'|: "
                                  "|dates.ndim=%d|.")
                                 % (type_dates, dates.ndim))
            if dates.dtype not in ['int', 'float']:
                raise ValueError(("Dates must be int, float, list of int, "
                                  "list of float, int np.ndarray or float "
                                  "np.ndarray because |type_dates='%s'|: "
                                  "|dates.dtype=%s|.")
                                 % (type_dates, dates.dtype))
        if type_dates in ['cal', 'doy']:
            if type_dates == 'cal' and dates.size == 3:
                dates = dates.reshape(1, -1)
            if type_dates == 'doy' and dates.size == 2:
                dates = dates.reshape(1, -1)
            if dates.ndim != 2:
                raise ValueError(("Dates must be list of lists or 2D "
                                  "np.ndarray because |type_dates='%s'|: "
                                  "|dates.ndim=%d|.")
                                 % (type_dates, dates.ndim))
            if dates.dtype not in ['int']:
                raise ValueError(("Dates must be list of int or int "
                                  "np.ndarray because |type_dates='%s'|: "
                                  "|dates.dtype=%s|.")
                                 % (type_dates, dates.dtype))
            if type_dates == 'cal' and dates.shape[1] != 3:
                raise ValueError(("Dates must be list of 3-value lists or "
                                  "np.ndarray with 3 colums because "
                                  "|type_dates='%s'|: |dates.shape[1]=%d|.")
                                 % (type_dates, dates.shape[1]))
            if type_dates == 'doy' and dates.shape[1] != 2:
                raise ValueError(("Dates must be list of 2-value lists or "
                                  "np.ndarray with 2 colomns because "
                                  "|type_dates='%s'|: |dates.shape[1]=%d|.")
                                 % (type_dates, dates.shape[1]))

        # Return
        return time, dates
    #####################################################

    # Check parameters
    (time, dates) = _check_param(time, dates, type_time, type_dates)

    # Import
    import numpy as np
    from itsa.lib.astrotime import decyear2mjd, cal2mjd, doy2mjd

    # Change time and dates type
    # |time|
    if type_time == 'decyear':
        time = decyear2mjd(time)
    if type_time == 'cal':
        time = cal2mjd(time[:, 0], time[:, 1], time[:, 2])
    if type_time == 'doy':
        time = doy2mjd(time[:, 0], time[:, 1])
    # |dates|
    if type_dates == 'decyear':
        dates = decyear2mjd(dates)
    if type_dates == 'cal':
        dates = cal2mjd(dates[:, 0], dates[:, 1], dates[:, 2])
    if type_dates == 'doy':
        dates = doy2mjd(dates[:, 0], dates[:, 1])

    # int np.ndarray
    time = time.astype(int)
    if not isinstance(dates, np.ndarray):
        dates = np.array([dates])
    dates = dates.astype(int)

    # Find index
    index = []
    for k in range(dates.shape[0]):
        diff = time-dates[k]
        find = np.where(diff == 0)[0]
        if find.size != 0:
            index.append(find[0])
        else:
            index.append(-1)

    # Return
    return np.array(index)


#########################################################
def get_indfid_window(time, jps_dates, jps_dur, nb_data):
    """
    Return index of the initial and final dates of the window

    Parameters
    ----------
    time : list or np.ndarray
        Time vector in which we search dates index, in modified Julian days.
    jps_dates : int, float, list or np.ndarray
        Dates of Jps events to possibly include within the window, in modified
        Julian days.
    jps_dur : int, float, list or np.ndarray
        Duration of Jps events to possibly include within the window, in days.
    nb_data : int or list
        Number of data before the first Jps event and after the last one.
        If |nb_data| is int, the same number of data will be kept before the
        first Jps event and after the last one.
    
    Raises
    ------
    ValueError
        If |time|, |jps_dates| or |jps_dur| is list and cannot be converted to
        np.ndarray.
        If |time| is not 1D list nor 1D np.ndarray.
        If |time|, |jps_dates| or |jps_dur| values are not int nor float.
        If |jps_dates| or |jps_dur| is np.ndarray but not 1D.
        If |nb_data| values are not positive nor 0.
    TypeError
        If any parameter does not have the right type.

    Returns
    -------
    idx_window : list
        Index of the initial and final dates of the window within |time|.
    nb_jps : int
        Number of Jps events within the window.

    """
    
    ####################################################
    def _check_param(time, jps_dates, jps_dur, nb_data):
        """
        Raise error if one parameter is invalid and adapt some parameter values
        """
        # Import
        import numpy as np
        from itsa.lib.modif_vartype import list2ndarray, nptype2pytype
        
        # Change type
        # |time|
        if isinstance(time, list):
            (time, err_time) = list2ndarray(time)
            if err_time:
                raise ValueError(('Time list must be convertible into '
                                  'np.ndarray: |time=%s|.') % str(time))
        # |jps_dates|
        if isinstance(jps_dates, list):
            (jps_dates, err_dates) = list2ndarray(jps_dates)
            if err_dates:
                raise ValueError(('Jps dates list must be convertible into '
                                  'np.ndarray: |jps_dates=%s|.')
                                 % str(jps_dates))
        # |jps_dur|
        if isinstance(jps_dur, list):
            (jps_dur, err_dur) = list2ndarray(jps_dur)
            if err_dur:
                raise ValueError(('Jps durations list must be convertible '
                                  'into np.ndarray: |jps_dur=%s|.')
                                 % str(jps_dur))
        
        # |jps_dates|, |jps_dur| and |nb_data|
        (jps_dates, jps_dur, nb_data) = nptype2pytype([jps_dates, jps_dur,
                                                       nb_data])
        
        # Check
        # |time|
        if not isinstance(time, np.ndarray):
            raise TypeError('Time must be list or np.ndarray: |type(time)=%s|.'
                            % type(time))
        if time.ndim != 1:
            raise ValueError(('Time must be 1D list or 1D np.ndarray: '
                              '|time.ndim=%d|.')
                             % time.ndim)
        if time.dtype not in ['int', 'float']:
            raise ValueError(('Time must be list of int, list of float, int '
                              'np.ndarray or float np.ndarray:'
                              ' |time.dtype=%s|.') % time.dtype)
        # |jps_dates|
        if not isinstance(jps_dates, (int, float, np.ndarray)):
            raise TypeError(('Jps dates must be int, float, list or '
                             'np.ndarray: |type(jps_dates)=%s|.')
                            % type(jps_dates))
        if isinstance(jps_dates, (int, float)):
            jps_dates = np.array(jps_dates)
        if jps_dates.size == 1:
            jps_dates = jps_dates.reshape(-1)
        if jps_dates.ndim != 1:
            raise ValueError(('Jps dates must be int, float, 1D list or '
                              '1D np.ndarray: |jps_dates.ndim=%d|.')
                             % jps_dates.ndim)
        if jps_dates.dtype not in ['int', 'float']:
            raise ValueError(('Jps dates must be int, float, list of int, '
                              'list of float, int np.ndarray or '
                              'float np.ndarray: |jps_dates.dtype=%s|.')
                             % jps_dates.dtype)
        # |jps_dur|
        if not isinstance(jps_dur, (int, float, np.ndarray)):
            raise TypeError(('Jps durations must be int, float, list or '
                             'np.ndarray: |type(jps_dur)=%s|.')
                            % type(jps_dur))
        if isinstance(jps_dur, (int, float)):
            jps_dur = np.array(jps_dur)
        if jps_dur.size == 1:
            jps_dur = jps_dur.reshape(-1)
        if jps_dur.ndim != 1:
            raise ValueError(('Jps durations must be int, float, 1D list or '
                              '1D np.ndarray: |jps_dur.ndim=%d|.')
                             % jps_dur.ndim)
        if jps_dur.dtype not in ['int', 'float']:
            raise ValueError(('Jps durations must be int, float, list of int, '
                              'list of float, int np.ndarray or '
                              'float np.ndarray: |jps_dur.dtype=%s|.')
                             % jps_dur.dtype)
        # |nb_data|
        if not isinstance(nb_data, (int, list)):
            raise TypeError(('Number of data must be int or list: '
                             '|type(nb_data)=%s|.')
                            % type(nb_data))
        if isinstance(nb_data, int):
            nb_data = [nb_data, nb_data]
        if (np.array(nb_data) < 0).any():
            raise ValueError(('Number of data must be positive or 0:'
                              '|nb_data=%s|.') % str(nb_data))
        
        # Return
        return jps_dates, jps_dur, nb_data
    ####################################################    
    
    # Check parameters
    (jps_dates, jps_dur, nb_data) = _check_param(time, jps_dates, jps_dur,
                                                 nb_data)
    
    # Import
    import numpy as np
    
    # Find inital index of the window
    # Find index of nearest date in |time|
    diff_mjd = jps_dates[0]-time
    try:
        idx_jp_ind = np.where(diff_mjd>=0)[0][-1]
        # Take the wanted number of data into the mid-window
        idx_ind = max(idx_jp_ind-nb_data[0],0)
    except:
        idx_ind = 0
    
    # Find final index of the window
    k = 0
    in_window = True
    mjd_jps_fid = jps_dates+jps_dur
    while k < len(jps_dates) and in_window:
        # Modified julian day of the end of the event
        mjd_jpk = max(mjd_jps_fid[:k+1])
        # Find index of the nearest date in |time|
        diff_mjd = mjd_jpk-time
        idx_jp_fid = np.where(diff_mjd<=0)[0][0]
        # Take the wanted number of data into the mid-window
        idx_fid = min(idx_jp_fid+nb_data[1],len(time)-1)
        # Along window (if another jump in window)?
        if k < len(jps_dates)-1 and jps_dates[k+1] < time[idx_fid]:
            k += 1
        else:
            in_window = False
        
    # Return
    return [idx_ind, idx_fid], k+1
