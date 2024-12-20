# ------------------------- #
# Routine to get Argo data  #
# ------------------------- #
import warnings
warnings.simplefilter("ignore")

import numpy as np

from fun_gen import *
from fun_io import *
import sys,os,argparse
import datetime as dt

import argopy
from argopy import DataFetcher  
from argopy import ArgoIndex  
from argopy import ArgoNVSReferenceTables 
from argopy import ArgoColors 
from argopy.plot import scatter_map, scatter_plot 
argopy.reset_options()
argopy.clear_cache()
argopy.set_options(cachedir='cache_bgc')



def argument():
    parser = argparse.ArgumentParser(description = '',formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(   '--config', '-c',
                                type = str,
                                required = True,
                                help ='Configuration name'
                                )
    return parser.parse_args()


# Get args
# --------
args = argument()
config = args.config  # Configuration name


# Load config file
# ----------------
load_config(config)
from fun_gen import *

# Create diagnostic arborescence
os.system('mkdir -p '+diagdir)
os.system('mkdir -p '+diagdir+'/'+config)
savedir = diagdir+'/'+config+'/ARGO'
os.system('mkdir -p '+savedir)


# Load coordinates
# ----------------
lon_mod,lat_mod,lev_mod=load_coords()

lon_min,lon_max = np.amin(lon_mod),np.amax(lon_mod)
lat_min,lat_max = np.amin(lat_mod),np.amax(lat_mod)


# Get Argo data
# -------------
box = [lon_min, lon_max, lat_min, lat_max, 0, 300, date_ini, date_end]

f = DataFetcher(ds=argo_ds, mode='expert', params='all',
                parallel=True, progress=True, cache=False,
                chunks_maxsize={'time': 30},
               )


f = f.region(box).load()

ds = f.data
df = f.index


ds_profiles = ds.argo.point2profile()

# Save data
# ---------
tag=''
if argo_ds == 'bgc':
  tag = 'bio'

fname = savedir+'/'+tag+'argo.nc'
ds.to_netcdf(path=fname, mode='w', format=None, group=None, engine=None, encoding=None, unlimited_dims=None, compute=True, invalid_netcdf=False)

print('[SAVED]',fname)


