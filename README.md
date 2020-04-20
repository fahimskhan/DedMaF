# Dedalus Management Framework (DedMaF)

## Usage:

## Step 1 (Clone GitHub repository):
#### Clone or download this git repository on your desired machine (local or Leavitt).  It is very important that this program is placed in thedirectory /home/`username`.  Otherwise the program will not run.  This is because the programis automatically run by Cron which needs to know the full path of the program.

#### If using Leavitt, the following command needs to be executed first.

#### $module load slurm intel-mpi hdf5 ffmpeg

#### It is strongly recommended to place the command in your .bashrc file, so you do not have toload Slurm upon every login.

## Step 2 (Set location for builds or runs - optional):

#### By default all runs, read from a particular spreadsheet, are placed in /home/`user_name`/projects/`project_name`/runs. And this is done for all projects. 

#### However, if you wish to specify a cerntain build location, do the following. Navigate to /DedMaF/file_manager/directory.cfg file.  Under the [Dir_paths] section, make sure that base_dir points to the desired location (path) for your dedalus simulations.  Do not include home directory at the beginning of this path.  

#### For Example, base_dir = viscoturbulence will place builds in /home/`user_name`/viscoturbulence/runs. 

## Step 3 (Set location for symlink files - optional):

#### If projects are placed in the same directory as simulation_builder (/home/`user_name`) they are automatically read.

#### If projects are placed in a different directory, do the following. Inside directory.cfg file, set copy_dir equal to path of git repo.  The reason we need to set this is to set the path to our symlink files that we will use to run dedalus simualtions  

#### For example, copy_dir = projects tells the program to look for a project in /home/`user_name`/projects.

#### Note: The symlink file(s), parameters file, run script and any other project files need toexist exactly below the project folder.  If there are sub-folders inside the project folder containingthe required files, DedMaF will not be able to read the files.  This is to ensure the consistencyand scalability of all Dedalus projects.

## Step 4 (Install or activate dependencies and packages):

#### There are a number of dependencies needed in order to use this program. First install conda if you have not already done so:

#### https://docs.conda.io/projects/conda/en/latest/user-guide/install/ 

#### Then, navigate to DedMaF and activate a conda environment using:

#### $conda env create -f environment.yml
#### $conda activate test

#### In order for the program to run 'test' environment has to be always kept activated. However if you exit out of leavitt, when you log back in, the environment will be reset to 'base'. To avoid this, place `source activate test` at the bottom of your .bashrc accessed from root directory. Once you do this, 'test' environment will be automatically activated upon each login.

#### After you've activated the environment check to see that the correct version of python is installed.  

#### $python -V

#### Version should be 3.6.5

## Step 5 (Create client_secret.json file):

#### In order for this program to be able to read and write to your google sheets you will need to create a service account with Google Drive API. To do so, follow this tutorial:  

#### https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html

#### Once you have successfully downloaded a .json file containing your keys, rename the file 'client_secert.json' and place in /DedMaF/file_manager

## Step 6 (Copy sheet template):

#### Follow link:

#### https://docs.google.com/spreadsheets/d/1VC85u7PdYtjve0Cbon9LMQBcNUWSnaKg3dCvFrF4IQs 

#### and copy sheet template. Make sure name of spreadsheet corresponds to the project name. Follow instructions in sheets. Do not forget to share your copied template sheet with client_email from inside client_secret.json. The program can only read worksheets that have been shared with client_email.

## Step 7 (Create {and remove} 'Cron Job'):

#### Navigate to /DedMaF and run the following command:

#### $python create_cronjob.py

#### This submits a 'Cron Job' that runs main.py inside file_manager every sixty seconds, which reads runs from sheets and updates status of running/completed jobs.

#### To cancel the 'Cron Job' run the command:

#### $python remove_cronjob.py

## Step 8 (Submit runs):

#### Input the row number of the run you wish the program to read in worksheet 2 of your spreadsheet. After a while you will see a new directory made /home/projects/`project_name`/runs/`run_letters`. Submit a job using the following command:

#### $sbatch r`run_letters`__`project_name`.sh

#### The job number of the submitted job will appear in worksheet 1 of your spreadsheet under appropriate column.

## Step 9 (Repeat for different projects):

#### Start process from Step 6.
