# --------------#
# Functions I/O #
# --------------#
import xarray as xr
import numpy as np
import datetime as dt
from glob import glob
import matplotlib.pyplot as plt

# ------------ #
# Load lon/lat #
# ------------ #
def load_coords():

  from fun_gen import outdir

  ds=xr.open_dataset(glob(outdir+'/*TEMP*.nc')[0])
  lon=np.array(ds['longitude'])
  lat=np.array(ds['latitude'])
  levels=np.array(ds['depth'])
  ds.close()

  return lon,lat,levels


# ----------------- #
# Load 2D variables #
# ----------------- #
def get_var_2D(fname,var,lev):

  ds = xr.open_dataset(fname)
  arr = ds[var][23,int(lev),:,:].squeeze()
  ds.close()

  return arr

# ----------------- #
# Load 3D variables #
# ----------------- #
def get_var_3D(fname,var):

  ds = xr.open_dataset(fname)
  arr = ds[var][23,:,:,:].squeeze()
  ds.close()

  return arr


# ------------ #
# Get filename #
# ------------ #
def get_filename(jd,ftag):

  from fun_gen import outdir

  # Get filename
  dobj = dt.datetime.fromordinal(jd)
  dtag = dobj.strftime('%Y%m%d')
  fname = glob(outdir+'/'+dtag+'_h-OGS--'+ftag+'-MITgcmBFM-pilot8-b*_fc-v01.nc' )[0]

  return fname,dtag


# ----------- #
# Save figure #
# ----------- #
def savefig(fout):

  from fun_gen import tight,fig_res

  if tight == "True" :
    plt.savefig(fout,bbox_inches='tight',dpi=int(fig_res))     

  else:
    plt.savefig(fout,dpi=int(fig_res))     

  print('[SAVED FIG] '+fout)






