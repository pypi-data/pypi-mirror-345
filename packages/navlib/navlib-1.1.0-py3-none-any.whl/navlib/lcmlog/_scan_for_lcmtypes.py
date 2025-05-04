#!/usr/bin/python

"""
This script is used to scan the python path for LCM types. It searches for python files that contain the string
"_get_packed_fingerprint" and imports the modules that contain the string. The script then checks if the module
contains a class with the right name and methods. If the module passes the checks, it is added to the list of LCM types.
This script is based on lcm-log2smat is based on libbot2 script bot-log2mat.

Authors: Sebastián Rodríguez-Martínez, Giancarlo Troni and Bastián Muñoz
Contact: srodriguez@mbari.org
Last Update: 2024-03-25
"""

import os
import pyclbr
import re
import sys
from io import open
from typing import Any, Dict, List, Union


def find_lcmtypes(lcm_packages: List[str] = []) -> List[str]:
    """
    Walks the directory tree looking for python files that contain the string "_get_packed_fingerprint"
    and imports the modules that contain the string. The function then checks if the module contains a class
    with the right name and methods. If the module passes the checks, it is added to the list of LCM types.

    Args:
        lcm_packages (List[str]): List of directories to search for LCM types in addition to the directories in the
        python path.

    Returns:
        lcmtypes (List[str]): List of LCM types
    """
    lcmtypes = []
    regex = re.compile("_get_packed_fingerprint")

    # Search for lcm types in all directories in the python path
    dirs_to_check = sys.path

    # Extend the list of directories to check with the specified lcm_packages
    for package in lcm_packages:
        if os.path.exists(package):
            dirs_to_check.append(package)

    for dir_name in dirs_to_check:
        # For each directory in the python path, walk the directory tree, looking
        # for python files that contain the string "_get_packed_fingerprint"
        for root, dirs, files in os.walk(dir_name):
            subdirs = root[len(dir_name) :].split(os.sep)
            subdirs = [s for s in subdirs if s]

            python_package = ".".join(subdirs)

            for fname in files:
                # Checks if the file is a python file (*.py)
                if not fname.endswith(".py"):
                    continue

                # Check if the file name is a valid python module name
                # 1. Must end in ".py"
                # 2. Must contain only valid characters (alphanumeric and underscore)
                # 3. Must start with an alphabetic character
                mod_basename = fname[:-3]
                if not re.match(r"[a-zA-Z][a-zA-Z0-9_]*$", mod_basename):
                    continue

                # Check if the file contains the word "_get_packed_fingerprint"
                full_fname = os.path.join(root, fname)
                try:
                    contents = open(full_fname, "r", encoding="latin1").read()
                except IOError:
                    continue
                if not regex.search(contents):
                    continue

                # Check to see if the file corresponds to a LCM type module genereated by lcm-gen. Parse the
                # file using pyclbr, and check if it contains a class with the right name and methods
                if python_package:
                    modname = "%s.%s" % (python_package, mod_basename)
                else:
                    modname = mod_basename
                try:
                    klass = pyclbr.readmodule(modname).get(mod_basename)
                    if klass and all(
                        method in klass.methods
                        for method in ["decode", "_get_packed_fingerprint"]
                    ):
                        lcmtypes.append(modname)
                except ImportError:
                    continue

            # Only recurse into subdirectories that correspond to python packages (i.e., they contain a file named
            # "__init__.py")
            subdirs_to_traverse = [
                subdir_name
                for subdir_name in dirs
                if os.path.exists(os.path.join(root, subdir_name, "__init__.py"))
            ]
            del dirs[:]
            dirs.extend(subdirs_to_traverse)
    return lcmtypes


def make_lcmtype_dictionary(
    lcm_packages: List[str] = [],
) -> Dict[Union[bytes, bytearray], Any]:
    """
    Create a dictionary of LCM types keyed by fingerprint.

    Searches the specified python package directories for modules
    corresponding to LCM types, imports all the discovered types into the
    global namespace, and returns a dictionary mapping packed fingerprints
    to LCM type classes.

    The primary use for this dictionary is to automatically identify and
    decode an LCM message.

    Args:
        lcm_packages (List[str]): List of directories to search for LCM types in
        addition to the directories in the python path.

    Returns:
        lcm_objects (Dict[Union[bytes, bytearray], Any]): LCM objects found on
        the specified python package directories keyed by fingerprint.
    """
    lcmtypes = find_lcmtypes(lcm_packages=lcm_packages)

    result = {}

    for lcmtype_name in lcmtypes:
        try:
            __import__(lcmtype_name)
            mod = sys.modules[lcmtype_name]
            type_basename = lcmtype_name.split(".")[-1]
            klass = getattr(mod, type_basename)
            fingerprint = klass._get_packed_fingerprint()
            result[fingerprint] = klass
        except ImportError:
            print("Error importing %s" % lcmtype_name)
    return result


if __name__ == "__main__":
    import binascii

    print("Searching for LCM types...")
    lcmtypes = make_lcmtype_dictionary()
    num_types = len(lcmtypes)
    print(f"Found {num_types} type{'s' if num_types != 1 else ''}")
    for fingerprint, klass in lcmtypes.items():
        print(binascii.hexlify(fingerprint), klass.__module__)
