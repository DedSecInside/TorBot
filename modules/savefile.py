import json
import time

__all__ = ['saveJson']

# open the file "TorBoT-Export" in write ("a") mode
def saveJson(datatype,data):
   "function_docstring"
   timestr = time.strftime("%Y%m%d-%H%M%S")
   #Json File Creation
   file = open("TorBoT-Export-"+datatype+timestr+".json", "a")
   #Store data in Json format
   output = {datatype : data}
   #Dump output to file 
   json.dump(output, file, indent=2)
   file.close()
   print("\nData will be saved with a File Name :"+ "TorBoT-Export-"+datatype+timestr+".json") 
   return



