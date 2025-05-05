# Standard library imports
import os
import json
import shutil
import pickle
import hashlib
import pathlib
from datetime import datetime

# Third-party imports
from tinydb import TinyDB

# Local application imports


def list_subfolders(directory):
    """
    List 1st level folders in the {directory}

    Usage:
        > list_subfolders(directory)
        > folder_a','folder_b','folder_c']
    """
    return [lst for lst in os.listdir(directory)]


def save_json(json_data: dict, filename: str) -> None:
    """
    Save a dictionary into a json file

    Args:
        json_data:  dict data to save as json file
        filename:   name of file where to save {json_data}
    """

    with open(filename, "w+") as json_file:
        json.dump(json_data, json_file)


def read_json(filename: str) -> dict:
    """
    Read a dictionary from a json file

    Args:
        filename:   name of file to read from
    """

    with open(filename, "r") as json_file:

        return json.load(json_file)


def save_pickle(obj, file_path):

    directory = os.path.dirname(file_path)
    os.makedirs(directory, exist_ok=True)

    with open(file_path, "wb") as file:
        pickle.dump(obj, file)


def read_pickle(file_path):

    with open(file_path, "rb") as file:
        return pickle.load(file)


def create_unique_name(prefix: str) -> str:
    """
    Create name string with timestamp suffix"

    Args:
        prefix:  str name to prefix timestamp data

    Example:
        ```
        create_unique_name("My Model")
        >> MY_MODEL-20250419.085956192146
        ```
    """

    stamp = datetime.now().strftime("%Y%m%d.%H%M%S%f")
    prefix = prefix.replace(" ", "_")

    return f"{prefix}-{stamp}".upper()


def get_timestamp():

    stamp = datetime.now().strftime("%Y%m%d.%H%M%S%f")

    return stamp


def get_file_obj_hash(file_path):

    if isinstance(file_path, str):
        path = pathlib.Path(file_path)

    DEFAULT_BLOCK_SIZE = 65536
    sha256_hash = hashlib.sha256()

    with open(path, "rb") as file:
        while file_buffer := file.read(DEFAULT_BLOCK_SIZE):
            sha256_hash.update(file_buffer)

    return sha256_hash.hexdigest()
