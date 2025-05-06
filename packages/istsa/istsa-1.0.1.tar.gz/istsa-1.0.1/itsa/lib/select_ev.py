"""
    !!! Warning: You need to add the module 'itsa' to your Python path to use 
    these functions

    ----
    Developed at: ISTerre
    By: Lou MARILL
"""


#########################################################################
def select_ev(sta_XYZ, cat_file, type_ev, Mw_min=None, d=1., Mw_post=None,
              dpost=1., warn=True):
    """
    Select events from |cat_file| impacting the station at |sta_XYZ|

    Parameters
    ----------
    sta_XYZ : np.ndarray
        XYZ coordinates of the station.
    cat_file : str
        Catalog file name (path).
    type_ev : str
        Type of events in catalog file:
            'ISC' for ISC earthquake catalog,
            'E' for handmade earthquake catalog,
            'S' for SSE catalog,
            'W' for swarm catalog,
            'U' for unknown event catalog.
        Post-seismic are considered only for |np.isin(type_ev, ['ISC', 'E'])|.
    Mw_min : int, float or None, optional
        Minimum Mw to select events: take only |Mw>=Mw_min| envents.
        The default is None: take all catalog's events
    d : float, optional
        Influence radius parameter: higher |d|, smaller the radius.
        The default is 1..
    Mw_post : int, float or None, optional
        Used only for |np.isin(type_ev, ['ISC', 'E'])|.
        Consider post-seismic for |Mw>=Mw_post| earthquakes.
        The default is None.
    dpost : float, optional
        Used only for |np.isin(type_ev, ['ISC', 'E'])|.
        Influence radius parameter to consider post-seismic impact.
        The default is 1..
    warn : bool, optional
        Print warning if true.
        The default is True.

    Raises
    ------
    TypeError
        If any parameter has not the right type.
    ValueError
        If |sta_XYZ| do not have exactly 3 values.
        If |d| or |dpost| is negative or 0.
    WARNING
        If |Mw_post<Mw_min|: |Mw_post| set to None.

    Returns
    -------
    cat : np.ndarray
        Selected events catalog with: Date [decimal year], Latitude, Longitude,
                                      Depth [km], Mw,
                                      Duration [day] (only if provided).
    type_ev : str or np.ndarray
        Type of events in |cat|: different from entry parameter in case of
                                 |np.isin(type_ev, ['ISC', 'E'])|.

    """

    ########################################################################
    def _check_param(sta_XYZ, cat_file, type_ev, Mw_min, d, Mw_post, dpost,
                     warn):
        """
        Raise error, if one parameter is invalid, and warning
        """
        # Import
        import numpy as np
        from itsa.lib.modif_vartype import adapt_bool
        
        # Check
        # |sta_XYZ|
        if not isinstance(sta_XYZ, np.ndarray):
            raise TypeError(('XYZ coordinates must be np.ndarray: '
                             '|type(sta_XYZ)=%s|.') % type(sta_XYZ))
        if sta_XYZ.size != 3:
            raise ValueError(('XYZ coordinates must have 3 values: '
                              '|sta_XYZ.size=%d|.') % sta_XYZ.size)
        # |cat_file|
        if not isinstance(cat_file, str):
            raise TypeError(('Catalog file must be str: '
                             '|type(cat_file)=%s|.') % type(cat_file))
        # |type_ev|
        if not isinstance(type_ev, str):
            raise TypeError(('Type of event must be str: '
                             '|type(type_ev)=%s|.') % type(type_ev))
        # |Mw_min|
        if Mw_min is not None and not isinstance(Mw_min, (int, float)):
            raise TypeError(('Minimum Mw must be int, float or None: '
                             '|type(Mw_min)=%s|.') % type(Mw_min))
        # |d|
        if not isinstance(d, (int, float)):
            raise TypeError(('Inflence radius parameter must be float: '
                             '|type(d)=%s|.') % type(d))
        if d <= 0:
            raise ValueError(('Inflence radius parameter must be positive '
                              '(and not 0): |d=%d|.') % d)
        # |Mw_post|
        if np.isin(type_ev, ['ISC', 'E']):
            if Mw_post is not None :
                if not isinstance(Mw_post, (int, float)):
                    raise TypeError(('Minimum post-seismic Mw must be None, '
                                     'int or float: |type(Mw_post)=%s|.')
                                    % type(Mw_post))
                # |dpost|
                if not isinstance(dpost, (int, float)):
                    raise TypeError(('Post-seismic inflence radius parameter '
                                     'must be float: type(d)=%s|.')
                                    % type(dpost))
                if dpost <= 0:
                    raise ValueError(('Post-seismic inflence radius parameter '
                                      'must be positive (and not 0): '
                                      '|dpost=%d|.') % dpost)
        # |warn|
            (warn, _) = adapt_bool(warn, True)

        # Warning
            if warn and Mw_post is not None and Mw_post < Mw_min:
                print('[WARNING] from method [select_ev] in [%s]:' % __name__)
                print(('\t|Mw_post<Mw_min| but only Mw>=Mw_min earthquake '
                        'are considered!'))
                print(('\tAll selected earthquakes are considered with '
                       'post-seismic!'))
                print()
    ########################################################################

    # Check parameters
    _check_param(sta_XYZ, cat_file, type_ev, Mw_min, d, Mw_post, dpost, warn)
    sta_XYZ = sta_XYZ.reshape(3)

    # Import
    import numpy as np
    from itsa.lib.astrotime import cal2decyear
    from itsa.lib.coordinates import geo2xyz

    # Read catalog
    if type_ev == 'ISC':
        from itsa.lib.read_cat import read_ISC
        cat = read_ISC(cat_file)
    else:
        if "sse_catalog" in cat_file or "unknown_ev_catalog" in cat_file:
            cat_all = np.genfromtxt(cat_file, usecols=[i for i in range(8)])
        else:
            cat_all = np.genfromtxt(cat_file, usecols=[i for i in range(7)])

        #cat_all = np.genfromtxt(cat_file, usecols=[i for i in range(7)])
        #cat_all = np.genfromtxt(cat_file, usecols=(1, 4, 5))
        cat_dates = cat_all[:, :3].astype(int)
        cat = np.c_[cal2decyear(cat_dates[:, 2], cat_dates[:, 1],
                                cat_dates[:, 0]),
                    cat_all[:, 3:]]

    # Keep only Mw>=Mw_min earthquake
    if Mw_min is not None:
        cat = cat[np.where(cat[:, 4] >= Mw_min)]

    # Influence radius
    r = 10**((.5*cat[:, 4]-.8)/d)*1e3  # km-->m

    # Distance to station
    # Convert coordinates
    (x, y, z) = geo2xyz(cat[:, 2], cat[:, 1],
                        -cat[:, 3]*1e3)  # km-->m for depth
    # Compute distance
    dist = np.sqrt((sta_XYZ[0]-x)**2+(sta_XYZ[1]-y)**2+(sta_XYZ[2]-z)**2)

    # Impacting events
    impact = np.where(dist <= r)
    cat = cat[impact]

    # Event type
    if np.isin(type_ev, ['ISC', 'E']):
        type_ev = np.repeat('E', cat.shape[0])

    # Post-seismic for earthquake catalog
        if Mw_post is not None:
            post = np.where(cat[:, -1] >= Mw_post)
        else:
            post = np.array([k for k in range(cat.shape[0])])
        if post[0].size > 0:
            rpost = (10**((.5*cat[post, 4]-.8)/dpost)
                     * 1e3).reshape(-1)  # km-->m
            dist_post = dist[impact][post]
            type_ev_post = type_ev[post]
            type_ev_post[np.where(dist_post < rpost)] = 'P'
            type_ev[post] = type_ev_post

    # Return
    return cat, type_ev
