"""
This module provides parser for [MB-System](https://github.com/dwcaress/MB-System) data files.

Functions:
    mbs_read_fnv(files, processed_files=True): Read MB-System fnv files and return a nav_structtype object.

Authors: Sebastián Rodríguez-Martínez and Giancarlo Troni
Contact: srodriguez@mbari.org
"""

import os
from typing import List, Union
from warnings import warn

import numpy as np

from navlib.lcmlog import nav_structtype


def mbs_read_fnv(files: Union[str, List[str]], processed_files=True) -> nav_structtype:
    """
    Read MB-System fnv files and return a nav_structtype object.

    Args:
        files (str or list of str): Path to the fnv files. If a string is passed, it is converted to a list.
        processed_files (bool): If True, the function looks for processed files with suffix "p.mb89.fnv".
            If False, it looks for raw files with suffix ".mb89.fnv". Default is True.

    Returns:
        fnv_nav (nav_structtype): A nav_structtype object containing the navigation data.

    Raises:
        TypeError: If files is not a string or a list of strings.
        FileNotFoundError: If any of the files do not exist.
        ValueError: If no files are found with the specified suffix.
    """
    # Check typing
    if not isinstance(files, (str, list)):
        raise TypeError("files must be a string or a list of strings")

    # Convert to list if a string is passed
    files = files if isinstance(files, list) else [files]

    for file in files:
        if not isinstance(file, str):
            raise TypeError("files must be a string or a list of strings")
    if not isinstance(processed_files, bool):
        raise TypeError("processed_files must be a boolean")

    # Check if files exist
    for file in files:
        if not os.path.isfile(file):
            raise FileNotFoundError(f"File {file} does not exist")

    # Parse the files
    # Initialize the variable to store the data
    fnv = None

    # Suffix to look for
    suffix = ".mb89.fnv"
    if processed_files:
        # if the files are processed, we look for the suffix "*p.mb89.fnv"
        suffix = "p" + suffix

    # Filter files by suffix
    filtered_files = []
    for file in files:
        if file.endswith(suffix):
            filtered_files.append(file)
        else:
            warn(f"File {file} rejected: does not end with {suffix}")
    if not filtered_files:
        raise ValueError(f"No files found with suffix {suffix}")

    # Process the files
    for file in filtered_files:
        # Check if the file is empty
        with open(file, "r") as f:
            content = f.read().strip()
        if not content:
            warn(
                f"File {file} is empty or contains only whitespace and will be skipped"
            )
            continue

        # Read the file and concatenate the data
        try:
            data = np.genfromtxt(file)
        except ValueError as e:
            warn(f"Error reading file {file}: {e}")
            continue

        data = np.atleast_2d(data)
        if data.shape[1] != 19:
            warn(
                f"File {file} has an unexpected number of columns: {data.shape[1]} (expected 19)"
            )
            continue

        # Concatenate the data
        if fnv is None:
            fnv = data
        else:
            fnv = np.concatenate([fnv, data], axis=0)

    # Check if fnv is empty
    if fnv is None or fnv.size == 0:
        raise ValueError("No valid data found in the files")

    nav = nav_structtype()
    nav.utime = fnv[:, 6]
    nav.longitude = fnv[:, 7]
    nav.latitude = fnv[:, 8]
    nav.heading = fnv[:, 9]
    nav.speed = fnv[:, 10]
    nav.sonardepth = fnv[:, 11]
    nav.roll = fnv[:, 12]
    nav.pitch = fnv[:, 13]
    nav.heave = fnv[:, 14]
    nav.portlon = fnv[:, 15]
    nav.portlat = fnv[:, 16]
    nav.stbdlon = fnv[:, 17]
    nav.stbdlat = fnv[:, 18]

    return nav
