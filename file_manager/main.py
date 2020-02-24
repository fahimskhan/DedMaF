from read_parameters import Parameters
from status_update import UpdateStatus
import time
import logging

#setup logging configuration
logging.basicConfig(filename='connection.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filemode='w', level=logging.DEBUG)
# uncomment following lines to ignore logging messages from libraries that use requests:

#logging.getLogger("urllib3").setLevel(logging.WARNING)
#logging.getLogger("oauth2client").setLevel(logging.WARNING)

#python main.py to run main process
def readDataFeed():
    #make folders and param files
    spreadsheetParameters = Parameters()
    logging.debug(spreadsheetParameters.__dict__)
    #check for and update statuses of job runs 
    spreadsheetStatusUpdate = UpdateStatus()
    logging.debug(spreadsheetStatusUpdate.__dict__)
readDataFeed()
