import json
import time


def saveJson(datatype, data):
    """
        Creates json file and stores json

        Args:
            datatype: the type of the object being passed
            data = data that is being stored with object
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
