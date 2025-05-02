#!/usr/bin/env python3
# =============================================================================
"""
Code Information:
    This script contains python utils.

    Maintainer:
    Alejandro Naranjo - alejandro.naranjo@kiwibot.com
	Kiwi Campus / Service Desk Team
"""
# =============================================================================

import os
import datetime
import inspect
from sys import stderr

# =============================================================================
class bcolors:
    """!
    Class for defining the color used by the printlog function
    """

    LOG = {
        "DEBUG": ["\033[35m", "DEBUG"],
        "INFO": ["\033[0m", "INFO"],  # ['\033[94m', "INFO"],
        "WARN": ["\033[93m", "WARN"],
        "ERROR": ["\033[91m", "ERROR"],
        "EXCEPTION": ["\033[91m", "EXCEPTION"],
        "CRITICAL": ["\033[91m", "CRITICAL"],
        "OK_BLUE": ["\033[34m", "INFO"],
        "OK_GREEN": ["\033[32m", "INFO"],
        "OK_PURPLE": ["\033[35m", "INFO"],
        "BOLD": ["\033[1m", "INFO"],
        "GRAY": ["\033[90m", "INFO"],
    }
    BOLD = "\033[1m"
    ENDC = "\033[0m"
    HEADER = "\033[95m"
    OK_BLUE = "\033[94m"
    GRAY = "\033[90m"
    UNDERLINE = "\033[4m"

def printlog(
    msg: str,
    msg_type: str = "INFO",
    flush: bool = True,
    verbose: bool = True,): 

    """!
    Function for printing messages on the console
    @param msg `string` message to print
    @param msg_type `string` message type
    @param flush  `boolean` sure that any output is buffered and go to the destination.
    @param verbose `boolean` show datetimes.

    @env LOG_RECORDS `str` Where to save the log files
    @env RECORD_LEVEL `list[str]` Which messages types should be saved
    """

    use_verbose = True if int(os.getenv(key="USE_VERBOSE", default=0)) == 1 else False

    if not flush:
        return

    org = os.path.splitext(os.path.basename(inspect.stack()[1][1]))[0].upper()
    _str = "[{}][{}]: {}".format(bcolors.LOG[msg_type][1], org, msg)

    if verbose or use_verbose:
        print(
            bcolors.LOG[msg_type][0]
            + "[{:%Y-%m-%d %H:%M:%S}]".format(datetime.datetime.now())
            + _str
            + bcolors.ENDC,
            file = stderr
        )
    else:
        print(bcolors.LOG[msg_type][0] + _str + bcolors.ENDC, file = stderr)

    log_path = os.getenv("LOG_RECORDS")
    log_show: str = os.getenv("RECORD_LEVEL", default=",".join(list(bcolors.LOG)))

    if log_show:
        log_level = [log_type.upper() for log_type in log_show.split(",")
                                      if log_type.upper() in list(bcolors.LOG.keys())]

    if log_path and (msg_type in log_level): # type: ignore
        with open(log_path, "a") as log_file:
            print(
                "[{:%Y-%m-%d %H:%M:%S}]".format(datetime.datetime.now()) + _str,
                file = log_file
            )


def inputlog(msg: str, msg_type: str = "INFO", verbose: bool = False):

    """!
    Function for printing messages on the console
    @param msg `str` message to print
    @param msg_type `str` message type
    @param flush  `bool` sure that any output is buffered and go to the destination.
    """

    use_verbose = True if int(os.getenv(key="USE_VERBOSE", default=0)) == 1 else False

    org = os.path.splitext(os.path.basename(inspect.stack()[1][1]))[0].upper()
    _str = "[{}][{}]: {}".format(bcolors.LOG[msg_type][1], org, msg)
    if verbose or use_verbose:
        return input(bcolors.LOG[msg_type][0] + "[{:%Y-%m-%d %H:%M:%S}]".format(datetime.datetime.now())+  _str + bcolors.ENDC)
    else:
        return input(bcolors.LOG[msg_type][0] + _str + bcolors.ENDC)

def select_option(
        msg: str,
        options: list[str] = ["Yes", "No"],
        msg_type: str = "INFO",
        verbose: bool = True,
        case_insensitive: bool = False) -> str:
    """!
    Function
    @param msg `string` message to print
    @param options `list` options to choose
    @param msg_type string` message type
    @param case_insensitive `bool` create case insensitive options
    """

    use_verbose = True if int(os.getenv(key="USE_VERBOSE", default=0)) == 1 else False

    opts = ([i.lower() for i in options] if case_insensitive else options)

    org = os.path.splitext(os.path.basename(inspect.stack()[1][1]))[0].upper()
    _str = "[{}][{}]: {} ({}): ".format(bcolors.LOG[msg_type][1], org, msg, '/'.join(options))
    if verbose or use_verbose:
        log_msg = bcolors.LOG[msg_type][0] + "[{:%Y-%m-%d %H:%M:%S}]".format(datetime.datetime.now())+  _str + bcolors.ENDC
    else:
        log_msg = bcolors.LOG[msg_type][0] + _str + bcolors.ENDC

    opt = ''
    while opt not in opts:
        opt = input(log_msg)
        if case_insensitive:
            opt = opt.lower()
    return options[opts.index(opt)]

