"""
    Developed at: ISTerre
    By: Lou MARILL
"""


##################################################################
def write(self, outdir='.', add_key='', replace=False, warn=True):
    """
    Write txt file from Jps catalog

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
        self.check_jps()
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
        txt_file = outdir+os.sep+self.code
        if add_key != '':
            txt_file += '_'+add_key
        txt_file += '.txt'
        if not replace and exists(txt_file):
            raise OSError(('File %s already exist: Jps %s not saved (change '
                           '|add_key| and/or look at |replace| argument).')
                          % (txt_file, self.code))

        # Return
        return warn, txt_file
    #######################################################

    # Check parameters
    (warn, txt_file) = _check_param(self, outdir, add_key, replace, warn)
    
    # Import
    from os import makedirs
    from os.path import isdir
    from datetime import datetime
    import numpy as np
    from itsa.lib.astrotime import mjd2cal, ut2hms
    
    # Output directory
    if not isdir(outdir):
        makedirs(outdir)
        
    # Open txt file
    with open(txt_file, 'w+') as f_txt:
        
        # Sort by increasing time and remove duplicated dates
        self.remove_duplicated_dates(warn=warn)
        
        # Header
        def format_epoch(Y, M, D, h, m, s):
            return '%04d%02d%02d %02d%02d%02d' % (Y, M, D, h, m, s)
        # First epoch
        if self.shape() > 0:
            (fday, fmonth, fyear, fut) = mjd2cal(np.round(self.dates[0, 1], 1))
            (fhour, fminute, fsecond) = ut2hms(fut)
            first_epoch = format_epoch(fyear, fmonth, fday, fhour, fminute,
                                       fsecond)
            # Last epoch
            (lday, lmonth, lyear, lut) = mjd2cal(np.round(self.dates[-1, 1],
                                                          1))
            (lhour, lminute, lsecond) = ut2hms(lut)
            last_epoch = format_epoch(lyear, lmonth, lday, lhour, lminute,
                                      lsecond)
        else:
            first_epoch = ''
            last_epoch = ''
        # Current epoch
        current_epoch = datetime.today()
        release_epoch = format_epoch(current_epoch.year, current_epoch.month,
                                     current_epoch.day, current_epoch.hour,
                                     current_epoch.minute,
                                     current_epoch.second)
        # Print header
        _print_header(f_txt, self.code, self.dco, self.dpost, self.dsse,
                      self.dsw, first_epoch, last_epoch, release_epoch,
                      self.mag_min, self.mag_post, self.mag_spe)
        
        # Corpus
        # Calendar date and time (hour, minute, second)
        if self.shape() > 0:
            (day, month, year, ut) = mjd2cal(np.round(self.dates[:, 1], 1))
            (hour, minute, second) = ut2hms(ut)
            cal = list(map(format_epoch, year, month, day, hour, minute, second))
            # Print content
            for k in range(self.shape()):
                f_txt.write((' %s %10.4lf   %s   %10.4lf %10.4lf %8.1lf    %4.2f'
                             ' %4d\n') % (cal[k], self.dates[k, 1],
                                          self.type_ev[k], self.coords[k, 0],
                                          self.coords[k, 1], self.coords[k, 2],
                                          self.mag[k], self.dur[k]))
   
        
##############################################################################
def _print_header(f_txt, code, dco, dpost, dsse, dsw, first_event, last_event,
                  release_date, mag_min, mag_post, mag_spe):
    """
    Write header for Jps text file

    Parameters
    ----------
    f_txt : TextIOWrapper
        File in which to write the header.
    code : str
        Station code (4 letters).
    dco : int or float
        Influence radius parameter for earthquakes.
    dpost : int or float
        Influence radius parameter for post-seismic effects.
    dsse : int or float
        Influence radius parameter for SSEs.
    dsw : int or float
        Influence radius parameter for swarms.
    first_event : str
        Time of the first Jps event.
    last_event : str
        Time of the last Jps event.
    release_date : str
        Time of the file creation.
    mag_min : int or float
        Minimum magnitude of accounted events.
    mag_post : int or float
        Minimum magnitude of earthquake to consider post-seismic effect.
    mag_spe : None, int or float
        Minimum magnitude of earthquake to consider special post-seismic
        effect.
        If None: no earthquake is considered with special post-seismic.

    """
    
    f_txt.write('Station Seismic and Aseismic Event Catalog.\n')
    f_txt.write('4-character ID            : %s\n' % code)
    f_txt.write(('Influence radius parameter: Earthquake: %g, Post-seismic: '
                 '%g,\n                            SSE: %g, and Swarm: %g\n')
                % (dco, dpost, dsse, dsw))
    f_txt.write('First event               : %s\n' % first_event)
    f_txt.write('Last event                : %s\n' % last_event)
    f_txt.write('Release date              : %s\n' % release_date)
    f_txt.write('Minimum magnitude         : %g, Post-seismic: %g' 
                % (mag_min, mag_post))
    if mag_spe is not None:
        f_txt.write(', Special: %g' % mag_spe)
    f_txt.write('\n')
    f_txt.write('Start Field Description\n')
    f_txt.write('YYYYMMDD      Year, month, day for the given event\n')
    f_txt.write('HHMMSS        Hour, minute, second for the given event\n')
    f_txt.write('JJJJJ.JJJJJ   Modified Julian day for the given event\n')
    f_txt.write(("T             Type of event: 'U': Unknown, 'A': Antenna "
                 "change,\n                             'E': Earthquake, 'P': "
                 "Post-seismic earthquake,\n                             'S': "
                 "SSE, and 'W': Swarm\n"))
    f_txt.write(('Nlat          North latitude, WGS-84 ellipsoid, decimal '
                'degrees\n'))
    f_txt.write(('Elong         East longitude, WGS-84 ellipsoid, decimal '
                 'degrees\n'))
    f_txt.write('Up            Depth relative to WGS-84 ellipsoid, km\n')
    f_txt.write('Mag           Moment magnitude\n')
    f_txt.write('Dur           Duration, days\n')
    f_txt.write('End Field Description\n')
    f_txt.write('*YYYYMMDD HHMMSS JJJJJ.JJJJ   T        Nlat      Elong       '
                'Up      Mag  Dur\n')
