#!/usr/bin/env python3
"""
Module to retrieve the ISO-3 country code from geographic coordinates.

The main function `get_iso3(lat, lon)` performs the following steps:
 1. Verify if the shapefile exists in the module directory.
 2. Download and extract the ZIP archive if the shapefile is missing.
 3. Load the GeoDataFrame of country boundaries and return the ISO-3 code.

Expected shapefile location:
  <module_dir>/world-administrative-boundaries/world-administrative-boundaries.shp
"""
import os
import zipfile
from pathlib import Path
import requests
import geopandas as gpd
from shapely.geometry import Point

# URL to download the compressed shapefile
SHAPE_URL = (
    "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/"
    "world-administrative-boundaries/exports/shp?lang=fr&timezone=Europe%2FBerlin"
)
# Local filenames and directories
ZIP_NAME = "world-administrative-boundaries.zip"
FOLDER_NAME = "world-administrative-boundaries"
SHP_NAME = "world-administrative-boundaries.shp"

# Cached GeoDataFrame
_countries_gdf = None
# Base directory of this module
BASE_DIR = Path(__file__).parent.parent.resolve()

def _ensure_shapefile():
    """
    Ensure the shapefile is present. Download and extract the ZIP if needed.
    """
    # shp_dir = BASE_DIR / FOLDER_NAME
    shp_path = BASE_DIR / SHP_NAME
    if shp_path.exists():
        return

    # Download the ZIP archive
    response = requests.get(SHAPE_URL, stream=True)
    response.raise_for_status()
    zip_path = BASE_DIR / ZIP_NAME
    with open(zip_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    # Extract the archive
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(BASE_DIR)

    # Remove the ZIP file
    os.remove(zip_path)


def _load_countries() -> gpd.GeoDataFrame:
    """
    Load the GeoDataFrame of country boundaries from the shapefile.
    """
    _ensure_shapefile()
    shp_path = BASE_DIR / SHP_NAME
    return gpd.read_file(str(shp_path))


def get_iso3(lat: float, lon: float) -> str:
    """
    Return the ISO-3 code of the country containing the given coordinates.

    :param lat: Latitude in decimal degrees
    :param lon: Longitude in decimal degrees
    :return: ISO-3 code (e.g., 'FRA') or None if no country is found
    """
    global _countries_gdf
    if _countries_gdf is None:
        _countries_gdf = _load_countries()

    point = Point(lon, lat)
    result = _countries_gdf[_countries_gdf.contains(point)]
    if not result.empty:
        return result.iloc[0]["iso3"]#.get("iso3")
    return None
