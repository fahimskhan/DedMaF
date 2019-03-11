#This file takes last row of spreadsheet as input
#Make sure the last row is corresponds to the simulation you wish to build!

#imports and packages
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import configparser
from pathlib import Path
import os, errno
from shutil import copyfile

#Parameters class is the main controller for the program
#upon initialization, establish connection with google sheet
class Parameters():
    def __init__(self):
        self.status = 'incomplete'
        self.sheet = self.makeConnection()
        self.lastIndex = len(self.sheet.get_all_values())
        self.setParameters()
        #pass in global .cfg file --> directory.cfg
        self.readConfig('directory.cfg')
        self.createConfig()
        self.createDirectory()

#Establishes connection with google sheet
    def makeConnection(self):
        print('making connection')
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
        client = gspread.authorize(creds)
        #pass in name of the spreadsheet to client.open (case sensitive)
        return client.open("viscoTurb_test").sheet1

#Read parameters from spreadsheet
#attribute corresponds to column in spreadsheet
    def setParameters(self):
        #array of values that are in the last row
        values_list = self.sheet.row_values(self.lastIndex)
        #parameters:
        self.identifier = values_list[0]
        self.stop_wall_time = values_list[1]
        self.stop_sim_time = values_list[2]
        self.dt = values_list[3]
        self.nL = values_list[5]
        self.nX = values_list[6]
        self.nY = values_list[7]
        self.Re = values_list[8]
        self.Wi = values_list[9]
        self.eta = values_list[10]


    #readConfig takes the directory.cfg file as input
    def readConfig(self, configFile):
        print('readingConfig')
        config = configparser.ConfigParser()
        config.read(configFile)
        #buildLocation is the path to run folder/self.identifer (for example: simulation_builder/B)
        self.buildLocation = config['Paths']['base_dir'] + '/' + str(self.identifier)
        #copyLocation points to top level folder in git repo (simulation_builder)
        self.copyLocation = config['Paths']['copy_dir']

    #createConfig will create the local config file inside the project directory
    #set parameters from spreadsheet inside run_'self.identifier'.cfg -->
    #run_B.cfg --> simulation_builder/runs/B/run_B.cfg
    def createConfig(self):
        print('creatingLocal conig')
        self.config = configparser.ConfigParser()
        self.config['run'] = {'stop_wall_time': self.stop_wall_time,
                             'stop_sim_time': self.stop_sim_time,
                             'dt': self.dt
                             }
        self.config['params'] = {'nL': self.nL,
                              'nx': self.nX,
				'ny': self.nY,
				'Re': self.Re,
				'Wi': self.Wi,
				'eta':self.eta}
        return self.config

#creates build directory
#writes run_B.cfg file, run_B_kturb.sh file, and symlink files (viscoturb.py, kturb.py) to build directory
#After this function, user should have a run directory with all neccesary files
    def createDirectory(self):
        print('creatingDirectory')
        run_dir = Path.home().joinpath(self.buildLocation)
        #run_dir example: /home/rfeldman/simulation_builder/runs/B
        copy_dir = Path.home().joinpath(self.copyLocation)
        #copy_dir example: /home/rfeldman/simulation_builder
        print('run dir: ' + str(run_dir))
        print('copy dir: ' + str(copy_dir))
        #create directory at appropriate location
        run_dir.mkdir(exist_ok=True, parents=True)
        #add configFile to directory we just created
        configFile = run_dir.joinpath('run_' + str(self.identifier) + '.cfg')
        #creates symlink from kturb.py in copy directory to kturb.py in run directory
        self.force_symlink(copy_dir.joinpath('kturb.py'), run_dir.joinpath('kturb.py'))
        #creates symlink from viscoturb.py in copy directory to kturb.py in run directory
        self.force_symlink(copy_dir.joinpath('viscoturb.py'), run_dir.joinpath('viscoturb.py'))
        #copy run.sh file from copy directory to run directory: --> runB_ktrub.sh for self.identifier = B
        copyfile(copy_dir.joinpath('run_kturb.sh'), str(run_dir) + '/run{}_kturb.sh'.format(self.identifier))
        #populate run_B.cfg file with contents from createConfig()
        with configFile.open('w') as wf:
            self.config.write(wf)

    #helper function to make sure symlink doesnt already exist
    #if symlink exsits, overwrite it
    def force_symlink(self, file1, file2):
        try:
            os.symlink(file1, file2)
        except OSError as  e:
            if e.errno == errno.EEXIST:
                os.remove(file2)
                os.symlink(file1, file2)
