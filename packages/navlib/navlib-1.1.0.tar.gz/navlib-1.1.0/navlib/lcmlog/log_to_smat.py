"""
This module provides a set of functions to convert an LCM log to a structured
format that is easier to work with external tools. The set of messages on a
given channel can be represented as a structure preserving the original LCM
message structure.


Reference:
    This module is based on libbot2 script bot-log2mat.

Functions:
    msg_getfields: Extracts the slots containing the field names from an lcm_msg object.
    msg_getconstants: Extracts the constant attributes from an lcm_msg object.
    msg_to_dict: Converts an LCM message to a dictionary. This function is recursive and can handle nested messages.
    delete_status_msg: Deletes a status message from the stderr.
    parse_and_save: Parse and LCM log file and save it to a pickle file based on a dictionary.

Authors: Giancarlo Troni, Bastián Muñoz, and Sebastián Rodríguez-Martínez
Contact: srodriguez@mbari.org
Last Update: 2024-03-26
"""

import os
import pickle
import re
import sys
from typing import Any, Dict, List

from lcm import EventLog

from ._scan_for_lcmtypes import make_lcmtype_dictionary


def msg_getfields(lcm_msg: Any) -> List[str]:
    """
    Extracts the slots containing the field names from an lcm_msg object.

    Args:
        lcm_msg (Any): LCM message object.

    Returns:
        field_names (List[str]): List of field names.
    """
    return lcm_msg.__slots__


def msg_getconstants(lcm_msg: Any) -> List[str]:
    """
    Extracts the constant attributes from an lcm_msg object.

    Args:
        lcm_msg (Any): LCM message object.

    Returns:
        constant_attrs (List[str]): List of constant attributes.
    """
    # Get full list of valid attributes
    fulllist = dir(lcm_msg)
    # Get constants
    constantslist = [
        x
        for x in fulllist
        if not (x[0] == "_")
        if not (x == "decode")
        if not (x == "encode")
        if not (x == "get_hash")
        if x not in msg_getfields(lcm_msg)
    ]
    return constantslist


def msg_to_dict(
    data: Dict[str, Any],
    e_channel: str,
    msg: Any,
    statusMsg: str,
    verbose=False,
    lcm_timestamp=-1,
):
    """
    Converts an LCM message to a dictionary. This function is recursive and can
    handle nested messages.

    Args:
        data (Dict[str, Any]): Dictionary to store the LCM message.
        e_channel (str): LCM channel name.
        msg (Any): LCM message object.
        statusMsg (str): Status message.
        verbose (bool): Verbose flag.
        lcm_timestamp (int): LCM timestamp.
    """
    # If the channel is not a key of the data dictionary, create a new entry in the dictionary with the channel name
    # as key and a dictionary as value
    if e_channel not in data:
        data[e_channel] = dict()

        # Iterate each constant of the LCM message
        constants = msg_getconstants(msg)
        for i in range(len(constants)):
            myValue = None
            myValue = eval("msg." + constants[i])
            data[e_channel][constants[i][:31]] = myValue

    # Get lcm fields and constants
    fields = msg_getfields(msg)

    # Iterate each field of the LCM message
    for i in range(len(fields)):
        myValue = None
        myValue = eval(" msg." + fields[i])
        if (
            isinstance(myValue, int)
            or isinstance(myValue, float)
            or isinstance(myValue, tuple)
            or isinstance(myValue, str)
        ):
            try:
                data[e_channel][fields[i][:31]].append(myValue)
            except KeyError:
                data[e_channel][fields[i][:31]] = [(myValue)]

        # If the field return an object with the __slots__ attribute, it means that it is a nested message
        elif hasattr(myValue, "__slots__"):
            submsg = eval("msg." + fields[i])
            msg_to_dict(data[e_channel], fields[i][:31], submsg, statusMsg, verbose)

        # If the field return a list of objects, iterate each object
        elif isinstance(myValue, list):
            for j, obj in enumerate(myValue):
                # If the object return an object with the __slots__ attribute, it means that it is a nested message
                if hasattr(obj, "__slots__"):
                    submsg = eval("msg." + fields[i])
                    msg_to_dict(
                        data[e_channel], fields[i][:31], submsg[j], statusMsg, verbose
                    )

        # Otherwise, the field will be ignored
        else:
            if verbose:
                statusMsg = delete_status_msg(statusMsg)
                sys.stderr.write(
                    "ignoring field %s from channel %s. \n" % (fields[i], e_channel)
                )
            continue

    # Add extra field with lcm_timestamp
    if lcm_timestamp > 0:
        try:
            data[e_channel]["lcm_timestamp"].append(lcm_timestamp)
        except KeyError:
            data[e_channel]["lcm_timestamp"] = [(lcm_timestamp)]


def delete_status_msg(statMsg: str) -> str:
    """
    Deletes a status message from the stderr.

    Args:
        statMsg (str): Status message.

    Returns:
        str: Empty string.
    """
    if statMsg:
        sys.stderr.write("\r")
        sys.stderr.write(" " * (len(statMsg)))
        sys.stderr.write("\r")
    return ""


def parse_and_save(
    log_name: str,
    output_file_name: str = "",
    channels_to_process: str = ".*",
    channels_to_ignore: str = "",
    verbose: bool = True,
    lcm_packages: List[str] = [],
) -> None:
    """
    Parse and LCM log file and save it to a pickle file based on a dictionary.

    Args:
        log_name (str): Path to the LCM log file.
        output_file_name (str): Path to the output file.
        channels_to_process (str): Regular expression to filter the channels to process.
        channels_to_ignore (str): Regular expression to filter the channels to ignore.
        verbose (bool): Verbose flag.
        lcm_packages (List[str]): List of directories to search for LCM types in addition to the directories in the
            python path.
    """
    # If the output file name is not provided, create a default name based on
    # the input file name
    if output_file_name == "":
        output_dir, output_file_name = os.path.split(os.path.abspath(str(log_name)))
        output_file_name = os.path.splitext(output_file_name)[0]
        output_file_name = output_dir + "/" + output_file_name + ".pkl"

    # Load the LCM log and convert it to a dictionary
    data = lcmlog_to_dict(
        log_name,
        channels_to_process,
        channels_to_ignore,
        verbose,
        lcm_packages,
    )

    # Save the dictionary to a pickle file
    if verbose:
        sys.stderr.write(f"loaded all messages, saving to {output_file_name}\n")
    output = open(output_file_name, "wb")
    pickle.dump(data, output, -1)
    output.close()


def lcmlog_to_dict(
    log_name: str,
    channels_to_process: str = ".*",
    channels_to_ignore: str = "",
    verbose: bool = True,
    lcm_packages: List[str] = [],
) -> None:
    """
    Gets an lcmlog and converts it to a dictionary.

    Args:
        log_name (str): Path to the lcmlog file.
        channels_to_process (str): Regular expression to filter the channels to process.
        channels_to_ignore (str): Regular expression to filter the channels to ignore.
        verbose (bool): Verbose flag.
        lcm_packages (List[str]): List of directories to search for LCM types in addition to the directories in the
            python path.

    Returns:
        data: a dictionary with the lcmlog data
    """
    check_ignore = True if channels_to_ignore != "" else False

    # Initialize dictionary to save the LCM log data
    data = {}

    # Search for LCM types recursively in the python path
    if verbose:
        print("Searching for LCM types...")
    type_db = make_lcmtype_dictionary(lcm_packages=lcm_packages)

    # Create the regular expression for the channels to process and ignore
    channelsToProcess = re.compile(channels_to_process)
    channelsToIgnore = re.compile(channels_to_ignore)

    # Open the LCM log file
    log = EventLog(str(log_name), "r")

    # Initialize variables
    ignored_channels = []
    msgCount = 0
    statusMsg = ""
    startTime = 0

    # Iterate LCM log file
    for e in log:
        # If it is the first message, initialize the conversion timer
        if msgCount == 0:
            startTime = e.timestamp

        # If the channel is in the ignored channels, skip it
        if e.channel in ignored_channels:
            continue
        # If the channel is in the channels to ignore, skip it
        if (
            check_ignore
            and channelsToIgnore.match(e.channel)
            and len(channelsToIgnore.match(e.channel).group()) == len(e.channel)
        ) or (not channelsToProcess.match(e.channel)):
            if verbose:
                statusMsg = delete_status_msg(statusMsg)
                sys.stderr.write("ignoring channel %s\n" % e.channel)
            ignored_channels.append(e.channel)
            continue

        # Get the LCM type of the message
        packed_fingerprint = e.data[:8]
        lcmtype = type_db.get(packed_fingerprint, None)

        # If the LCM type is not found, skip the message and add the channel to the ignored channels
        if not lcmtype:
            if verbose:
                statusMsg = delete_status_msg(statusMsg)
                sys.stderr.write(
                    "ignoring channel %s -not a known LCM type\n" % e.channel
                )
            ignored_channels.append(e.channel)
            continue

        # Decode the LCM message
        try:
            msg = lcmtype.decode(e.data)
        except Exception:
            statusMsg = delete_status_msg(statusMsg)
            sys.stderr.write("error: couldn't decode msg on channel %s\n" % e.channel)
            continue

        # Output the progress of the conversion every 5000 messages
        msgCount = msgCount + 1
        if (msgCount % 5000) == 0:
            statusMsg = delete_status_msg(statusMsg)
            statusMsg = "read % d messages, % d %% done" % (
                msgCount,
                log.tell() / float(log.size()) * 100,
            )
            sys.stderr.write(statusMsg)
            sys.stderr.flush()

        # Convert the LCM message to a dictionary
        msg_to_dict(
            data, e.channel, msg, statusMsg, verbose, (e.timestamp - startTime) / 1e6
        )

    delete_status_msg(statusMsg)

    return data
