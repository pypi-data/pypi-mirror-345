"""
    Create Green's function matrix for jump and post-sesimic inversion
    
    ----
    Developed at: ISTerre
    By: Lou MARILL
"""


########################################################
def G_jps(G_longt, time, jps, tau=10, mod_post='log10'):
    """
    Create Green's function matrix for jump inversion

    Parameters
    ----------
    G_longt : np.ndarray
        Green's function matrix of long-term phenomena to model.
    time : list or np.ndarray
        Time vector of the model, in modified Julian days.
    jps : Jps object
        Jps catalog of events to model.
    tau : int, optional
        Relaxation time for post-seismic transient.
        The default is 10.
    mod_post : 'log10' or 'exp', optional
        Post-seismic model used.
        The default is 'log10'.

    Raises
    ------
    ValueError
        If |time| is list and cannot be converted to np.ndarray.
        If |G_longt| is not 2D np.ndarray.
        If |G_lont| or |time| values are not int nor float.
        If |time| is not 1D list nor 1D np.ndarray.
        If |G_longt| and |time| do not have the same number of rows.
        If |tau| is null or negatif.
        If |mod| is not 'log10' nor 'exp'.
    TypeError
        If any parameter does not have the right type.

    Return
    ------
    G_window : np.ndarray
        Green's function matrix for jump inversion.
        
    See Also
    --------
    Jps class in [itsa.jps.Jps]

    """
    
    ####################################################
    def _check_param(G_longt, time, jps, tau, mod_post):
        """
        Raise error if one parameter is invalid and adapt some parameter values
        """
        # Import
        import numpy as np
        from itsa.lib.modif_vartype import list2ndarray
        from itsa.jps.Jps import Jps
        
        # Change type
        # |time|
        if isinstance(time, list):
            (time, err_time) = list2ndarray(time)
            if err_time:
                raise ValueError(('Time list must be convertible into '
                                  'np.ndarray: |time=%s|.') % str(time))
                
        # Check
        # |G_longt|
        if not isinstance(G_longt, np.ndarray):
            raise TypeError(("Green's function matrix must be np.ndarray: "
                             "|type(G_longt)=%s|.") % type(G_longt))
        if G_longt.ndim != 2:
            raise ValueError(("Green's function must be 2D np.ndarray: "
                             "|G_longt.ndim=%d|.") % G_longt.ndim)
        if G_longt.dtype not in ['int', 'float']:
            raise ValueError(("Green's function must be int np.ndarray or "
                              "float np.ndarray: |G_longt.dtype=%s|.")
                             % G_longt.dtype)        
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
        if time.shape[0] != G_longt.shape[0]:
            raise ValueError(("Time and Green's function must have the same "
                              "number of rows (as the matrix is for the "
                              "|time| period): |time.shape[0]=%d| and "
                              "|G_longt.shape[0]=%d|.")
                             % (time.shape[0], G_longt.shape[0]))
        # |jps|
        if not isinstance(jps, Jps):
            raise TypeError('Jps events must be Jps object: |type(jps)=%s|.'
                            % type(jps))            
        jps.check_jps()
        # |tau|
        if tau == int(tau):
            tau = int(tau)
        if not isinstance(tau, int):
            raise TypeError('Relaxation time must be int: |type(tau)=%s|.'
                            % type(tau))
        if tau <= 0:
            raise ValueError(('Relaxation time must be positive (not 0): '
                              '|tau=%d|.') % tau)
        # |mod_post|
        if not isinstance(mod_post, str):
            raise TypeError(("Post-seismic model must be str ('log10' or "
                             "'exp'): |type(mod_post)=%s|." % type(mod_post)))
        if mod_post not in ['log10', 'exp']:
            raise ValueError(("Post-seismic model must be 'log10' or 'exp': "
                             "|mod_post='%s'|." % mod_post))
        
        # Return
        return time, tau
    ####################################################
    
    # Check parameters
    (time, tau) = _check_param(G_longt, time, jps, tau, mod_post)
    
    # Import
    import numpy as np
    from itsa.lib.index_dates import get_indfid_window
    
    # Initialisation
    G= np.array([]).reshape(len(time), 0)
    
    # For all Jps events
    for num in range(jps.dates.shape[0]):       
 
        # Find index of start and end of event
        (idx_jp, _) = get_indfid_window(time, jps.dates[num, 1],
                                        jps.dur[num], 0)        

        # Jps model: 0 before the event and 1 after
        model_jps = np.zeros(len(time))
        model_jps[idx_jp[1]:] = 1        

        # If duration>0: cosine-line function
        if jps.dur[num] > 0:
            # Normalized time
            time_norm = (time[idx_jp[0]:idx_jp[1]]-time[idx_jp[0]]) \
                        / (time[idx_jp[1]]-time[idx_jp[0]])
            # Cosine-like function during the event
            model_jps[idx_jp[0]:idx_jp[1]] = -1/2*np.cos(time_norm*np.pi)+1/2
            
        # Add Jps model to Green's function matrix
        G = np.c_[G, model_jps]
    
    # For all 'P' Jps events
    jps_P = np.where(jps.type_ev == 'P')[0]
    for num_P in jps_P:
        # Add post-seismic model to Green's function matrix
        G = np.c_[G, _model_post(time, jps.dates[num_P, 1], tau, mod_post)]

    # Add long term Green's functions
    G = np.c_[G, G_longt]

    # Return
    return G

#####################################################################
def G_post(G_longt, time, jps, tau=100, mod_post='log10', tau_spe=1):
    """
    Create Green's function matrix for post-seismic inversion

    Parameters
    ----------
    p.ndarray
        Green's function matrix of long-term phenomena to model.
    time : list or np.ndarray
        Time vector of the model, in modified Julian days.
    jps : Jps object
        Jps catalog of events to model.
    tau : int, optional
        Relaxation time for post-seismic transient.
        The default is 100.
    mod_post : 'log10' or 'exp', optional
        Post-seismic model used.
        The default is 'log10'.
    tau_spe : int, optional
        Relaxation time for special model of post-seismic transient.
        The default is 1.

    Raises
    ------
    ValueError
        If |time| is list and cannot be converted to np.ndarray.
        If |G_longt| is not 2D np.ndarray.
        If |G_lont| or |time| values are not int nor float.
        If |time| is not 1D list nor 1D np.ndarray.
        If |G_longt| and |time| do not have the same number of rows.
        If |tau| is null or negatif.
        If |mod| is not 'log10' nor 'exp'.
        If |tau_spe| is null or negatif.
    TypeError
        If any parameter does not have the right type.

    Return
    ------
    G_window : np.ndarray
        Green's function matrix for jump inversion.
        
    See Also
    --------
    Jps class in [itsa.jps.Jps]

    """
    
    #############################################################
    def _check_param(G_longt, time, jps, tau, mod_post, tau_spe):
        """
        Raise error if one parameter is invalid and adapt some parameter values
        """
        # Import
        import numpy as np
        from itsa.lib.modif_vartype import list2ndarray
        from itsa.jps.Jps import Jps
        
        # Change type
        # |time|
        if isinstance(time, list):
            (time, err_time) = list2ndarray(time)
            if err_time:
                raise ValueError(('Time list must be convertible into '
                                  'np.ndarray: |time=%s|.') % str(time))
                
        # Check
        # |G_longt|
        if not isinstance(G_longt, np.ndarray):
            raise TypeError(("Green's function matrix must be np.ndarray: "
                             "|type(G_longt)=%s|.") % type(G_longt))
        if G_longt.ndim != 2:
            raise ValueError(("Green's function must be 2D np.ndarray: "
                             "|G_longt.ndim=%d|.") % G_longt.ndim)
        if G_longt.dtype not in ['int', 'float']:
            raise ValueError(("Green's function must be int np.ndarray or "
                              "float np.ndarray: |G_longt.dtype=%s|.")
                             % G_longt.dtype)        
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
        if time.shape[0] != G_longt.shape[0]:
            raise ValueError(("Time and Green's function must have the same "
                              "number of rows (as the matrix is for the "
                              "|time| period): |time.shape[0]=%d| and "
                              "|G_longt.shape[0]=%d|.")
                             % (time.shape[0], G_longt.shape[0]))
        # |jps|
        if not isinstance(jps, Jps):
            raise TypeError('Jps events must be Jps object: |type(jps)=%s|.'
                            % type(jps))            
        jps.check_jps()
        # |tau|
        if tau == int(tau):
            tau = int(tau)
        if not isinstance(tau, int):
            raise TypeError('Relaxation time must be int: |type(tau)=%s|.'
                            % type(tau))
        if tau <= 0:
            raise ValueError(('Relaxation time must be positive (not 0): '
                              '|tau=%d|.') % tau)
        # |mod_post|
        if not isinstance(mod_post, str):
            raise TypeError(("Post-seismic model must be str ('log10' or "
                             "'exp'): |type(mod_post)=%s|." % type(mod_post)))
        if mod_post not in ['log10', 'exp']:
            raise ValueError(("Post-seismic model must be 'log10' or 'exp': "
                             "|mod_post='%s'|." % mod_post))
        # |tau_spe|
        if jps.mag_spe is not None:             
            if tau_spe == int(tau_spe):
                tau_spe = int(tau_spe)
            if not isinstance(tau_spe, int):
                raise TypeError(('Relaxation time for special post-seismic '
                                 'model must be int: |type(tau_spe)=%s|.')
                                % type(tau_spe))
            if tau_spe <= 0:
                raise ValueError(('Relaxation time for special post-seismic '
                                  'model must be positive (not 0): '
                                  '|tau_spe=%d|.') % tau_spe)
        # Return
        return time, tau, tau_spe
     #############################################################
     
    # Check parameters
    (time, tau, tau_spe) = _check_param(G_longt, time, jps, tau, mod_post,
                                        tau_spe)
    
    # Import
    import numpy as np
    
    # Initialisation
    G = np.array([]).reshape(len(time), 0)
    
    # For all Jps events
    for num in range(jps.dates.shape[0]):
        # Add post-seismic model to Green's function matrix
        G = np.c_[G, _model_post(time, jps.dates[num, 1], tau, mod_post)]
    
    # Look at special events
    if jps.mag_spe is not None: 
        jps_spe = list(np.where(jps.mag >= jps.mag_spe)[0])
        for num_spe in jps_spe:
            G = np.c_[G, _model_post(time, jps.dates[num_spe, 1], tau_spe,
                                     mod_post)]
            
    # Add long term Green's functions
    G = np.c_[G, G_longt]
    
    # Return
    return G

##################################################
def _model_post(time, jps_dates, tau, mod='log10'):
    """
    Compute the post-seismic transient model to add in the Green's function

    Parameters
    ----------
    time : numpy.ndarray
        Time vector of the model, in modified Julian days.
    jps_date : int or float
        Dates of post-seismic Jps events to model, in modified Julian days.
    tau : int
        Relaxation time of the post-seismic transient.
    mod : 'log10' or 'exp', optional
        Post-seismic model used.
        The default is 'log10'.

    Return
    ------
    model : np.ndarray
        Model of the post-seismic transient.

    """
    
    # Import
    import numpy as np
    
    # Model coefficient
    model_coeff = (time-jps_dates)/tau
    # Set negative coefficient to 0
    model_coeff[model_coeff<0] = 0
    
    # Post-seismic model
    if mod == 'log10':
        return np.log10(1+model_coeff)
    else:
        return 1-np.exp(-model_coeff)