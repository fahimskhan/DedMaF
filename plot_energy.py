import sys
import pathlib
import h5py
import matplotlib.pyplot as plt

from pathlib import Path
from glob import glob
import os

result=os.path.split(os.getcwd())[1]

basedir = Path.cwd()
dfile = basedir.joinpath('scratch', 'kturb_run_{}'.format(result), 'timeseries', 'timeseries_s1.h5')

plot_dir = Path.cwd().joinpath('plots')
plot_dir.mkdir(exist_ok=True, parents=True)

data = h5py.File(str(dfile), "r")

t = data['scales/sim_time'][:]
KE = data['tasks/Ekin'][:,0,0]
#sigma = data['tasks/Σ'][:,0,0]
#sigma = data['tasks/Sigma'][:,0,0]
plt.subplot(121)
plt.plot(t, KE)
plt.xlabel("time")
plt.ylabel("Kinetic energy")
plt.subplot(122)
plt.plot(t, KE, 'x-')
plt.xlim(0,500)
plt.xlabel("time")
plt.ylabel("Kinetic energy")

# plt.plot(t, sigma)
# plt.xlabel("time")
# plt.ylabel(r"$\Sigma$")

plt.savefig('plots/energy.png')

