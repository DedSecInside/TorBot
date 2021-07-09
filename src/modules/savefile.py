"""
Module that facilitates the saving of data to JSON file.
"""
import json
import time

from .utils import join_local_path 

def saveJson(datatype, data):
    """
    Creates json file and stores data as JSON.

    Args:
        datatype (str): Type of the object being passed.
        data (list): List of data elements of type 'datatype' to be saved.

    Returns:
        (str): Name of file data was saved to.
    """
    timestr = time.strftime("%Y%m%d-%H%M%S")
    file_name = "TorBot-Export-"+datatype+timestr+".json"
    file_path = join_local_path(file_name)
    # Json File Creation
    with open(file_path, 'w+') as f:
        # Store data in Json format
        output = {datatype: data}
        # Dump output to file
        json.dump(output, f, indent=2)

    print("\nData will be saved with a File Name :", file_name)
    return file_name
