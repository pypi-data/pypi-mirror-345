"""
    Read and write G and MOD files from Gts

    ----
    Developed at: ISTerre
    By: Lou MARILL
"""

import shutil
from pathlib import Path

##############################################################
def read_GMOD(self, tsdir_G='.', tsdir_MOD='.', tsfile_G=None,
              tsfile_MOD=None):
    """
    Read G matrix and model files to populate given Gts object

    Parameters
    ----------
    tsdir_G : str, optional
        Directory of the G matrix file to be readed.
        The default is '.'.
    tsdir_MOD : str, optional
        Directory of the model file to be readed.
        The default is '.'.
    tsfile_G : str, optional
        G matrix text file to be readed.
        The default is None: |read_GMOD| look for '|self.code|*.txt' file.
    tsfile_MOD : str, optional
        Model text file to be readed.
        The default is None: |read_GMOD| look for '|self.code|*.txt' file.
        
    Raises
    ------
    TypeError
        If any parameter does not have the right type.
    GtsError
        If readed G matrix or model is incompatible with |self| Gts.

    """
    
    #################################################################
    def _check_param(self, tsdir_G, tsdir_MOD, tsfile_G, tsfile_MOD):
        """
        Raise error is one parameter is invalid and adapt some parameter values
        """
        # Check
        # |self|
        self.check_gts()
        # |tsdir_G|
        if not isinstance(tsdir_G, str):
            raise TypeError(('G matrix directory must be str: '
                             '|type(tsdir_G)=%s|.') % type(tsdir_G))
        # |tsdir_MOD|
        if not isinstance(tsdir_MOD, str):
            raise TypeError(('Model directory must be str: '
                             '|type(tsdir_MOD)=%s|.') % type(tsdir_MOD))
        # |tsfile_G|
        if tsfile_G is not None and not isinstance(tsfile_G, str):
            raise TypeError('G matrix file must be str: |type(tsfile_G)=%s|.'
                            % type(tsfile_G))
        # |tsfile_MOD|
        if tsfile_MOD is not None and not isinstance(tsfile_MOD, str):
            raise TypeError('Model file must be str: |type(tsfile_MOD)=%s|.'
                            % type(tsfile_MOD))
    ################################################################

    # Check parameters
    _check_param(self, tsdir_G, tsdir_MOD, tsfile_G, tsfile_MOD)
    
    # Import
    from itsa.gts.errors import GtsError
    
    # Populate |G|
    # Read |G|
    (file_G, time_G, G, names_G) = _read_G(self.code, tsdir_G, tsfile_G)
    # Check |G| dimension with |self.time| 
    if G.shape[0] != self.time.shape[0]:
        raise GtsError(('G matrix from %s does not correspond to Gts %s '
                        '|time| dimension (|G| and |time| must have the same '
                        'number of lines to be part of the same Gts object): '
                        '|G.shape[0]=%d| and |self.time.shape[0]=%d|.\nCheck '
                        'you give the right G file.')
                       % (file_G, self.code, G.shape[0], self.time.shape[0]))
    # Populate
    self.G = G
    self.GMOD_names = names_G
    
    # Populate |MOD|
    # Read |MOD|
    (file_MOD, MOD, names_MOD) = _read_MOD(self.code, tsdir_MOD, tsfile_MOD)
    # Check |MOD| dimensions with |G|
    if MOD.shape[0] != G.shape[1]:
        raise GtsError(('Model from %s does not correspond to Gts %s |G| '
                        'dimension (|MOD| must have the same number of lines '
                        'than the number of columns of |G| to be part of the '
                        'same Gts object): |MOD.shape[0]=%d| and '
                        '|self.G.shape[1]=%d|.\nCheck you give the right MOD '
                        'file.') % (file_MOD, self.code, MOD.shape[0],
                                    self.G.shape[1]))
    # Check |MOD_names| with |MOD_G|
    if (names_MOD != self.GMOD_names).any():
        raise GtsError(('Model parameter names from %s does not correspond to '
                        'Gts %s |GMOD_names| (|MOD| and |G| component names '
                        'must be identical to be part of the same Gts object):'
                        ' |names_MOD=%s| and |self.GMOD_names=%s|.\nCheck you '
                        'give the right MOD file.')
                       % (file_MOD, self.code, names_MOD, self.GMOD_names))
    # Populate
    self.MOD = MOD
   
    
##########################################
def _read_G(code, tsdir='.', tsfile=None):
    """
    Read G matrix file

    Parameters
    ----------
    code : Station code to find |code|*.txt file
        Station code to find CODE*.txt file.
    tsdir : str, optional
        Directory of the G matrix file to be readed.
        The default is '.'.
    tsfile : str, optional
        G matrix text file to be readed.
        The default is None: |read_GMOD| look for '|code|*.txt' file.

    Raise
    -----
    FileNotFoundError
        If there is no '|code|*.txt' file in |tsdir|.

    Returns
    -------
    txt_file : str
        Name of G matrix file readed.
    time: np.ndarray
        Time vector associted to the G matrix.
    G: np.ndarray
        G matrix.
    names : np.ndarray
        Names of G matrix component.

    """
    
    # Import
    import numpy as np
    import os
    from linecache import getline
    
    # Name of the file - if not provided, tries to guess
    if tsfile is None:
        from glob import glob
        txt_file = glob(tsdir+os.sep+code.upper()+'*.txt')
        if len(txt_file) == 0:
            raise FileNotFoundError('No file %s/%s*.txt was found.'
                                    % (tsdir, code.upper()))
        txt_file = txt_file[0]
    else:
        txt_file = tsdir+os.sep+tsfile
    
    # Read array data
    # Read all data
    data = np.genfromtxt(txt_file, skip_header=14)
    # Ensure 2D array
    if data.ndim == 1:
        data = data.reshape(-1, 1)
    
    # Read columns names
    names = np.array(getline(txt_file, 14).split()[3:])
    
    # Return
    return txt_file, data[:, 2], data[:, 3:], names
    

###########################################
def _read_MOD(code, tsdir='.', tsfile=None):
    """
    Read model file

    Parameters
    ----------
    code : Station code to find |code|*.txt file
        Station code to find CODE*.txt file.
    tsdir : str, optional
        Directory of the model file to be readed.
        The default is '.'.
    tsfile : str, optional
        Model text file to be readed.
        The default is None: |read_GMOD| look for '|code|*.txt' file.

    Raise
    -----
    FileNotFoundError
        If there is no '|code|*.txt' file in |tsdir|.

    Returns
    -------
    txt_file : str
        Name of model file readed.
    MOD: np.ndarray
        Model matrix.
    names : np.ndarray
        Names of model component.

    """
    
    # Import
    import numpy as np
    import os
    
    # Name of the file - if not provided, tries to guess
    if tsfile is None:
        from glob import glob
        txt_file = glob(tsdir+os.sep+code.upper()+'*.txt')
        if len(txt_file) == 0:
            raise FileNotFoundError('No file %s/%s*.txt was found.'
                                    % (tsdir, code.upper()))
        txt_file = txt_file[0]
    else:
        txt_file = tsdir+os.sep+tsfile
        
    # Read array data
    # Read all data
    data = np.genfromtxt(txt_file, skip_header=17, dtype=str)
    # Ensure 2D array
    if data.ndim == 1:
        data = data.reshape(-1, 1)
    
    # Return
    return txt_file, data[:, 1:].astype(float), data[:, 0]
        

###############################################################################
def make_GMOD_names(self, names_longt, tau_post=100, tau_spe=1, pre_post=False,
                    warn=True):
    """
    Populate Gts |GMOD_names| corresponding to |G| and |MOD| component names

    Parameters
    ----------
    names_longt : list, np.ndarray
        Names for the long-term phenomena whithin |G|
        (Jps event effects will be directly named from |self.jps|).
    tau_post : int, optional
        Used whithin post-seismic effect names.
        The default is 100.
    tau_spe : TYPE, optional
        Used only if |self.jps.mag_spe| is not None.
        Used whithin post-seismic effect names.
        The default is 1.
    pre_post : bool or int, optional
        Need to be True if post-seismic before the time window was taken into
        account to have the right number of names according to |G| and |MOD|
        components.
        The default is False.
    warn : bool, optional
        Print warnings if true.
        The default is True.

    Raises
    ------
    TypeError
        If any parameter does not have the right type.
    ValueError
        If |tau_post| or |tau_spe| is not positive.
    WARNING
        If |pre_post| is not bool nor int: |pre_post| set to False.
        If |self.GMOD_names| already populated: pass the method.

    """
    
    #######################################################################
    def _check_param(self, names_longt, tau_post, tau_spe, pre_post, warn):
        """
        Raise error if one parameter is invalid and adapt some parameter values
        """
        # Import
        import numpy as np
        from itsa.lib.modif_vartype import list2ndarray
        
        # Change type
        # |names_longt|
        if isinstance(names_longt, list):
            (names_longt, err_names) = list2ndarray(names_longt)
            if err_names:
                raise ValueError(('Long-term phenomena names list must be '
                                  'convertible into np.ndarray: '
                                  '|names_longt=%s|.') % str(names_longt))
                
        # Check
        # |self|
        self.check_gts()
        # |names_longt|
        if not isinstance(names_longt, np.ndarray):
            raise TypeError(('Long-term phenomena names must be list or '
                             'np.ndarray: |type(names_longt)=%s|.')
                            % type(names_longt))
        if names_longt.dtype != str and 'U' not in str(names_longt.dtype):
            raise ValueError(('Long-term phenomena names must be list of str '
                              'or str np.ndarray: |names_longt.dtype=%s|.')
                             % names_longt.dtype)
        # |tau_post|
        if not isinstance(tau_post, int):
            raise TypeError('Relaxation time must be int: |type(tau_post)=%s|.'
                            % type(tau_post))
        if tau_post <= 0:
            raise ValueError(('Relaxation time must be positive (and not 0): '
                              '|tau_post=%d|.') % tau_post)
        # |tau_spe|
        if self.jps.mag_spe is not None:
            if not isinstance(tau_spe, int):
                raise TypeError(('Relaxation time for special events must be '
                                 'int: |type(tau_spe)=%s|.') % type(tau_spe))
            if tau_spe <= 0:
                raise ValueError(('Relaxation time for special events be '
                                  'positive (and not 0): |tau_spe=%d|.')
                                 % tau_spe)
                
        # Adapt
        # |pre_post|
        if not isinstance(pre_post, (bool, int)):
            pre_post = False
            warn_post = True
        else:
            warn_post = False
        
        # Warning
        if warn and warn_post:
            print('[WARNING] from method [make_GMOD_names] in [%s]:' 
                  % __name__)
            print(('\t|pre_post| parameter set to False because '
                   '|type(pre_post)!=bool| and |type(pre_post)!=int|!'))
            print(('\tPost-seismic before the time period will not be '
                   'taking into account!'))
            print()
            
        # Return
        return pre_post
    #######################################################################
                    
    # Check parameters
    from itsa.lib.modif_vartype import adapt_bool
    (warn, _) = adapt_bool(warn, True)
    if self.GMOD_names is not None:
        print('[WARNING] from method [make_GMOD_names] in [%s]:' 
              % __name__)
        print(('\t|self.GMOD_names| already populated!'))
        print(('\tMethod [make_GMOD_names] does not apply new names!'))
        print()
        return
    pre_post = _check_param(self, names_longt, tau_post, tau_spe, pre_post,
                            warn)
    
    # Import
    import numpy as np
    from itsa.lib.astrotime import mjd2cal
    
    # Jps event names
    if self.jps.shape() == 0:
        names_jps = np.array([])
        sort_names_jps = np.array([])
    else:
        # Consider post-seismic
        idx_ok = np.where((self.MOD[:self.jps.shape(), :3]!=0).any(axis=1))[0]  
        if pre_post:
            idx = np.array(range(1,self.jps.shape()))
            idx_ok = idx_ok[idx_ok<self.jps.shape()-1]
            idx_ok = [0]+list(idx_ok+1)
        else:
            idx = np.array(range(0,self.jps.shape()))
        # Jps names format
        def format_names_jps(T, D, M, Y):
            return 'J%04d%02d%02d_%s' % (Y, M, D, T)
        # Jps event names
        if len(idx) > 0:
            (jps_day, jps_month, jps_year, _) = mjd2cal(self.jps.dates[idx, 1])
            names_jps = list(map(format_names_jps, self.jps.type_ev[idx],
                                 jps_day, jps_month, jps_year))
        else:
            names_jps = []
        # Post-seismic effects
        if len(idx_ok) > 0:
            jps_ok = self.jps.select_ev(idx_ok)
            jps_post = jps_ok.select_ev(jps_ok.type_ev=='P')
            if jps_post.shape() > 0:
                (post_day, post_month, post_year, _) = mjd2cal(
                    jps_post.dates[:, 1])
                names_post = list(map(format_names_jps, jps_post.type_ev, post_day,
                                      post_month, post_year))
                nb_c_tau = max(len(str(tau_post)), len(str(tau_spe)))
                tau_str = ('%0'+str(nb_c_tau)+'d') % tau_post
                names_post = np.char.add(names_post,
                                         np.repeat(tau_str, len(names_post)))
                names_jps += list(names_post)
                # Special post-seismic effects
                if jps_post.mag_spe is not None:
                    idx_spe = np.where(jps_post.mag>=jps_post.mag_spe)[0]
                    if pre_post:
                        idx_spe = idx_spe[idx_spe>0]
                    if len(idx_spe) > 0:
                        names_spe = names_post[idx_spe].astype('<U11')
                        tau_str = ('%0'+str(nb_c_tau)+'d') % tau_spe
                        names_spe = np.char.add(names_spe,
                                                np.repeat(tau_str,len(names_spe)))
                        names_jps += list(names_spe)
        # Sort names by dates order
        sort_names_jps = np.argsort(names_jps)
        names_jps = np.array(names_jps)[sort_names_jps]
   
    # Add long-term phenomena names
    names = np.hstack((names_longt, names_jps))
    self.GMOD_names = names    
   
    # Sort |MOD| and |G| according to |GMOD_names|
    sort_names = np.hstack((np.array(range(len(names_longt)))+len(names_jps),
                            sort_names_jps)).astype(int)
    self.MOD = self.MOD[sort_names, :]
    self.G = self.G[:, sort_names]
    
    # Check the names
    self.check_gts()
    
    
#######################################################################
def write_Gtxt(self, outdir='.', add_key='', replace=False, warn=True):
    """
    Write G matrix text file from Geodetic time series (Gts)

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
        from itsa.gts.errors import GtsError
        from itsa.lib.modif_vartype import adapt_bool

        # Check
        # |self|
        self.check_gts()
        if self.GMOD_names is None:
            raise GtsError(('Gts %s |GMOD_name| must be populated to write '
                            '|G| text file.'))
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
            print('[WARNING] from method [write_Gtxt] in [%s]' % __name__)
            print('\t|replace| set to False because |type(replace)!=bool|!')
            print('\tNo file will be replaced in the output directory!')

        # Replace?
        txt_file = outdir+os.sep+self.code
        if add_key != '':
            txt_file += '_'+add_key
        txt_file += '.txt'
        if not replace and exists(txt_file):
            raise OSError(('File %s already exist: Gts %s |G| not saved '
                           '(change |add_key| and/or look at |replace| '
                           'argument).') % (txt_file, self.code))

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
    
        # Sort by increasing time, remove duplicated dates and NaN values
        self.remove_duplicated_dates(warn=warn)
        
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
        # Print header
        format_G = _print_G_header(f_txt, self.code, first_epoch, last_epoch,
                                   release_epoch, self.GMOD_names)
        
        # Corpus
        # Calendar date and time (hour, minute, second)
        (day, month, year, ut) = mjd2cal(np.round(self.time[:, 1], 1))
        (hour, minute, second) = ut2hms(ut)
        cal = list(map(format_epoch, year, month, day, hour, minute, second))
        # G content
        G_str = list(map(lambda x: format_G % tuple(x), self.G))
        # Print content
        for k in range(self.G.shape[0]):
            f_txt.write(' %s %10.4lf %s\n' % (cal[k], self.time[k, 1],
                                              G_str[k]))
            
        
###############################################################################
def _print_G_header(f_txt, code, first_epoch, last_epoch, release_date, names):
    """
    Write header of G matrix text file

    Parameters
    ----------
    f_txt : TextIOWrapper
        File in which to write the header.
    code : str
        Station code (4 letters).
    first_epoch : str
        Inital time of the time period (first data).
    last_epoch : str
        Final time of the time period (last data).
    release_date : str
        Time of the file creation.
    names : list or np.ndarray
        G matrix component (columns) names

    Return
    ------
    format_G : str
        Format used for G matrix data while writing the corpus (made according
        to the length of each component name).

    """
    
    f_txt.write("Station Associated Green's functions.\n")
    f_txt.write('4-character ID: %s\n' % code)
    f_txt.write('First Epoch   : %s\n' % first_epoch)
    f_txt.write('Last Epoch    : %s\n' % last_epoch)
    f_txt.write('Release Date  : %s\n' % release_date)
    f_txt.write('Start Field Description\n')
    f_txt.write('YYYYMMDD         Year, month, day for each epoch\n')
    f_txt.write('HHMMSS           Hour, minute, second for each epoch\n')
    f_txt.write('JJJJJ.JJJJJ      Modified Julian day for each epoch\n')
    f_txt.write(('Functions names: Cst: Constant; Vel: Velocity; '
                 '(Acc: Acceleration;)\n                 An: Annual seasonal '
                 'variations; Sm: semi-annual variations;\n                 '
                 'JYYYYMMDD_T: Jps at DD/MM/YYYY of type T (for post-seismic, '
                 'number after = relaxation parameter)\n'))
    f_txt.write('End Field Description\n')
    fields = '*YYYYMMDD HHMMSS JJJJJ.JJJJ '
    format_G = ''
    for k in range(len(names)):
        if len(names[k]) > 10:
            fields += ' %s'
            format_G += ' %'+str(len(names[k]))+'.5f'
        else:
            for l in range(10-len(names[k])+1):
                fields += ' '
            fields += '%s'
            format_G += ' %10.5f'
    fields += '\n'
    f_txt.write(fields % tuple(names))
    
    return format_G


#########################################################################
def write_MODtxt(self, outdir='.', add_key='', replace=False, warn=True):
    """
    Write model text file from Geodetic time series (Gts)

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
        from itsa.gts.errors import GtsError
        from itsa.lib.modif_vartype import adapt_bool

        # Check
        # |self|
        self.check_gts()
        if self.GMOD_names is None:
            raise GtsError(('Gts %s |GMOD_name| must be populated to write '
                            '|MOD| text file.'))
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
            print('[WARNING] from method [write_Gtxt] in [%s]' % __name__)
            print('\t|replace| set to False because |type(replace)!=bool|!')
            print('\tNo file will be replaced in the output directory!')

        # Replace?
        txt_file = outdir+os.sep+self.code
        if add_key != '':
            txt_file += '_'+add_key
        txt_file += '.txt'
        if not replace and exists(txt_file):
            raise OSError(('File %s already exist: Gts %s |G| not saved '
                           '(change |add_key| and/or look at |replace| '
                           'argument).') % (txt_file, self.code))

        # Return
        return warn, txt_file
    #######################################################

    # Check parameters
    (warn, txt_file) = _check_param(self, outdir, add_key, replace, warn)
    
    # Import
    from os import makedirs
    from os.path import isdir
    from datetime import datetime
    from itsa.lib.astrotime import mjd2cal, ut2hms
    
    # Output directory
    if not isdir(outdir):
        makedirs(outdir)
        
    # Open txt file
    with open(txt_file, 'w+') as f_txt:
    
        # Sort by increasing time, remove duplicated dates and NaN values
        self.remove_duplicated_dates(warn=warn)
        
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
        # Print header
        nb_c_names = max(list(map(len, self.GMOD_names)))
        _print_MOD_header(f_txt, self.code, first_epoch, last_epoch,
                          release_epoch, nb_c_names)
        
        # Corpus
        for k in range(self.MOD.shape[0]):
            param = '%s' % self.GMOD_names[k]
            for s in range(nb_c_names-len(self.GMOD_names[k])):
             param += ' '
            f_txt.write(' %s  %12.5f %12.5f %12.5f  %10.5f %10.5f %10.5f\n'
                        % (param, self.MOD[k, 0], self.MOD[k, 1],
                           self.MOD[k, 2], self.MOD[k, 3], self.MOD[k, 4],
                           self.MOD[k, 5]))

    if str(Path(outdir).name) == "MODEL_AMP" and str((Path(outdir).parent).name) == "OUTPUT_FILES":
        file = str(Path(txt_file).name)
        extension = file.split(".")[-1]
        name = file.split(".")[0]
        shutil.copy(txt_file, f"{str((Path(outdir).parent).parent)}/{name}_parameters.{extension}")
            
#########################################################################
def _print_MOD_header(f_txt, code, first_epoch, last_epoch, release_date,
                      nb_c_names):
    """
    Write header for model text file

    Parameters
    ----------
    f_txt : TextIOWrapper
        File in which to write the header.
    code : str
        Station code (4 letters).
    first_epoch : str
        Inital time of the time period.
    last_epoch : str
        Final time of the time period.
    release_date : str
        Time of the file creation.
    nb_c_names : int
        Maximum number of characters whithin the components names (writing in
                                                                   the corpus).

    """
    
    f_txt.write("Station Model Amplitude (for Green's functions).\n")
    f_txt.write('4-character ID: %s\n' % code)
    f_txt.write('First Epoch   : %s\n' % first_epoch)
    f_txt.write('Last Epoch    : %s\n' % last_epoch)
    f_txt.write('Release Date  : %s\n' % release_date)
    f_txt.write('Start Field Description\n')
    f_txt.write(('Param           Parameter names: Cst: Constant; Vel: '
                 'Velocity; (Acc: Acceleration;)\n                An: Annual '
                 'seasonal variations; Sm: semi-annual variations;\n'
                 '                JYYYYMMDD_T: Jps at DD/MM/YYYY of type T '
                 '(for post-seismic, number after = relaxation parameter)\n'))
    f_txt.write('dN              Amplitude in North component, millimeters\n')
    f_txt.write('dE              Amplitude in East component, millimeters\n')
    f_txt.write('dU              Amplitude in vertical component, millimeters\n')
    f_txt.write('Sn              Error on dN, millimeters\n')
    f_txt.write('Se              Error on dE, millimeters\n')
    f_txt.write('Su              Error on dU, millimeters\n')
    f_txt.write('End Field Description\n')
    fields = '*Param'
    for k in range(nb_c_names-5):
        fields += ' '
    fields += ('         dN           dE           dU           Sn         Se'
               '         Su\n')
    f_txt.write(fields)
