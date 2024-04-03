#####################################
# Routine reading DYFAMED data      #
# and interpolating model variables #
#####################################
import warnings
warnings.simplefilter("ignore")

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

# Create diagnostics arborescence
savedir = create_arbo(config,var,'MOOSE')

# Variable correspondance
if var == 'thetao':
  moose_var = 'TEMP'

loaded = 'none'

# Loop on days
print('Searching for correspondance with simulation dates ...')
for jd in range(jdini,jdend+1):

  # Load data
  d = dt.datetime.fromordinal(jd)
  year = d.strftime('%Y')

  if loaded != year:
    jdlist,depth,lon,lat,data = load_moose(year,moose_var)
    loaded = year
    print('Year =>',year)












