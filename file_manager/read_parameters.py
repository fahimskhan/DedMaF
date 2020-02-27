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

################################################################################

#Parameters class is the main controller for the program
#upon initialization, establish connection with google sheet
class Parameters():
    def __init__(self):
        self.status = 'incomplete'
        sheets = self.makeConnection()
        self.logistics_sheets = sheets[0]
        self.params_sheets = sheets[1]
        self.sheet_names = sheets[2]
        #executes all functions for each run
        self.runAll()

################################################################################

    #Establishes connection with google sheet
    def makeConnection(self):
        logging.debug('making connections inside read_parameters.py')
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(Path.home().joinpath('simulation_builder/file_manager/client_secret.json'), scope)
        client = gspread.authorize(creds)
        #open all sheets associated with client email
        all_sheets = client.openall()[:-2] #for now opening all sheets except the last two, cause of old client email
        #detach and return logistics_sheets, params_sheets and sheet names
        sheet_names = []
        for sheet in all_sheets:
            sheet_names.append(str(sheet).split("'")[1])
        params_sheets = []
        logistics_sheets = []
        for sheet_name in sheet_names:
            params_sheet = client.open(sheet_name).get_worksheet(0)
            logistics_sheet = client.open(sheet_name).get_worksheet(1)
            params_sheets.append(params_sheet)
            logistics_sheets.append(logistics_sheet)
        return [logistics_sheets, params_sheets, sheet_names]

################################################################################

    #read parameters from spreadsheet
    #takes in labels and values of run
    def setParameters(self, labels, values):
        self.run_labels = []
        self.run_values = []
        self.params_labels = []
        self.params_values = []

        for i in range(0,len(labels)): #changed 0 to 3
        #this ensures that nothing before [run] is read
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

################################################################################

    #read directory.cfg and assemble build/copy paths
    #takes in project name
    def readConfig(self, project_name):
        logging.debug('readingConfig')
        config = configparser.ConfigParser()
        config.read(Path.home().joinpath('simulation_builder/file_manager/directory.cfg'))
        #buildLocation is the path to run folder/self.identifer (for example: projects/project_name/run)
        if config['Dir_paths']['base_dir']: #if build path is specified build new dir there
            self.buildLocation = config['Dir_paths']['base_dir'] + '/' + str(project_name) + '/runs/' + str(self.identifier)
        else: #if build path is not specified build in home_dir/projects
            self.buildLocation = 'projects/' + str(project_name) + '/runs/' + str(self.identifier)
        #copyLocation points to top level folder in git repo (simulation_builder)
        if config['Dir_paths']['copy_dir']: #same here
            self.copyLocation = config['Dir_paths']['copy_dir'] + '/' + str(project_name)
        else: # copy form home_dir/project_name
            self.copyLocation = str(project_name)

################################################################################

    #create params file
    def createConfig(self):
        logging.debug('creatingLocal config file')
        self.config = configparser.ConfigParser()
        self.config.optionxform = str
        self.config['run'] = {}
        for i in range(0,len(self.run_labels)):
            if (self.run_values[i] != ''):
                self.config['run'][self.run_labels[i]] = self.run_values[i]

        self.config['params'] = {}
        for i in range(0,len(self.params_labels)):
            if (self.params_values[i] != ''):
                self.config['params'][str(self.params_labels[i])] = self.params_values[i]

        # return self.config #edit why is this needed?

################################################################################

    #helper function to make sure symlink doesnt already exist
    #if symlink exsits, overwrite it
    def force_symlink(self, file1, file2):
        try:
            os.symlink(file1, file2)
        except OSError as  e:
            if e.errno == errno.EEXIST:
                os.remove(file2)
                os.symlink(file1, file2)

################################################################################

    #create directory and place symlink file, params file and shell script in it
    def createDirectory(self, project_name, logistics_sheet):
        logging.debug('creatingDirectory')
        run_dir = Path.home().joinpath(self.buildLocation)
        #run_dir example: /home/fkhan/projects/project_name/runs/AAB
        copy_dir = Path.home().joinpath(self.copyLocation)
        #copy_dir example: /home/fkhan/project_name
        logging.debug('run dir: ' + str(run_dir))
        logging.debug('copy dir: ' + str(copy_dir))
        #create directory at appropriate location
        run_dir.mkdir(exist_ok=True, parents=True)

        #add paramsFile to directory we just created
        paramsFile = run_dir.joinpath('run_' + str(self.identifier) + '.cfg')
        #populate params file with contents from createConfig()
        with paramsFile.open('w') as wf:
            self.config.write(wf)

        #read in symlink file name
        symlink_files = logistics_sheet.row_values(1)
        if len(symlink_files) == 0:
            print('Symlink file missing! Please specify symlink file name in sheet.')
        else:
            #copy symlink file
            self.symlink_files = symlink_files[-1].split(',')
            for i in range(0,len(self.symlink_files)): #not_working
                self.symlink_files[i] = self.symlink_files[i].strip()
                self.force_symlink(copy_dir.joinpath(str(self.symlink_files[i])), run_dir.joinpath(str(self.symlink_files[i])))
                path = copy_dir.joinpath(str(self.symlink_files[i]))
                #check if there is a success logger info a the bottom of symlink file
                with open(path, 'r') as symfile:
                    lines = symfile.readlines()
                    symfile.close()
                    if 'SuCcEsS!' not in lines[-1]:
                        with open(path, 'a') as symfile:
                            symfile.write('logger.info("SuCcEsS!")')
                            symfile.close()

            #wrtie new run.sh file
            to_path = str(run_dir) + '/r{}_{}.sh'.format(self.identifier, project_name)
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

################################################################################

    #executes defined functions for specified runs
    def runAll(self):
        #array of values that are in the last row
        for i in range(0,len(self.logistics_sheets)):
            project_name = self.sheet_names[i]
            logistics_sheet = self.logistics_sheets[i]
            params_sheet = self.params_sheets[i]
            lastIndex = len(params_sheet.get_all_values())
            values_lines = logistics_sheet.row_values(2)
            labels = params_sheet.row_values(1)[3:] #this is excluding the first three columns

            #checking if there is an input in params value line in logistics_sheet
            if len(values_lines) != 1:
                #if there is an input read the line indicated in the input
                values_lines = values_lines[-1].split(',')
                values_lines = [x.strip() for x in values_lines]
                for values_line in values_lines:
                    values = params_sheet.row_values(values_line) #this is excluding the first three columns
                    #if a job is running for a particular run, do not read in run params
                    if values[0] == '':
                        values = values[3:]
                        self.setParameters(labels, values)
                        self.readConfig(project_name)
                        self.createConfig()
                        self.createDirectory(project_name, logistics_sheet)
            else:
                #if not read the last line
                values = params_sheet.row_values(lastIndex) #this is excluding the first three columns
                if values[0] == '':
                    values = values[3:]
                    self.setParameters(labels, values)
                    self.readConfig(project_name)
                    self.createConfig()
                    self.createDirectory(project_name, logistics_sheet)

################################################################################
