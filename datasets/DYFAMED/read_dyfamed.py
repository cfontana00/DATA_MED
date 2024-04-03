#####################################
# Routine reading DYFAMED data      #
# and interpolating model variables #
#####################################

import numpy as np
from fun_gen import *
from fun_io import *
import sys,os
import xarray as xr


# Get args
# --------
config = sys.argv[1]  # Configuration name
var = sys.argv[2]     # Variable name


# Load config file
# ----------------
load_config(config)
from fun_gen import *



# Create diagnostic arborescence
os.system('mkdir -p '+diagdir)
os.system('mkdir -p '+diagdir+'/'+config)
savedir = diagdir+'/'+config+'/DYFAMED'
os.system('mkdir -p '+savedir)

print('create_arbo !!!!')
exit()


# --------- #
# Load data #
# --------- #
init = True
for year in range(2017,2022):
   fname = 'dyfamed-mooring/OS_DYFAMED_'+str(year)+'_D_TSCTD.nc'
   ds = xr.open_dataset(fname)




# Loop on variables
# ------------------
loaded = 'none'

for var in ['thetao','o2','so']:

  # Name correspondance
  if var == 'o2':
    dyf_var = 'DOX2'

  elif var == 'so':
    dyf_var = 'PSAL'

  elif var == 'thetao':
    dyf_var = 'TEMP'

  # Loop on days
  # ------------
  for jd in range(jdini-700,jdend+1+700):

    # Load data
    d = dt.datetime.fromordinal(jd)
    d.strftime('%Y')
    
    if loaded != year:
      time,depth,var = load_dyfamed(year,dyf_var)

      # Convert date
      jdtime=[]
      for t in time:
         t = dt.datetime.utcfromtimestamp(t.tolist()/1e9)
         jdtime.append(t.toordinal())

      loaded = year

    # Daliy mean data
    jdist = np.unique(jdtime)

    # Loop on depth
    print('DEPTH')
    for d in depth:
      print(d)
    exit()

    '''    
    mean=[]
    for j in jdlist:
      idx = np.where(jdtime == j)
      mean.append
    '''

    
  






