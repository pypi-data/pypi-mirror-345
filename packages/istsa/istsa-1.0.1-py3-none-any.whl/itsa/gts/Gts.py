"""
    Geodetic Time Series Class 

    A Geodetic time series (Gts) is a series of 3 component North, East, 
    Vertical as a function of increasing dates

    All the associated functions are imported after the class definition (look 
    at the section to see which function used Gts)

    !!! Warning: You need to add the module 'itsa' to your Python path to use 
    this class (and the associated functions)

    ----
    Developed at: ISTerre
    By: Lou MARILL
    Based on: PYACS module
"""

#%%######################
## CLASS METHOD IMPORT ##
#########################

from dataclasses import dataclass

from itsa.gts.lib.analysis import window_analysis, longt_analysis

from itsa.gts.lib.format.F3pos import read_F3pos
from itsa.gts.lib.format.GMODfiles import read_GMOD, make_GMOD_names
from itsa.gts.lib.format.GMODfiles import write_Gtxt, write_MODtxt
from itsa.gts.lib.format.GXpos import read_GXpos
from itsa.gts.lib.format.NGLtxyz import read_NGLtxyz
from itsa.gts.lib.format.PBOpos import read_PBOpos, write_PBOpos
from itsa.gts.lib.format.read_pos import read_allpos

from itsa.gts.lib.frame.euler_pole import remove_pole
from itsa.gts.lib.frame.fixed_plate import fixed_plate
from itsa.gts.lib.frame.itrf_convert import itrf_convert

from itsa.gts.lib.outliers import find_outliers, remove_outliers

from itsa.gts.lib.primitive.check_gts import check_gts, reorder
from itsa.gts.lib.primitive.check_gts import remove_duplicated_dates
from itsa.gts.lib.primitive.coordinates import xyz2dneu, dneu2xyz
from itsa.gts.lib.primitive.coordinates import change_ref
from itsa.gts.lib.primitive.copy import copy
from itsa.gts.lib.primitive.plot import plot
from itsa.gts.lib.primitive.select import select_data
from itsa.gts.lib.primitive.time import continuous_time, nonan_time
from itsa.gts.lib.primitive.velocity import remove_velocity


#%%###################
## CLASS DEFINITION ##
######################

@dataclass
class Gts:
    """
    Geodetic time series class

    Gts has the following structure:
        Mandatory attributes
            - code : station 4-letters code
            - time : array with 2 colums: decimal year, modified julian day
            - data : array with 9 colums: dN, dE, dU, Sn, Se, Su, Rne, Rnu, Reu

        Reference coordinates attributes
            - t0 : reference time with 2 values: decimal year, modified julian
                                                 day
            - XYZ0 : array with 3 colums: reference XYZ position in the
                                          Geocentric Frame (at |t0|)
            - NEU0 : array with 3 colums: reference NEU position (with respect
                     to |X0|, |Y0|, |Z0|, at |t0|)
            - ref_frame : reference frame

        Optional attributes
            Many Gts method used |data|, then these attributes are often set to
            None
            - data_xyz : array with 9 colums: X, Y, Z, Sx, Sy, Sz, Rxy, Rxz,
                                              Ryz
                         Can be built using neu2xyz method
            - data_neu : array with 3 colums: N, E, U
                         Can be built using xyz2geo from itsa.lib.coordinates

        Metadata attribute
            - in_file : input file of the time serie (with absolut path)

        Analysis attributes
            - outliers : index of outliers in the time series (looking at all 
                         components)
            - velocity : velocity removed from raw time series with 3 columns: 
                         Vx, Vy, Vz
            - jps : seismic and aseismic catalog (see Jps class)
            - G : Green's functions
            - MOD : model values for each |G|'s column in N, E and U
            - GMOD_names : names of the model component
                           (columns of |G| and lines of |MOD|)

        Units Conventions
            - XYZ coordinates are in meter
            - NEU coordinates are in decimal degree
            - dN, dE, dU coordinates are in millimeter
            - time are found both in decimal year and modified Julian day
            
    """
    import numpy as np
    from itsa.jps.Jps import Jps

    # Mandatory attributes
    code: str
    time: np.ndarray = None
    data: np.ndarray = None

    # Reference coordinates attributes
    t0: np.ndarray = None
    XYZ0: np.ndarray = None
    NEU0: np.ndarray = None
    ref_frame: str = 'Unknown'

    # Optional attributes
    data_xyz: np.ndarray = None
    data_neu: np.ndarray = None

    # Metadata attribute
    in_file: str = ''
    process: str = 'Unknown'

    # Analysis attributes
    outliers: np.ndarray = None
    velocity: np.ndarray = None
    jps: Jps = None
    G: np.ndarray = None
    MOD: np.ndarray = None
    GMOD_names: np.ndarray = None


#%%######################
## METHODS ASSOCIATION ##
#########################

# ANALYSIS
Gts.window_analysis = window_analysis
Gts.longt_analysis = longt_analysis

# FORMATS
Gts.read_F3pos = read_F3pos
Gts.read_GMOD = read_GMOD
Gts.make_GMOD_names = make_GMOD_names
Gts.write_Gtxt = write_Gtxt
Gts.write_MODtxt = write_MODtxt
Gts.read_GXpos = read_GXpos
Gts.read_NGLtxyz = read_NGLtxyz
Gts.read_PBOpos = read_PBOpos
Gts.write_PBOpos = write_PBOpos
Gts.read_allpos = read_allpos

# FRAME
Gts.remove_pole = remove_pole
Gts.fixed_plate = fixed_plate
Gts.itrf_convert = itrf_convert

# OUTLIERS
Gts.find_outliers = find_outliers
Gts.remove_outliers = remove_outliers

# PRIMITIVE
Gts.check_gts = check_gts
Gts.reorder = reorder
Gts.remove_duplicated_dates = remove_duplicated_dates
Gts.xyz2dneu = xyz2dneu
Gts.dneu2xyz = dneu2xyz
Gts.change_ref = change_ref
Gts.copy = copy
Gts.plot = plot
Gts.select_data = select_data
Gts.continuous_time = continuous_time
Gts.nonan_time = nonan_time
Gts.remove_velocity = remove_velocity
