import gspread
from gspread.models import Cell
from gspread_formatting import *
from oauth2client.service_account import ServiceAccountCredentials
import configparser
from pathlib import Path
import os, errno, textwrap, subprocess
from shutil import copyfile
import logging
import re
import pickle
#connect to google sheet
logging.debug('making connections')
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(Path.home().joinpath('simulation_builder/file_manager/client_secret.json'), scope)
client = gspread.authorize(creds)
# service = discovery.build('drive', 'v3', credentials=creds)
# list = service.drive().list()
#pass in name of the spreadsheet to client.open (case sensitive)
# logistics_sheet = client.open("Logistics").sheet1
# full_titles = logistics_sheet.row_values(4)[-1].split(',')
# full_titles = [x.strip() for x in full_titles]
# short_titles = [x.strip()[:3] for x in full_titles]
# titles = {}
# for i in range(0,len(short_titles)):
#     titles[short_titles[i]] = full_titles[i]
#read all sheets
all_sheets = client.openall()[:-2]
full_titles = []
for sheet in all_sheets:
    full_titles.append(str(sheet).split("'")[1])
short_titles = [x[:3] for x in full_titles]
titles = {}
for i in range(0,len(short_titles)):
    titles[short_titles[i]] = full_titles[i]
#print(titles)

#format cells (colors)

# fmt = cellFormat(
#             backgroundColor = color(1, 1, 0)
#             )

# setting `status` to NULL by default #no need
# def null_status():
#     for title in full_titles:
#         sheet = client.open(title).sheet1
#         lastIndex = len(sheet.get_all_values())
#         # resp = sheet.spreadsheet.fetch_sheet_metadata({
#         #         'includeGridData': True,
#         #         'ranges': ['%s!%s' % (sheet.title, f'A{str(i)}')],
#         #         'fields': 'sheets.data.rowData.values.effectiveFormat'
#         #     })
#         # props = resp['sheets'][0]['data'][0]['rowData'][0]['values'][0].get('effectiveFormat')
#         # print("HERE",i)
#         # print(props['backgroundColor'])
#         # for i in range (2,lastIndex+1):
#         #     print(i)
#         #     print('HERE')
#         #     crnt_fmt = get_effective_format(sheet,'A'+str(i))
#         #     print(crnt_fmt)
#         # #     # cell_list = sheet.range('A{}'.format(i)+':'+'A{}'.format(i))
#         #     format_cell_range(sheet, 'A'+str(i), fmt)
#         #     # cell_list[0].value = ''
#         #     # sheet.update_cells(cell_list)

#grab proj name, run, job numbers using squeue
home_dir = str(Path.home())
user_name = home_dir.split('/')[-1]
user_cmd = f'/cm/shared/apps/slurm/17.02.11/bin/squeue | grep {user_name}'
# user_cmd = '/cm/shared/apps/slurm/17.02.11/bin/squeue | grep "' + user_name + '" | grep "run._..."'
# cmd = '/cm/shared/apps/slurm/17.02.11/bin/squeue | grep "' + user_name + '" | grep -o "run._..."'
#dummy var
running = True
try:
    result = subprocess.check_output(user_cmd, shell=True)
except subprocess.CalledProcessError as e:
    # null_status()
    running = False
    #raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
#print('HERE', result)
#if there is sth currently running
if running:
    print('inside running')
    jobs_list = str(result, 'utf-8').split('\n')[:-1]
    ##################
    jobs = [x.strip().split(' ') for x in jobs_list]
    # print(jobs)
    job_nums = [int(x[0]) for x in jobs]
    proj_runs = []
    for job in jobs:
        proj_runs.append(list(filter(lambda x: re.search(r'run', x), job))[0])
    #print(job_nums)
    # print(proj_run)
    # print("HERE")
    # print(jobs)
    ##########
    # ind_jobs = [x[3:].split('_') for x in jobs]
    #########
    proj_runs = [x[3:].split('_') for x in proj_runs]
    for x in proj_runs:
        x[0], x[1] = x[1], x[0]
    #print(proj_runs)

#########
# ind_jobs = [tuple(x[3:].split('_')) for x in jobs]
# ind_jobs = set(ind_jobs)  # store as a set to handle possible duplicates
# print(ind_jobs)
# d = dict()
# for i in ind_jobs:
#     # d[i[0]] = i[1]
#     exec '%s' = {} % (i[0])
# print(liq)

# for i in ind_jobs:
#     print(i[1])
#     if i[1] in short_titles:
#         # print(str(titles[i[1]]))
#         sheet = client.open(titles[i[1]]).sheet1
#         #this is hard coded, needs to be the same as col of [run]
#         col = sheet.col_values(3)
#         row = col.index(i[0]) + 1
#         format_cell_range(sheet, 'A'+str(row), fmt)
#         cell_list = sheet.range('A{}'.format(row)+':'+'B{}'.format(row))
#         print(cell_list[0].value)
        # cell_list[0].value = 'running...'
        # sheet.update_cells(cell_list)

#edit what was I trying to do here?
# to_path = '/home/fkhan/simulation_builder/file_manager/temp.pickle'
# file_text = '\n'.join(['{},{}'.format(u, v) for (u, v) in ind_jobs])


# pickle_jar = open(to_path, "wb")
# pickle.dump(ind_jobs, pickle_jar)
# pickle_jar.close()

    #put all in one 2D array
    for i in range(len(proj_runs)):
        proj_runs[i].append(job_nums[i])
    proj_run_job = sorted(proj_runs)
    print('curr reading of runs', proj_run_job)
    #define paths to read local file from
    fpath = Path.home().joinpath('.simulation_builder/curr_status')
    fdir = Path.home().joinpath('.simulation_builder')
    dir_cmd = f'[ -d {fdir} ]'
    file_cmd = f'ls {fpath}'
    #bool to check if last array is available
    last_array_avail = True
    #check if anything previously stored
    try:
        subprocess.check_output(file_cmd, shell=True)
    except subprocess.CalledProcessError as e: #find an easier way to handle
        # fdir.mkdir(exist_ok=True, parents=True)
        last_array_avail = False
        # raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
    #to store completed jobs
    comp_proj_run_job = []
    # read in last stored array
    if last_array_avail:
        pickle_in = open(fpath, 'rb')
        last_proj_run_job = pickle.load(pickle_in)
        print('inside running, old file load successful!')
        print('last runs', last_proj_run_job)
        # compare curr and last nested arrays
        for i in range(len(last_proj_run_job)):
            if last_proj_run_job[i] not in proj_run_job:
                comp_proj_run_job.append(last_proj_run_job[i])
                # proj_run_job.append([last_proj_run_job[i][0], last_proj_run_job[i][1], last_proj_run_job[i][2]])
        print('comp runs', comp_proj_run_job)

    #print(proj_run_job)
    #proj_run_job[i][0] is proj short sheet_name
    #proj_run_job[i][1] is run letter
    #proj_run_job[i][2] is job number
    proj_hash = {}
    #populate nested hash table for use in updating sheets
    for i in range(0,len(proj_run_job)):
        if proj_run_job[i][0] in proj_hash:
            if proj_run_job[i][1] in proj_hash[proj_run_job[i][0]]:
                proj_hash[proj_run_job[i][0]][proj_run_job[i][1]].append(proj_run_job[i][2])
            else:
                proj_hash[proj_run_job[i][0]][proj_run_job[i][1]] = []
                proj_hash[proj_run_job[i][0]][proj_run_job[i][1]].append(proj_run_job[i][2])
        else:
            proj_hash[proj_run_job[i][0]] = {}
            proj_hash[proj_run_job[i][0]][proj_run_job[i][1]] = []
            proj_hash[proj_run_job[i][0]][proj_run_job[i][1]].append(proj_run_job[i][2])
    print('curr runs hash table', proj_hash)

    comp_proj_hash = {}
    #hash table for completed project
    for i in range(0,len(comp_proj_run_job)):
        if comp_proj_run_job[i][0] in comp_proj_hash:
            if comp_proj_run_job[i][1] in comp_proj_hash[comp_proj_run_job[i][0]]:
                comp_proj_hash[comp_proj_run_job[i][0]][comp_proj_run_job[i][1]].append(comp_proj_run_job[i][2])
            else:
                comp_proj_hash[comp_proj_run_job[i][0]][comp_proj_run_job[i][1]] = []
                comp_proj_hash[comp_proj_run_job[i][0]][comp_proj_run_job[i][1]].append(comp_proj_run_job[i][2])
        else:
            comp_proj_hash[comp_proj_run_job[i][0]] = {}
            comp_proj_hash[comp_proj_run_job[i][0]][comp_proj_run_job[i][1]] = []
            comp_proj_hash[comp_proj_run_job[i][0]][comp_proj_run_job[i][1]].append(comp_proj_run_job[i][2])
    print('comp proj hash', comp_proj_hash)

    #update sheets
    for proj in proj_hash:
        #print(proj)
        if proj in short_titles:
            print('project', proj)
            # #print(str(titles[i[1]]))
            sheet = client.open(titles[proj]).sheet1
            #grab all run numbers from [run] column
            col_num = sheet.col_values(4)
            # row = col.index(i[0]) + 1
            cell_list = []
                #print(cell_list)
                # cell = sheet.range('B{}'.format(row)+':'+'B{}'.format(row))
            #     cell[0].value = str(proj_hash[proj][run])
            #     cell_list.append(cell[0])
            #     #print(cell_list)
            #this has to be before next loop, cause alphabeticl cell update!!
            for run in proj_hash[proj]:
                #populate curr_job column
                row_num = col_num.index(run) + 1
                cell_list.append(Cell(row = row_num,
                                      col = 2,
                                      value = str(proj_hash[proj][run])))

            if proj in list(comp_proj_hash.keys()):
                #empty comp job numbers from curr_job col and populate to comp_job column
                for comp_run in comp_proj_hash[proj]:
                    print('inside comp run', comp_run)
                    row_num = col_num.index(comp_run) + 1
                    cell_list.append(Cell(row = row_num,
                                          col = 2,
                                          value = ''))
                    #add to comp list, do not replace it
                    comp_cell = sheet.range('C{}'.format(row_num)+':'+'C{}'.format(row_num))
                    comp_cell_value = comp_cell[0].value
                    comp_cell_list = comp_cell_value[1:-1].split(', ')
                    comp_cell_list = [int(x) for x in comp_cell_list]
                    comp_cell_list = comp_cell_list + comp_proj_hash[proj][comp_run]
                    print('comp list', comp_cell_list)
                    cell_list.append(Cell(row = row_num,
                                         col = 3,
                                         value = str(comp_cell_list)))

            print('before update', cell_list)
            sheet.update_cells(cell_list)

    #store current array in local file
    try:
        subprocess.check_output(dir_cmd, shell=True)
    except subprocess.CalledProcessError as e:
        fdir.mkdir(exist_ok=True, parents=True)
        # raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
    #write current array to file
    f = open(fpath, 'wb')
    pickle.dump(proj_run_job, f)
    f.close()
    # print('File Saved!')
#if there is nothing currently running
else:
    print('inside not running')
    fpath = Path.home().joinpath('.simulation_builder/curr_status')
    fdir = Path.home().joinpath('.simulation_builder')
    dir_cmd = f'[ -d {fdir} ]'
    file_cmd = f'ls {fpath}'
    #bool to check if last array is available
    last_array_avail = True
    #check if anything previously stored
    try:
        subprocess.check_output(file_cmd, shell=True)
    except subprocess.CalledProcessError as e: #find an easier way to handle
        # fdir.mkdir(exist_ok=True, parents=True)
        #print('cannot find file')
        last_array_avail = False
        # raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
    # read in last stored array
    if last_array_avail:
        pickle_in = open(fpath, 'rb')
        last_proj_run_job = pickle.load(pickle_in)
        #print('load successful!')
        #print(last_proj_run_job)
        #all jobs have completed
        #to store completed jobs
        comp_proj_run_job = last_proj_run_job
        comp_proj_hash = {}
        for i in range(0,len(comp_proj_run_job)):
            if comp_proj_run_job[i][0] in comp_proj_hash:
                if comp_proj_run_job[i][1] in comp_proj_hash[comp_proj_run_job[i][0]]:
                    comp_proj_hash[comp_proj_run_job[i][0]][comp_proj_run_job[i][1]].append(comp_proj_run_job[i][2])
                else:
                    comp_proj_hash[comp_proj_run_job[i][0]][comp_proj_run_job[i][1]] = []
                    comp_proj_hash[comp_proj_run_job[i][0]][comp_proj_run_job[i][1]].append(comp_proj_run_job[i][2])
            else:
                comp_proj_hash[comp_proj_run_job[i][0]] = {}
                comp_proj_hash[comp_proj_run_job[i][0]][comp_proj_run_job[i][1]] = []
                comp_proj_hash[comp_proj_run_job[i][0]][comp_proj_run_job[i][1]].append(comp_proj_run_job[i][2])
        #print(comp_proj_hash)
        #move previously running job numbers to completed column
        for proj in comp_proj_hash:
            #print(proj)
            if proj in short_titles:
                # #print(str(titles[i[1]]))
                sheet = client.open(titles[proj]).sheet1
                #grab all run numbers from [run] column
                col_num = sheet.col_values(4)
                # row = col.index(i[0]) + 1
                cell_list = []
                    #print(cell_list)
                    # cell = sheet.range('B{}'.format(row)+':'+'B{}'.format(row))
                #     cell[0].value = str(proj_hash[proj][run])
                #     cell_list.append(cell[0])
                #     #print(cell_list)
                    #empty comp job numbers from curr_job col and populate to comp_job column
                for comp_run in comp_proj_hash[proj]:
                    row_num = col_num.index(comp_run) + 1
                    cell_list.append(Cell(row = row_num,
                                          col = 2,
                                          value = ''))
                    comp_cell = sheet.range('C{}'.format(row_num)+':'+'C{}'.format(row_num))
                    comp_cell_value = comp_cell[0].value
                    comp_cell_list = comp_cell_value[1:-1].split(', ')
                    comp_cell_list = [int(x) for x in comp_cell_list]
                    comp_cell_list = comp_cell_list + comp_proj_hash[proj][comp_run]
                    print('comp list', comp_cell_list)
                    cell_list.append(Cell(row = row_num,
                                         col = 3,
                                         value = str(comp_cell_list)))

            sheet.update_cells(cell_list)
        #no current array to store, so remove pickle file
        rmv_file_cmd = f'rm {fpath}'
        try:
            subprocess.check_output(rmv_file_cmd, shell=True)
        except subprocess.CalledProcessError as e:
            #fdir.mkdir(exist_ok=True, parents=True)
            print('unable to delete file')
            # raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
        # #write current array to file
        # f = open(fpath, 'wb')
        # pickle.dump(proj_run_job, f)
        # f.close()
        # print('File Saved!')
