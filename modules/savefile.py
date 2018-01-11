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
    # Json File Creation
    with open("TorBoT-Export-"+datatype+timestr+".json", "x") as file:
        # Store data in Json format
        output = {datatype: data}
        # Dump output to file
        json.dump(output, file, indent=2)

    print("\nData will be saved with a File Name :",
          "TorBoT-Export-"+datatype+timestr+".json")
