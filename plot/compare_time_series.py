# ------------------- #
# Compare time series #
# ------------------- #
import warnings
warnings.simplefilter("ignore")
from fun_gen import *
from fun_io import *
import sys,os,argparse

import numpy as np
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdates
import datetime as dt
from datetime import datetime
from matplotlib.ticker import FormatStrFormatter,StrMethodFormatter,ScalarFormatter


# Get variable name
var = sys.argv[1]
typ = sys.argv[2]

# Get configs name
l = []
for i in range(3,10):
  try : 
    l.append(sys.argv[i])
  except :
    pass

# Plot data
# ---------

# Init fig

load_config(l[0])
from fun_gen import *
fig,ax = plt.subplots(1,1,figsize=(float(fig_tsx), float(fig_tsy)))


# Loop on config
for config in l:

   # Load config
   load_config(config)
   from fun_gen import *


   # Load data
   if typ == "mean" :
     data = np.loadtxt(diagdir+'/'+config+'/TIME_SERIES/time_series_'+var+'.dat')
   elif typ == "point" :
     data = np.loadtxt(diagdir+'/'+config+'/TIME_SERIES/time_series_'+var+'_'+str(px)+'_'+str(py)+'.dat')



   # Convert date
   for i in range(0,data.shape[0]):

      d = dt.datetime.fromordinal(int(data[i,0]))
      s = d.strftime('%m-%d')
      j = datetime.strptime('1999-'+s,'%Y-%m-%d').toordinal()
      data[i,0] = j


   plt.plot(data[:,0],data[:,1],marker='o',linestyle='-',label=config)

vname, ftag, cmap, islog, vmod, vmin, vmax, label, units\
      = load_variable(config,var)

plt.ylabel(label+' ('+units+')')

ax.yaxis.set_minor_formatter(FormatStrFormatter('%.2f'))
ax.tick_params(axis='both', which='minor', labelsize=tck_size_ts)

# Format axes
loc = mdates.AutoDateLocator()
ax.xaxis.set_major_locator(loc)
ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(loc))

plt.legend()   
plt.show()
plt.close()





 




 











