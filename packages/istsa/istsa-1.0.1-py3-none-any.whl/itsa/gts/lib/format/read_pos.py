"""
    Developed at: ISTerre
    By: Lou MARILL
"""


##################################################################
def read_allpos(self, tsdir='.', tsfile=None, ref_frame='Unknown',
                process='Unknown', neu=False, warn=True):
    """
    Read PBO, GipsyX, F3 solution and NGL solution pos files

    Parameters
    ----------
    tsdir : str, optional
        Directory of the file to be readed.
        The default is '.'.
    tsfile : str, optional
        Pos file to be readed.
        The default is None: |read_allpos| look for '|self.code|*' file.
    ref_frame : str, optional
        Reference frame of the solution.
        The default is 'Unknown'.
    process : str, optional
        Processing used to get the solution.
        The default is 'Unknown'.
    neu : bool, optional
        Populate |data_neu| if true.
        The default is False.
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
    FileNotFoundError
        If there is no '|self.code|*' file in |tsdir|.
    WARNING
        If |neu| is not bool: |neu| set to False.
        If |ref_frame| is different from the reference frame in file
        (only for PBO files).

    Note
    ----
    For NGL solution, the station code will be changed according to GipsyX code
    station.

    """

    #####################################################################
    def _check_param(self, tsdir, tsfile, ref_frame, process, neu, warn):
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

        # Adapt
        # |neu|
        (neu, warn_neu) = adapt_bool(neu)
        # |warn|
        (warn, _) = adapt_bool(warn, True)

        # Warning
        if warn and warn_neu:
            print('[WARNING] from method [read_allpos] in [%s]' % __name__)
            print('\t|neu parameter set to False because |type(neu)!=bool)|!')
            print('\tGts %s |data_neu| will not be populated!' % self.code)
            print()

        # Return
        return neu, warn
    #####################################################################

    # Check parameters
    (neu, warn) = _check_param(self, tsdir, tsfile, ref_frame, process, neu,
                               warn)

    # Import
    import os
    from os.path import abspath
    from itsa.lib.find_format import find_posformat

    # Name of the file
    if tsfile is None:
        from glob import glob
        pos_file = glob(tsdir+os.sep+self.code.upper()+"*")
        if len(pos_file) == 0:
            return False
        pos_file = pos_file[0]
    else:
        pos_file = tsdir+os.sep+tsfile
    self.in_file = abspath(pos_file)

    # Find pos file type
    pos_format = find_posformat(self.in_file)

    # Read pos file
    
    # GipsyX pos
    if pos_format == 'GX':
        self.read_GXpos(tsdir, tsfile, ref_frame, process, neu, warn=warn)
    # F3 solution pos
    elif pos_format == 'F3':
        self.read_F3pos(tsdir, tsfile, ref_frame, process, neu, warn=warn)
    # NGL pos
    elif pos_format == 'NGL':
        self.read_NGLtxyz(tsdir, tsfile, ref_frame, process, neu, warn=warn)
    # PBO pos
    else:
        self.read_PBOpos(tsdir, tsfile, process, neu, warn=warn)
        if warn and self.ref_frame != ref_frame:
            print('[WARNING] from method [read_allpos] in [%s]' % __name__)
            print(("\tReference frame in %s different from the given reference"
                   " frame: |self.ref_frame='%s'| and |ref_frame='%s'|!")
                  % (pos_file, self.ref_frame, ref_frame))
            print("\tReference frame '%s' kept!" % self.ref_frame)
            print()

    # |self| was succesfully populated
    return True
