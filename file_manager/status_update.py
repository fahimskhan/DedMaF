import gspread
from oauth2client.service_account import ServiceAccountCredentials
import configparser
from pathlib import Path
import os, errno, textwrap, subprocess
from shutil import copyfile
import logging
# import pickle


cmd = 'squeue | grep "fkhan" | grep -o "run._..."'
result = subprocess.check_output(cmd, shell=True)
jobs = str(result, 'utf-8').split('\n')[:-1]
# ind_jobs = [x[3:].split('_') for x in jobs]
ind_jobs = [tuple(x[3:].split('_')) for x in jobs]
ind_jobs = set(ind_jobs)  # store as a set to handle possible duplicates

# print(ind_jobs)

logging.debug('making connections')
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)
# service = discovery.build('drive', 'v3', credentials=creds)
# list = service.drive().list()
#pass in name of the spreadsheet to client.open (case sensitive)
logistics_sheet = client.open("Logistics").sheet1
full_titles = logistics_sheet.row_values(4)[-1].split(',')
full_titles = [x.strip() for x in full_titles]
short_titles = [x.strip()[:3] for x in full_titles]
titles = {}
for i in range(0,len(short_titles)):
    titles[short_titles[i]] = full_titles[i]

# set `status` to NULL by default

for title in full_titles:
    sheet = client.open(title).sheet1
    lastIndex = len(sheet.get_all_values())
    for i in range (2,lastIndex+1):
        cell_list = sheet.range('A{}'.format(i)+':'+'A{}'.format(i))
        cell_list[0].value = ''
        sheet.update_cells(cell_list)

for i in ind_jobs:
    # print(i[1])
    if i[1] in short_titles:
        # print(str(titles[i[1]]))
        sheet = client.open(titles[i[1]]).sheet1
        col = sheet.col_values(2)
        row = col.index(i[0]) + 1
        cell_list = sheet.range('A{}'.format(row)+':'+'B{}'.format(row))
        cell_list[0].value = 'running...'
        sheet.update_cells(cell_list)

to_path = '/home/fkhan/simulation_builder/file_manager/temp.pickle'
# file_text = '\n'.join(['{},{}'.format(u, v) for (u, v) in ind_jobs])


# pickle_jar = open(to_path, "wb")
# pickle.dump(ind_jobs, pickle_jar)
# pickle_jar.close()
