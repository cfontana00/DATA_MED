# ------------------------- #
# Routine to get Argo data  #
# ------------------------- #
import warnings
warnings.simplefilter("ignore")
import numpy as np

from fun_gen import *
from fun_io import *
import sys,os
import datetime as dt
import xarray as xr
import datetime as dt


# Get args
# --------
config = sys.argv[1]  # Configuration name


# Load config file
# ----------------
load_config(config)
from fun_gen import *

# Load coordinates
# ----------------
lon_mod,lat_mod,lev_mod=load_coords()


# Load data
# ---------
savedir = diagdir+'/'+config+'/ARGO'
ds = xr.load_dataset(savedir+'/argo.nc')

lat = ds['LATITUDE']
lon = ds['LONGITUDE']
time = ds['TIME']
num = ds['PLATFORM_NUMBER']
cyc = ds['CYCLE_NUMBER']
pres = ds['PRES_ADJUSTED']

time = np.array(time,dtype=str)

# Define profiles position
# ------------------------

lon_uni = np.unique(lon)
print(lon_uni.shape[0],'profiles found\n')

# Loop on profiles
# ----------------
for plon in lon_uni:

  # Get all indexes
  idx = np.where( lon == plon )

  for var in ['CHLA_ADJUSTED','PSAL_ADJUSTED','TEMP_ADJUSTED']:

    if var == 'CHLA_ADJUSTED':
       mod_var = 'chl'
    elif var == 'PSAL_ADJUSTED':
       mod_var = 'so'
    elif var == 'TEMP_ADJUSTED':
       mod_var = 'thetao'


    # Get current variable parameters
    vname, ftag, cmap, islog, vmod, vmin, vmax, label, units\
        = load_variable(config,mod_var)

    # Convert date
    ptime = []
    dstr = str(time[idx][0]).split('T')[0]
    jd = dt.datetime.strptime(dstr,'%Y-%m-%d').toordinal()

    # Get filename
    fname,dtag = get_filename(int(np.floor(jd)),ftag)

    print(fname,dtag)


    exit()













