#!~/miniconda3/bin/python
from read_parameters import Parameters
import time

def readDataFeed():
    print('readDataFeed function started')
    runs = []
    last = len(runs)-1
    spreadsheetParameters = Parameters()
    runs.append(spreadsheetParameters)
    print(runs[last].__dict__)
    #make folders and param files
readDataFeed()
