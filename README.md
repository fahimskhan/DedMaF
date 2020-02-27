# Simulation Builder/Management Software

## Usage:

## Step 1: (Clone repo)
#### Clone/download this git repo on your desired machine (local or leavitt). It is very important that this program is placed in the directory /home/`user_name`. Otherwise the program will not run. This is because the program is automatically run by cronjob which needs to know the full path of the program.

#### If using leavitt the following command needs to be executed first.

#### $module load slurm intel-mpi hdf5 ffmpeg

#### It is strongly recommended to place the command in your .bashrc file.

## Step 2: (Set location for builds)

#### By default all runs, read from a particular spreadsheet, are placed in /home/`user_name`/projects/`project_name`/runs. And this is done for all projects. 

#### However, if you wish to specify a cerntain build location, do the following. Navigate to /simulation_builder/file_manager/directory.cfg file.  Under the [Dir_paths] section, make sure that base_dir points to the desired location (path) for your dedalus simulations.  Do not include home directory at the beginning of this path.  

#### For Example, base_dir = viscoturbulence will place builds in /home/`user_name`/viscoturbulence/runs. 

## Step 3: (Set location for copy)

#### If projects are placed in the same directory as simulation_builder (/home/`user_name`) they are automatically read.

#### If projects are placed in a different directory, do the following. Inside directory.cfg file, set copy_dir equal to path of git repo.  The reason we need to set this is to set the path to our symlink files that we will use to run dedalus simualtions  

#### For example, copy_dir = projects tells the program to look for a project in /home/`user_name`/projects.

## Step 4: (Dependencies and packages)
#### There are a number of dependencies needed in order to use this program.  Navigate to simulation_builder and activate a conda environment using:

#### $conda env create -f environment.yml
#### $conda activate test

#### In order for the program to run 'test' environment has to be always kept activated. However if you exit out of leavitt, when you log back in, the environment will be reset to 'base'. To avoid this, place the contents of bashrc.txt in your .bashrc. Once you do this, 'test' environment will be automatically activated upon each login.

#### After you've activated the environment check to see that the correct version of python is installed.  

#### $python -V

### Version should be 3.6.5

## Step 5: (Create client_secret.json)

#### In order for this program to be able to read and write to your google sheets you will need to create a service account with Google Drive API. To do so, follow this tutorial:  

#### https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html

#### Once you have successfully downloaded a .json file containing your keys, rename the file 'client_secert.json' and place in /simulation_builder/file_manager

## Step 7 (Copy sheet template):

#### Follow link:

#### `link will be inserted later` 

#### and copy sheet template. Make sure name of spreadsheet corresponds to the project name. Follow instructions in sheets. Do not forget to share your copied template sheet with client_email from inside client_secret.json. The program can only read worksheets that have been shared with client_email.

## Step 6 (Submit cronjob):

#### Navigate to /simulation_builder and run the following command:

#### $python create_cronjob.py

#### This submits a cronjob that runs main.py inside file_manager every sixty seconds, which reads runs from sheets and updates status of running/completed jobs.

## Step 7 (Try it!)

#### Input the row number of the run you wish the program to read in worksheet 1 of your spreadsheet. After a while you will see a new directory made /home/projects/`project_name`/runs/`run_letters`. Submit a job using the following command:

### $sbatch r`run_letters_project_name`.sh

### The job number of the submitted job will appear in worksheet 2 of your spreadsheet under appropriate column.
