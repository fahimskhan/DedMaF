#This file takes last row of spreadsheet as input
# reads parameters into key value pairs
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import configparser
from pathlib import Path
import os, errno
from shutil import copyfile


class Parameters():
    idCounter = 0
    stop = False
    def __init__(self):
        Parameters.idCounter += 1
        self.name = 'Parameters_{0}'.format(Parameters.idCounter)
        self.status = 'incomplete'
        self.sheet = self.makeConnection()
        self.lastIndex = len(self.sheet.get_all_values())
        self.setParameters()
        self.readConfig()
        self.createConfig()
        self.createDirectory()

    def makeConnection(self):
        print('making connection')
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
        client = gspread.authorize(creds)
        return client.open("viscoTurb_test").sheet1

    def getLastIndex(self):
        return len(self.makeConnection().get_all_values())

    #write functionality that doesn't break if someone doesn't have enough params
    def setParameters(self):
        values_list = self.sheet.row_values(self.lastIndex)
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
        #run sim and update self.status to be in progress --> read parameter status

    #readConfig takes the global .cfg file as input
    def readConfig(self):
        print('readingConfig')
        config = configparser.ConfigParser()
        config.read('example.cfg')
        self.buildLocation = config['Paths']['base_dir'] + '/' + str(self.identifier)
        self.copyLocation = config['Paths']['copy_dir']

    #createConfig will create the local config file inside the project directory
    #Must read global config first so that you know where to put local one
    #this function should be called by createDirectory()
    def createConfig(self):
        print('creatingLocal conig')
        self.config = configparser.ConfigParser()
        self.config['run'] = {'stop_wall_time': self.stop_wall_time,
                             'stop_sim_time': self.stop_sim_time,
                             'dt': self.dt
                             }
        #place location corresponding to Levitt folder structure
        self.config['params'] = {'nL': self.nL,
                              'nx': self.nX,
				'ny': self.nY,
				'Re': self.Re,
				'Wi': self.Wi,
				'eta':self.eta}
        return self.config

    #use pathlib to create directory
    #take example config as input
    def createDirectory(self):
        print('creatingDirectory')
        run_dir = Path.home().joinpath(self.buildLocation)
        copy_dir = Path.home().joinpath(self.copyLocation) 
        print('run dir: ' + str(run_dir))
        print('copy dir: ' + str(copy_dir))
        run_dir.mkdir(exist_ok=True, parents=True)
        configFile = run_dir.joinpath('run_' + str(self.identifier) + '.cfg')
        with configFile.open('w') as wf:
            self.config.write(wf)
        simFile = '/Users/Reed/Desktop/thesis/simulation_builder/viscoturb.py'
        simFile2 = '/Users/Reed/Desktop/thesis/simulation_builder/kturb.py'
        self.force_symlink(copy_dir.joinpath('kturb.py'), run_dir.joinpath('kturb.py'))
        self.force_symlink(copy_dir.joinpath('viscoturb.py'), run_dir.joinpath('viscoturb.py'))
        copyfile(copy_dir.joinpath('run_kturb.sh'), str(run_dir) + '/run{}_kturb.sh'.format(self.identifier))

    def force_symlink(self, file1, file2):
        try:
            os.symlink(file1, file2)
        except OSError as  e:
            if e.errno == errno.EEXIST:
                os.remove(file2)
                os.symlink(file1, file2)  

