#This program cancels existing cronjob

#import libraries and modules
from crontab import CronTab
from pathlib import Path

#find home directory path
home_dir = str(Path.home())
#extract username from home directory path
user_name = home_dir.split('/')[-1]

#open crontab
cron = CronTab(user=user_name)
#remove all jobs
cron.remove_all()
#write to crontab
cron.write()
