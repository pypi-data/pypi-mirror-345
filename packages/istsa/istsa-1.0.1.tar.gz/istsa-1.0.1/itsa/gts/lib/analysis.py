"""
    Developed at: ISTerre
    By: Lou MARILL
    Based on: PyGdalSar (https://github.com/simondaout/PyGdalSAR)
"""


###############################################################################
def window_analysis(self, nb_data, G_longt, tau=10, mod_post='log10',
                    type_window='jps', tau_spe=1, pre_post=False,
                    in_place=False, disp=False, folder_disp='', warn=True):
    """
    Populate |G| and |MOD| of Gts object by inverting data within specific
    window

    Parameters
    ----------
    nb_data : int or list
        Number of data before the first Jps event and after the last one.
        If |nb_data| is int, the same number of data will be kept before the
        first Jps event and after the last one.
    G_longt : np.ndarray
        Green's function matrix of long-term phenomena to model.
    tau : int, optional
        Relaxation time for post-seismic transient.
        The default is 10.
    mod_post : 'log10' or 'exp', optional
        Post-seismic model used.
        The default is 'log10'.
    type_window : 'jps' or 'post', optional
        Type of window analysis.
        The default is 'jps'.
    tau_spe : int, optional
        Used only if |self.jps.mag_spe| is not None.
        Relaxation time for special post-seismic transient.
        The default is 1.
    pre_post : bool or int, optional
        Used only if |self.jps.mag_spe| is not None.
        Look at post-seismic before the time period if not False.
        The default is False.
    in_place : bool, optional
        Change data directly in |self| if true.
        The default is False: create and return new Gts 
                              (|self| is not updated).
    disp : bool, optional
        Save window's figures.
        The default is False.
    folder_disp : TYPE, optional
        Used only if |disp| is not False.
        Folder in which save the figures.
        The default is ''.
    warn : bool, optional
        Print warnings if true.
        The default is True.

    Raises
    ------
    TypeError
        If any parameter does not have the right type.
    ValueError
        If |nb_data| values are not positive nor 0.
        If |G_longt| has wrong dimensions.
        If |tau| or |tau_spe| is not positive.
        If |mod_post| is not 'log10' nor 'exp'.
        If |type_window| is not 'jps' nor 'post'.
    WARNING
        If |pre_post| is not bool nor int: |pre_post| set to False.
        If |in_place| is not bool: |in_place| set to False.
        If |disp| is not bool: |disp| set to False.

    Return
    ------
    ts: Gts
        Only if |in_place| is false.
        New Gts with model |np.dot(self.G, self.MOD)| removed.

    """
    
    #######################################################################
    def _check_param(self, nb_data, G_longt, tau, mod_post, type_window,
                     tau_spe, pre_post, in_place, disp, folder_disp, warn):
        """
        Raise error if one parameter is invalid and adapt some parameter values
        """
        # Import
        import numpy as np
        from itsa.lib.modif_vartype import adapt_bool
        
        # Check
        # |self|
        self.check_gts()
        # |nb_data|
        if not isinstance(nb_data, (int, list)):
            raise TypeError(('Number of data must be int or list: '
                             '|type(nb_data)=%s|.')
                            % type(nb_data))
        if isinstance(nb_data, int):
            nb_data = [nb_data, nb_data]
        if (np.array(nb_data) < 0).any():
            raise ValueError('Number of data must be positive: |nb_data=%s|.'
                             % str(nb_data))
        # |G_longt|
        if not isinstance(G_longt, np.ndarray):
            raise TypeError(("Green's functions must be np.ndarray: "
                             "|type(self.G)=%s|.") % type(G_longt))
        if G_longt.ndim != 2:
            raise ValueError(("Green's functions must be 2D np.ndarray: "
                             "|G_longt.ndim=%d|.") % G_longt.ndim)
        if self.time.shape[0] != G_longt.shape[0]:
            raise ValueError(("Green's functions must have the same number of "
                              "rows than |self.time|: |self.time.shape[0]=%d| "
                              "and |G_longt.shape[0]=%d|.")
                             % (self.time.shape[0], G_longt.shape[0]))
        # |tau|
        if not isinstance(tau, int):
            raise TypeError('Relaxation time must be int: |type(tau)=%s|.'
                            % type(tau))
        if tau <= 0:
            raise ValueError(('Relaxation time must be positive (and not 0): '
                              '|tau=%d|.') % tau)
        # |mod_post|
        if not isinstance(mod_post, str):
            raise TypeError(("Post-seismic model must be str ('log10' or "
                             "'exp'): |type(mod_post)=%s|." % type(mod_post)))
        if mod_post not in ['log10', 'exp']:
            raise ValueError(("Post-seismic model must be 'log10' or 'exp': "
                             "|mod_post='%s'|." % mod_post))
        # |type_window|
        if not isinstance(type_window, str):
            raise TypeError(("Window type must be str ('jps' or 'post'): "
                             "|type(type_window)=%s|." % type(type_window)))
        if type_window not in ['jps', 'post']:
            raise ValueError(("Window type model must be 'jps' or 'post': "
                             "|type_window='%s'|." % type_window))
        if type_window == 'post':
            # |tau_spe|
            if self.jps.mag_spe is not None:
                if not isinstance(tau_spe, int):
                    raise TypeError(('Relaxation time for special events must '
                                     'be int: |type(tau_spe)=%s|.')
                                    % type(tau_spe))
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
        # |in_place|
        (in_place, warn_place) = adapt_bool(in_place)
        # |disp|
        (disp, warn_disp) = adapt_bool(disp)
        if disp:
            # |folder_disp|
            if not isinstance(folder_disp, str):
                raise TypeError(('Display folder must be str: '
                                 '|type(folder_disp)=%s|.')
                                % type(folder_disp))
        # |warn|
        (warn, _) = adapt_bool(warn, True)
        
        # Warnings
        if (warn and ((type_window == 'post' and warn_post) or warn_place
                      or warn_disp)):
            print('[WARNING] from method [window_analysis] in [%s]:'
                  % __name__)
            if isinstance(pre_post, (bool, int)):
                print(('\t|pre_post| parameter set to False because '
                       '|type(pre_post)!=bool| and |type(pre_post)!=int|!'))
                print(('\tPost-seismic before the time period will not be '
                       'taking into account!'))
                print()
            if warn_place:
                print(('\t|in_place| parameter set to False because '
                       '|type(in_place)!=bool|!'))
                print(('\tNew Gts returned (and the old one is not updated)!'))
                print()
            if warn_disp:
                print(('\t|disp| parameter set to False because '
                       '|type(disp)!=bool|!'))
                print("\tWindow's figures will not be saved!")
                print()
        # Return
        return nb_data, pre_post, in_place, disp
    #######################################################################
    
    # Check parameters
    (nb_data, pre_post, in_place, disp) = _check_param(self, nb_data, G_longt,
                                                       tau, mod_post,
                                                       type_window, tau_spe,
                                                       pre_post, in_place,
                                                       disp, folder_disp, warn)
    
    # Import
    import numpy as np
    from itsa.lib.index_dates import get_indfid_window, get_index_from_dates
    from itsa.lib.Green_functions import G_jps, G_post
    
    # Initialisation
    # |G_post| and |MOD_post| from special events
    G_spe = self.G.copy()
    MOD_spe = self.MOD.copy()
    # Evolutive Gts
    ts = self.copy(data_xyz=False, data_neu=False)
    # Index for Gts without NaN
    idx_nonan = np.unique(np.where(~np.isnan(ts.data))[0])
    # Index in |self.jps| of the jumps in the current window
    nums_jp = [0]
    
    # Post-seismic before the 1st window
    idx_prepost = False
    if type_window == 'post' and pre_post:
        idx_prepost = np.where(
            (ts.jps.type_ev=='P') &
            (ts.jps.dates[:, 1]<=ts.time[idx_nonan[0], 1]))[0]
        if idx_prepost.size > 0:
            idx_prepost = idx_prepost[-1]
            if isinstance(pre_post, int):
                time_lim = ts.time[idx_nonan[0], 1]-pre_post
                if ts.jps.dates[idx_prepost, 1] > time_lim:
                    idx_prepost = False
        else:
            idx_prepost = False
                   
    # For each jump window
    while nums_jp[0] < ts.jps.shape():
        if ((ts.jps.dates[nums_jp[0], 1] > ts.time[idx_nonan[0], 1]
             and ts.jps.dates[nums_jp[0], 1] < ts.time[idx_nonan[-1], 1])
            or (pre_post and nums_jp[0] == idx_prepost)):
            
            # Find index for start and end of the widnow
            # Find index for window in |ts_nonan.time| 
            (idx_window_nonan, nb_jp_add) = get_indfid_window(
                ts.time[idx_nonan, 1], ts.jps.dates[nums_jp[0]:, 1],
                ts.jps.dur[nums_jp[0]:], nb_data)
            # Index of all the events involved
            nums_jp = nums_jp[0]+np.array(range(nb_jp_add))
            # Create mask for the window
            # (take only no NaN data within the window)
            if idx_window_nonan[1] > idx_window_nonan[0]:
                mask_window = idx_nonan[range(idx_window_nonan[0],
                                              idx_window_nonan[1])]
            else:
                mask_window = idx_nonan[idx_window_nonan[0]]
                
            # Window data
            # Gts
            ts_window = ts.copy()
            # Jps
            jps_window = ts.jps.select_ev(nums_jp)
            if pre_post and nums_jp[0] == idx_prepost:
                jps_window.mag[0] = 0
            # Green's function
            if type_window == 'jps':
                G_window = G_jps(G_longt, ts.time[:, 1], jps_window, tau,
                                 mod_post)
            else:
                G_window = G_post(G_longt, ts.time[:, 1], jps_window, tau,
                                  mod_post, tau_spe)
                
            # Inversion solution
            MOD_window = _inverse(ts_window.data[mask_window, :3],
                                  G_window[mask_window, :], jps_window,
                                  type_window)
            
            # Display
            if disp:
                # Find index for window in |self.time|
                idx_window = get_index_from_dates(
                    ts.time[:, 1], ts.time[idx_nonan, 1][idx_window_nonan])
                # Gts only on window
                if idx_window_nonan[1] == idx_window_nonan[0]:
                    idx_window[1] += 1
                ts_disp = ts.select_data(list(range(idx_window[0],
                                                    idx_window[1])))
                ts_disp.G = G_window[range(idx_window[0], idx_window[1]), :]
                ts_disp.jps = jps_window.copy()
                ts_disp.MOD = MOD_window.copy()
                # Title, name figure and color point
                if type_window == 'jps':
                    title_disp = ('Station %s - Jumps inversion - Date: %.3f'
                                  % (ts_disp.code, ts_disp.jps.dates[0, 0]))
                    color_disp = 'blue'
                    size_marker = 10
                    ts_disp.jps.mag_spe = None
                else:
                    title_disp = (('Station %s - Post-seismic inversion - '
                                   'Date: %.3f, tau: %d')
                                  % (ts_disp.code, ts_disp.jps.dates[0, 0],
                                     tau))
                    if (ts_disp.jps.mag_spe is not None
                        and (ts_disp.jps.mag>=ts_disp.jps.mag_spe).any()):
                        title_disp = '%s, Special tau: %d' % (title_disp,
                                                               tau_spe)
                    color_disp = 'navy'
                    size_marker = 1
                name_fig = '%s_%.3f' % (ts_disp.code, ts_disp.jps.dates[0, 0])
                ts_disp.plot(color_disp, title_disp, name_fig, folder_disp,
                             size_marker=size_marker)
            
            # Populate |self.G| and |self.MOD|
            self.G = np.c_[self.G, G_window[:, :len(nums_jp)]]
            self.MOD = np.vstack((self.MOD, MOD_window[:len(nums_jp), :]))
            
            # Remove window's Jps events from |ts|
            ts.data[:, :3] = (ts.data[:, :3]
                              - np.dot(G_window[:, :len(nums_jp)],
                                       MOD_window[:len(nums_jp), :3]))
            
            # Populate |G_post| and |MOD_post| for special events
            if (type_window == 'post' and jps_window.mag_spe is not None
                and (jps_window.mag>=jps_window.mag_spe).any()):
                idx_cowpost = np.where(jps_window.mag
                                       >= jps_window.mag_spe)[0]
                idx_post = (np.array(range(len(idx_cowpost)))
                            + jps_window.shape())
            
                G_spe = np.c_[G_spe, G_window[:, idx_post]]
                MOD_spe = np.vstack((MOD_spe, MOD_window[idx_post, :]))
            
                # Remove window's Jps special events from |ts|
                ts.data[:, :3] = (ts.data[:, :3]
                                  - np.dot(G_window[:, idx_post],
                                           MOD_window[idx_post, :3]))
                        
        # Go to the next window
        nums_jp = [nums_jp[-1]+1]
    
    # Populate |self.G| and |self.MOD| with |G_post| and |MOD_post|
    self.G = np.c_[self.G, G_spe]
    self.MOD = np.vstack((self.MOD, MOD_spe))
    
    # Return
    if not in_place:
        return ts
    else:
        self.data = ts.data.copy()
        self.data_xyz = None
        self.data_neu = None
        self.G = None
        self.MOD = None
    
    
#############################################################
def longt_analysis(self, G_longt, in_place=False, warn=True):
    """
    Populate |G| and |MOD| of Gts object by inverting long-term phenomena

    Parameters
    ----------
    G_longt : np.ndarray
        Green's function matrix of long-term phenomena to model.
    in_place : bool, optional
        Change data directly in |self| if true.
        The default is False: create and return new Gts 
                              (|self| is not updated).
    warn : bool, optional
        Print warnings if true.
        The default is True.

    Raises
    ------
    TypeError
        If any parameter does not have the right type.   
    ValueError
        If |G_longt| has wrong dimensions.
    WARNING
        If |in_place| is not bool: |in_place| set to False.

    Return
    ------
    ts: Gts
        Only if |in_place| is false.
        New Gts with model |np.dot(self.G, self.MOD)| removed.

    """
    
    ################################################
    def _check_param(self, G_longt, in_place, warn):
        """
        Raise error if one parameter is invalid and adapt some parameter values
        """
        # Import
        import numpy as np
        from itsa.lib.modif_vartype import adapt_bool
        
        # Check
        # |self|
        self.check_gts()
        # |G_longt|
        if not isinstance(G_longt, np.ndarray):
            raise TypeError(("Green's functions must be np.ndarray: "
                             "|type(self.G)=%s|.") % type(G_longt))
        if G_longt.ndim != 2:
            raise ValueError(("Green's functions must be 2D np.ndarray: "
                             "|G_longt.ndim=%d|.") % G_longt.ndim)
        if self.time.shape[0] != G_longt.shape[0]:
            raise ValueError(("Green's functions must have the same number of "
                              "rows than |self.time|: |self.time.shape[0]=%d| "
                              "and |G_longt.shape[0]=%d|.")
                             % (self.time.shape[0], G_longt.shape[0]))
        
        # Adapt
        # |in_place|
        (in_place, warn_place) = adapt_bool(in_place)
        # |warn|
        (warn, _) = adapt_bool(warn, True)
        
        # Warning
        if warn and warn_place:
            print('[WARNING] from method [longt_analysis] in [%s]:' % __name__)
            print(('\t|in_place| parameter set to False because '
                   '|type(in_place)!=bool|!'))
            print(('\tNew Gts returned (and the old one is not updated)!'))
            print()
            
        # Return
        return in_place
    ################################################
    
    # Check parameters
    in_place = _check_param(self, G_longt, in_place, warn)
    
    # Import
    import numpy as np
    
    # Initialisation
    # New Gts
    ts = self.copy(data_xyz=False, data_neu=False)
    # Index for Gts without NaN
    idx_nonan = np.unique(np.where(~np.isnan(ts.data))[0])
    # Green's functions
    self.G = G_longt
    
    # Inversion solution
    self.MOD = _inverse(ts.data[idx_nonan, :3], self.G[idx_nonan, :])
    
    # Remove model
    ts.data[:, :3] = ts.data[:, :3]-np.dot(self.G, self.MOD[:, :3])
    
    # Return
    if not in_place:
        return ts
    else:
        self.data = ts.data.copy()
        self.data_xyz = None
        self.data_neu = None
        self.G = None
        self.MOD = None
        
    
###################################################
def _inverse(data, G, jps=None, type_window='jps'):
    """
    Least-square inversion with infinite solutions and post-seismic constraints

    Parameters
    ----------
    data : np.ndarray
        Data to invert.
    G : np.ndarray
        Green's function for the inversion.
    jps : None or Jps, optional
        Jps catalog.
        The default is None.
    type_window : 'jps' or 'post', optional
        Used only if |jps| is not None.
        Type of window analysis.
        The default is 'jps'.

    Return
    ------
    NEU : np.ndarray
        Inversion solution.

    """
    
    # Import 
    import numpy as np
    from numpy.linalg import lstsq
    import warnings
    warnings.filterwarnings("error")
    
    # Initialistation
    if data.ndim == 1:
        data = data.reshape(1, -1)
    if G.ndim == 1:
        G = G.reshape(1, -1)
    NEU = np.zeros((G.shape[1],6))
    
    # 1st solution of the equation
    res_N = lstsq(G, data[:, 0], rcond=None)
    res_E = lstsq(G, data[:, 1], rcond=None)
    res_U = lstsq(G, data[:, 2], rcond=None)
    NEU[:, :3] = np.c_[res_N[0], res_E[0], res_U[0]]
    
    # If call from inversion window
    if jps is not None:
        # Test infinite solutions
        if res_N[1].size == 0 or res_E[1].size == 0 or res_U[1].size == 0:
            nb_sol_ok = np.array([res_N[2], res_E[2], res_U[2]])
            comp = np.argmin(np.c_[res_N[2], res_E[2], res_U[2]])
            idx_use = _solv_inf_sol(NEU[:, comp], nb_sol_ok[comp], jps,
                                    type_window)
            # New inversion
            NEU = np.zeros(NEU.shape)
            for c in range(3):
                NEU[idx_use, c] = lstsq(G[:, idx_use], data[:, c],
                                        rcond=None)[0]
        else:
            idx_use = np.array(range(NEU.shape[0]))        
        # Post-seismic with same sign than associated co-seismic
        idx_jps = idx_use[idx_use<jps.shape()]
        for c in range(3):
            NEU[idx_use, c] = _solv_post_inv(NEU[idx_use, c],
                                             jps.select_ev(idx_jps),
                                             G[:, idx_use], data[:, c],
                                             type_window)
    else:
        idx_use = np.array(range(NEU.shape[0]))
        
    # Error model from Tarantola
    for c in range(3):
        try:
            varx = np.linalg.inv(np.dot(G[:, idx_use].T, G[:, idx_use]))
            res2 = np.sum(pow(data[:, c]-np.dot(G[:, idx_use],
                                                NEU[idx_use, c]), 2))
            scale = 1/(G.shape[0]-len(idx_use))
            NEU[idx_use, c+3] = np.sqrt(scale*res2*np.diag(varx))
        except:
            NEU[idx_use, c+3] *= np.nan

    # Return
    return NEU
    
    
##########################################################
def _solv_inf_sol(sol, nb_sol_ok, jps, type_window='jps'):
    """
    Solve infinite solutions

    Parameters
    ----------
    sol : np.ndarray
        Solutions used to defined problematic events (with infinite solution).
    nb_sol_ok : int
        Number of solutions without problem.
    jps : Jps
        Jps catalog.
    type_window : 'jps' or 'post', optional
        Type of window analysis.
        The default is 'jps'.

    Return
    ------
    idx_use : np.ndarray
        Index to use for the inversion.

    """
    
    # Import
    import numpy as np
    
    # Find index of Jps events with infinite solution
    idx_pb = np.sort(np.argsort(np.abs(np.diff(sol)))[:sol.size-nb_sol_ok])+1
    idx_pb = idx_pb[idx_pb < jps.shape()]    
    if len(idx_pb) > 0:
        
        # Group problematic index
        idx_prem_group = np.where(idx_pb[1:]-idx_pb[:-1]>1)[0]+1
        if idx_prem_group.size == 0:
            group = [idx_pb]
        else:
            group = [idx_pb[:idx_prem_group[0]]]
            for idx in range(1,len(idx_prem_group)):
                group += [idx_pb[idx_prem_group[idx-1]:idx_prem_group[idx]]]
            group += [idx_pb[idx_prem_group[-1]:]]
        
        # Look at higher magnitude event and post-seismic
        if type_window == 'jps':
            idx_cowpost = np.where(jps.type_ev=='P')[0]
        elif jps.mag_spe is not None:
            idx_cowpost = np.where(jps.mag>=jps.mag_spe)[0]
        else:
            idx_cowpost = np.array([])
        idx_post = np.array(range(len(idx_cowpost)))+jps.shape()
        for g in range(len(group)):
            idx_g = [group[g][0]-1]+list(group[g])
            # Find higher magnitude event within group
            idx_keep = idx_g[np.argsort(jps.select_ev(idx_g).mag)[-1]]
            # Remove index from problematic events
            idx_g.remove(idx_keep)
            # Add post-seismic to problematic index
            for idx in idx_post[np.isin(idx_cowpost, idx_g)]:
                idx_g.append(idx)            
            # Keep all problematic index of the group
            group[g] = idx_g
            
        # Group all groups
        idx_pb_all = group[0]
        for g in range(1,len(group)):
            idx_pb_all += group[g]
        
    else:
        idx_pb_all = []
        
    # Index used for the new inversion
    idx_use = np.array(range(len(sol)))
    idx_use = idx_use[~np.isin(idx_use,idx_pb_all)]
    
    # Return
    return idx_use
    

#########################################################
def _solv_post_inv(sol, jps, G, data, type_window='jps'):
    """
    Impose post-seismic solutions to be with the same sign than associated
    co-seismic.

    Parameters
    ----------
    sol : np.ndarray
        Solutions used as basis for the new inversion.
    jps : Jps
        Jps catalog.
    G : np.ndarray
        Green's function for the new inversion.
    data : np.ndarray
        Data used during the inversion.
    type_window : 'jps' or 'post', optional
        Type of window analysis.
        The default is 'jps'.

    Raise
    -----
    GtsError
        If scipy.optimize.fmin_slsqp inversion does not work.

    Return
    ------
    np.ndarray
        New solution.

    See Also
    --------
    scipy.optimize.fmin_slsqp

    """
    
    # Import
    import numpy as np
    from scipy.optimize import fmin_slsqp
    from itsa.gts.errors import GtsError
    
    # Find index for post-seismic events
    if type_window == 'jps':
        idx_cowpost = np.where(jps.type_ev=='P')[0]
    elif jps.mag_spe is not None:
        idx_cowpost = np.where(jps.mag>=jps.mag_spe)[0]
    else:
        idx_cowpost = np.array([])
        
    if len(idx_cowpost) > 0:
        # Find associated post-seismic solution
        idx_post = np.array(range(len(idx_cowpost)))+jps.shape()
        
        # Bondary for new inversion
        b_min = -np.ones(len(sol))*np.inf
        b_max = np.ones(len(sol))*np.inf
        
        # Set co-seismic to be inferior or egual to the initial
        # Set post-seismic te be the same sign than co-seismic
        for idx in range(len(idx_cowpost)):
            if sol[idx_cowpost[idx]] > 0:
                b_min[idx_cowpost[idx]] = 0
                
                b_min[idx_post[idx]] = 0
                if sol[idx_post[idx]] < 0:
                    sol[idx_post[idx]] = 0
            else:
                b_max[idx_cowpost[idx]] = 0
                
                b_max[idx_post[idx]] = 0
                if sol[idx_post[idx]] > 0:
                    sol[idx_post[idx]] = 0
                    
        # New inversion
        _func = lambda x: np.sum((np.dot(G,x)-data)**2)
        bounds = list(zip(b_min, b_max))
        res = fmin_slsqp(_func, sol, bounds=bounds, full_output=True, iprint=0)
             
        # Inversion error
        if res[-2] != 0:
            raise GtsError(('Following error using '
                            '[scipy.optimize.fmin_slsqp]: %s (Exit: %d)')
                            % (res[-1], res[-2]))
        
        # Return
        return res[0]
    else:
        return sol