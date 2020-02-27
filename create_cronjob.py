#This program submits a new cronjob

#import libraries and modules
from crontab import CronTab
import os, errno, textwrap, subprocess
from pathlib import Path

#find home directory path
home_dir = str(Path.home())
#extract username from home directory path
user_name = home_dir.split('/')[-1]

#command to find path of python
python_path_cmd = 'which python'
#execute command
try:
    #store python path
    python_path = subprocess.check_output(python_path_cmd, shell=True)
    #convert python_path from bytes to string
    python_path = str(python_path, 'utf-8').split('\n')[0]
#if path not found
except subprocess.CalledProcessError as e:
    #print warning
    print('WARNING: Python path not found! Please make sure python is installed.')
    #raise error
    raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

#open crontab
cron = CronTab(user=user_name)
#define job
job = cron.new(command = f'{python_path} {home_dir}/simulation_builder/file_manager/main.py')
#define execution time
job.minute.every(1)
#write to crontab
cron.write()
