"""
    Developed at: ISTerre
    By: Lou MARILL
"""

##################################################################
def read_F3pos(self, tsdir='.', tsfile=None, ref_frame='ITRF2005',
               process='F3', neu=False, warn=True):
    """
    Read F3 solution pos file and load the time series into Gts object

    Parameters
    ----------
    tsdir : str, optional
        Directory of the file to be readed.
        The default is '.'.
    tsfile : str, optional
        Pos file from of F3 solution to be readed.
        The default is None: |read_F3pos| look for '|self.code|*.pos' file.
    ref_frame : str, optional
        Reference frame of F3 solution.
        The default is 'ITRF2005'.
    process : str, optional
        Processing used to get the solution.
        The default is 'F3'.
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
    WARNING
        If |neu| is not bool: |neu| set to False.
    
    Note
    ----
    With this function the information of |code|, |time|, |data|, |t0|, |XYZ0|,
    |NEU0|, |ref_frame|, |data_xyz| and |in_file| will be populated in |ts|
    (and |data_neu| if asked)

    """

    #####################################################################
    def _check_param(self, tsdir, tsfile, ref_frame, process, neu, warn):
        """
        Raise error is one parameter is invalid and adapt some parameter values
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

        # Adapt
        # |neu|
        (neu, warn_neu) = adapt_bool(neu)
        # |warn|
        (warn, _) = adapt_bool(warn, True)

        # Warning
        if warn and warn_neu:
            print('[WARNING] from method [read_F3pos] in [%s]:' % __name__)
            print('\t|neu| parameter set to False because |type(neu)!=bool|!')
            print('\tGts %s |data_neu| will not be populated!' % self.code)
            print()

        # Return
        return neu
    #####################################################################

    # Check parameters
    neu = _check_param(self, tsdir, tsfile, ref_frame, process, neu, warn)

    # Import
    import numpy as np
    import os
    from os.path import abspath
    from itsa.lib.astrotime import cal2decyear, decyear2mjd
    from itsa.lib.coordinates import xyz2geo

    # Name of the file
    if tsfile is None:
        pos_file = os.path.join(tsdir, self.code.upper(), '.pos')
    else:
        pos_file = os.path.join(tsdir, tsfile)
    self.in_file = abspath(pos_file)

    # Read data
    t, x, y, z = [], [], [], []
    k = 0
    # Special characters prevent pre-existing reading function to work
    with open(pos_file, 'r', errors='ignore') as data_file:
        for line in data_file:
            # Skip header
            if k < 21:
                k += 1
            else:
                # Get values
                s_line = line.split(' ')
                if len(s_line[0]) == 0:  # If we are not at the footer
                    t.append(cal2decyear(int(s_line[3]), int(
                        s_line[2]), int(s_line[1])))
                    x.append(float(s_line[5]))
                    y.append(float(s_line[7]))
                    z.append(float(s_line[9]))

    # Populate
    # Make time array
    self.time = np.c_[t, decyear2mjd(t)]
    # Make XYZ data array
    self.data_xyz = np.c_[x, y, z, np.zeros((len(x), 6))*np.nan]   
    # Reference variables
    self.t0 = self.time[0, :]
    self.XYZ0 = self.data_xyz[0, :3]
    (E0, N0, U0) = xyz2geo(self.XYZ0[0], self.XYZ0[1], self.XYZ0[2])
    self.NEU0 = np.array([N0, E0, U0])
    self.ref_frame = ref_frame
    self.process = process
    # Make dN, dE, dU data array
    self.xyz2dneu()

    # Populate if asked
    if neu:
        from itsa.lib.coordinates import xyz2geo
        (lon, lat, h) = xyz2geo(
            self.data_xyz[:, 0], self.data_xyz[:, 1], self.data_xyz[:, 2])
        self.data_neu = np.c_[lat, lon, h]

    # Order by increasing time
    self.reorder()
