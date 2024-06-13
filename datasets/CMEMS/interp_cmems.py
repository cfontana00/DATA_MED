################################
# Routine to interpolate CMEMS #  
#   products on model grid     #
################################

import warnings
warnings.simplefilter("ignore")
from fun_gen import *
from fun_io import *
import os
import sys
import argparse
import datetime as dt
from netCDF4 import Dataset
from scipy.interpolate import griddata
import numpy as np
from numpy import array


def argument():
    parser = argparse.ArgumentParser(description = '',formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(   '--config', '-c',
                                type = str,
                                required = True,
                                help ='Configuration name'
                                )
    parser.add_argument(   '--variable',"-v",
                                type = str,
                                required = True,
                                help = 'variable : thetao or chl')
    return parser.parse_args()


# Get args
# --------
args = argument()
config = args.config  # Configuration name
var = args.variable   # Variable name



# Load parameters
# ---------------
load_config(config)
from fun_gen import *

datadir = diagdir+'/'+config+'/CMEMS/data'
odir = diagdir+'/'+config+'/CMEMS/'+var+'/ITP_NC'
os.system('mkdir -p '+odir)

# Load variable parameters
# ------------------------
vname, ftag, cmap, islog, vmod, vmin, vmax, label, units\
        = load_variable(config,var)


# Load coordinates
# ----------------
lon_mod,lat_mod,lev = load_coords()
LON_MOD,LAT_MOD = np.meshgrid(array(lon_mod),array(lat_mod))



# Load CMEMS parameters
# ---------------------
pars = np.loadtxt('../../config/cmems_'+config+'.dat',dtype=str)

# Loop on variables
for par in pars:
  if par[0] == var:
    break

ds_id = par[1]
cvar = par[2]


# Load CMEMS file
ds = Dataset(datadir+'/'+ds_id+'.nc')

lon = array(ds['longitude'])
lat = array(ds['latitude'])


LON,LAT = np.meshgrid(lon,lat)
LON,LAT = LON.flatten(),LAT.flatten()

# Loop on days 
#------------
i = 0
for jd in range(jdini,jdend+1):

  # Get CMEMS data
  data = array(ds[cvar][i,:,:]).squeeze().flatten()
  # => /!\ Ensure that same dates were used for downloads !!!
  data[np.where(data < -99) ] = np.nan


  # Interpolate
  idata = griddata((LON,LAT),data.T,(LON_MOD,LAT_MOD),method='linear')  


  # Save file
  # ---------
  dori = dt.datetime(1900,1,1).toordinal()
  time = np.array([(jd - dori )*24])

  d = dt.datetime.fromordinal(jd)
  dstr = d.strftime('%Y%m%d')

  fname = odir+'/'+var+'_'+dstr+'.nc'
  write_nc(fname,time,lon_mod,lat_mod,var,idata,label,units)

  i = i+1

 
ds.close()

