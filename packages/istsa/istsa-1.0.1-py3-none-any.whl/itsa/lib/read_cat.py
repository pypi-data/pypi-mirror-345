"""
    Functions to read events catalogs
    
    Warning: !!! You need to add the module 'itsa' to your Python path to use
    these functions

    ----
    Developed at: ISTerre
    By: Lou MARILL
"""


###################################
def read_antenna(stadb_path, code):
    # Issue 31: allow use of GAMIT station.info
    """
    Read staDB file to get antenna change dates

    Parameter
    ---------
    stadb_path : str
        Path to the staDB file to read.
    code : str
        Station code and name of the staDB to read.

    Raise
    -----
    TypeError
        If |stadb_file| does not have the right type.

    Return
    ------
    np.ndarray
        Dates of the antenna changes.

    """

    # Check parameters
    if not isinstance(stadb_path, str):
        raise TypeError('staDB path must be str: |type(stadb_file)=%s|.'
                        % type(stadb_path))
    if not isinstance(code, str):
        raise TypeError('Station code must be str: |type(stadb_file)=%s|.'
                        % type(code))

    # Import
    import numpy as np
    import os
    from os.path import exists
    from itsa.lib.astrotime import cal2decyear

    # Read file
    t = []
    stadb_file = os.path.join(stadb_path, f"{code.lower()}.sta_db")
    if not exists(stadb_file):
        stadb_file = os.path.join(stadb_path, f"{code.upper()}.sta_db")
    with open(stadb_file, 'r') as data_file:
        for line in data_file:
            s_line = line.split()
            if s_line == []:
                continue
            if s_line[1] == 'ANT':
                date = np.array(s_line[2].split('-'), dtype=int)
                t.append(cal2decyear(date[2], date[1], date[0]))
                # TODO ^ date does not hold hour/minute/second info
                # This info is present in input files and required in PBO offset files
                # Is it sensible to discard it this way?

    # Return
    return np.array(t).reshape(-1)


###################################
def read_station_info(station_info_path, code):
    # Issue 31: allow use of GAMIT station.info
    """
    Read station.info file to get antenna change dates

    Parameter
    ---------
    station_info_path : str
        Path to the station.info file to read.
    code : str
        Station code.

    Raise
    -----
    TypeError
        If |station_info_path| does not have the right type.
        If |code| does not have the right type.

    Return
    ------
    np.ndarray
        Dates of the antenna changes.

    """

    # Check parameters
    if not isinstance(station_info_path, str):
        raise TypeError('Station.info path must be str: |type(station_info_path)=%s|.'
                        % type(station_info_path))
    if not isinstance(code, str):
        raise TypeError('Station code must be str: |type(code)=%s|.'
                        % type(code))

    # Import
    # TODO
    import numpy as np
    from os.path import exists
    from itsa.lib.astrotime import doy2decyear

    # Read file
    t = []
    with open(station_info_path, 'r') as data_file:
        for line in data_file:
            s_line = line.split()
            if s_line == []:
                continue
            if len(s_line) > 4 and s_line[0] == code:
                year = int(s_line[2])
                day = int(s_line[3])
                t.append(doy2decyear(day,year))
                # TODO ^ date does not hold hour/minute/second info
                # This info is present in input files and required in PBO offset files
                # Is it sensible to discard it this way?

    # Return
    return np.array(t).reshape(-1)




#######################
def read_ISC(isc_file):
    """
    Read earthquake catalog from ISC (International Seismological Center)

    Parameter
    ---------
    isc_file : str
        Name of the file with ISC catalog to read.

    Raise
    -----
    TypeError
        If |isc_file| does not have the right type.

    Return
    ------
    np.ndarray
        5-columns array:
            - dates: Dates of the earthquakes, in decimal year,
            - latitude: Coordinates of the earthquake, in decimal degrees,
            - longitude: Coordinates of the earthquake, in decimal degrees,
            - depth: Depth of the earthquake, in meter,
            - magnitude: Maximum magnitude of the earthquake find in file.

    """

    # Check parameters
    if not isinstance(isc_file, str):
        raise TypeError('ISC file must be str: |type(isc_file)=%s|.'
                        % type(isc_file))

    # Import
    import numpy as np
    from itsa.lib.astrotime import cal2decyear

    # Read file
    cat = []
    with open(isc_file, 'r') as data_file:
        for line in data_file:
            s_line = line.split(',')
            if len(s_line) >= 12 and s_line[1] != 'TYPE':
                date = np.array(s_line[3].split('-'), dtype=int)
                # TODO ^ date does not hold hour/minute/second info
                # This info is present in input files and required in PBO offset files
                # Is it sensible to discard it this way?
                lat = float(s_line[5])
                lon = float(s_line[6])
                depth = float(s_line[7])
                mag = np.array([s_line[k] for k in range(11, len(s_line), 3)],
                               dtype=float)
                cat.append([cal2decyear(date[2], date[1], date[0]),
                           lat, lon, depth, np.max(mag)])

    # Return
    return np.array(cat).reshape(-1, 5)
