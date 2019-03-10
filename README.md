# Simulation Builder/Management Software

## Usage:

## Step 1: (Clone repo)
#### Clone/Download git repo on your desired machine (local or leavitt)

## Step 2: (Set location for builds)
#### Navigate to file_manager/directory.cfg file.  Under the [Paths] section, make sure that base_dir points to the desired location (path) for your dedalus simulations.  Do not include home directory at the beginning of this path.  

#### For Example, base_dir = viscoturbulence/runs will place builds in /home/rfeldman/viscoturbulence/runs for a user named rfeldman.  

## Step 3: (Set location for copy)
#### Inside directory.cfg file, set copy_dir equal to path of git repo.  The reason we need to set this is to set the path to our symlink files that we will use to run deadalus simualtions  

#### For example, copy_dir = simulation_builder will work if simulation_builder is your top level directory.  

## Step 4: (Dependencies and packages)
#### There are a number of Dependencies needed in order to use this package.  Activate a conda environment using:

#### $conda env create -f environment.yml
#### $conda activate test

#### After you've activated the environment check to see that the correct version of python is installed.  $python = 3.6.5

## Step 5: (Create Simulations)
#### Go to the spreadsheet: https://docs.google.com/spreadsheets/d/1TOUPNYog7RITssPil9atp5nwdF_UQOnpU_FCMGXQKY0/edit#gid=0
#### Fill out parameters accordingly.  Note that parameters correspond to attributes on Parameters() object inside of file_manager/read_parameters.py
#### Navigate to file_manager and run:

## $python main.py

#### To verify if the build worked, navigate to simulation_builder/runs  You should see the name of the folder that corresponds with the identifier on the google sheet

## Step 6: (Repeat)
#### Repeat for different parameters and keep track of builds
