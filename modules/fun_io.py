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
from netCDF4 import Dataset



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

  # Get calling function
  curframe = inspect.currentframe()
  calframe = inspect.getouterframes(curframe, 2)
  fun_call = calframe[1][3]

  # Do not crop if loaded by load_config
  if fun_call != 'load_config':
     from fun_gen import ibmin,ibmax,\
                         jbmin,jbmax\

  #try :
  if 1==1:
    search = outdir+'/*TEMP*.nc'
    ds = xr.open_dataset(glob(search)[0])

    lon = np.array(ds['longitude'])
    lat = np.array(ds['latitude'])
    levels = np.array(ds['depth'])
    ds.close()

    if fun_call != 'load_config':
       lon = lon[ibmin:ibmax]
       lat = lat[jbmin:jbmax]


  #except Exception as e :
  #  file_error(e,search,inspect.currentframe().f_code.co_name)

  return lon,lat,levels


# ----------------- #
# Load 2D variables #
# ----------------- #
def get_var_2D(fname,var,hour,lev):

  from fun_gen import ibmin,ibmax,\
                      jbmin,jbmax

  try :
    ds = xr.open_dataset(fname)
    arr = ds[var][hour,int(lev),jbmin:jbmax,ibmin:ibmax].squeeze()
    ds.close()

  except Exception as e :
    file_error(e,search,inspect.currentframe().f_code.co_name)

  return arr


# ------------------ #
# Load 2D satellites #
# ------------------ #
def get_sat_2D(fname,var):

  try :
    ds = xr.open_dataset(fname)
    arr = ds[var][:,:].squeeze()
    ds.close()

  except Exception as e :
    file_error(e,fname,inspect.currentframe().f_code.co_name)

  return arr


# -------------------- #
# Vertical integration #
# -------------------- #
def get_integre_2D(fname,var,levels,hour):

  from fun_gen import ibmin,ibmax,\
                      jbmin,jbmax

  # Load model data
  ds = xr.open_dataset(fname)
  arr = np.array(ds[var][hour,:,jbmin:jbmax,ibmin:ibmax].squeeze())
  ds.close()

  # Compute thickness of levels
  thick = np.zeros(levels.shape[0])
  tot = 0
  for l in range(0,levels.shape[0]):
    thick[l] = (levels[l]-tot)*2 
    tot += thick[l]

  #lmax = 10
  lmax = 6
  tot = np.sum(thick[0:lmax])

  # Integrate values
  coeff_att = 0.03

  att = arr[0,:,:].copy().squeeze()
  att[:] = 0

  iarr = arr[0,:,:].copy().squeeze()
  iarr[:] = 0

  for l in range(0,lmax):

     tmp = np.array(arr[l,:,:])

     idx = np.where(np.isnan(tmp))
     tmp[idx] = 0.

     corr = np.ones([att.shape[0],att.shape[1]])-coeff_att*att
     corr[np.where(corr<0)] = 0

     iarr[:] += tmp*thick[l]*corr

     att = att + tmp*thick[l]

  iarr[iarr==0.] = np.nan
  iarr = iarr*0.05#/tot

  return iarr
    


# ----------------- #
# Load 3D variables #
# ----------------- #
def get_var_3D(fname,hours,var,**kargs):

  from fun_gen import ibmin,ibmax,\
                      jbmin,jbmax

  try :

    dmn = kargs['domain']

    idz = np.array(dmn[0][0]) 
    idy = np.array(dmn[1][0]) 
    idx = np.array(dmn[2][0]) 
  except:
    pass

  try:

    #ds = xr.open_dataset(fname)
    ds = Dataset(fname,format='NETCDF4-CLASSIC')

    # Reduce domain
    try:
      arr = ds[var][hours,idz,idy,idx]
      arr = arr.squeeze()

    except:
      arr = ds[var][hours,:,jbmin:jbmax,ibmin:ibmax].squeeze()

    ds.close()

  except Exception as e:
    file_error(e,fname,inspect.currentframe().f_code.co_name)

  return arr


# ------------------------ #
# Get value from 3D fields #
# ------------------------ #
def get_model_val_3d(fname,hours,var,lon_mod,lat_mod,lev_mod,lon,lat,depth):

  start = time.time()

  from fun_gen import itp_meth,dump

  # Load file
  dump = float(dump)
  idx = np.where( (lon_mod > lon[0]-dump) & (lon_mod < lon[0]+dump) )
  idy = np.where( (lat_mod > lat[0]-dump) & (lat_mod < lat[0]+dump) )
  idz = np.where( (lev_mod < depth[-1]+800))

  var3d = np.array(get_var_3D(fname,hours,var,domain=[idz,idy,idx]))

  # Prepare interpolation
  LAT,LEV,LON = np.meshgrid(lat_mod[idy],lev_mod[idz],lon_mod[idx]) 
  LAT,LON,LEV = LAT.flatten(),LON.flatten(),LEV.flatten()

  var3d = var3d.flatten()

  var3d[np.where(var3d > 9999) ] = np.nan

  # Interpolation
  val = griddata((LON,LAT,LEV),var3d,(lon,lat,depth),method=itp_meth)

  end = np.round(time.time()-start,decimals=2)

  print('Interpolation done for [',lon.shape[0],'] data in',end,'sec',end='\r')

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



def write_nc(fname,time,lon,lat,var,data,long_name,units):


  # Open file
  dataset = Dataset(fname,'w',format='NETCDF4_CLASSIC')

  # Create dimension
  dlon = dataset.createDimension('longitude',lon.shape[0])
  dlat = dataset.createDimension('latitude',lat.shape[0])
  dlat = dataset.createDimension('time',1)

  # Create variables & set attributes
  vlon = dataset.createVariable('longitude',np.float32,('longitude'))
  vlon.units = "degrees east"
  vlon.long_name = "longitude"
  vlon[:] = lon

  vlat = dataset.createVariable('latitude',np.float32,('latitude'))
  vlat.units = "degrees north"
  vlat.long_name = "latitude"
  vlat[:] = lat

  vtime = dataset.createVariable('time',np.float32,('time'))
  vtime.units = "hours since 1900-01-01 00:00:00"
  vtime.calendar = "gregorian"

  vtime[:] = time


  # Write variable to NetCDF
  # ------------------------
  vdata = dataset.createVariable(var,np.float32,('time','latitude','longitude'),fill_value=-9999)
  vdata.units = units
  vdata.long_name = long_name
  vdata[:] = data

  print('')
  print('[FILE SAVED] '+fname+'\n')
  dataset.close()

















