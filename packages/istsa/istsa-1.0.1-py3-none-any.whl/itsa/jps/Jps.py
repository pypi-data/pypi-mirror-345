"""
    Seismic and aseismic event catalog (Jps) Class

    !!! Warning: You need to add the module 'itsa' to your Python path to use 
    this class

    ----
    Developed at: ISTerre
    By: Lou MARILL
"""

#%%######################
## CLASS METHOD IMPORT ##
#########################

from dataclasses import dataclass

from itsa.jps.lib.check_jps import check_jps, reorder, remove_duplicated_dates
from itsa.jps.lib.copy import copy
from itsa.jps.lib.fill_jps import read, add_ev
from itsa.jps.lib.select import select_ev, delete
from itsa.jps.lib.write_jps import write


#%%###################
## CLASS DEFINITION ##
######################

@dataclass
class Jps:
    """
    Seismic and aseismic catalog class
    
    The catalog as the following structure:
        - date : beginning of the events, array with 2 columns:
            decimal year, modified julian day of the events
        - type_ev : type of the events
            - 'E': earthquake without post-seismic
            - 'P': earthquake with post-seismic
            - 'S': slow slip event
            - 'W': earthqquake swarm
            - 'U': unknown phenomenon
        - coords : array with 3 columns: latitude, longitude, depth
        - mag : moment magnitude of the events
        - dur : duration of the events

        Units Convention
        - Latitude and longitude coordinates are in decimal degree
        - Depths are in km
        - Durations are in days
    """
    
    import numpy as np

    # Data
    code: str
    dates: np.ndarray = np.array([]).reshape(0, 2)
    type_ev: np.ndarray = np.array([])
    coords: np.ndarray = np.array([]).reshape(0, 3)
    mag: np.ndarray = np.array([])
    dur: np.ndarray = np.array([]).astype(int)
    
    # Metadata
    mag_min: float = np.nan    
    mag_post: float = np.nan
    mag_spe: float = None
    dco: float = np.nan
    dpost: float = np.nan
    dsse: float = np.nan
    dsw: float = np.nan
    
    
def shape(self):
    return self.dates.shape[0]


#%%######################
## METHODS ASSOCIATION ##
#########################

Jps.shape = shape

Jps.check_jps = check_jps
Jps.reorder = reorder
Jps.remove_duplicated_dates = remove_duplicated_dates
Jps.copy = copy
Jps.read = read
Jps.add_ev = add_ev
Jps.select_ev = select_ev
Jps.delete = delete
Jps.write = write
