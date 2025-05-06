"""
    Developed at: ISTerre
    By: Lou MARILL
"""


#############################################################
def select_data(self, idx_select, in_place=False, warn=True):
    """
    Create Gts with only selected data.
    

    Parameters
    ----------
    idx_select : int, list or np.ndarray
        Index of the selected data.
    in_place : bool, optional
        Change data directly in |self| if true.
        The default is False: create and return new Jps 
                              (|self| is not updated).
    warn : bool, optional
        Print warning if true.
        The default is True.

    Raises
    ------
    ValueError
        If |idx_select| is list and cannot be converted to np.ndarray.
        If |idx_select| is not 1D list nor 1D np.ndarray.
        If |idx_select| values are not int or bool.
        If |idx_select| values are not positive nor 0.
        If |idx_select| values are above the number of Jps events.
    TypeError
        If any parameter does not have the right type.
    WARNING
        If |in_place| is not bool: |in_place| is set to False.

    Return
    ------
    ts: Gts
        Only if |in_place| is false.
        New Gts with only selected data.
        
    Note
    ----
    Only attribute with the same number of rows than |self.time| are changed:
        - |self.time|
        - |self.data|
        - |self.data_xyz| (if not None)
        - |self.data_neu| (if not None)
        - |self.velocity| (if not None)
        - |self.G| (if not None)

    """
    
    ###################################################
    def _check_param(self, idx_select, in_place, warn):
        """
        Raise error if one parameter is invalid and adapt some parameter values
        """
        # Import
        import numpy as np
        from itsa.lib.modif_vartype import list2ndarray, nptype2pytype
        from itsa.lib.modif_vartype import adapt_bool
        
        # Change type
        # |idx_select|
        if isinstance(idx_select, list):
            (idx_select, err_idx) = list2ndarray(idx_select)
            if err_idx:
                raise ValueError(('Index list must be convertible into '
                                  'np.ndarray: |idx_select=%s|.')
                                 % str(idx_select))
        idx_select = nptype2pytype(idx_select)
        
        # Check
        # |self|
        self.check_gts()
        # |idx_select|
        if not isinstance(idx_select, (int, np.ndarray)):
            raise TypeError(('Index must be int, list or np.ndarray: '
                             '|type(idx_select)=%s|.') % type(idx_select))
        if isinstance(idx_select, np.ndarray):
            if idx_select.ndim != 1:
                raise ValueError(('Index must be int, 1D list or '
                                  '1D np.ndarray: |idx_select.ndim=%d|.')
                                 % idx_select.ndim)
            if idx_select.dtype not in ['int', 'int64', 'bool']:
                raise ValueError(('Index must be int, list of int, list of '
                                  'bool, int np.ndarray or bool np.ndarray: '
                                  '|idx_select.dtype=%s|.')
                                 % idx_select.dtype)
            if ((idx_select < 0).any()
                or (idx_select >= self.time.shape[0]).any()):
                raise ValueError(('Index must be positive or 0 and less than '
                                  'the number of Jps events: |idx_select=%s|.')
                                 % str(idx_select))
        if (isinstance(idx_select, int)
            and (idx_select < 0 or idx_select >= self.time.shape[0])
            and idx_select != True):
                raise ValueError(('Index must be positive or 0 and less than '
                                  'the number of Jps events: |idx_select=%s|.')
                                 % str(idx_select))
                
        # Adapt
        # |in_place|
        (in_place, warn_place) = adapt_bool(in_place)
        # |warn|
        (warn, _) = adapt_bool(warn, True)

        # Warning
        if warn and warn_place:
            print('[WARNING] from method [select_data] in [%s]' % __name__)
            print(('\t|in_place| parameter set to False because '
                   '|type(in_place)!=bool|!'))
            print('\tNew Gts is returned (and the old one is not updated)!')
            print()

        # Return
        return in_place
    ###################################################
    
    # Check parameters
    in_place = _check_param(self, idx_select, in_place, warn)
    
    # Copy Gts
    ts = self.copy()
    
    # Keep only selected data
    # Mandatory attributes
    ts.time = ts.time[idx_select, :]
    ts.data = ts.data[idx_select, :]
    # Optional attributes
    if ts.data_xyz is not None:
        ts.data_xyz = ts.data_xyz[idx_select, :]
    if ts.data_neu is not None:
        ts.data_neu = ts.data_neu[idx_select, :]
    # Analysis attributes
    if ts.G is not None:
        ts.G = ts.G[idx_select, :]
        
    # Return
    if not in_place:
        return ts
    else:
        # Keep only |ts| data
        self.time = ts.time.copy()
        self.data = ts.data.copy()
        if self.data_xyz is not None:
            self.data_xyz = ts.data_xyz.copy()
        if self.data_neu is not None:
            self.data_neu = ts.data_neu.copy()
        if self.G is not None:
            self.G = ts.G.copy()
        
