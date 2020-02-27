#This program checks which jobs are currently running and updates sheets accordingly,
#whether a completed job run is successful or not

#import libraries and modules
import gspread
from gspread.models import Cell
from oauth2client.service_account import ServiceAccountCredentials
import configparser
from pathlib import Path
import os, errno, textwrap, subprocess
import logging
import re
import pickle

################################################################################

#main controller for the program, runs all containing functions
class UpdateStatus():
    def __init__ (self):
        self.status = 'incomplete'
        self.makeConnection()
        self.readConfig()
        self.locatePrevRuns()
        self.execSqueue()
        self.updateSheets(self.execScancel)

################################################################################

    def makeConnection(self):
        logging.debug('connecting to sheet inside status_update.py')
        #connect to google sheet
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        #import credentials from client_secret.json (included in .gitignore)
        #read on how to make a client_secret.json in READ_ME
        creds = ServiceAccountCredentials.from_json_keyfile_name(Path.home().joinpath('simulation_builder/file_manager/client_secret.json'), scope)
        self.client = gspread.authorize(creds)

        #read all sheets associated with client email
        all_sheets = self.client.openall()[:-2]
        #initialize empty array to store full titles of spreeadsheets
        full_titles = []
        #loop over each sheet in all_sheets
        for sheet in all_sheets:
            #store in full_titles
            full_titles.append(str(sheet).split("'")[1])
        #trim full_titles and store in short_titles, this is important for squeue grep that only includes
        #first three letters of title name
        self.short_titles = [x[:3] for x in full_titles]
        #make a hash table for storing full titles to corresponding short titles
        self.titles = {}
        #store short_titles and full_titles as key value pairs
        for i in range(0,len(self.short_titles)):
            self.titles[self.short_titles[i]] = full_titles[i]

################################################################################

    def readConfig(self):
        logging.debug('reading configuration file for user defined paths')
        #read config file where custom build locations for copies of project runs can be specified
        #we will need to access output files of different runs to check if the run is successful or not
        config = configparser.ConfigParser()
        config.read(Path.home().joinpath('simulation_builder/file_manager/directory.cfg'))
        #store base directory path in self
        self.buildLocation = config['Dir_paths']['base_dir']

################################################################################

    def locatePrevRuns(self):
        logging.debug('constructing os commands to locate file containing previous job runs')
        #define paths to read local hidden file where previous job runs are stored
        self.fpath = Path.home().joinpath('.simulation_builder/curr_status')
        self.fdir = Path.home().joinpath('.simulation_builder')
        #define command to check of directory .simulation_builder exists
        self.dir_cmd = f'[ -d {self.fdir} ]'
        #define command to check if file curr_status exists
        # self.file_cmd = f'ls {self.fpath}'
        self.file_cmd = f'find {self.fdir} -name curr_status'

################################################################################

    def execSqueue(self):
        logging.debug('executing squeue to find all current runs')
        #grab name of projects currently running, run letters and job numbers using squeue
        #find home directory path
        home_dir = str(Path.home())
        #extract user name from home directory path
        user_name = home_dir.split('/')[-1]
        #find full path of squeue, this is important for cronjob
        squeue_cmd = 'locate -b "\\squeue"'
        #execute find squeue path command
        try:
            #store squeue path
            squeue_path = subprocess.check_output(squeue_cmd, shell=True)
            #convert squeue_path from bytes to string
            squeue_path = str(squeue_path, 'utf-8').split('\n')[0]
        #if path not found
        except subprocess.CalledProcessError as e:
            #raise error
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
        #construct squeue command
        squeue_cmd = f'{squeue_path} | grep {user_name}'
        #initialize a running variable, indicating there are currently running jobs, as True
        self.running = True
        #execute squeue command
        try:
            #store run specifications including JOBID and NAME
            self.jobs_list = subprocess.check_output(squeue_cmd, shell=True)
        #if there are no jobs running
        except subprocess.CalledProcessError as e:
            #set running as False
            self.running = False
            #avoid raising error
            #raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

################################################################################

    def execScancel(self, job_number):
        logging.debug('executing scancel to delete multiple job runs')
        #find home directory path
        home_dir = str(Path.home())
        #extract user name from home directory path
        user_name = home_dir.split('/')[-1]
        #find full path of scancel, this is important for cronjob
        scancel_cmd = 'locate -b "\\scancel"'
        #execute find scancel path command
        try:
            #store scancel path
            scancel_path = subprocess.check_output(scancel_cmd, shell=True)
            #convert scancel path from bytes to string
            scancel_path = str(scancel_path, 'utf-8').split('\n')[0]
        #if path not found
        except subprocess.CalledProcessError as e:
            #raise error
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        #construct scancel command
        cncl_mult_jobs_cmd = f'{scancel_path} {job_number}'
        #execute scancel commmand
        try:
            subprocess.check_output(cncl_mult_jobs_cmd, shell=True)
        #if job not cancelled
        except subprocess.CalledProcessError as e:
            #raise error
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

################################################################################

    def updateSheets(self, execScancel):
        logging.debug('updating sheets with job numbers')
        #if there are current running jobs
        #extract job ids, proj names and run letters
        if self.running:
            #convert list of job specifications from bytes to array of strings
            self.jobs_list = str(self.jobs_list, 'utf-8').split('\n')[:-1]
            #form 2D array of job specifications
            self.jobs_list = [x.strip().split(' ') for x in self.jobs_list]
            #store JOBIDs in job_nums array, e.g. jobs_nums = ['5678', '5679' ... ]
            job_nums = [int(x[0]) for x in self.jobs_list]
            #initialize proj_runs array for storing project names and run letters
            proj_runs = []
            #loop over each job in jobs_list
            for job in self.jobs_list:
                #append NAME to proj_runs, e.g. proj_runs = ['rAAM_vis', 'rAAD_liq' ... ]
                proj_runs.append(list(filter(lambda x: re.search(r'r', x), job))[0])
            #form 2D array of proj names and run letters, e.g. proj_runs = [['AAM', 'vis'], ['AAD', 'liq'] ... ]
            proj_runs = [x[1:].split('_') for x in proj_runs]
            #switch order of proj names and run letters so that proj names come first
            #e.g. proj_runs = [['vis', 'AAM'], ['liq', 'AAD'] ... ]
            for x in proj_runs:
                x[0], x[1] = x[1], x[0]
            #add job numbers to corresponding proj_runs arrays
            for i in range(len(proj_runs)):
                proj_runs[i].append(job_nums[i])
            #sort proj_runs, e.g. proj_run_job = [['liq', 'AAD', '5679'], ['vis', 'AAM', '5678'] ... ]
            #when we update sheets, this sort makes sure runs are updated in order
            proj_run_job = sorted(proj_runs)

            #boolean for whether any previous job runs exist
            last_array_avail = True
            #execute command to check if local file exists
            try:
                #store file path in result
                result = subprocess.check_output(self.file_cmd, shell=True)
                result = str(result, 'utf-8').split('\n')[0]
            #if command not properly executed
            except subprocess.CalledProcessError as e:
                #raise error
                raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
            #if result is empty string, local file does not exist
            if result == '':
                #set last_array_avail to False
                last_array_avail = False

            #initialize array to store completed jobs
            comp_proj_run_job = []
            #read in last stored array if available
            if last_array_avail:
                #open local file
                pickle_in = open(self.fpath, 'rb')
                #load stored array
                last_proj_run_job = pickle.load(pickle_in)
                #loop over each previous job run in locally stored array
                for i in range(len(last_proj_run_job)):
                    #if previous job run not in current job runs
                    if last_proj_run_job[i] not in proj_run_job:
                        #store job run in comp_proj_run_job as completed
                        #comp_proj_run_job looks like proj_run_job
                        comp_proj_run_job.append(last_proj_run_job[i])

            #store elements in proj_run_job and comp_proj_run_job in nested hash tables
            #initialize hash table for current runs
            proj_hash = {}
            #populate nested hash table for use in updating sheets
                #proj_run_job[i][0] is proj short sheet_name
                #proj_run_job[i][1] is run letters
                #proj_run_job[i][2] is job number
            #loop over each array in proj_run_job
            #initialize array to store indices of multiple job numbers for a run
            remove_is = []
            for i in range(0,len(proj_run_job)):
                #if proj short name already a first key
                if proj_run_job[i][0] in proj_hash:
                    #if run letters already a second key
                    if proj_run_job[i][1] in proj_hash[proj_run_job[i][0]]:
                        #print warning to user
                        print(f'WARNING: Multiple job runs submitted for project {proj_run_job[i][0]}, run {proj_run_job[i][1]}. Job {proj_run_job[i][2]} cancelled.')
                        #call execScancel() with job number to scancel job
                        execScancel(proj_run_job[i][2])
                        #append job number to comp_proj_run_job
                        comp_proj_run_job.append(proj_run_job[i])
                        #still append job number to array value of second key to ensure first job number is not set to empty while updating sheet
                        proj_hash[proj_run_job[i][0]][proj_run_job[i][1]].append(proj_run_job[i][2])
                        #store i to be removed letter from proj_run_job
                        remove_is.append(i)
                    else:
                        #set run letters as second key
                        proj_hash[proj_run_job[i][0]][proj_run_job[i][1]] = []
                        #append job number to array value of second key
                        proj_hash[proj_run_job[i][0]][proj_run_job[i][1]].append(proj_run_job[i][2])
                else:
                    #set proj short name as first key
                    proj_hash[proj_run_job[i][0]] = {}
                    #set run letters as second key
                    proj_hash[proj_run_job[i][0]][proj_run_job[i][1]] = []
                    #append job number to array value of second key
                    proj_hash[proj_run_job[i][0]][proj_run_job[i][1]].append(proj_run_job[i][2])
            #e.g. proj_hash = {'liq': {'AAD' : [5679]}, 'vis': {'AAM' : [5678]}}

            #remove multiple job numbers from proj_run_job
            if remove_is != []:
                del proj_run_job[remove_is[0]:remove_is[-1]+1]
            #sort comp_proj_run_job so that sheet is updated in order
            comp_proj_run_job = sorted(comp_proj_run_job)

            #initialize hash table for completed runs
            comp_proj_hash = {}
            #populate nested hash table for use in updating sheets
                #comp_proj_run_job[i][0] is proj short sheet_name
                #comp_proj_run_job[i][1] is run letters
                #comp_proj_run_job[i][2] is job number
            #loop over each array in comp_proj_run_job
            for i in range(0,len(comp_proj_run_job)):
                #if proj short name already a first key
                if comp_proj_run_job[i][0] in comp_proj_hash:
                    #if run letters already a second key
                    if comp_proj_run_job[i][1] in comp_proj_hash[comp_proj_run_job[i][0]]:
                        #append job number to array value of second key
                        comp_proj_hash[comp_proj_run_job[i][0]][comp_proj_run_job[i][1]].append(comp_proj_run_job[i][2])
                    else:
                        #set run letters as second key
                        comp_proj_hash[comp_proj_run_job[i][0]][comp_proj_run_job[i][1]] = []
                        #append job number to array value of second key
                        comp_proj_hash[comp_proj_run_job[i][0]][comp_proj_run_job[i][1]].append(comp_proj_run_job[i][2])
                else:
                    #set proj short name as first key
                    comp_proj_hash[comp_proj_run_job[i][0]] = {}
                    #set run letters as second key
                    comp_proj_hash[comp_proj_run_job[i][0]][comp_proj_run_job[i][1]] = []
                    #append job number to array value of second key
                    comp_proj_hash[comp_proj_run_job[i][0]][comp_proj_run_job[i][1]].append(comp_proj_run_job[i][2])
            #e.g. proj_hash = {'liq': {'AAD' : [5677]}, 'vis': {'AAO' : [5676]}}


            #update sheets
            #loop over each proj short name in proj hash
            for proj in proj_hash:
                #proj short name exists in short_titles
                if proj in self.short_titles:
                    #open google sheet with proj full name
                    sheet = self.client.open(self.titles[proj]).sheet1
                    #grab all run letters from [run] column
                    col_num = sheet.col_values(4)
                    #initialize an array for storing update cell values
                    cell_list = []

                    #populate Running column first
                    #loop over current runs for each sheet
                    for run in proj_hash[proj]:
                        #calculate row number
                        row_num = col_num.index(run) + 1
                        #append new value to cell_list
                        cell_list.append(Cell(row = row_num,
                                              col = 1,
                                              value = str(proj_hash[proj][run][0])))

                    #populate Complete and Error columns
                    #if proj name exists in completed proj hash table
                    if proj in list(comp_proj_hash.keys()):
                        #empty comp job numbers from running col and populate to either Complete or Error column
                        #loop over completed runs for each sheet
                        for comp_run in comp_proj_hash[proj]:
                            #if more than one job numbers present, do not empty cell
                            if len(proj_hash[proj][comp_run]) == 1:
                                #calculate row number
                                row_num = col_num.index(comp_run) + 1
                                #remove job number from Running column
                                cell_list.append(Cell(row = row_num,
                                                      col = 1,
                                                      value = ''))

                            #determine whether completed job number should be moved to Complete or Error
                            #check for 'Success!' in slurm output file
                            #initially set success to False
                            success = False
                            #if build path is specified in directory.cfg
                            if self.buildLocation:
                                #define output path according to specified path
                                out_path = self.buildLocation + '/' + str(self.titles[proj]) + '/runs/' + str(comp_run) + '/slurm-' + str(comp_proj_hash[proj][comp_run][0]) + '.out'
                            else:
                                #if build path is not specified look for slurm output in projects
                                out_path = 'projects/' + str(self.titles[proj]) + '/runs/' + str(comp_run) + '/slurm-' + str(comp_proj_hash[proj][comp_run][0]) + '.out'

                            #add user name to define fill output path
                            full_out_path = Path.home().joinpath(out_path)
                            #open output file
                            out_read = open(full_out_path, 'r')
                            #read all lines of output file
                            lines = out_read.readlines()
                            #close output file
                            out_read.close()

                            #check for 'Success!' starting from the last line
                            for i in reversed(range(len(lines))):
                                #if 'Success!' found
                                if 'SuCcEsS!' in lines[i]:
                                    #set sucess to True
                                    success = True
                                    #break out of loop
                                    break

                            #if run completed successfully
                            if success:
                                #job number will be added to Complete column
                                comp_cell = sheet.range('B{}'.format(row_num)+':'+'B{}'.format(row_num))
                                comp_cell_value = comp_cell[0].value
                                #if there are previous job numbers in cell
                                if comp_cell_value != '':
                                    #append job number to existing numbers
                                    comp_cell_value = str(comp_cell_value) + ', ' + ', '.join(str(x) for x in comp_proj_hash[proj][comp_run])
                                    #append to cell_list
                                    cell_list.append(Cell(row = row_num,
                                                          col = 2,
                                                          value = comp_cell_value))
                                #if cell is empty
                                else:
                                    #insert job number, append to cell_list
                                    cell_list.append(Cell(row = row_num,
                                                          col = 2,
                                                          value = ', '.join(str(x) for x in comp_proj_hash[proj][comp_run])))

                            #if run did not complete successfully
                            else:
                                #job number will be added to Error column
                                comp_cell = sheet.range('C{}'.format(row_num)+':'+'C{}'.format(row_num))
                                comp_cell_value = comp_cell[0].value
                                #if there are previous job numbers in cell
                                if comp_cell_value != '':
                                    #append job number to existing numbers
                                    comp_cell_value = str(comp_cell_value) + ', ' + ', '.join(str(x) for x in comp_proj_hash[proj][comp_run])
                                    #append to cell_list
                                    cell_list.append(Cell(row = row_num,
                                                          col = 3,
                                                          value = comp_cell_value))
                                #if cell is empty
                                else:
                                    #insert job number, append to cell_list
                                    cell_list.append(Cell(row = row_num,
                                                          col = 3,
                                                          value = ', '.join(str(x) for x in comp_proj_hash[proj][comp_run])))

                    #update all edited cells in sheet
                    sheet.update_cells(cell_list)

            #store current array of job numbers in local file
            #check if directory .simulation_builder exists
            try:
                subprocess.check_output(self.dir_cmd, shell=True)
            except subprocess.CalledProcessError as e:
                #if not, make directory
                self.fdir.mkdir(exist_ok=True, parents=True)
                #avoid raising error
                # raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

            #write current array, proj_run_job, to file curr_status
            f = open(self.fpath, 'wb')
            pickle.dump(proj_run_job, f)
            #close file
            f.close()

        #if there are no jobs currently running
        else:
            #boolean for whether any previous job runs exist
            last_array_avail = True
            #execute command to check if local file exists
            try:
                #store file path in result
                result = subprocess.check_output(self.file_cmd, shell=True)
                result = str(result, 'utf-8').split('\n')[0]
            #if command not properly executed
            except subprocess.CalledProcessError as e:
                #raise error
                raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
            #if result is empty string, local file does not exist
            if result == '':
                #set last_array_avail to False
                last_array_avail = False

            #read in last stored array if available
            if last_array_avail:
                #open local file
                pickle_in = open(self.fpath, 'rb')
                #load stored array
                last_proj_run_job = pickle.load(pickle_in)
                #set comp_proj_run_job as last_proj_run_job since all running jobs have been completed
                comp_proj_run_job = last_proj_run_job

                #initialize hash table for completed runs
                comp_proj_hash = {}
                #populate nested hash table for use in updating sheets
                    #comp_proj_run_job[i][0] is proj short sheet_name
                    #comp_proj_run_job[i][1] is run letters
                    #comp_proj_run_job[i][2] is job number
                #loop over each array in comp_proj_run_job
                for i in range(0,len(comp_proj_run_job)):
                    if comp_proj_run_job[i][0] in comp_proj_hash:
                        #if run letters already a second key
                        if comp_proj_run_job[i][1] in comp_proj_hash[comp_proj_run_job[i][0]]:
                            #append job number to array value of second key
                            comp_proj_hash[comp_proj_run_job[i][0]][comp_proj_run_job[i][1]].append(comp_proj_run_job[i][2])
                        else:
                            #set run letters as second key
                            comp_proj_hash[comp_proj_run_job[i][0]][comp_proj_run_job[i][1]] = []
                            #append job number to array value of second key
                            comp_proj_hash[comp_proj_run_job[i][0]][comp_proj_run_job[i][1]].append(comp_proj_run_job[i][2])
                    else:
                        #set proj short name as first key
                        comp_proj_hash[comp_proj_run_job[i][0]] = {}
                        #set run letters as second key
                        comp_proj_hash[comp_proj_run_job[i][0]][comp_proj_run_job[i][1]] = []
                        #append job number to array value of second key
                        comp_proj_hash[comp_proj_run_job[i][0]][comp_proj_run_job[i][1]].append(comp_proj_run_job[i][2])
                #e.g. proj_hash = {'liq': {'AAD' : [5677]}, 'vis': {'AAO' : [5676]}}

                #update sheets
                #loop over each proj short name in comp proj hash
                for proj in comp_proj_hash:
                    #if proj short name exists in short_titles
                    if proj in self.short_titles:
                        #open google sheet with proj full name
                        sheet = self.client.open(self.titles[proj]).sheet1
                        #grab all run letters from [run] column
                        col_num = sheet.col_values(4)
                        #initialize an array for storing updated cell values
                        cell_list = []

                        #empty comp job numbers from Running col and populate to either Complete or Error col
                        #loop over completed runs for each sheet
                        for comp_run in comp_proj_hash[proj]:
                            #calculate row number
                            row_num = col_num.index(comp_run) + 1
                            #remove job number from Running column
                            cell_list.append(Cell(row = row_num,
                                                  col = 1,
                                                  value = ''))

                            #determine whether completed job number should be moved to Complete or Error
                            #check for 'Success!' in slurm output file
                            #initially set success to False
                            success = False
                            #if build path is specified in directory.cfg
                            if self.buildLocation:
                                #define output path according to specified path
                                out_path = self.buildLocation + '/' + str(self.titles[proj]) + '/runs/' + str(comp_run) + '/slurm-' + str(comp_proj_hash[proj][comp_run][0]) + '.out'
                            else:
                                #if build path is not specified look for slurm output in projects
                                out_path = 'projects/' + str(self.titles[proj]) + '/runs/' + str(comp_run) + '/slurm-' + str(comp_proj_hash[proj][comp_run][0]) + '.out'

                            #add user name to define fill output path
                            full_out_path = Path.home().joinpath(out_path)
                            #open output file
                            out_read = open(full_out_path, 'r')
                            #read all lines of output file
                            lines = out_read.readlines()
                            #close output file
                            out_read.close()

                            for i in reversed(range(len(lines))):
                                if 'SuCcEsS!' in lines[i]:
                                    success = True
                                    break

                            #if run completed successfully
                            if success:
                                #job number will be added to Complete column
                                comp_cell = sheet.range('B{}'.format(row_num)+':'+'B{}'.format(row_num))
                                comp_cell_value = comp_cell[0].value
                                #if there are previous job numbers in cell
                                if comp_cell_value != '':
                                    #append job number to existing numbers
                                    comp_cell_value = str(comp_cell_value) + ', ' + ', '.join(str(x) for x in comp_proj_hash[proj][comp_run])
                                    #append to cell_list
                                    cell_list.append(Cell(row = row_num,
                                                          col = 2,
                                                          value = comp_cell_value))
                                #if cell is empty
                                else:
                                    #insert job number, append to cell_list
                                    cell_list.append(Cell(row = row_num,
                                                          col = 2,
                                                          value = ', '.join(str(x) for x in comp_proj_hash[proj][comp_run])))

                            #if run did not complete successfully
                            else:
                                #job number will be added to Error column
                                comp_cell = sheet.range('C{}'.format(row_num)+':'+'C{}'.format(row_num))
                                comp_cell_value = comp_cell[0].value
                                #if there are previous job numbers in cell
                                if comp_cell_value != '':
                                    #append job number to existing numbers
                                    comp_cell_value = str(comp_cell_value) + ', ' + ', '.join(str(x) for x in comp_proj_hash[proj][comp_run])
                                    #append to cell_list
                                    cell_list.append(Cell(row = row_num,
                                                          col = 3,
                                                          value = comp_cell_value))
                                #if cell is empty
                                else:
                                    #insert job number, append to cell_list
                                    cell_list.append(Cell(row = row_num,
                                                          col = 3,
                                                          value = ', '.join(str(x) for x in comp_proj_hash[proj][comp_run])))

                    #update all edited cells in sheet
                    sheet.update_cells(cell_list)

                #no current array to store, so remove pickle file
                rmv_file_cmd = f'rm {self.fpath}'
                #execute remove file command
                try:
                    subprocess.check_output(rmv_file_cmd, shell=True)
                #if file cannot be removed
                except subprocess.CalledProcessError as e:
                    print('unable to delete local file')
                    #raise error
                    raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

################################################################################
