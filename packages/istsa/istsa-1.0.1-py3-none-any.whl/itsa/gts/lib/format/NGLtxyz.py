"""
    Developed at: ISTerre
    By: Lou MARILL
"""

###############################################################################
def read_NGLtxyz(self, tsdir='.', tsfile=None, ref_frame='Unkown',
                 process='Nevada Geodetic Laboratory', neu=False,
                 other_pos_name=None, pos_type='PBO', warn=True):
    """
    Read the Nevada Geodetic Laboratory (NGL) pos file and load the times 
    series into Gts object

    Parameters
    ----------
    tsdir : str, optional
        Directory of the file to be readed.
        The default is '.'.
    tsfile : str, optional
        Pos file from NGL processing to be readed.
        The default is None: |read_NGTtxyz| look for '|self.code|*.txyz2' file.
    ref_frame : str, optional
        Reference frame of NGL processing.        
        The default is 'Unkown'.
    process : str, optional
        Processing used to get the solution.
        The default is 'NGL'.
    neu : bool, optional
        Populate |data_neu| if true.
        The default is False.
    other_pos_name : None or str, optional
        Find the other name of the station from the |other_pos_name| folder.
        The default is None.
    pos_type : 'PBO', 'GX' or 'F3', optional
        Used only if |other_pos_name is not None|.
        Determine the type of pos files to read in |other_pos_name|.
            'PBO': PBO pos files
            'GX': GipsyX pos files
            'F3': F3 pos files
        The default is 'PBO'.
    warn : bool, optional
        Print warnings if true.
        The default is True.

    Raises
    ------
    GtsTypeError
        If |self.code| is not str.
    GtsValueError
        If |self.code| does not have exactly 4 letters.
    TypeError
        If any parameter does not have the right type.
    ValueError
        If |pos_type| is not 'PBO', 'GX' nor 'F3'.
    WARNING
        If |neu| is not bool: |neu| set to False.
        If there is no equivalent pos file in |other_pos_name|
    
    !!! Warning (for Japan)
    -----------
    NGL station do not have the same name as Japanese Rinex files. To match the
    names, you need put into |other_sta_name| the folder with pos file with the
    wanted used name. The pos files need to be in PBO format or the folder need
    to finish with 'GX' for the GipsyX pos files, or 'F3' for the F3 pos files
    (as the read functions are not identical).
    - Advise: Name your folder with GipsyX pos files 'POS_FILES_GX' and put
    other_sta_name='POS_FILES_GX'|
    - NB: If your stations are not in Japan, this particularity of NGL code
    station may not apply. In this case, let |other_sta_name=None|

    Note
    ----
    With this function the information of |code|, |time|, |data|, |t0|, |XYZ0|,
    |NEU0|, |ref_frame|, |data_xyz| and |in_file| will be populated in |ts|
    (and |data_neu| if asked)

    """

    ##############################################################
    def _check_param(self, tsdir, tsfile, ref_frame, process, neu,
                     other_pos_name, pos_type, warn):
        """
        Raise error if one parameter is invalid and adapt some parameter values
        """
        # Import
        from itsa.gts.errors import GtsTypeError, GtsValueError
        from itsa.lib.modif_vartype import adapt_bool

        # Check
        # |self.code|
        if not isinstance(self.code, str):
            raise GtsTypeError(('Gts |code| must be str: '
                                '|type(self.code)=%s|.') % type(self.code))
        if len(self.code) != 4:
            raise GtsValueError(('Gts |code| must have exactly 4 letters: '
                                 '|len(self.code)=%d|.') % len(self.code))
        # |tsdir|
        if not isinstance(tsdir, str):
            raise TypeError(('Directory must be str: '
                             '|type(tsdir)=%s|.') % type(tsdir))
        # |tsfile|
        if tsfile is not None and not isinstance(tsfile, str):
            raise TypeError(('File must be given in str: '
                             '|type(tsfile)=%s|.') % type(tsfile))
        # |ref_frame|
        if not isinstance(ref_frame, str):
            raise TypeError(('Reference frame must be str: '
                             '|type(ref_frame)=%s|.') % type(ref_frame))
        # |process|
        if not isinstance(process, str):
            raise TypeError(('Processing name must be str: '
                             '|type(process)=%s|.') % type(process))
        # |other_pos_name|
        if other_pos_name is not None and not isinstance(other_pos_name, str):
            raise TypeError(('Directory to find other station names must be '
                             'str: |type(other_pos_name)=%s|.')
                            % type(other_pos_name))
        # |pos_type|
        if (other_pos_name is not None and 
            pos_type.upper() not in ['PBO', 'GX', 'F3']):
            raise ValueError(("Type of pos files to read must be 'PBO', 'GX' "
                              "or 'F3': |pos_type=%s|.") % pos_type)

        # Adapt
        # |neu|
        (neu, warn_neu) = adapt_bool(neu)
        # |warn|
        (warn, _) = adapt_bool(warn, True)

        # Warning
        if warn and warn_neu:
            print('[WARNING] from method [read_NGLtxyz] in [%s]:' % __name__)
            print('\t|neu| parameter set to False because |type(neu)!=bool|!')
            print('\tGts %s |data_neu| will not be populated!' % self.code)
            print()

        # Return
        return neu, warn
    ##############################################################

    # Check parameters
    (neu, warn) = _check_param(self, tsdir, tsfile, ref_frame, process, neu,
                               other_pos_name, pos_type, warn)

    # Import
    import numpy as np
    import os
    from os.path import abspath
    from itsa.lib.astrotime import decyear2mjd
    from itsa.lib.coordinates import xyz2geo

    # Name of the file
    if tsfile is None:
        pos_file = tsdir+os.sep+self.code.upper()+'.txyz2'
    else:
        pos_file = tsdir+os.sep+tsfile
    self.in_file = abspath(pos_file)

    # Read data
    data = np.genfromtxt(pos_file)
    # Ensure 2D array
    if data.ndim == 1:
        data = np.array([data])

    # Populate
    # Make time array
    self.time = np.c_[data[:, 2], decyear2mjd(data[:, 2])]
    # Make data array
    self.data_xyz = data[:, 3:-1]
    # Reference variables
    self.t0 = self.time[0, :]
    self.XYZ0 = self.data_xyz[0, :3]
    (E0, N0, U0) = xyz2geo(self.XYZ0[0], self.XYZ0[1], self.XYZ0[2])
    self.NEU0 = np.array([N0, E0, U0])
    self.ref_frame = ref_frame
    self.process = process
    # Make dN, dE, dU data array
    self.xyz2dneu(corr=True, warn=warn)
    
    # Populate if asked
    if neu:
        from itsa.lib.coordinates import xyz2geo
        (lon, lat, h) = xyz2geo(
            self.data_xyz[:, 0], self.data_xyz[:, 1], self.data_xyz[:, 2])
        self.data_neu = np.c_[lat, lon, h]

    # Order by increasing time
    self.reorder()

    # Look at other name of the station if asked
    if other_pos_name is not None:
        from glob import glob
        from itsa.gts.Gts import Gts

        # Get station files
        pos_files = glob(other_pos_name+os.sep+'*.pos')
        if len(pos_files) > 0:
            # Get station names and coordinates
            (sta, coords) = _read_ref_coords(pos_files, pos_type)
            # Find nearest station in |sta|
            dist = np.sum(np.abs(coords-self.XYZ0), axis=1)
            code_sta = sta[dist == np.min(dist)][0]

            # Verify |sta| and |code_sta| are the same station
            ts = Gts(code_sta)
            if pos_type == 'GX':
                ts.read_GXpos(other_pos_name)
            elif pos_type == 'F3':
                ts.read_F3pos(other_pos_name)
            else:
                ts.read_PBOpos(other_pos_name)

            if ts.t0[0] < self.t0[0]:
                date = np.abs(ts.time[:, 0]-self.t0[0])
                dist_date = np.sum(
                    np.abs(ts.data_xyz[date == np.min(date), :3]-self.XYZ0),
                    axis=1
                    )
            else:
                date = np.abs(self.time[:, 0]-ts.t0[0])
                dist_date = np.sum(
                    np.abs(self.data_xyz[date == np.min(date), :3]-ts.XYZ0),
                    axis=1
                    )

            # Change station code if verification OK
            if dist_date < 10:
                self.code = code_sta

        # Warnings
        if warn and (len(pos_files) == 0 or dist_date >= 10):
            print('[WARNING] from method [read_NGLtxyz] in [%s]' % __name__)
            if len(pos_files) == 0:
                print('\tThere are no pos file in %s!' % other_pos_name)
            elif dist_date >= 10:
                print('\tGts %s as no equivalent in %s!' %
                      (self.code, other_pos_name))
            print('\tGts %s |code| has not been changed!' % self.code)
            print()


################################################
def _read_ref_coords(pos_files, pos_type='PBO'):
    """
    Read the reference coordinates for all the files in |pos_files|

    Parameters
    ----------
    pos_files : list
        List of all the pos files.
    pos_type : str, optional
        If 'GX': pos files to read are GipsyX solutions,
        If 'F3': pos files to read are F3 solutions,
        Else: pos files to read are PBO pos.
        The default is 'PBO'.

    Returns
    -------
    sta : np.ndarray
        List of the station codes.
    coords : np.ndarray
        XYZ coordinates of the stations in |sta|.

    """

    # Import
    import numpy as np
    import os
    from linecache import getline

    # Change type
    if isinstance(pos_files, list):
        pos_files = np.array(pos_files)

    # Read
    if isinstance(pos_files, np.ndarray):
        pos_type = np.repeat(pos_type, len(pos_files))
        res = np.array(list(map(_read_ref_coords, pos_files, pos_type)),
                       dtype='U4,3f')
        sta = res['f0']
        coords = res['f1']
    else:
        sta = pos_files.split(os.sep)[-1][:4]
        if pos_type == 'GX':
            coords = np.array(getline(pos_files, 2).split()[3:6], dtype=float)
        elif pos_type == 'F3':
            with open(pos_files, 'r', errors='ignore') as data_file:
                for k in range(21):
                    line = data_file.readline()
            coords = np.array(line.split()[4:7], dtype=float)
        else:
            coords = np.array(getline(pos_files, 8).split(':')[-1].split()[:3],
                              dtype=float)

    # Return
    return sta, coords
