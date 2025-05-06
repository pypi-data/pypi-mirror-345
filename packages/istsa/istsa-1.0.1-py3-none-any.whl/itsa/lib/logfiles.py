#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 09:09:37 2024

@author: tsaponga
"""

import re
import json
import shutil
import requests
from pathlib import Path
from caching import CacheHandling
from datetime import datetime, timedelta


def fetch_and_parse_index(source_url: str) -> list[str]:
    """
    Download and parse the HTML index from a metadata server.

    Parameters
    ----------
    source_url : str
        URL of the metadata directory listing.

    Returns
    -------
    list[str]
        List of filenames ending in .log available at the source.
    """
    response = requests.get(source_url, timeout=10)
    response.raise_for_status()
    filenames = []
    for line in response.text.splitlines():
        if 'href' in line and '.log' in line:
            list_files = [item for item in re.split(r'[<,>]+', line) if len(item)==22 and ".log" in item]
            if list_files and len(list_files) == 1:
                file =list_files[0]
                filenames.append(file)
    return filenames


def load_index(cache_path: Path, source_url: str) -> list[str]:
    """
    Load a cached index or refresh it if outdated.

    Parameters
    ----------
    cache_path : Path
        Path to the local cache file for the index.
    source_url : str
        URL to download the index if cache is missing or stale.

    Returns
    -------
    list[str]
        List of available log filenames.
    """
    # How long before re-downloading the index (in days)
    INDEX_REFRESH_INTERVAL = timedelta(days=7)
    
    if cache_path.exists():
        mod_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        if datetime.now() - mod_time < INDEX_REFRESH_INTERVAL:
            return cache_path.read_text().splitlines()
    # Otherwise fetch fresh
    entries = fetch_and_parse_index(source_url)
    cache_path.write_text("\n".join(entries))
    return entries


def find_latest_for_station(filenames: list[str], station_code: str):
    """
    Find the most recent log filename for a given station code.

    Parameters
    ----------
    filenames : list[str]
        List of available log filenames.
    station_code : str
        Nine-character station identifier (e.g., 'aaer00fra').

    Returns
    -------
    str | None
        The latest matching filename, or None if not found.
    """
    matches = [name for name in filenames if name.startswith(station_code)]
    return max(matches) if matches else None


def download_station_log(station_id: str, output_dir: Path):
    """
    Download the latest log file for a station from M3G or IGS.

    The function checks the M3G index first; if no entry is found,
    it falls back to the IGS index. Cached index files are refreshed
    every INDEX_REFRESH_INTERVAL days.

    Parameters
    ----------
    station_id : str
        Nine-character station code (lowercase).
    output_dir : Path
        Directory where the downloaded log will be saved.

    Returns
    -------
    Path | None
        Path to the downloaded .log file, or None if not available.
    """
    
    # Constants for metadata sources
    M3G_BASE_URL = "https://gnss-metadata.eu/data/station/log/"
    IGS_BASE_URL = "https://files.igs.org/pub/station/log/"
    # Local cache filenames
    M3G_INDEX_CACHE = Path("m3g_log_index.txt")
    IGS_INDEX_CACHE = Path("igs_log_index.txt")
    
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load or refresh indices
    m3g_filenames = load_index(output_dir / M3G_INDEX_CACHE, M3G_BASE_URL)
    igs_filenames = load_index(output_dir / IGS_INDEX_CACHE, IGS_BASE_URL)

    # Find latest log
    m3g_match = find_latest_for_station(m3g_filenames, station_id)
    igs_match = find_latest_for_station(igs_filenames, station_id)

    if m3g_match:
        chosen = m3g_match
        source_url = M3G_BASE_URL
    elif igs_match:
        chosen = igs_match
        source_url = IGS_BASE_URL
    else:
        return None

    download_url = source_url + chosen
    destination = output_dir / chosen
    response = requests.get(download_url, timeout=10)
    response.raise_for_status()
    destination.write_bytes(response.content)
    return destination


def date_format(install_date):
    if install_date.strip() and install_date[-1] != 'Z':
        return "%Y-%m-%d"
    else:
        return "%Y-%m-%dT%H:%MZ"

def convert_log_to_staDB(log_file, output_directory):
    """
    Convert a station log file to staDB format by extracting receiver and antenna information.

    :param log_file: The station log file to process
    :param output_directory: The directory to save the staDB output file
    """

    # Lists to store receiver and antenna data
    receiver_data = []
    antenna_data = []

    # Open and read the log file
    with open(log_file, 'r', errors="ignore") as file:
        line = file.readline()
        while not line.strip():
            line = file.readline()

        station_marker = line.split()[0][0:4]  # Extract station marker (first 4 characters)
        #station_marker = line.split()[0]

        while line:
            line = file.readline()

            # Extract coordinates and installation date
            if "Site Identification" in line:
                while "Receiver Information" not in line:
                    if "Date Installed" in line:
                        install_date = line.split(" :")[-1].strip()
                    elif "X coordinate" in line:
                        x_coordinate = line.split()[-1]
                    elif "Y coordinate" in line:
                        y_coordinate = line.split()[-1]
                    elif "Z coordinate" in line:
                        z_coordinate = line.split()[-1]
                    line = file.readline()

                try:
                    # Format the installation date and create the coordinate entry
                    install_date = datetime.strptime(install_date,  date_format(install_date)).strftime("%Y-%m-%d %H:%M:%S")
                    coordinates_entry = f"{station_marker}  STATE  {install_date}  {x_coordinate}  {y_coordinate}  {z_coordinate}   0.0   0.0   0.0"
                except ValueError:
                    pass

            # Extract antenna information
            if "Antenna Type" in line:
                while "Date Removed" not in line:
                    if "Antenna Type" in line:
                        antenna_type = ' '.join(line.split(" :")[-1].split())
                    elif "Up Ecc" in line:
                        up_eccentricity = line.split(" :")[-1].strip()
                    elif "North Ecc" in line:
                        north_eccentricity = line.split(" :")[-1].strip()
                    elif "East Ecc" in line:
                        east_eccentricity = line.split(" :")[-1].strip()
                    elif "Serial Number" in line:
                        antenna_serial_number = line.split(" :")[-1].strip()
                    elif "Date Installed" in line:
                        antenna_install_date = line.split(" :")[-1].strip()
                    line = file.readline()

                try:
                    # Format the antenna installation date and create the antenna entry
                    antenna_install_date = datetime.strptime(antenna_install_date,  date_format(antenna_install_date)).strftime("%Y-%m-%d %H:%M:%S")
                    antenna_data.append(f"{station_marker}  ANT    {antenna_install_date}  {antenna_type}   {east_eccentricity}   {north_eccentricity}   {up_eccentricity} #{antenna_serial_number}")
                except ValueError:
                    pass

            # Extract receiver information
            if "Receiver Type" in line:
                while "Date Removed" not in line:
                    if "Receiver Type" in line:
                        receiver_type = line.split(" :")[-1].strip()
                    elif "Firmware Version" in line:
                        firmware_version = line.split(" :")[-1].strip()
                    elif "Date Installed" in line:
                        receiver_install_date = line.split(" :")[-1].strip()
                    line = file.readline()

                try:
                    # Format the receiver installation date and create the receiver entry
                    receiver_install_date = datetime.strptime(receiver_install_date,  date_format(receiver_install_date)).strftime("%Y-%m-%d %H:%M:%S")
                    receiver_data.append(f"{station_marker}  RX     {receiver_install_date}  {receiver_type} #{firmware_version}")
                except ValueError:
                    pass

    # Save the data in the staDB format
    output_file = f"{output_directory}/{station_marker.lower()}.sta_db"

    with open(output_file, 'w', errors="ignore") as output:
        output.write("KEYWORDS: ID STATE END ANT RX\n")
        output.write(f"{station_marker}  ID  UNKNOWN  {station_marker}\n")
        output.write(f"{coordinates_entry}\n")

        for antenna_entry in antenna_data:
            output.write(f"{antenna_entry}\n")

        for index, receiver_entry in enumerate(receiver_data, 1):
            if index == len(receiver_data):
                gotoLine = ""
            else:
                gotoLine = "\n"
            output.write(f"{receiver_entry}{gotoLine}")
