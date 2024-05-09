# --------------#
# Functions I/O #
# --------------#
import xarray as xr
import numpy as np
import datetime as dt
import os
from glob import glob
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import keyword
import inspect
import time


# ------------ #
# Get filename #
# ------------ #
def get_filename(jd,ftag):

  from fun_gen import outdir

  # Get filename
  dobj = dt.datetime.fromordinal(jd)
  dtag = dobj.strftime('%Y%m%d')
 
  search = outdir+'/'+dtag+'_h-OGS--'+ftag+'-MITgcmBFM-pilot8-b*_fc-v01.nc' 

  try : 
    fname = glob(search )[0]

  except Exception as e :
    file_error(e,search,inspect.currentframe().f_code.co_name)

  return fname,dtag


# ------------ #
# Load lon/lat #
# ------------ #
def load_coords():

  from fun_gen import outdir

  try :
    ds=xr.open_dataset(glob(outdir+'/*TEMP*.nc')[0])
    lon=np.array(ds['longitude'])
    lat=np.array(ds['latitude'])
    levels=np.array(ds['depth'])
    ds.close()

  except Exception as e :
    file_error(e,search,inspect.currentframe().f_code.co_name)

  return lon,lat,levels


# ----------------- #
# Load 2D variables #
# ----------------- #
def get_var_2D(fname,var,lev):

  try :
    ds = xr.open_dataset(fname)
    arr = ds[var][23,int(lev),:,:].squeeze()
    ds.close()

  except Exception as e :
    file_error(e,search,inspect.currentframe().f_code.co_name)

  return arr

# ----------------- #
# Load 3D variables #
# ----------------- #
def get_var_3D(fname,var,**kargs):

  dmn = kargs['domain']

  idz = np.array(dmn[0][0]) 
  idy = np.array(dmn[1][0]) 
  idx = np.array(dmn[2][0]) 

  try:

    ds = xr.open_dataset(fname)
    if dmn:
      arr = ds[var][23,idz,idy,idx].squeeze()

    else:
      arr = ds[var][23,:,:,:].squeeze()

    ds.close()

  except Exception as e:
    file_error(e,fname,inspect.currentframe().f_code.co_name)

  return arr


# ------------------------ #
# Get value from 3D fields #
# ------------------------ #
def get_model_val_3d(fname,var,lon_mod,lat_mod,lev_mod,lon,lat,depth):

  start = time.time()

  from fun_gen import itp_meth,dump

  # Load file
  dump = float(dump)
  idx = np.where( (lon_mod > lon[0]-dump) & (lon_mod < lon[0]+dump) )
  idy = np.where( (lat_mod > lat[0]-dump) & (lat_mod < lat[0]+dump) )
  idz = np.where( (lev_mod < depth[-1]+800))

  var3d = np.array(get_var_3D(fname,var,domain=[idz,idy,idx]))
  
  # Prepare interpolation
  LAT,LEV,LON = np.meshgrid(lat_mod[idy],lev_mod[idz],lon_mod[idx]) 
  LAT,LON,LEV = LAT.flatten(),LON.flatten(),LEV.flatten()

  var3d = var3d.flatten()

  # Interpolation
  val = griddata((LON,LAT,LEV),var3d,(lon,lat,depth),method=itp_meth)

  end = np.round(time.time()-start,decimals=2)

  print('Interpolation done for [',lon.shape[0],'] data in',end,'sec')

  return val



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




# ---------- #
# File error #
# ---------- #
def file_error(e,fname,func):

   print(e,'\n')
   print('=> in',func,':')
   print('Error processing file',fname)

   if not os.path.exists(fname):
     print('File not found')

   else:
     print('Loading error')

   exit(1)


# ----------------- #
# Load DYFAMED data #
# ----------------- #
def load_dyfamed(year,var):

  fname = 'dyfamed-mooring/OS_DYFAMED_'+str(year)+'_D_TSCTD.nc'
  ds = xr.open_dataset(fname)
  time = ds['TIME'].values
  depth  = ds['DEPTH'].values
  data = ds[var].values
  ds.close()
 

  print('File',fname,'loaded')
  return time,depth,data



# --------------- #
# Load MOOSE data #
# --------------- #
def load_moose(year,var):

  fname = glob('data/'+year+'_*.nc')[0]
  ds = xr.open_dataset(fname)
  time = ds['TIME'].values
  depth  = ds['PRES'].values
  lon  = ds['LONGITUDE'].values
  lat  = ds['LATITUDE'].values
  data = ds[var].values
  ds.close()


  # Convert date
  jdlist = []
  for i in range(0,time.shape[0]):

    time = np.array(time,dtype=str)
    dstr = time[i].split(' ')[0]
    jdlist.append(dt.datetime.strptime(dstr,'%Y-%m-%d').toordinal())


  return jdlist,depth,lon,lat,data
  











