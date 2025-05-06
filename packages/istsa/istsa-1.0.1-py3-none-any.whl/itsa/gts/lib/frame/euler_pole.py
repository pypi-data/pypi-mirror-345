"""
    Developed at: ISTerre
    By: Lou MARILL
    Based on: PYACS module
"""


#################################################################
def remove_pole(self, pole, type_pole='rot', unit_pole='radians',
                in_place=False, warn=True):
    """
    Remove velocity predicted by an Euler pole or a rotation rate vector from 
    Gts

    Parameters
    ----------
    pole : list or np.ndarray
        Euler pole or cartesian rotation rate vector in |unit_pole|.
    type_pole : 'rot' or 'euler', optional
        Rotation type:
            'rot': |pole| is a cartesian rotation rate vector,
            'euler': |pole| is an Euler pole.
        The default is 'rot'.
    unit_pole : 'radians', 'mas' or 'dec_deg', optional
        Unit of |pole| variable:
            'mas' must be for cartesian rotation,
            'dec_deg' must be for Euler pole.
        The default is 'radians'.
    in_place : bool, optional
        Change data directly in |self| if true.
        The default is False: create and return new Gts 
                              (|self| is not updated).
    warn : bool, optional
        Print warning if true.
        The default is True.

    Raises
    ------
    ValueError
        If |pole| is list and cannot be convert to np.ndarray.
        If |pole| does not have exactly 3 values.
        If |type_pole| is not 'rot' nor 'euler'.
        If |unit_pole| is not 'radians', 'mas' nor 'dec_deg'.
    TypeError
        If any parameter does not have the right type.
    WARNING
        If |in_place| is not bool: |in_place| set to False.

    Return
    ------
    Gts
        Only if |in_place| is false.
        New Gts with the pole removed.

    """

    ###################################################################
    def _check_param(self, pole, type_pole, unit_pole, in_place, warn):
        """
        Raise error is one parameter is invalid and adapt some parameter values
        """
        # Import
        import numpy as np
        from itsa.lib.modif_vartype import list2ndarray, adapt_bool

        # Change type
        # |pole|
        if isinstance(pole, list):
            (pole, err_pole) = list2ndarray(pole)
            if err_pole:
                raise ValueError(('Rotation list must be convertible '
                                  'into np.ndarray: |pole=%s|.') % str(pole))

        # Check
        # |self|
        self.check_gts()
        # |pole|
        if not isinstance(pole, np.ndarray):
            raise TypeError(('Rotation must be list or np.ndarray: '
                             '|type(pole)=%s|.') % type(pole))
        if pole.size != 3:
            raise ValueError(('Rotation must have exactly 3 values: '
                              '|pole.size=%d|.') % pole.size)
        # |type_pole|
        if not isinstance(type_pole, str):
            raise TypeError(('Rotation type must be str: '
                             '|type(type_pole)=%s|') % type(type_pole))
        if type_pole not in ['rot', 'euler']:
            raise ValueError(("Rotation type must be 'rot' (for cartesian "
                              "rotation rate vector) or 'euler' (for Euler "
                              "pole): |type_pole='%s'|.") % type_pole)
        # |unit_pole|
        if not isinstance(unit_pole, str):
            raise TypeError(('Rotation unit must be str: '
                             '|type(unit_pole)=%s|.') % type(unit_pole))
        if unit_pole not in ['radians', 'mas', 'dec_deg']:
            raise ValueError(("Rotation unit must be 'radians', 'mas' or "
                              "'dec_deg': |unit_pole=%s|.") % unit_pole)

        # Adapt
        # |pole|
        pole = pole.reshape(3, 1)
        # |in_place|
        (in_place, warn_place) = adapt_bool(in_place)
        # |warn|
        (warn, _) = adapt_bool(warn, True)

        # Warning
        if warn and warn_place:
            print('[WARNING] from method [remove_pole] in [%s]' % __name__)
            print(('\t|in_place| parameter set to False because '
                   '|type(in_place)!=bool|!'))
            print('\tNew Gts %s is returned (and old one is not updated)!'
                  % self.code)
            print()

        # Return
        return pole, in_place
    ###################################################################

    # Check parameters
    (pole, in_place) = _check_param(
        self, pole, type_pole, unit_pole, in_place, warn)

    # Import
    from itsa.lib.euler import pole as euler_pole

    # Get velocity from rotation vector
    (Vn, Ve) = euler_pole(self.NEU0[1], self.NEU0[0],self.NEU0[2], pole,
                          type_euler=type_pole, unit_W=unit_pole)

    # Return
    return self.remove_velocity(Vn, Ve, 0., in_place=in_place)
