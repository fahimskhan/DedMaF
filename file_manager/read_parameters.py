#This file takes last row of spreadsheet as input
#Make sure the last row is corresponds to the simulation you wish to build!

#imports and packages
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import configparser
from pathlib import Path
import os, errno, textwrap
from shutil import copyfile
import logging

#Parameters class is the main controller for the program
#upon initialization, establish connection with google sheet
class Parameters():
    def __init__(self):
        self.status = 'incomplete'
        sheets = self.makeConnection()
        self.logistics_sheets = sheets[0]
        self.params_sheets = sheets[1]
        self.sheet_names = sheets[2]
        # self.lastIndex = len(self.params_sheet.get_all_values())
        #self.setParameters()
        self.doEverything('directory.cfg')
        #pass in global .cfg file --> directory.cfg
        #self.readConfig('directory.cfg')
        #self.createConfig()
        #self.createDirectory()

#Establishes connection with google sheet
    def makeConnection(self):
        logging.debug('making connections')
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
        client = gspread.authorize(creds)
        #for prop, value in vars(client).items():
        #    print('{}: {}'.format(prop, value))
        #pass in name of the spreadsheet to client.open (case sensitive)
        all_sheets = client.openall()[:-2]
        sheet_names = []
        for sheet in all_sheets:
            sheet_names.append(str(sheet).split("'")[1])
        print(sheet_names)
        params_sheets = []
        logistics_sheets = []
        for sheet_name in sheet_names:
            params_sheet = client.open(sheet_name).get_worksheet(0)
            logistics_sheet = client.open(sheet_name).get_worksheet(1)
            params_sheets.append(params_sheet)
            logistics_sheets.append(logistics_sheet)
        return [logistics_sheets, params_sheets, sheet_names]


#Read parameters from spreadsheet
#attribute corresponds to column in spreadsheet
    # def setParameters(self):
    def doEverything(self, configFile):
        #array of values that are in the last row
        for i in range(0,len(self.logistics_sheets)):
            project_name = self.sheet_names[i]
            logistics_sheet = self.logistics_sheets[i]
            params_sheet = self.params_sheets[i]
            lastIndex = len(params_sheet.get_all_values())
            values_line = logistics_sheet.row_values(2)
            if len(values_line) != 1:
                values = params_sheet.row_values(values_line[-1])[1:]
            else:
                values = params_sheet.row_values(lastIndex)[1:]
            labels = params_sheet.row_values(1)[1:]
            print(labels)
            print(values)
            #edit working fine till here

            #edit need to make an object here
            #or do everything in one for loop
            self.run_labels = []
            self.run_values = []
            self.params_labels = []
            self.params_values = []

            for i in range(0,len(labels)): #changed 0 to 1
                if labels[i] == '[run]':
                    tag = 'run'
                    self.identifier = values[i]
                    continue
                elif labels[i] == '[params]':
                    tag = 'params'
                    continue
                elif labels[i] == '[outputs]':
                    tag = 'outputs'
                    continue

                if tag == 'run':
                    self.run_labels.append(labels[i])
                    self.run_values.append(values[i])
                elif tag == 'params':
                    self.params_labels.append(labels[i])
                    self.params_values.append(values[i])

            ##READING CONFIG
            logging.debug('readingConfig')
            config = configparser.ConfigParser()
            config.read(configFile)
            # project_name = logistics_sheet.row_values(1)
            # self.project_name = project_name[-1]
            #buildLocation is the path to run folder/self.identifer (for example: simulation_builder/B)
            self.buildLocation = config['Paths']['base_dir'] + '/' + str(project_name) + '/runs/' + str(self.identifier)
            #copyLocation points to top level folder in git repo (simulation_builder)
            self.copyLocation = config['Paths']['copy_dir'] + '/' + str(project_name)

            #CREATING CONFIG
            logging.debug('creatingLocal config file')
            self.config = configparser.ConfigParser()
            self.config.optionxform = str
            # self.config['run'] = {'stop_wall_time': self.stop_wall_time,
            #                      'stop_sim_time': self.stop_sim_time,
            #                      'dt': self.dt
            #                      }
            self.config['run'] = {}
            for i in range(0,len(self.run_labels)):
                # print(self.run_labels[i])
                if (self.run_values[i] != ''):
                    self.config['run'][self.run_labels[i]] = self.run_values[i]
            # print(self.config['run']['stop_sim_time'])
            # self.config['params'] = {'nL': self.nL,
            #                         'nx': self.nX,
            #         				'ny': self.nY,
            #         				'Re': self.Re,
            #         				'Wi': self.Wi,
            #         				'eta':self.eta}
            self.config['params'] = {}
            for i in range(0,len(self.params_labels)):
                if (self.params_values[i] != ''):
                    self.config['params'][str(self.params_labels[i])] = self.params_values[i]

            # return self.config #edit why is this needed?

            #BUILDING directory
            logging.debug('creatingDirectory')
            run_dir = Path.home().joinpath(self.buildLocation)
            #run_dir example: /home/rfeldman/simulation_builder/runs/B
            copy_dir = Path.home().joinpath(self.copyLocation)
            #copy_dir example: /home/rfeldman/simulation_builder
            logging.debug('run dir: ' + str(run_dir))
            logging.debug('copy dir: ' + str(copy_dir))
            #create directory at appropriate location
            run_dir.mkdir(exist_ok=True, parents=True)
            #add paramsFile to directory we just created
            paramsFile = run_dir.joinpath('run_' + str(self.identifier) + '.cfg')
            # #creates symlink from kturb.py in copy directory to kturb.py in run directory
            # self.force_symlink(copy_dir.joinpath('kturb.py'), run_dir.joinpath('kturb.py'))
            # #creates symlink from viscoturb.py in copy directory to kturb.py in run directory
            # self.force_symlink(copy_dir.joinpath('viscoturb.py'), run_dir.joinpath('viscoturb.py'))
            symlink_files = logistics_sheet.row_values(1)
            self.symlink_files = symlink_files[-1].split(',')
            #print(self.symlink_file[1])
            #self.force_symlink(copy_dir.joinpath(strip(self.symlink_file[1])), run_dir.joinpath(strip(self.symlink_file[1])))
            for i in range(0,len(self.symlink_files)): #not_working
                self.symlink_files[i] = self.symlink_files[i].strip()
                # print(self.symlink_files[i])
                self.force_symlink(copy_dir.joinpath(str(self.symlink_files[i])), run_dir.joinpath(str(self.symlink_files[i])))
            #copy run.sh file from copy directory to run directory: --> runB_ktrub.sh for self.identifier = B
            #copyfile(copy_dir.joinpath('run_{}.sh'.format(self.project_name)), str(run_dir) + '/run{}_{}.sh'.format(self.identifier, self.project_name))
            to_path = str(run_dir) + '/run{}_{}.sh'.format(self.identifier, project_name)
            file_text = '\n'.join([
                '#!/usr/bin/bash',
                '##SBATCH --ntasks-per-node=16',
                '#SBATCH --time=5-0',
                '#SBATCH --nodes=1',
                '#SBATCH --ntasks=16',
                '#SBATCH --distribution=cyclic:cyclic',
                '#SBATCH --cpus-per-task=1',

                'source /home/projects/AFDGroup/build/dedalus/bin/activate',
                'result=${PWD##*/}',

                'date',
                'mpirun -np 8 python3 {} run_${{result}}.cfg'.format(str(self.symlink_files[0])),
                'date'])

            f = open(to_path, "w")
            f.write(file_text)
            f.close()
            # copyfile('parse_{}.py'.format(self.project_name), str(run_dir) + '/parse{}_{}.py'.format(self.identifier, self.project_name))
            # plot_file = self.sheet.row_values(5)
            # plot_file = plot_file[-1]
            # copyfile(copy_dir.joinpath('{}.py'.format(plot_file)), str(run_dir) + '/{}_{}.py'.format(plot_file, self.identifier))
            #populate run_B.cfg file with contents from createConfig()
            with paramsFile.open('w') as wf:
                self.config.write(wf)


    #readConfig takes the directory.cfg file as input
    #startd from here in winter sem
    # def readConfig(self, configFile):
    #     logging.debug('readingConfig')
    #     config = configparser.ConfigParser()
    #     config.read(configFile)
    #     project_name = self.logistics_sheet.row_values(1)
    #     self.project_name = project_name[-1]
    #     #buildLocation is the path to run folder/self.identifer (for example: simulation_builder/B)
    #     self.buildLocation = config['Paths']['base_dir'] + '/' + str(self.project_name) + '/runs/' + str(self.identifier)
    #     #copyLocation points to top level folder in git repo (simulation_builder)
    #     self.copyLocation = config['Paths']['copy_dir'] + '/' + str(project_name[-1])

    #createConfig will create the local config file inside the project directory
    #set parameters from spreadsheet inside run_'self.identifier'.cfg -->
    #run_B.cfg --> simulation_builder/runs/B/run_B.cfg
    # def createConfig(self):
        # logging.debug('creatingLocal config file')
        # self.config = configparser.ConfigParser()
        # self.config.optionxform = str
        # # self.config['run'] = {'stop_wall_time': self.stop_wall_time,
        # #                      'stop_sim_time': self.stop_sim_time,
        # #                      'dt': self.dt
        # #                      }
        # self.config['run'] = {}
        # for i in range(0,len(self.run_labels)):
        #     # print(self.run_labels[i])
        #     if (self.run_values[i] != ''):
        #         self.config['run'][self.run_labels[i]] = self.run_values[i]
        # # print(self.config['run']['stop_sim_time'])
        # # self.config['params'] = {'nL': self.nL,
        # #                         'nx': self.nX,
        # #         				'ny': self.nY,
        # #         				'Re': self.Re,
        # #         				'Wi': self.Wi,
        # #         				'eta':self.eta}
        # self.config['params'] = {}
        # for i in range(0,len(self.params_labels)):
        #     if (self.params_values[i] != ''):
        #         self.config['params'][str(self.params_labels[i])] = self.params_values[i]
        #
        # return self.config

#creates build directory
#writes run_B.cfg file, run_B_kturb.sh file, and symlink files (viscoturb.py, kturb.py) to build directory
#After this function, user should have a run directory with all neccesary files
    # def createDirectory(self):
        # logging.debug('creatingDirectory')
        # run_dir = Path.home().joinpath(self.buildLocation)
        # #run_dir example: /home/rfeldman/simulation_builder/runs/B
        # copy_dir = Path.home().joinpath(self.copyLocation)
        # #copy_dir example: /home/rfeldman/simulation_builder
        # logging.debug('run dir: ' + str(run_dir))
        # logging.debug('copy dir: ' + str(copy_dir))
        # #create directory at appropriate location
        # run_dir.mkdir(exist_ok=True, parents=True)
        # #add configFile to directory we just created
        # configFile = run_dir.joinpath('run_' + str(self.identifier) + '.cfg')
        # # #creates symlink from kturb.py in copy directory to kturb.py in run directory
        # # self.force_symlink(copy_dir.joinpath('kturb.py'), run_dir.joinpath('kturb.py'))
        # # #creates symlink from viscoturb.py in copy directory to kturb.py in run directory
        # # self.force_symlink(copy_dir.joinpath('viscoturb.py'), run_dir.joinpath('viscoturb.py'))
        # symlink_files = self.logistics_sheet.row_values(2)
        # self.symlink_files = symlink_files[-1].split(',')
        # #print(self.symlink_file[1])
        # #self.force_symlink(copy_dir.joinpath(strip(self.symlink_file[1])), run_dir.joinpath(strip(self.symlink_file[1])))
        # for i in range(0,len(self.symlink_files)): #not_working
        #     self.symlink_files[i] = self.symlink_files[i].strip()
        #     # print(self.symlink_files[i])
        #     self.force_symlink(copy_dir.joinpath(str(self.symlink_files[i])), run_dir.joinpath(str(self.symlink_files[i])))
        # #copy run.sh file from copy directory to run directory: --> runB_ktrub.sh for self.identifier = B
        # #copyfile(copy_dir.joinpath('run_{}.sh'.format(self.project_name)), str(run_dir) + '/run{}_{}.sh'.format(self.identifier, self.project_name))
        # to_path = str(run_dir) + '/run{}_{}.sh'.format(self.identifier, self.project_name)
        # file_text = '\n'.join([
        #     '#!/usr/bin/bash',
        #     '##SBATCH --ntasks-per-node=16',
        #     '#SBATCH --time=5-0',
        #     '#SBATCH --nodes=1',
        #     '#SBATCH --ntasks=16',
        #     '#SBATCH --distribution=cyclic:cyclic',
        #     '#SBATCH --cpus-per-task=1',
        #
        #     'source /home/projects/AFDGroup/build/dedalus/bin/activate',
        #     'result=${PWD##*/}',
        #
        #     'date',
        #     'mpirun -np 8 python3 {} run_${{result}}.cfg'.format(str(self.symlink_files[0])),
        #     'date'])
        #
        # f = open(to_path, "w")
        # f.write(file_text)
        # f.close()
        # # copyfile('parse_{}.py'.format(self.project_name), str(run_dir) + '/parse{}_{}.py'.format(self.identifier, self.project_name))
        # # plot_file = self.sheet.row_values(5)
        # # plot_file = plot_file[-1]
        # # copyfile(copy_dir.joinpath('{}.py'.format(plot_file)), str(run_dir) + '/{}_{}.py'.format(plot_file, self.identifier))
        # #populate run_B.cfg file with contents from createConfig()
        # with configFile.open('w') as wf:
        #     self.config.write(wf)

    #helper function to make sure symlink doesnt already exist
    #if symlink exsits, overwrite it
    def force_symlink(self, file1, file2):
        try:
            os.symlink(file1, file2)
        except OSError as  e:
            if e.errno == errno.EEXIST:
                os.remove(file2)
                os.symlink(file1, file2)
