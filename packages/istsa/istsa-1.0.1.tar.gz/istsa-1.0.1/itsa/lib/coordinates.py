"""
    Functions for coordinates conversions

    Conversions:
    - Geocentric/Local frame conversion
    - Geocentric/Geodetic frame conversion
    - Geocentric/Geospherical conversion

    !!! Warning: You need to add the module 'itsa' to your Python path to use 
    these functions

    ----
    Developed at: ISTerre
    By: Lou MARILL
    Based on: PYACS module
"""

#%%###################
## GEOCENTRIC/LOCAL ##
######################

#######################################################
def mat_rot_general_to_local(lon, lat, unit='dec_deg'):
    """
    Generate rotation matrix R to convert general geocentric cartesian
    coordinates (XYZ) to local cartesian coordinates (ENU)

    Parameters
    ----------
    lon : int or float
        Reference longitude for the conversion, in |unit|.
    lat : int or float
        Reference latitude for the conversion, in |unit|.
    unit : 'dec_deg' or 'radians', optional
        Unit of |lon| and |lat|: decimal degrees or radians.
        The default is 'dec_deg'.

    Raises
    ------
    TypeError
        If any parameter does not have the right type.
    ValueError
        If |unit| is not 'dec_deg' nor 'radians'.

    Return
    ------
    R : np.ndarray
        Rotation matrix to convert general geocentric to local cartesian
        coordinates.
        
    Note
    ----
    R = [[     -sin(lon)     ,       cos(lon)     ,    0    ],
         [-sin(lat)*cos(lon) , -sin(lat)*sin(lon) , cos(lat)],
         [ cos(lat)*cos(lon) ,  cos(lat)*sin(lon) , sin(lat)]]

    Examples
    --------
    In [1]: from itsa.lib.coordinates import mat_rot_general_to_local

    In [2]: mat_rot_general_to_local(141.75,45.40)
    Out[2]:
    array([[-0.61909395, -0.78531693,  0.        ],
           [ 0.55916611, -0.44081102,  0.70215305],
           [-0.55141268,  0.43469871,  0.71202605]])

    In [3]: import numpy as np

    In [4]: mat_rot_general_to_local(np.radians(141.75),np.radians(45.40),
                                     'radians')
    Out[4]:
    array([[-0.61909395, -0.78531693,  0.        ],
           [ 0.55916611, -0.44081102,  0.70215305],
           [-0.55141268,  0.43469871,  0.71202605]])

    """

    #################################
    def _check_param(lon, lat, unit):
        """
        Raise error if one parameter is invalid
        """
        # Import
        from itsa.lib.modif_vartype import nptype2pytype
        # Change type
        (lon, lat) = nptype2pytype([lon, lat])
        # |lon|
        if not isinstance(lon, (int, float)):
            raise TypeError('Longitude must be int or float: |type(lon)=%s|.'
                            % type(lon))
        # |lat|
        if not isinstance(lat, (int, float)):
            raise TypeError('Latitude must be int or float: |type(lat)=%s|.'
                            % type(lat))
        # |unit|
        if not isinstance(unit, str):
            raise TypeError('Unit must be str: |type(unit)=%s|.' % type(unit))
        if unit not in ['dec_deg', 'radians']:
            raise ValueError(("Unit must be 'dec_deg' or 'radians': "
                              "|unit='%s'|.") % unit)
    #################################

    # Check parameters
    _check_param(lon, lat, unit)

    # Import
    import numpy as np

    # Change unit
    if unit == 'dec_deg':
        lon = np.radians(lon)
        lat = np.radians(lat)

    # Compute R
    R = np.zeros([3, 3], float)
    R[0, 0] = -np.sin(lon)
    R[0, 1] = np.cos(lon)

    R[1, 0] = -np.sin(lat)*np.cos(lon)
    R[1, 1] = -np.sin(lat)*np.sin(lon)
    R[1, 2] = np.cos(lat)

    R[2, 0] = np.cos(lat)*np.cos(lon)
    R[2, 1] = np.cos(lat)*np.sin(lon)
    R[2, 2] = np.sin(lat)

    # Return
    return R


#######################################################
def mat_rot_local_to_general(lon, lat, unit='dec_deg'):
    """
    Generate rotation matrix R to convert local cartesian coordinates (ENU) to
    general cartesian coodinates (XYZ)

    Parameters
    ----------
    lon : int or float
        Reference logitude for the conversion, in |unit|.
    lat : int or float
        Reference latitude for the conversion, in |unit|.
    unit : TYPE, optional
        Unit of |lon| and |lat|: decimal degrees or radians.
        The default is 'dec_deg'.

    Raises
    ------
    TypeError
        If any parameter does not have the right type.
    ValueError
        If |unit| is not 'dec_deg' nor 'radians'.

    Returns
    -------
    np.ndarray
        Rotation matrix to convert local to general geocentric cartesian
        coordinates.
        
    Note
    ----
    Since R is orthogonal, it is the inverse and also the tranpose of the
    conversion matrix from general geocentric to local cartesian coordinates.

    Examples
    --------
    In [1]: from itsa.lib.coordinates import mat_rot_local_to_general

    In [2]: mat_rot_local_to_general(141.75,45.40)
    Out[2]:
    array([[-0.61909395,  0.55916611, -0.55141268],
           [-0.78531693, -0.44081102,  0.43469871],
           [ 0.        ,  0.70215305,  0.71202605]])

    In [3]: import numpy as np

    In [4]: mat_rot_local_to_general(np.radians(141.75),np.radians(45.40),
                                     unit='radians')
    Out[4]:
    array([[-0.61909395,  0.55916611, -0.55141268],
           [-0.78531693, -0.44081102,  0.43469871],
           [ 0.        ,  0.70215305,  0.71202605]])

    """

    #################################
    def _check_param(lon, lat, unit):
        """
        Raise error if one parameter is invalid 
        """
        # Import
        from itsa.lib.modif_vartype import nptype2pytype
        # Change type
        (lon, lat) = nptype2pytype([lon, lat])
        # |lon|
        if not isinstance(lon, (int, float)):
            raise TypeError('Longitude must be int or float: |type(lon)=%s|.'
                            % type(lon))
        # |lat|
        if not isinstance(lat, (int, float)):
            raise TypeError('Latitude must be int or float: |type(lat)=%s|.'
                            % type(lat))
        # |unit|
        if not isinstance(unit, str):
            raise TypeError('Unit must be str: |type(unit)=%s|.' % type(unit))
        if unit not in ['dec_deg', 'radians']:
            raise ValueError(("Unit must be 'dec_deg' or 'radians': "
                              "|unit='%s'|.") % unit)
    #################################

    # Check parameters
    _check_param(lon, lat, unit)

    # Return
    return mat_rot_general_to_local(lon, lat, unit).T


#%%######################
## GEOCENTRIC/GEODETIC ##
#########################

#######################################################################
def xyz2geo(x, y, z, unit='dec_deg', A=6378137., E2=0.006694380022903):
    """
    Convert geocentric cartesian coordinates (XYZ) to geodetic coordinates
    (lon,lat,h)

    Parameters
    ----------
    x : int, float, list or np.ndarray
        X coordinates, in meters.
    y : int, float, list or np.ndarray
        Y coordinates, in meters.
    z : int, float, list or np.ndarray
        Z coordinates, in meters.
    unit : 'dec_deg' or 'radians', optional
        Unit of the returned |lon| and |lat|: decimal degrees or radians.
        The default is 'dec_deg'.
    A : int or float, optional
        Semi major axis (equatorial radius) of the ellipsoid.
        The default is 6378137.: for WGS84.
    E2 : int or float, optional
        Eccentricity of the ellipsoid.
        The default is 0.006694380022903: for WGS84.

    Raises
    ------
    TypeError
        If any parameter does not have the right type.
    ValueError
        If |unit| is not 'dec_deg' nor 'radians'.

    Returns
    -------
    lon : float or np.ndarray
        Longitude, in |unit|.
    lat : float or np.ndarray
        Latitude, in |unit|.
    h : float or np.ndarray
        Height above the ellipsoid, in meters.
        
    Note
    ----
    Default ellpsoid is GRS80, used for WGS84 with:
     - A = 6378137.            # semi major axis = equatorial radius
     - E2 = 0.006694430022903  # eccentricity
     - F = 1.-sqrt(1-E2)       # flattening

    Examples
    --------
    In [1]: from itsa.lib.coordinates import xyz2geo

    In [2]: xyz2geo(-3522845.0631,2777144.0519,4518959.1684)
    Out[2]: (141.7504319598889, 45.402994292886575, 74.65988670475781)

    In [3]: xyz2geo(-3522845.0631,2777144.0519,4518959.1684,'radians')
    Out[3]: (2.4740117538242603, 0.7924317406750654, 74.65988670475781)

    In [4]: xyz2geo([-3522845.0631,-3522845.0657],2777144.0519,4518959.1684)
    Out[4]:
    (array([141.75043196, 141.75043198]),
     array([45.40299429, 45.40299428]),
     array([74.6598867 , 74.66132031]))

    In [5]: xyz2geo([-3522845.0631,-3522845.0657],[2777144.0519,2777144.0518],
                    4518959.1684,'radians')
    Out[5]:
    (array([2.47401175, 2.47401175]),
     array([0.79243174, 0.79243174]),
     array([74.6598867 , 74.66127684]))

    In [6]: xyz2geo([-3522845.0631,-3522845.0657],[2777144.0519,2777144.0518],
                    [4518959.1684,4518959.1690])
    Out[6]:
    (array([141.75043196, 141.75043198]),
     array([45.40299429, 45.40299428]),
     array([74.6598867 , 74.66170408]))

    """

    #######################################
    def _check_param(x, y, z, unit, A, E2):
        """
        Raise error if one parameter is invalid an adapt values
        """
        # Import
        from itsa.lib.modif_vartype import adapt_shape
        # Check |x|, |y| and |z|
        _xyzOK(x, y, z)
        (x, y, z) = adapt_shape([x, y, z])
        # Check |unit|
        if not isinstance(unit, str):
            raise TypeError('Unit must be str: |type(unit)=%s|.' % type(unit))
        if unit not in ['dec_deg', 'radians']:
            raise ValueError(("Unit must be 'dec_deg' or 'radians': "
                              "|unit='%s'|.") % unit)
        # Check |A|
        if not isinstance(A, (int, float)):
            raise TypeError(('Semi major axis must be int or float: '
                             '|type(A)=%s|.') % type(A))
        # Check |E2|
        if not isinstance(E2, (int, float)):
            raise TypeError(('Eccentricity must be int or float: '
                             '|type(E2)=%s|.') % type(E2))
        # Adapt |x|, |y| and |z|
        return adapt_shape([x, y, z])
    #######################################

    # Check parameters
    (x, y, z) = _check_param(x, y, z, unit, A, E2)

    # Import
    import numpy as np

    # Get lat,lon,h
    F = 1.-np.sqrt(1-E2)

    TP = np.sqrt(x**2+y**2)
    R = np.sqrt(TP**2+z**2)

    TMU = np.arctan2(z/TP*((1.-F)+E2*A/R), 1)
    lon = np.arctan2(y, x)

    S3 = np.sin(TMU)**3
    C3 = np.cos(TMU)**3
    T1 = z*(1-F)+E2*A*S3
    T2 = (1-F)*(TP-E2*A*C3)

    lat = np.arctan2(T1, T2)
    h = TP*np.cos(lat)+z*np.sin(lat)
    h = h-A*np.sqrt(1-E2*np.sin(lat)**2)

    # Change unit
    if unit == 'dec_deg':
        lon = np.degrees(lon)
        lat = np.degrees(lat)

    # Return
    return lon, lat, h


###########################################################################
def geo2xyz(lon, lat, h, unit='dec_deg', A=6378137., E2=0.006694380022903):
    """
    Convert geodetic coordinates (lon,lat,h) to geocentric cartesian
    coordinates (XYZ)

    Parameters
    ----------
    lon : int, float, list or np.ndarray
        Longitude, in |unit|.
    lat : int, float, list or np.ndarray
        Latitude, in |unit|.
    h : int, float, list or np.ndarray
        Height above the ellipsoid, in meter.
    unit : 'dec_deg' or 'radians', optional
        Unit of the given |lon| and |lat|: decimal degrees or radians.
        The default is 'dec_deg'.
    A : int or float, optional
        Semi major axis (equatorial radius) of the ellipsoid.
        The default is 6378137.: for WGS84.
    E2 : int or float, optional
        Eccentricity of the ellipsoid.
        The default is 0.006694380022903: for WGS84.

    Raises
    ------
    TypeError
        If any parameter does not have the right type.
    ValueError
        If |unit| is not 'dec_deg' nor 'radians'.

    Returns
    -------
    x : float or np.ndarray
        X coordinates, in meters.
    y : float or np.ndarray
        Y coordinates, in meters.
    z : float or np.ndarray
        Z coordinates, in meters.
        
     Note
     ----
     Default ellpsoid is GRS80, used for WGS84 with:
      - A = 6378137.            # semi major axis = equatorial radius
      - E2 = 0.006694430022903  # eccentricity
      - F = 1.-sqrt(1-E2)       # flattening

     Examples
     --------
     In [1]: from itsa.lib.coordinates import geo2xyz

     In [2]: geo2xyz(141.75,45.40,74.66)
     Out[2]: (-3523010.2146712523, 2777317.3116407953, 4518725.506221269)

     In [3]: import numpy as np

     In [4]: geo2xyz(np.radians(141.75),np.radians(45.40),74.66,'radians')
     Out[4]: (-3523010.2146712523, 2777317.3116407953, 4518725.506221269)

     In [5]: geo2xyz([141.75,141.76],45.40,74.66)
     Out[5]:
     (array([-3523010.21467125, -3523494.89432488]),
      array([2777317.3116408 , 2776702.38806468]),
      array([4518725.50622127, 4518725.50622127]))

     In [6]: geo2xyz(np.radians([141.75,141.76]),np.radians([45.40,45.41]),
                     74.66,'radians')
     Out[6]:
     (array([-3523010.21467125, -3522873.29256287]),
      array([2777317.3116408 , 2776212.53263739]),
      array([4518725.50622127, 4519505.81705015]))

     In [7]: geo2xyz(np.radians([141.75,141.76]),np.radians([45.40,45.41]),
                     [74.66,74.65],'radians')
     Out[7]:
     (array([-3523010.21467125, -3522873.28704896]),
      array([2777317.3116408 , 2776212.52829214]),
      array([4518725.50622127, 4519505.80992867]))

    """

    ###########################################
    def _check_param(lon, lat, h, unit, A, E2):
        """
        Raise error if one parameter is invalid and adapt values
        """
        # Import
        from itsa.lib.modif_vartype import adapt_shape
        # Check |lon|, |lat| and |h|
        _llhOK(lon, lat, h)
        # Check |unit|
        if not isinstance(unit, str):
            raise TypeError('Unit must be str: |type(unit)=%s|.' % type(unit))
        if unit not in ['dec_deg', 'radians']:
            raise ValueError(("Unit must be 'dec_deg' or 'radians': "
                              "|unit='%s'|.") % unit)
        # Check |A|
        if not isinstance(A, (int, float)):
            raise TypeError(('Semi major axis must be int or float: '
                             '|type(A)=%s|.') % type(A))
        # Check |E2|
        if not isinstance(E2, (int, float)):
            raise TypeError('Eccentricity must be int or float: |type(E2)=%s|.'
                            % type(E2))
        # Adapt |lon|, |lat| and |h|
        return adapt_shape([lon, lat, h])
    ###########################################

    # Check parameters
    (lon, lat, h) = _check_param(lon, lat, h, unit, A, E2)

    # Import
    import numpy as np

    # Change unit
    if unit == 'dec_deg':
        lon = np.radians(lon)
        lat = np.radians(lat)

    # Get XYZ
    wnorm = A/np.sqrt(1-E2*np.sin(lat)**2)

    x = (wnorm+h)*np.cos(lat)*np.cos(lon)
    y = (wnorm+h)*np.cos(lat)*np.sin(lon)
    z = (wnorm*(1-E2)+h)*np.sin(lat)

    # Return
    return (x, y, z)


#%%########################
## GEOCENTRIC/GEOSPHERIC ##
###########################

############################################
def xyz2geospheric(x, y, z, unit='dec_deg'):
    """
    Convert geocentric cartesian coordinates (XYZ) to geo-spherical coordinates
    (lon,lat,radius)

    Parameters
    ----------
    x : int, float, list or np.ndarray
        X coordinates, in meters.
    y : int, float, list or np.ndarray
        Y coordinates, in meters.
    z : int, float, list or np.ndarray
        Z coordinates, in meters.
    unit : 'dec_deg' or 'radians', optional
        Unit of the returned |lon| and |lat|: decimal degrees or radians.
        The default is 'dec_deg'.

    Raises
    ------
    TypeError
        If any parameter does not have the right type.
    ValueError
        If |unit| is not 'dec_deg' nor 'radians'.

    Returns
    -------
    lon : float or np.ndarray
        Longitude, in |unit|.
    lat : float or np.ndarray
        Latitude, in |unit|.
    r : float or np.ndarray
        Radius from the Earth's center, in meters.

    Note
    ----
    Be aware that the obtained coordinates are not what is usually taken as
    spherical coordinates, which uses co-latitude

    Examples
    --------
    In [1]: from itsa.lib.coordinates import xyz2geospheric

    In [2]: xyz2geospheric(-3522845.0631,2777144.0519,4518959.1684)
    Out[2]: (141.7504319598889, 45.21058328049073, 6367413.791271776)

    In [3]: xyz2geospheric(-3522845.0631,2777144.0519,4518959.1684,'radians')
    Out[3]: (2.4740117538242603, 0.7890735349916623, 6367413.791271776)

    In [4]: xyz2geospheric([-3522845.0631,-3522845.0657],2777144.0519,
                           4518959.1684)
    Out[4]:
    (array([141.75043196, 141.75043198]),
     array([45.21058328, 45.21058327]),
     array([6367413.79127178, 6367413.79271026]))

    In [5]: xyz2geospheric([-3522845.0631,-3522845.0657],
                           [2777144.0519,2777144.0518],4518959.1684,'radians')
    Out[5]: 
    (array([2.47401175, 2.47401175]),
     array([0.78907353, 0.78907353]),
     array([6367413.79127178, 6367413.79266664]))

    In [6]: xyz2geospheric([-3522845.0631,-3522845.0657],
                           [2777144.0519,2777144.0518],
                           [4518959.1684,4518959.1690])
    Out[6]: 
    (array([141.75043196, 141.75043198]),
     array([45.21058328, 45.21058327]),
     array([6367413.79127178, 6367413.79309246]))

    """

    #############################
    def _check_param(x, y, z, unit):
        """
        Raise error if one parameter is invalid and adapt values
        """
        # Import
        from itsa.lib.modif_vartype import adapt_shape
        # Check |x|, |y| and |z|
        _xyzOK(x, y, z)
        # Check |unit|
        if not isinstance(unit, str):
            raise TypeError('Unit must be str: |type(unit)=%s|.' % type(unit))
        if unit not in ['dec_deg', 'radians']:
            raise ValueError(("Unit must be 'dec_deg' or 'radians': "
                              "|unit='%s'|.") % unit)
        # Adapt |x|, |y| and |z|
        return adapt_shape([x, y, z])
    #############################

    # Check parameters
    (x, y, z) = _check_param(x, y, z, unit)

    # Import
    import numpy as np

    # Get lat,lon,r
    r = np.sqrt(x**2+y**2+z**2)
    lon = np.arctan2(y, x)

    Req = np.sqrt(x**2+y**2)
    if (np.array(Req) != 0.).all():
        lat = np.arctan(z/Req)
    elif (np.array(Req) == 0.).all():
        lat = np.pi/2*z/np.sqrt(z**2)
    else:
        lat = np.zeros(Req.shape)
        lat[Req != 0] = np.arctan(z[Req != 0]/Req[Req != 0])
        lat[Req == 0] = np.pi/2*z[Req == 0]/np.sqrt(z[Req == 0]**2)

    # Change unit
    if unit == 'dec_deg':
        lon = np.degrees(lon)
        lat = np.degrees(lat)

    # Return
    return (lon, lat, r)


#%%###################
## INTERN FUNCTIONS ##
######################

####################
def _xyzOK(x, y, z):
    """
    Raise error if XYZ parameters have not the same type or shape

    Parameters
    ----------
    x : int, float, list or np.ndarray
        X coordinates to test.
    y : int, float, list or np.ndarray
        Y coordinates to test.
    z : int, float, list or np.ndarray
        Z coordinates to test.

    Raises
    ------
    ValueError
        If any parameter is list and cannot be converted to np.ndarray.
        If any parameter is not 1D list nor array.
        If any parameter values are not int nor float.
        If np.ndarray parameters do not have the same size.
    TypeError
        If any parameter does not have the right type.

    """
    # Import
    import numpy as np
    from itsa.lib.modif_vartype import list2ndarray, nptype2pytype

    # Change type
    # List to np.ndarray
    if isinstance(x, list):
        (x, err_x) = list2ndarray(x)
        if err_x:
            raise ValueError(('X list must be convertible into np.ndarray (or '
                              'X can be int, float or np.ndarray): |x=%s|.')
                             % str(x))
    if isinstance(y, list):
        (y, err_y) = list2ndarray(y)
        if err_y:
            raise ValueError(('Y list must be convertible into np.ndarray (or '
                              'Y can be int, float or np.ndarray): |y=%s|.')
                             % str(y))
    if isinstance(z, list):
        (z, err_z) = list2ndarray(z)
        if err_z:
            raise ValueError(('Z list must be convertible into np.ndarray (or '
                              'Z can be int, float or np.ndarray): |z = %s|.')
                             % str(z))
    # Numpy type to Python type
    (x, y, z) = nptype2pytype([x, y, z])

    # Type errors
    if not isinstance(x, (int, float, np.ndarray)):
        raise TypeError(('X must be int, float, list or np.ndarray: '
                         '|type(x)=%s|.') % type(x))
    if not isinstance(y, (int, float, np.ndarray)):
        raise TypeError(('Y must be int, float, list or np.ndarray: '
                         '|type(y)=%s|.') % type(y))
    if not isinstance(z, (int, float, np.ndarray)):
        raise TypeError(('Z must be int, float, list or np.ndarray: '
                         '|type(z)=%s|.') % type(z))

    # Dimension and value errors
    # |x|
    if isinstance(x, np.ndarray):
        # 1D?
        if x.ndim != 1:
            raise ValueError(('X must be int, float, 1D list or 1D np.ndarray:'
                              ' |x.dim=%d|.') % x.dim)
        # Same shape?
        if isinstance(y, np.ndarray) and x.shape != y.shape:
            raise ValueError(('X and Y must have the same shape: '
                              '|x.shape=%s| and |y.shape=%s|.')
                             % (x.shape, y.shape))
        if isinstance(z, np.ndarray) and x.shape != z.shape:
            raise ValueError(('X and Z must have the same shape: |x.shape=%s| '
                              'and |z.shape=%s|.') % (x.shape, z.shape))
        # Valid values?
        if x.dtype not in ['int', 'float']:
            raise ValueError(('X must be int, float, list of int, list of '
                              'float, int np.ndarray or float np.ndarray: '
                              '|x.dtype=%s|.') % x.dtype)
    # |y|
    if isinstance(y, np.ndarray):
        # 1D?
        if y.ndim != 1:
            raise ValueError(('Y must be int, float, 1D list or 1D np.ndarray:'
                              ' |y.ndim=%d|.') % y.ndim)
        # Same shape?
        if isinstance(z, np.ndarray) and y.shape != z.shape:
            raise ValueError(('Y and Z must have the same shape: |y.shape=%s| '
                              'and |z.shape=%s|.') % (y.shape, z.shape))
        # Valid values?
        if y.dtype not in ['int', 'float']:
            raise ValueError(('Y must be int, float, list of int, list of '
                              'float, int np.ndarray or float np.ndarray: '
                              '|y.dtype=%s|.') % y.dtype)
    # |z|
    if isinstance(z, np.ndarray):
        # 1D?
        if z.ndim != 1:
            raise ValueError(('Z must be int, float, 1D list or 1D np.ndarray:'
                              ' |z.ndim=%d|.') % z.ndim)
        # Valid values?
        if z.dtype not in ['int', 'float']:
            raise ValueError(('Z must be int, float, list of int, list of '
                              'float, int np.ndarray or float np.ndarray: '
                              '|z.dtype=%s|.') % z.dtype)


########################
def _llhOK(lon, lat, h):
    """
    Raise error if longitude, latitude and height parameters have not the same
    type or shape

    Parameters
    ----------
    lon : int, float, list or np.ndarray
        Longitude test.
    lat : int, float, list or np.ndarray
        Latitude to test.
    h : int, float, list or np.ndarray
        Height above the ellipsoid to test.

    Raises
    ------
    ValueError
        If any parameter is list and cannot be converted to np.ndarray.
        If any parameter is not 1D list nor array.
        If any parameter values are not int nor float.
        If np.ndarray parameters do not have the same size.
    TypeError
        If any parameter does not have the right type.
    
    """
    # Import
    import numpy as np
    from itsa.lib.modif_vartype import list2ndarray, nptype2pytype

    # Change type
    # List to np.ndarray
    if isinstance(lon, list):
        (lon, err_lon) = list2ndarray(lon)
        if err_lon:
            raise ValueError(('Longitude list must be convertible into '
                              'np.ndarray (or longitude can be int, float or '
                              'np.ndarray): |lon=%s|.') % str(lon))
    if isinstance(lat, list):
        (lat, err_lat) = list2ndarray(lat)
        if err_lat:
            raise ValueError(('Latitude list must be convertible into '
                              'np.ndarray (or latitude can be int, float or '
                              'np.ndarray): |lat=%s|.') % str(lat))
    if isinstance(h, list):
        (h, err_h) = list2ndarray(h)
        if err_h:
            raise ValueError(('Height list must be convertible into np.ndarray'
                              ' (or height can be int, float or np.ndarray): '
                              '|h = %s|.') % str(h))
    # Numpy type to Python type
    (lon, lat, h) = nptype2pytype([lon, lat, h])

    # Type errors
    if not isinstance(lon, (int, float, np.ndarray)):
        raise TypeError(('Longitude must be int, float, list or np.ndarray: '
                         '|type(lon)=%s|.') % type(lon))
    if not isinstance(lat, (int, float, np.ndarray)):
        raise TypeError(('Latitude must be int, float, list or np.ndarray: '
                         '|type(lat)=%s|.') % type(lat))
    if not isinstance(h, (int, float, np.ndarray)):
        raise TypeError(('Height must be int, float, list or np.ndarray: '
                         '|type(h)=%s|.') % type(h))

    # Dimension and value errors
    # |lon|
    if isinstance(lon, np.ndarray):
        # 1D?
        if lon.ndim != 1:
            raise ValueError(('Longitude must be int, float, 1D list or 1D '
                              'np.ndarray: |lon.dim=%d|.') % lon.dim)
        # Same shape?
        if isinstance(lat, np.ndarray) and lon.shape != lat.shape:
            raise ValueError(('Longitude and latitude must have the same '
                              'shape: |lon.shape=%s| and |lat.shape=%s|.')
                             % (lon.shape, lat.shape))
        if isinstance(h, np.ndarray) and lon.shape != h.shape:
            raise ValueError(('Longitude and height must have the same shape:'
                              ' |lon.shape=%s| and |h.shape=%s|.')
                             % (lon.shape, h.shape))
        # Valid values?
        if lon.dtype not in ['int', 'float']:
            raise ValueError(('Longitude must be int, float, list of int, '
                              'list of float, int np.ndarray or float '
                              'np.ndarray: |lon.dtype=%s|.') % lon.dtype)
    # |lat|
    if isinstance(lat, np.ndarray):
        # 1D?
        if lat.ndim != 1:
            raise ValueError(('Latitude must be int, float, 1D list or 1D '
                              'np.ndarray: |lat.ndim=%d|.') % lat.ndim)
        # Same shape?
        if isinstance(h, np.ndarray) and lat.shape != h.shape:
            raise ValueError(('Latitude and height must have the same shape: '
                              '|lat.shape=%s| and |h.shape=%s|.')
                             % (lat.shape, h.shape))
        # Valid values?
        if lat.dtype not in ['int', 'float']:
            raise ValueError(('Latitude must be int, float, list of int, list '
                              'of float, int np.ndarray or float np.ndarray: '
                              '|lat.dtype=%s|.') % lat.dtype)
    # |h|
    if isinstance(h, np.ndarray):
        # 1D?
        if h.ndim != 1:
            raise ValueError(('Height must be int, float, 1D list or 1D '
                              'np.ndarray: |h.ndim=%d|.') % h.ndim)
        # Valid values?
        if h.dtype not in ['int', 'float']:
            raise ValueError(('Height must be int, float, list of int, '
                              'list of float, int np.ndarray or float '
                              'np.ndarray: |h.dtype=%s|.') % h.dtype)
