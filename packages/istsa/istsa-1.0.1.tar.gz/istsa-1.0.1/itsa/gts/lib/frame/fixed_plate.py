"""
    Developed at: ISTerre
    By: Lou MARILL
"""

#%%###################
## GLOBAL VARIABLES ##
######################

# From Altamimi et al. [2017]: ITRF2014 plate motion model
_plate_trans = {}
_plate_trans['2014'] = {'ANTA': [-0.248, -0.324,  0.675],
                        'ARAB': [+1.154, -0.136,  1.444],
                        'AUST': [+1.510,  1.182,  1.215],
                        'EURA': [-0.085, -0.531,  0.770],
                        'INDI': [+1.154, -0.005,  1.454],
                        'NAZC': [-0.333, -1.544,  1.623],
                        'NOAM': [+0.024, -0.694, -0.063],
                        'NUBI': [+0.099, -0.614,  0.733],
                        'PCFC': [-0.409,  1.047, -2.169],
                        'PS': [0.1308, -0.3115, 0.0496],
                        'SOAM': [-0.270, -0.301, -0.140],
                        'SOMA': [-0.121, -0.794,  0.884]}
# Antartica       ANTA
# Arabia          ARAB
# Australia       AUST
# Eurasia         EURA
# India           INDI
# Nasca           NAZC
# North America   NOAM
# Nubia           NUBI
# Pacific         PCFC
# Peruvian Sliver   PS (Villegas-Lanza et al., 2016)
# South America   SOAM
# Somalia         SOMA

# You can add more keys to |_plate_trans| dictionary to allow more conversions

#%%##########
## METHODS ##
#############

########################################################################
def fixed_plate(self, plate='NOAM', itrf_ref='ITRF2014', in_place=False,
                warn=True):
    """
    Convert Gts reference frame from ITRF or IGS to plate fixed

    Parameters
    ----------
    plate : str, optional
        Fixed plate for the final reference frame.
        The default is 'NOAM'.
    itrf_ref : str, optional
        Reference ITRF or IGS frame for the conversion.
        The default is 'ITRF2014'.
    in_place : bool, optional
        Change data directly in |self| if true.
        The default is False: create and return new Gts 
                              (|self| is not updated).
    warn : bool, optional
        Print warning if true.
        The default is True.

    Raises
    ------
    GtsValueError
        If |self.ref_frame| does not start by 'IGS' nor 'ITRF'.
    TypeError
        If any parameter does not have the right type.
    ValueError
        If |ref_frame| does not start by 'IGS' nor 'ITRF'.
    KeyError
        If the conversion is not defined in GLOBAL VARIABLES.
    WARNING
        If |in_place| is not bool: |in_place| set to False.

    Return
    ------
    Gts
        Only if |in_place| is false.
        New Gts with the |plate| fixed reference frame.

    """

    ########################################################
    def _check_param(self, plate, itrf_ref, in_place, warn):
        """
        Raise error is one parameter is invalid and adapt some parameter values
        """
        # Import
        from itsa.gts.errors import GtsValueError
        from itsa.gts.lib.frame.itrf_convert import _itrf_year
        from itsa.lib.modif_vartype import adapt_bool

        # Check type and specific values
        # |self|
        self.check_gts()
        # |self.ref_frame|
        if (self.ref_frame[:3].upper() != 'IGS' and
            self.ref_frame[:4].upper() != 'ITRF'):
            raise GtsValueError(("Gts %s reference frame must be 'IGS' or "
                                 "'ITRF': |ref_frame='%s'|.")
                                % (self.code, self.ref_frame))
        # |plate|
        if not isinstance(plate, str):
            raise TypeError('Fixed plate must be str: |type(plate)=%s|.'
                            % type(plate))
        # |itrf_ref|
        if not isinstance(itrf_ref, str):
            raise TypeError(('Reference frame for the conversion must be str: '
                             '|type(itrf_ref)=%s|.') % type(itrf_ref))
        if itrf_ref[:3].upper() != 'IGS' and itrf_ref[:4].upper() != 'ITRF':
            raise ValueError(("Reference frame for the conversion must be "
                              "'IGS' or 'ITRF': |itrf_ref='%s'|.") % itrf_ref)

        # Check values in _plate_trans
        # |itrf_ref|
        year_ref = _itrf_year(itrf_ref)
        if year_ref not in list(_plate_trans.keys()):
            raise KeyError('Conversion from %s not defined.' % itrf_ref)
        # |plate|
        if plate not in list(_plate_trans[year_ref].keys()):
            raise KeyError('Conversion from %s to %s fixed not defined.'
                           % (itrf_ref, plate))

        # Adapt
        # |in_place|
        (in_place, warn_place) = adapt_bool(in_place)
        # |warn|
        (warn, _) = adapt_bool(warn, True)

        # Warning
        if warn and warn_place:
            print('[WARNING] from method [fixed_plate] in [%s]' % __name__)
            print(('\t|in_place| parameter set to False because '
                   '|type(in_place)!=bool|!'))
            print('\tNew %s Gts is returned (and old one not updated)!'
                  % self.code)
            print()

        # Return
        return in_place
    ########################################################

    # Check parameters
    in_place = _check_param(self, plate, itrf_ref, in_place, warn)

    # Import
    from itsa.gts.lib.frame.itrf_convert import _itrf_year

    # Change ITRF/IGS frame
    ts = self.itrf_convert(itrf_end=itrf_ref)

    # Predict and remove Euler pole velocity
    year_ref = _itrf_year(itrf_ref)
    ts.remove_pole(_plate_trans[year_ref][plate], unit_pole='mas',
                   in_place=True)
    ts.ref_frame = plate+' fixed'

    # Change in |self|
    if in_place:
        self.data = ts.data.copy()
        self.velocity = ts.velocity.copy()
        self.ref_frame = plate+' fixed'
        if self.data_xyz is not None:
            self.data_xyz = ts.data_xyz.copy()
        if self.data_neu is not None:
            self.data_neu = ts.data_neu.copy()
    else:
        return ts
