#!/usr/bin/env python3
#
# Partially adapted from gallery-dl:
# https://github.com/mikf/gallery-dl

import os
import metadata_magic.file_tools
from typing import List

def get_default_config_paths() -> List[str]:
    """
    Returns a list of default locations for the gallery-dvk config file.
    
    :return: List of default locations for the config file.
    :rytpe: list[str]
    """
    # Get the default path based on OS type
    config_paths = []
    if os.name == "nt":
        # Windows paths
        config_paths.append(r"%APPDATA%\gallery-dvk\config.json")
        config_paths.append(r"%USERPROFILE%\gallery-dvk\config.json")
        config_paths.append(r"%USERPROFILE%\gallery-dvk.json")
    else:
        # Linux/MacOS/Unix-based paths
        config_paths.append(r"/etc/gallery-dvk.json")
        config_paths.append(r"${HOME}/.config/gallery-dvk/config.json")
        config_paths.append(r"${HOME}/.gallery-dvk.json")
    # Replace the environment variables in paths
    for i in range(0, len(config_paths)):
        config_paths[i] = os.path.abspath(os.path.expandvars(config_paths[i]))
    # Return the config paths
    return config_paths

def get_config(files:List[str]) -> dict:
    """
    Returns the info from a given config file.
    Returns the info from the first given file in the files list to be a valid JSON.
    
    :param files: List of potential config files
    :type files: list[str], required
    :return: Dictionary containing the info from the config file
    :rtype: dict
    """
    for file in files:
        # Attempt to read config file
        config = metadata_magic.file_tools.read_json_file(os.path.abspath(file))
        if not config == {}:
            return config
    # Return empty dictionary if file couldn't be read
    return {}