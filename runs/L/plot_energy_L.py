import sys
import pathlib
import h5py
import matplotlib.pyplot as plt
from pathlib import Path

basedir = Path.cwd()
dfile = basedir.joinpath('scratch', 'kturb_run_L', 'timeseries', 'timeseries_s1', 'timeseries_s1_p0.h5')
print(dfile)
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
plot_dir = Path.cwd().joinpath('plots')
print(plot_dir)
plot_dir.mkdir(exist_ok=True, parents=True) 
plt.savefig('plots/energy.png')

