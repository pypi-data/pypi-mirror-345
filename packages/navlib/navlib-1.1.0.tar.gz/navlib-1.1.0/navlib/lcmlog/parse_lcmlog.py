"""
This module contains functions to parse LCMLogs to a nav_structtype object.

Functions:
    dict_to_struct: Convert a dictionary to a nav_structtype object.
    read_log: Read a LCMLog file and return a nav_structtype object.

Authors: Sebastián Rodríguez-Martínez, Giancarlo Troni and Bastián Muñoz
Contact: srodriguez@mbari.org
"""

import os.path
import pickle
from pathlib import Path
from typing import Any, Dict

import numpy as np  # noqa: F401

from navlib.lcmlog.log_to_smat import parse_and_save


class nav_structtype:
    """
    Base class to store data as a structure with numpy arrays.
    """

    pass


def dict_to_struct(ddata: Dict[str, Any]) -> nav_structtype:
    """
    nav_dict_to_struct takes as input a simple or nested dictionary with
    data and returns an object of the class nav_structtype with the data

    Args:
        ddata (Dict[str, Any]): Dictionary with data

    Returns:
        nav_structtype: Object with data as a structure with numpy arrays
    """
    # Create new object
    sdata = nav_structtype()

    # Iterate each element of the dictionary
    for k, v in ddata.items():
        # Fix dictionary key name (remove '.')
        k = k.replace(".", "_")
        k = k.replace("$", "S")

        # Recursive function to deal with nested dictionaries
        if isinstance(v, dict):
            exec(compile("sdata." + k + " = dict_to_struct(v)", "<string>", "exec"))
        else:
            try:
                exec(compile("sdata." + k + " = np.array(v)", "<string>", "exec"))
            except ValueError:
                print(
                    f"Warning: Non homogeneous array {k} cannot be converted to numpy array."
                )
                exec(compile("sdata." + k + " = v", "<string>", "exec"))
    return sdata


def read_log(file_name: str, verbose=True) -> nav_structtype:
    """
    nav_read_log gets a file name and returns the data as a nav_structtype
    object.
    If the file_name does not correspond to a .pkl file the transforms a lcm_log
    to a pickle file.

    Args:
        file_name (str): File name of the log file

    Returns:
        nav_structtype: Object with data as a structure with numpy arrays
    """
    fname = Path(file_name)
    parent, stem = Path(fname.parent), Path(fname.stem)
    # Check if file is not already parsed to a pickle file
    if not os.path.isfile(str(parent / stem) + ".pkl"):
        # If it is not a file, replace "." and "-" by "_"
        stem_alt = str(stem).replace(".", "_").replace("-", "_")
        try:
            if not os.path.isfile("/".join([str(parent), ".".join([stem_alt, "pkl"])])):
                if verbose:
                    print("Pickle file not found, looking for lcmlog with same stem")
                parse_and_save(
                    str(fname),
                    output_file_name=str(parent / stem) + ".pkl",
                    verbose=verbose,
                )
                if verbose:
                    print(f"LCMLogs {str(fname)} parsed to .pkl format")
                fname_alt = str(parent / stem)
        except FileNotFoundError:
            print(f"{fname} not found neither as lcmlog nor as .pkl file.")
            return
    else:
        fname_alt = str(parent / stem)

    # Load Pickle file
    print(f"Loading pickle logfile:  {fname_alt}.pkl")
    pkl_file = open(fname_alt + ".pkl", "rb")
    ddata = pickle.load(pkl_file)

    # Convert dictionary to a structure with numpy arrays
    data = dict_to_struct(ddata)
    if verbose:
        print("LCMLog successfully transformed to nav_structtype object")
    return data
