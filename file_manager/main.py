from read_parameters import Parameters
import time
import logging

#setup logging configuration
logging.basicConfig(filename='connection.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filemode='w', level=logging.DEBUG)
#ignore logging messages from libraries that use requests:
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("oauth2client").setLevel(logging.WARNING)

#python main.py to run main process
def readDataFeed():
    spreadsheetParameters = Parameters()
    logging.debug(spreadsheetParameters.__dict__)
    #make folders and param files
readDataFeed()
