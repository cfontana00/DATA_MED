##############################
# Plot satellite time series #
##############################


import warnings
warnings.simplefilter("ignore")
from fun_gen import *
from fun_io import *
import sys,os

import numpy as np
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")

import matplotlib.dates as mdates


# Get args
# --------
config=sys.argv[1]  # Configuration name
var=sys.argv[2]     # Variable name
sat=sys.argv[3]     # Dataset dir


# Get variables parameters
if var == 'chl':
  color = 'g'
elif var == 'thetao':
  color = 'orange'

vname, ftag, cmap, islog, vmod, vmin, vmax, label, units\
        = load_variable(config,var)

# Load CMEMS parameters
# ---------------------
pars = np.loadtxt('../config/cmems_'+config+'.dat',dtype=str)

# Loop on variables
for par in pars:
  if par[0] == var:
    break

ds_id = par[1]



# Load parameters
# ---------------
load_config(config)
from fun_gen import *


# Plot time series
# ----------------
fname = os.path.join(diagdir,config,sat,var,'ITP_NC/time_series.dat')
data = np.loadtxt(fname)

fig,ax = plt.subplots(1,1,figsize=(float(fig_tsx), float(fig_tsy)))

idx = np.where(data[:,3] > 0.2 ) # Keep only data with +10% cover

data = data[idx,:].squeeze()


# Tune dates
for i in range(0,data.shape[0]):
   data[i,0] = data[i,0] + - dt.datetime(1970,1,1).toordinal()


plt.plot(data[:,0],data[:,1],marker='o',linestyle='-',color=color,label='Model')

plt.plot(data[:,0],data[:,2],marker='s',linestyle=':',color=color,label='Data')

for d in data:
   #print(d[0]+0.3,d[1],str(d[3]*100)+'%')
   plt.text(d[0]+0.3,d[2],str(np.round(d[3]*100,decimals=1))+'%',fontsize=7)


plt.legend()

if islog:
  ax.set_yscale('log')

# Format axes
loc = mdates.AutoDateLocator()
ax.xaxis.set_major_locator(loc)
ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(loc))

plt.ylabel(label+' ('+units+')')
plt.title('Satellite '+sat+' / '+ds_id)

fname = fname.replace('dat',fig_fmt)

savefig(fname)

plt.close()

