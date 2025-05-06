"""
    Read and write PBO pos files

    ----
    Developed at: ISTerre
    By: Lou MARILL
    Based on: PYACS module
"""

####################################################################
def read_PBOpos(self, tsdir='.', tsfile=None, process='', neu=False,
                warn=True):
    """
    Read PBO pos file and load the time series into Gts object

    Parameters
    ----------
    tsdir : str, optional
        Directory of the file to be readed.
        The default is '.'.
    tsfile : str, optional
        File in PBO pos format to be readed.
        The default is None: |read_PBOpos| look for '|self.code|*.pos' file.
    process : str, optional
        Processing used to get the solution.
        The default is 'Unknown'.
    neu : bool, optional
        Populate |data_neu| if true.
        The default is False.
    warn : bool, optional
        Print warning if true.
        The default is True.

    Raises
    ------
    GtsTypeError
        If |self.code| is not str.
    GtsValueError
        If |self.code| does not have exactly 4 letters.
    TypeError
        If any parameter does not have the right type.
    FileNotFoundError
        If there is no '|self.code|*.pos' file in |tsdir|.
    WARNING
        If |neu| is not bool: |neu| set to False.

    Notes
    ----
    - With this function the information of |code|, |time|, |data|, |t0|,
    |XYZ0|, |NEU0|, |ref_frame| and |in_file| will be populated in |ts|.
    - |data_xyz| can be populated even if |xyz=False|: if the 1rst coordinates
    is not the same than the reference ones.

    """

    ##########################################################
    def _check_param(self, tsdir, tsfile, process, neu, warn):
        """
        Raise error is one parameter is invalid and adapt some parameter values
        """
        # Import
        from itsa.gts.errors import GtsTypeError, GtsValueError
        from itsa.lib.modif_vartype import adapt_bool

        # Check
        # |self.code|
        if not isinstance(self.code, str):
            raise GtsTypeError('Gts |code| must be str: |type(self.code)=%s|.'
                               % type(self.code))
        if len(self.code) != 4:
            raise GtsValueError(('Gts |code| must have exactly 4 letters: '
                                 '|len(self.code)=%d|.') % len(self.code))
        # |tsdir|
        if not isinstance(tsdir, str):
            raise TypeError('Directory must be str: |type(tsdir)=%s|.'
                            % type(tsdir))
        # |tsfile|
        if tsfile is not None and not isinstance(tsfile, str):
            raise TypeError('File must be str: |type(tsfile)=%s|.'
                            % type(tsfile))
        # |process|
        if not isinstance(process, str):
            raise TypeError('Processing name must be str: |type(process)=%s|.'
                            % type(process))
            
        # Adapt
        # |neu|
        (neu, warn_neu) = adapt_bool(neu)
        # |warn|
        (warn, _) = adapt_bool(warn, True)

        # Warings
        if warn and warn_neu:
            print('[WARNING] from method [read_PBOpos] in [%s]' % __name__)
            print('\t|neu| parameter set to False because |type(neu)!=bool|!')
            print('\t|data_neu| will not be populated.')
            print()

        # Return
        return neu, warn
    ##########################################################

    # Check parameters
    (neu, warn) = _check_param(self, tsdir, tsfile, process, neu, warn)

    # Import
    import numpy as np
    import os
    from os.path import abspath
    from linecache import getline
    from itsa.lib.astrotime import cal2decyear, mjd2decyear

    # Name of the file - if not provided, tries to guess
    if tsfile is None:
        from glob import glob
        pos_file = glob(tsdir+os.sep+self.code.upper()+'*.pos')
        if len(pos_file) == 0:
            raise FileNotFoundError('No file %s/%s*.pos was found.'
                                    % (tsdir, self.code.upper()))
        pos_file = pos_file[0]
    else:
        pos_file = tsdir+os.sep+tsfile
    self.in_file = abspath(pos_file)

    # Read array data
    # Read all data
    data = np.genfromtxt(pos_file, skip_header=37)
    # Ensure 2D array
    if data.ndim == 1:
        data = data.reshape(1, -1)

    # Populate data
    # Time
    self.time = np.c_[mjd2decyear(np.round(data[:, 2], 1)),
                      np.round(data[:, 2], 1)]
    # dN, dU, dU
    self.data = np.c_[data[:, 15:18]*1e3, data[:, 18:24]]
    # XYZ
    self.data_xyz = data[:, 3:12]
    # NEU
    if neu:
        self.data_neu = data[:, 12:15]
        
    # Populate reference data
    # Reference coordinates
    self.t0 = self.time[0, :]
    self.XYZ0 = self.data_xyz[0, :3]
    self.NEU0 = data[0, 12:15]
    # Reference frame
    self.ref_frame = getline(pos_file, 1).split(':')[-1].split()[0]
    # Processing?
    test_process = getline(pos_file, 4).split(':')[0][0] == 'P'
    if test_process:
        self.process = getline(pos_file, 4).split(':')[-1].split()[0]
        if warn and process != '' and self.process != process:
            print('[WARNING] from method [read_PBOpos] in [%s]' % __name__)
            print(("\tProcessing name in %s different from the given "
                   "processing name: |self.process='%s'| and |process='%s'|!")
                  % (pos_file, self.process, process))
            print("\tProcessing name '%s' kept!" % self.process)
            print()
    else:
        self.process = process
    
    # Change reference coordinates for t0 if needed
    XYZ0 = np.array(getline(pos_file, 8).split(':')[-1].split()[:3],
                    dtype=float)
    if (XYZ0 != self.XYZ0).any():
        self.change_ref(self.t0[1])

    # Time vector from initial to final date
    # Initial time
    iccal = getline(pos_file, 5).split(':')[-1].strip().split()[0]
    ical = [int(iccal[0:4]), int(iccal[4:6]), int(iccal[6:])]
    ti = cal2decyear(ical[2], ical[1], ical[0])
    # Final time
    fccal = getline(pos_file, 6).split(':')[-1].strip().split()[0]
    fcal = [int(fccal[0:4]), int(fccal[4:6]), int(fccal[6:])]
    tf = cal2decyear(fcal[2], fcal[1], fcal[0])
    # Make ontinuous time vector and remove duplicate dates
    self.continuous_time(ini_time=ti, fin_time=tf, in_place=True)


#########################################################################
def write_PBOpos(self, outdir='.', add_key='', replace=False, warn=True):
    """
    Write PBO pos file from Geodetic time series (Gts)

    Parameters
    ----------
    outdir : str, optional
        Output directory.
        The default is '.'.
    add_key : str, optional
        Output file name will be '|self.code|_add_key.pos' if |add_key|
        is not empty.
        The default is '': output file will be '|self.code|.pos'.
    replace : bool, optional
        Replace existing file with the same name in the output directory by the
        writen file if true.
        The default is False.
    warn : bool, optional
        Print warning if true.
        The default is True.

    Raises
    ------
    TypeError
        If any parameter does not have the right type.
    OSError
        If output file name is already taken and |replace| is false.
    WARNING
        If |replace| is not bool: |replace| set to False.

    """

    #######################################################
    def _check_param(self, outdir, add_key, replace, warn):
        """
        Raise error if one parameter is invalid and adapt some parameter values
        """
        # Import
        import os
        from os.path import exists
        from itsa.lib.modif_vartype import adapt_bool

        # Check
        # |self|
        self.check_gts()
        # |outdir|
        if not isinstance(outdir, str):
            raise TypeError(('Output directory must be str: '
                             '|type(outdir)=%s|.') % type(outdir))
        # |add_key|
        if not isinstance(add_key, str):
            raise TypeError(('Key name to add must be str: '
                             '|type(add_key)=%s|.') % type(add_key))

        # Adapt
        # |replace|
        (replace, warn_replace) = adapt_bool(replace)
        # |warn|
        (warn, _) = adapt_bool(warn, True)

        # Warning
        if warn and warn_replace:
            print('[WARNING] from method [write_PBOpos] in [%s]' % __name__)
            print('\t|replace| set to False because |type(replace)!=bool|!')
            print('\tNo file will be replaced in the output directory!')

        # Replace?
        pos_file = outdir+os.sep+self.code
        if add_key != '':
            pos_file += '_'+add_key
        pos_file += '.pos'
        if not replace and exists(pos_file):
            raise OSError(('File %s already exist: Gts %s not saved (change '
                           '|add_key| and/or look at |replace| argument).')
                          % (pos_file, self.code))

        # Return
        return warn, pos_file
    #######################################################

    # Check parameters
    (warn, pos_file) = _check_param(self, outdir, add_key, replace, warn)

    # Import
    from os import makedirs
    from os.path import isdir
    import numpy as np
    from datetime import datetime
    from itsa.lib.coordinates import xyz2geo
    from itsa.lib.astrotime import mjd2cal, ut2hms

    # Output directory
    if not isdir(outdir):
        makedirs(outdir)

    # Open pos file
    with open(pos_file, 'w+') as f_pos:

        # Sort by increasing time, remove duplicated dates and NaN values
        self.remove_duplicated_dates(warn=warn)
        ts = self.nonan_time()

        # Header
        def format_epoch(Y, M, D, h, m, s):
            return '%04d%02d%02d %02d%02d%02d' % (Y, M, D, h, m, s)
        # First epoch
        (fday, fmonth, fyear, fut) = mjd2cal(self.time[0, 1])
        (fhour, fminute, fsecond) = ut2hms(fut)
        first_epoch = format_epoch(fyear, fmonth, fday, fhour, fminute,
                                   fsecond)
        # Last epoch
        (lday, lmonth, lyear, lut) = mjd2cal(self.time[-1, 1])
        (lhour, lminute, lsecond) = ut2hms(lut)
        last_epoch = format_epoch(lyear, lmonth, lday, lhour, lminute, lsecond)
        # Current epoch
        current_epoch = datetime.today()
        release_epoch = format_epoch(current_epoch.year, current_epoch.month,
                                     current_epoch.day, current_epoch.hour,
                                     current_epoch.minute,
                                     current_epoch.second)
        # XYZ reference position
        XYZ0 = '%15.6lf %15.6lf %15.6lf' % tuple(ts.XYZ0)
        # NEU reference position
        NEU0 = '%15.10lf %15.10lf %15.10lf' % tuple(ts.NEU0)
        # Print header
        _print_header(f_pos, ts.code, ts.process, first_epoch, last_epoch,
                      release_epoch, XYZ0, NEU0, ts.ref_frame)

        # Corpus
        # Populate |data_xyz|
        if ts.data_xyz is None:
            ts.dneu2xyz(corr=True, warn=warn)
        # Populate |data_neu|
        if ts.data_neu is None:
            (E, N, U) = xyz2geo(ts.data_xyz[:, 0], ts.data_xyz[:, 1],
                                ts.data_xyz[:, 2])
            ts.data_neu = np.c_[N, E, U]
        # Calendar date and time (hour, minute, second)
        (day, month, year, ut) = mjd2cal(ts.time[:, 1])
        (hour, minute, second) = ut2hms(ut)
        cal = list(map(format_epoch, year, month, day, hour, minute, second))
        # XYZ coordinates
        XYZ = list(map(lambda x: ('%14.5lf %14.5lf %14.5lf %8.5lf %8.5lf '
                                  '%8.5lf %6.3lf %6.3lf %6.3lf') % tuple(x),
                       ts.data_xyz))
        # NEU coordinates
        NEU = list(map(lambda x: '%14.10lf  %14.10lf %10.5lf' % tuple(x),
                       ts.data_neu))
        # dNEU coordinates
        ts.data[:, :3] = ts.data[:, :3]*1e-3
        dNEU = list(map(lambda x: ('%10.5lf%10.5lf%10.5lf   %8.5lf %8.5lf '
                                   '%8.5lf %6.3lf %6.3lf %6.3lf') % tuple(x),
                        ts.data))
        # Print content
        for k in range(ts.time.shape[0]):
            f_pos.write(' %s %10.4lf %s     %s  %s itsa \n'
                        % (cal[k], ts.time[k, 1], XYZ[k], NEU[k], dNEU[k]))


##############################################################################
def _print_header(f_pos, code, process, first_epoch, last_epoch, release_date,
                  XYZ0, NEU0, ref_frame):
    """
    Write header of PBO pos file

    Parameters
    ----------
    f_pos : TextIOWrapper
        File in which to write the header.
    code : str
        Station code (4 letters).
    process: str
        Processing name from which come the data.
    first_epoch : str
        Inital time of the time period (may not correspond to the first
        data point according to the available data).
    last_epoch : str
        Final time of the time period (may not correspond to the last
        data point according to the available data).
    release_date : str
        Time of the file creation.
    XYZ0 : str
        XYZ reference coordinates of the station.
    NEU0 : str
        NEU reference coordinates of the station.
    ref_frame : str
        Reference frame of the saved data.

    """

    f_pos.write(('PBO Station Position Time Series. Reference Frame : %s\n'
                % ref_frame))
    f_pos.write('Format Version: 1.1.0\n')
    f_pos.write('4-character ID: %s\n' % code)
    f_pos.write('Processing    : %s\n' % process)
    f_pos.write('First Epoch   : %s\n' % first_epoch)
    f_pos.write('Last Epoch    : %s\n' % last_epoch)
    f_pos.write('Release Date  : %s\n' % release_date)
    f_pos.write('XYZ Reference position : %s (%s)\n' % (XYZ0, ref_frame))
    f_pos.write('NEU Reference position : %s (%s/WGS84)\n' % (NEU0, ref_frame))
    f_pos.write('Start Field Description\n')
    f_pos.write(('YYYYMMDD      Year, month, day for the given position epoch'
                 '\n'))
    f_pos.write(('HHMMSS        Hour, minute, second for the given position '
                 'epoch\n'))
    f_pos.write(('JJJJJ.JJJJJ   Modified Julian day for the given position '
                 'epoch\n'))
    f_pos.write(('X             X coordinate, Specified Reference Frame, '
                 'meters\n'))
    f_pos.write(('Y             Y coordinate, Specified Reference Frame, '
                 'meters\n'))
    f_pos.write(('Z             Z coordinate, Specified Reference Frame, '
                 'meters\n'))
    f_pos.write('Sx            Standard deviation of the X position, meters\n')
    f_pos.write('Sy            Standard deviation of the Y position, meters\n')
    f_pos.write('Sz            Standard deviation of the Z position, meters\n')
    f_pos.write('Rxy           Correlation of the X and Y position\n')
    f_pos.write('Rxz           Correlation of the X and Z position\n')
    f_pos.write('Ryz           Correlation of the Y and Z position\n')
    f_pos.write(('Nlat          North latitude, WGS-84 ellipsoid, decimal '
                'degrees\n'))
    f_pos.write(('Elong         East longitude, WGS-84 ellipsoid, decimal '
                 'degrees\n'))
    f_pos.write('Height (Up)   Height relative to WGS-84 ellipsoid, m\n')
    f_pos.write(('dN            Difference in North component from NEU '
                'reference position, meters\n'))
    f_pos.write(('dE            Difference in East component from NEU '
                 'reference position, meters\n'))
    f_pos.write(('dU            Difference in vertical component from NEU '
                 'reference position, meters\n'))
    f_pos.write('Sn            Standard deviation of dN, meters\n')
    f_pos.write('Se            Standard deviation of dE, meters\n')
    f_pos.write('Su            Standard deviation of dU, meters\n')
    f_pos.write('Rne           Correlation of dN and dE\n')
    f_pos.write('Rnu           Correlation of dN and dU\n')
    f_pos.write('Reu           Correlation of dE and dU\n')
    f_pos.write('Soln\n')
    f_pos.write('End Field Description\n')
    f_pos.write(('*YYYYMMDD HHMMSS JJJJJ.JJJJ         X             Y         '
                 '    Z            Sx        Sy       Sz     Rxy   Rxz    Ryz '
                 '           NLat         Elong          Height        dN     '
                 '   dE        dU         Sn       Se       Su      Rne    Rnu'
                 '    Reu  Soln\n'))
