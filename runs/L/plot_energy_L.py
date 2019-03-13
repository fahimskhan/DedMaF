import sys
import pathlib
import h5py
import matplotlib.pyplot as plt
from pathlib import Path

from glob import glob

basedir = Path.cwd()
datadir = basedir.joinpath('scratch', 'kturb_run_L', 'timeseries', 'timeseries_s1').glob('**/*')
files = [str(x) for x in datadir if x.is_file()]
print(files)
print('--------------------')
# dfile = basedir.joinpath('scratch', 'kturb_run_L', 'timeseries', 'timeseries_s1', 'timeseries_s1_p0.h5')
# print(dfile)


plot_dir = Path.cwd().joinpath('plots')
plot_dir.mkdir(exist_ok=True, parents=True)

def make_plot(filename):
    data = h5py.File(str(filename), "r")
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
    plt.savefig('plots/energy_{}.png'.format(i))

for i in range(0, len(files)):
    make_plot(i)
