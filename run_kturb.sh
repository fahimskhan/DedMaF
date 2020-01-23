#!/usr/bin/bash
##SBATCH --ntasks-per-node=16
#SBATCH --time=5-0
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --distribution=cyclic:cyclic
#SBATCH --cpus-per-task=1

source /home/projects/AFDGroup/build/dedalus/bin/activate
result=${PWD##*/} 

date
mpirun -np 8 python3 kturb.py run_${result}.cfg
date
