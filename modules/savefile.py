"""
Module that facilitates the saving of data to JSON file.
"""
import json
import time


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
    # Json File Creation
    with open(file_name, "w+") as f:
        # Store data in Json format
        output = {datatype: data}
        # Dump output to file
        json.dump(output, f, indent=2)

    print("\nData will be saved with a File Name :", file_name)
    return file_name
