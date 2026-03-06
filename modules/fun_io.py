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

  from fun_gen import domain,outdir,ftype,freq,date_ini

  dobj = dt.datetime.fromordinal(jd)
  dtag = dobj.strftime('%Y%m%d')

  # Get filename
  if ftype == 'netcdf':
   
    search = http+ '/' +outdir+'/'+dtag+'_h-OGS--'+ftag+'-MITgcmBFM-pilot8-b*_fc-v01.nc' 

    try : 
      fname = glob(search )[0]

    except Exception as e :
      file_error(e,search,inspect.currentframe().f_code.co_name)

  elif ftype == 'zarr':

      d = date_ini.replace('-','')
      fname = outdir+"/"+d+"-MER-MITgcmBFM-"+domain+"-fc-"+freq+"-v01.zarr"



  return fname,dtag


# ------------ #
# Load lon/lat #
# ------------ #
def load_coords():

  from fun_gen import outdir,maskfile

  # Get calling function
  curframe = inspect.currentframe()
  calframe = inspect.getouterframes(curframe, 2)
  fun_call = calframe[1][3]

  # Do not crop if loaded by load_config
  if fun_call != 'load_config':
     from fun_gen import ibmin,ibmax,\
                         jbmin,jbmax\

  # Try to load for outputs
  try :
    search = outdir+'/*TEMP*.nc'
    ds = xr.open_dataset(glob(search)[0])

  # Or load by mask 
  except:
    ds = xr.open_dataset(maskfile,engine="netcdf4")

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
def get_var_2D(jd,jdini,fname,var,hour,lev):

  from fun_gen import ibmin,ibmax,\
                      jbmin,jbmax,\
                      ftype,freq

  if 1 ==1:
  #try :
      
    ds = xr.open_dataset(fname,engine=ftype)
    
   
    if ftype == 'netcdf':  
      arr = ds[var][hour,int(lev),jbmin:jbmax,ibmin:ibmax].squeeze()

    elif ftype == 'zarr':
      if freq == 'hourly':
        rec = (jd-jdini)*24+hour
        arr = ds[var].squeeze()
        arr = arr[rec,int(lev),jbmin:jbmax,ibmin:ibmax].squeeze()

      elif freq == 'daily':
        rec = jd-jdini
        arr = ds[var].squeeze()
        arr = arr[rec,int(lev),jbmin:jbmax,ibmin:ibmax].squeeze()


      
    ds.close()
        
  #except Exception as e :
  #  file_error(e,search,inspect.currentframe().f_code.co_name)

  return arr


# ------------------ #
# Load 2D satellites #
# ------------------ #
def get_sat_2D(fname,var):

  from fun_gen import ftype

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
def get_integre_2D(jd,jdini,fname,var,levels,hour):

  from fun_gen import ibmin,ibmax,\
                      jbmin,jbmax,ftype 

  # Load model data
  ds = xr.open_dataset(fname,engine=ftype)
  arr = ds[var].squeeze()
  
  # WORK ONLY FOR DAILY NOW (TO CHANGE)
  rec = jd-jdini
  arr = arr[rec,:,jbmin:jbmax,ibmin:ibmax].squeeze()
  ds.close()

  arr = np.array(arr)

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
def get_var_3D(jd,jdini,fname,hours,var,called_by,**kargs):

  from fun_gen import ibmin,ibmax,\
                      jbmin,jbmax,ftype

  try :

    dmn = kargs['domain']

    idz = np.array(dmn[0][0]) 
    idy = np.array(dmn[1][0]) 
    idx = np.array(dmn[2][0]) 
  except:
    pass

  try:
    ds = xr.open_dataset(fname,engine=ftype)

    # Reduce domain
    try:

      rec = (jd-jdini)*24

      # Special case operational
      if called_by == 'compare_argo.py'\
        and ftype == 'zarr' \
        and var == 'chl' :
        rec = jd-jdini
  
      arr = ds[var][0,rec,idz,idy,idx]
      arr = arr.squeeze()



    except:
      arr = ds[var][0,rec,:,jbmin:jbmax,ibmin:ibmax].squeeze()

    ds.close()

  except Exception as e:
    file_error(e,fname,inspect.currentframe().f_code.co_name)

  return arr


# ------------------------ #
# Get value from 3D fields #
# ------------------------ #
def get_model_val_3d(jd,jdini,fname,hours,var,lon_mod,lat_mod,lev_mod,lon,lat,depth):

  start = time.time()

  from fun_gen import itp_meth,dump

  # Load file
  dump = float(dump)

  idx = np.where( (lon_mod > lon[0]-dump) & (lon_mod < lon[0]+dump) )
  idy = np.where( (lat_mod > lat[0]-dump) & (lat_mod < lat[0]+dump) )
  idz = np.where( (lev_mod < depth[-1]+800))


  if idz[0].size == 0:
    val = np.nan
      
  else:

    # Special case operational 
    frame = inspect.currentframe()
    caller_frame = frame.f_back
    caller_file = caller_frame.f_code.co_filename
    called_by = os.path.basename(caller_file)

    var3d = np.array(get_var_3D(jd,jdini,fname,hours,var,called_by,domain=[idz,idy,idx]))
    #var3d = np.array(get_var_3D(jd,jdini,fname,hours,var))

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

   #exit(1)


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

















