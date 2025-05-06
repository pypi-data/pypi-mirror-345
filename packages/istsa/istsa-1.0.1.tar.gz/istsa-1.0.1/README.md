## ITSA = ISTerre Time Series Analysis

ITSA was developped by Lou Marill during her PhD, as a member of the ISTerre Cycle team.
This tool developped in python produces a trajectory model for GNSS time series. 

Inputs:
- the time series in PBO pos format
- the dates and types of discontinuities (antenna, earthquakes, slow-slip events, swarms)
- station coordinates (used to get earthquakes-station distance)
- optionally, a list of position outliers

ITSA calculates:
- the 3 dimensional offset for each equipment discontinuity
- post-seismic relaxation, currently without inversion (tau is an input parameter)
- linear, seasonal, and acceleration on the full time series

Outputs:
- Final time series
- Intermediate time series
- All modelled and applied corrections

ITSA is distributed under the licence CC-BY-NC: https://creativecommons.org/licenses/by-nc/4.0/

Documentation is available on the gitlab wiki: https://gricad-gitlab.univ-grenoble-alpes.fr/isterre-cycle/itsa/-/wikis/home

