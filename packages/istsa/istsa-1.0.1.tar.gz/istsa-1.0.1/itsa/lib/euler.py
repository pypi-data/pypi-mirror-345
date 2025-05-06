"""
    Euler poles manipulation and prediction

    !!! Warning: You need to add the module 'itsa' to your Python path to use
    these functions

    ----
    Developed at: ISTerre
    By: Lou MARILL
    Based on: PYACS module
"""


################################################################
def rot2euler(wx, wy, wz, unit_rot='mas', unit_euler='dec_deg'):
    """
    Convert rotation rate vector (wx,wy,wz) into Euler pole (lon,lat,omega)

    Parameters
    ----------
    wx : int or float
        X component of the rotation rate vector, in |rot_unit|/yr.
    wy : int or float
        Y component of the rotation rate vector, in |rot_unit|/yr.
    wz : int or float
        Z component of the rotation rate vector, in |rot_unit|/yr.
    unit_rot : 'mas' or 'radians', optional
        Unit of the rotation rate vector.
        The default is 'mas'.
    unit_euler : 'dec_deg' or 'radians', optional
        Unit of the returned Euler pole.
        The default is 'dec_deg'.

    Raises
    ------
    TypeError
        If any parameter does not have the right type.
    ValueError
        If |unit_rot| is not 'mas' nor 'radians'.
        If |unit_euler| is not 'dec_deg' or 'radians'.

    Returns
    -------
    lon : float
        Longitude of the Euler pole, in |euler_unit|.
    lat : float
        Latitude of the Euler pole, in |euler_unit|.
    omega : float
        Angular velocity of the Euler pole, in |euler_unit|/Myr.
        
    Note
    ----
    Longitude and latitude are relative to the sphere, not the ellipsoid.
    This is because Euler pole and rigid rotation only have sense on a sphere.

    Examples
    --------
    In [1]: from itsa.lib.euler import rot2euler

    In [2]: rot2euler(-0.085,-0.531,0.770)
    Out[2]: (-99.09448520428982, 55.06994336719981, 0.26088731544102467)

    In [3]: import numpy as np

    In [4]: rot2euler(np.radians(-0.085),np.radians(-0.531),np.radians(0.770),
                      unit_rot='radians')
    Out[4]: (-99.09448520428982, 55.06994336719981, 939194.3355876887)

    In [5]: rot2euler(-0.085,-0.531,0.770,unit_euler='radians')
    Out[5]: (-1.729525037383663, 0.9611518306444493, 0.004553342631134923)

    """

    ###################################################
    def _check_param(wx, wy, wz, unit_rot, unit_euler):
        """ Raise error is one parameter is invalid """
        # Import
        from itsa.lib.modif_vartype import nptype2pytype

        # Change type
        (wx, wy, wz) = nptype2pytype([wx, wy, wz])

        # Check
        # |wx|
        if not isinstance(wx, (int, float)):
            raise TypeError('X rotation must be int or float: |type(wx)=%s|.'
                            % type(wx))
        # |wy|
        if not isinstance(wy, (int, float)):
            raise TypeError('Y rotation must be int or float: |type(wy)=%s|.'
                            % type(wy))
        # |wz|
        if not isinstance(wz, (int, float)):
            raise TypeError('Z rotation must be int or float: |type(wz)=%s|.'
                            % type(wz))
        # |unit_rot|
        if not isinstance(unit_rot, str):
            raise TypeError(('Rotation vector unit must be str: '
                             '|type(unit_rot)=%s|.') % type(unit_rot))
        if unit_rot not in ['mas', 'radians']:
            raise ValueError(("Rotation vector unit must be 'mas' or "
                              "'radians': |unit_rot='%s'|.") % unit_rot)
        # |unit_euler|
        if not isinstance(unit_euler, str):
            raise TypeError(('Euler pole unit must be str: '
                             '|type(unit_euler)=%s|.') % type(unit_euler))
        if unit_euler not in ['dec_deg', 'radians']:
            raise ValueError(("Euler pole unit must be 'dec_deg' or "
                              "'radians': |unit_euler='%s'|.") % unit_euler)
    ###################################################

    # Check parameters
    _check_param(wx, wy, wz, unit_rot, unit_euler)

    # Import
    import numpy as np

    # Change rotation vector unit
    if unit_rot == 'mas':
        wx = np.radians(wx/3.6e6)
        wy = np.radians(wy/3.6e6)
        wz = np.radians(wz/3.6e6)

    # Find Euler pole latitude
    W = np.sqrt(wx**2+wy**2+wz**2)
    lat = np.pi/2-np.arccos(wz/W)

    # Find Euler pole longitude
    if wx > 0:
        lon = np.arctan(wy/wx)
    elif wx < 0:
        if wy > 0:
            lon = np.arctan(wy/wx)+np.pi
        else:
            lon = np.arctan(wy/wx)-np.pi
    else:  # Wx==0
        if wy > 0:
            lon = np.pi/2
        else:
            lon = -np.pi/2

    # Find Euler pole angular velocity
    omega = W*1e6

    # Change Euler pole unit
    if unit_euler == 'dec_deg':
        lat = np.degrees(lat)
        lon = np.degrees(lon)
        omega = np.degrees(omega)

    return lon, lat, omega


#####################################################################
def euler2rot(lon, lat, omega, unit_euler='dec_deg', unit_rot='mas'):
    """
    Convert Euler pole (lon,lat,omega) into cartesian geocentric rotation rate
    vector (Wx,Wy,Wz)

    Parameters
    ----------
    lon : float
        Longitude of the Euler pole, in |euler_unit|.
    lat : float
        Latitude of the Euler pole, in |euler_unit|.
    omega : float
        Angular velocity of the Euler pole, in |euler_unit|/Myr.
    unit_euler : 'dec_deg' or 'radians', optional
        Unit of the returned Euler pole.
        The default is 'dec_deg'.
    unit_rot : 'mas' or 'radians', optional
        Unit of the rotation rate vector.
        The default is 'mas'.

    Raises
    ------
    TypeError
        If any parameter does not have the right type.
    ValueError
        If |unit_euler| is not 'dec_deg' or 'radians'.
        If |unit_rot| is not 'mas' nor 'radians'.    

    Returns
    -------
    wx : float
        X component of the rotation rate vector, in |rot_unit|/yr.
    wy : float
        Y component of the rotation rate vector, in |rot_unit|/yr.
    wz : float
        Z component of the rotation rate vector, in |rot_unit|/yr.

    Note
    ----
    Longitude and latitude are relative to the sphere, not the ellipsoid.

    Examples
    --------
    In [1]: from itsa.lib.euler import euler2rot

    In [2]: euler2rot(-99,55,0.26)
    Out[2]: (-0.08398458710952142, -0.530257814072099, 0.7667263134544964)

    In [3]: import numpy as np

    In [4]: euler2rot(np.radians(-99),np.radians(55),np.radians(0.26),
                      unit_euler="radians")
    Out[4]: (-0.08398458710952142, -0.530257814072099, 0.7667263134544964)

    In [5]: euler2rot(-99,55,0.26,unit_rot="radians")
    Out[5]: (-4.071687683303156e-10, -2.5707624277739025e-09,
             3.717194064294183e-09)
    
    """

    ########################################################
    def _check_param(lon, lat, omega, unit_euler, unit_rot):
        """
        Raise error is one parameter is invalid 
        """
        # Import
        from itsa.lib.modif_vartype import nptype2pytype

        # Change type
        (lon, lat, omega) = nptype2pytype([lon, lat, omega])

        # Check
        # |lon|
        if not isinstance(lon, (int, float)):
            raise TypeError('Longitude must be int or float: |type(lon)=%s|.'
                            % type(lon))
        # |lat|
        if not isinstance(lat, (int, float)):
            raise TypeError('Latitude must be int or float: |type(lat)=%s|.'
                            % type(lat))
        # |omega|
        if not isinstance(omega, (int, float)):
            raise TypeError(('Angular velocity must be int or float: '
                             '|type(omega)=%s|.') % type(omega))
        # |unit_euler|
        if not isinstance(unit_euler, str):
            raise TypeError(('Euler pole unit must be str: '
                             '|type(unit_euler)=%s|.') % type(unit_euler))
        if unit_euler not in ['dec_deg', 'radians']:
            raise ValueError(("Euler pole unit must be 'dec_deg' or 'radians':"
                              " |unit_euler='%s'|.") % unit_euler)
        # |unit_rot|
        if not isinstance(unit_rot, str):
            raise TypeError(('Rotation vector unit must be str: '
                             '|type(unit_rot)=%s|.') % type(unit_rot))
        if unit_rot not in ['mas', 'radians']:
            raise ValueError(("Rotation vector unit must be 'mas' or "
                              "'radians': |unit_rot='%s'|.") % unit_rot)
    ########################################################

    # Check parameters
    _check_param(lon, lat, omega, unit_euler, unit_rot)

    # Import
    import numpy as np

    # Change Euler pole unit
    if unit_euler == 'dec_deg':
        lon = np.radians(lon)
        lat = np.radians(lat)
        omega = np.radians(omega)

    # Compute rotation vector
    wx = np.cos(lat)*np.cos(lon)*omega*1e-6
    wy = np.cos(lat)*np.sin(lon)*omega*1e-6
    wz = np.sin(lat)*omega*1e-6

    # Change rotation vector unit
    if unit_rot == 'mas':
        wx = np.degrees(wx)*3.6e6
        wy = np.degrees(wy)*3.6e6
        wz = np.degrees(wz)*3.6e6

    return (wx, wy, wz)


##############################################################
def pole(lon, lat, h, W, type_euler='rot', unit_ll='dec_deg',
         unit_W='radians'):
    """
    Predict velocity at (|lon|,|lat|,|h|) for a given Euler pole or cartesian
    rotation rate vector |W|

    Parameters
    ----------
    lon : float
        Longitude of the point, in |unit_ll|.
    lat : float
        Latitude of the point, in |unit_ll|.
    he : float
        Height of the point, in meter.
    W : np.ndarray
        Euler pole or cartesian rotation rate vector, in |unit_W|.
    type_euler : 'rot' or 'euler', optional
        Rotation type:
            'rot': |W| is a cartesian rotation rate vector,
            'euler': |W| is an Euler pole.
        The default is 'rot'.
    unit_ll : 'dec_deg' or 'radians', optional
        Unit of the longitude and latitude of the point.
        The default is 'dec_deg'.
    unit_W : radians', 'mas' or 'dec_deg', optional
        Unit of |W| variable:
            'mas' must be for cartesian rotation,
            'dec_deg' must be for Euler pole.
        The default is 'radians'.

    Raises
    ------
    ValueError
        If |W| is list and cannot be convert to np.ndarray.
        If |W| does not have exactly 3 values.
        If |W| values are not int nor float
        If |type_euler| is not 'rot' nor 'euler'.
        If |unit_ll| is not 'dec_deg' nor 'radians'.
        If |unit_W| is not 'radians', 'mas' nor 'dec_deg'.
    TypeError
        If any parameter does not have the right type.

    Returns
    -------
    Vn : float
        North velocity predicted at the given point for the given Euler pole,
        in milimeter.
    Ve : float
        East velocity predicted at the given point for the given Euler pole,
        in milimeter.

    Note
    ----
    You can use 'mas' unit for Euler pole and 'dec_deg' for cartesian rotation
    rate vector but these are not conventional units.

    Examples
    --------
    In [1]: from itsa.lib.euler import pole

    In [2]: pole(141.75,45.40,74.66,[-0.085,-0.531,0.770],unit_W='mas')
    Out[2]: (-14.497409450391434, 22.486356838178036)

    In [3]: import numpy as np

    In [4]: pole(np.radians(141.75),np.radians(45.40),74.66,
                 np.radians(np.array([-0.085,-0.531,0.770])/3.6e6),
                 unit_ll='radians')
    Out[4]: (-14.497409450391434, 22.486356838178036)

    In [5]: from itsa.lib.euler import rot2euler

    In [6]: (wx,wy,wz) = rot2euler(-0.085,-0.531,0.770,'mas','radians')

    In [7]: pole(141.75,45.40,74.66,[wx,wy,wz],type_euler='euler')
    Out[7]: (-14.497409450391435, 22.486356838178036)

    In [8]: (wx,wy,wz) = rot2euler(-0.085,-0.531,0.770,'mas','dec_deg')

    In [9]: pole(141.75,45.40,74.66,[wx,wy,wz],type_euler='euler',
                 unit_W='dec_deg')
    Out[9]: (-14.497409450391435, 22.486356838178033)

    """

    ###############################################################
    def _check_param(lon, lat, h, W, type_euler, unit_ll, unit_W):
        """
        Raise error is one parameter is invalid and adapt some parameter values
        """
        # Import
        import numpy as np
        from itsa.lib.modif_vartype import list2ndarray, nptype2pytype

        # Change type
        # |lon|, |lat| and |he|
        (lon, lat, h) = nptype2pytype([lon, lat, h])
        # |W|
        if isinstance(W, list):
            (W, err_W) = list2ndarray(W)
            if err_W:
                raise ValueError(('Rotation vector list must be convertible '
                                  'into np.ndarray: |W=%s|.') % str(W))

        # Check
        # |lon|
        if not isinstance(lon, (int, float)):
            raise TypeError('Longitude must be int or float: |type(lon)=%s|.'
                            % type(lon))
        # |lat|
        if not isinstance(lat, (int, float)):
            raise TypeError('Latitude must be int or float: |type(lat)=%s|.'
                            % type(lat))
        # |he|
        if not isinstance(h, (int, float)):
            raise TypeError('Height must be int or float: |type(he)=%s|.'
                            % type(h))
        # |W|
        if not isinstance(W, np.ndarray):
            raise TypeError(('Rotation vector must be list or np.ndarray: '
                             '|type(W)=%s|.') % type(W))
        if W.size != 3:
            raise ValueError(('Rotation vector must have exactly 3 values: '
                              '|W.size=%d|.') % W.size)
        if W.dtype not in ['int', 'float']:
            raise ValueError(('Rotation vector must be list of int, list of '
                              'float, int np.ndarray or float np.ndarray: '
                              '|W.dtype=%s|.') % W.dtype)
        # |type_euler|
        if not isinstance(type_euler, str):
            raise TypeError('Rotation type must be str: |type(type_euler)=%s|'
                            % type(type_euler))
        if type_euler not in ['rot', 'euler']:
            raise ValueError(("Rotation type must be 'rot' (for cartesian "
                              "rotation rate vector) or 'euler' (for Euler "
                              "pole): |type_euler='%s'|.") % type_euler)
        # |unit_ll|
        if not isinstance(unit_ll, str):
            raise TypeError('Coordinates unit must be str: |type(unit_ll)=%s|.'
                            % type(unit_ll))
        if unit_ll not in ['dec_deg', 'radians']:
            raise ValueError(("Coordinates unit must be 'dec_deg' or "
                              "'radians': |unit_ll=%s|.") % unit_ll)
        # |unit_W|
        if not isinstance(unit_W, str):
            raise TypeError('Rotation unit must be str: |type(unit_W)=%s|.'
                            % type(unit_W))
        if unit_W not in ['radians', 'mas', 'dec_deg']:
            raise ValueError(("Rotation unit must be 'radians', 'mas' or "
                              "'dec_deg': |unit_W=%s|.") % unit_W)

        # Return
        return W.reshape(3, 1)
    ###############################################################

    # Check parameters
    W = _check_param(lon, lat, h, W, type_euler, unit_ll, unit_W)

    # Import
    import numpy as np
    from itsa.lib.coordinates import geo2xyz, xyz2geospheric
    from itsa.lib.coordinates import mat_rot_general_to_local

    # Get rotation rate vector
    if unit_W == 'mas':
        W = W/3.6e6
        unit_W = 'dec_deg'

    if type_euler == 'euler':
        (wx, wy, wz) = euler2rot(W[0, 0], W[1, 0], W[2, 0],
                                 unit_euler=unit_W, unit_rot='radians')
        W = np.array([[wx], [wy], [wz]])
    else:
        if unit_W == 'dec_deg':
            W = np.radians(W)

    # Get spherical coordinates
    (x, y, z) = geo2xyz(lon, lat, h, unit=unit_ll)
    (l, p, _) = xyz2geospheric(x, y, z)
    R = mat_rot_general_to_local(l, p)

    # Observation equation in local frame
    Ai = np.array([[0, z, -y], [-z, 0, x], [y, -x, 0]])
    RAi = np.dot(R, Ai)

    # Predicted velocity
    Pi = np.dot(RAi, W)
    Vn = Pi[1, 0]*1e3
    Ve = Pi[0, 0]*1e3

    return Vn, Ve
