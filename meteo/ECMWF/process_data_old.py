# ------------------------------------------- #
#  Process ECMWF atmospheric data             #
#   and create NetCDF files for               #
#  visualisation and binary files for MITgcm  #
# ------------------------------------------- #

import warnings
warnings.filterwarnings("ignore")

import sys,os
from glob import glob
import numpy as np
import datetime as dt
import cdsapi
from fun_gen import *
from fun_io import *
import xarray as xr
from scipy.interpolate import griddata
from netCDF4 import Dataset



# Get args
# --------
config = sys.argv[1]  # Configuration name

# Load config file
# ----------------
load_config(config)
from fun_gen import *

print('NB /!\: 3-h fields hard coded ...\n')


# Get args
# --------
config=sys.argv[1]  # Configuration name

indir = diagdir+'/'+config+'/METEO'

ncdir = diagdir+'/'+config+'/METEO/ITP_NC' 
os.system('mkdir -p '+ncdir)

bindir = diagdir+'/'+config+'/METEO/ITP_BIN' 
os.system('mkdir -p '+bindir)


# Load lon/lat
# ------------
lon,lat,levels = load_coords()

# Mesh model lon/lat
LAT,LON = np.meshgrid(lat,lon)


# Define parameters
# -----------------
mdini = dt.datetime.strptime(meteo_ini,'%Y-%m-%d').toordinal()
mdend = dt.datetime.strptime(meteo_end,'%Y-%m-%d').toordinal()
name = 'reanalysis-cerra-single-levels'


# --------------------------------------------------------------------------------
#                            VARIABLE DEFINITION
# --------------------------------------------------------------------------------
tags = []      # File tag                  Variable name    'Units'      Output tag        
# --------------------------------------------------------------------------------
tags.append(['2m_temperature',                 't2m'     ,  'degK'      , 'atemp'  ])
tags.append(['mean_sea_level_pressure',        'msl'    ,    'Pa'       , 'apress'  ])
tags.append(['2m_relative_humidity',           'r2'      ,   '%'        , 'aqh'  ])
tags.append(['surface_net_solar_radiation',    'ssr'     ,   'W m**-2'  , 'swflux'  ])
tags.append(['surface_net_thermal_radiation',  'str'     ,   'W m**-2'  , 'lwflux'  ])
tags.append(['total_precipitation',            'tp'    ,    'kg m**-2'  , 'precip'  ])
#tags.append(['total_cloud_cover',              'tcc'    ,    '%'        ,  'tag'  ])
# --------------------------------------------------------------------------------


# Load meteo lon/lat
# ------------------
fname = glob(indir+'/*2m_temperature*')[0]
ds = xr.open_dataset(fname)
met_lon = np.array(ds['longitude']).flatten()
met_lat = np.array(ds['latitude']).flatten()
ds.close()



# Load model outputs for mask
# ---------------------------
fname = glob(outdir+'/*TEMP*.nc')[0]
ds = xr.open_dataset(fname)
mask = np.array(ds['thetao'][0,0,:,:]).squeeze()
ds.close()




# Initialize NetCDF file for writing
# -----------------------------------
meteo_ini = meteo_ini.replace('-','') 
meteo_end = meteo_end.replace('-','') 

oname = name + '_'+ meteo_ini +'_'\
                  + meteo_end +'.nc'

# Open file
dataset = Dataset(ncdir+'/'+oname,'w',format='NETCDF4_CLASSIC')

# Create dimension
dlon = dataset.createDimension('longitude',lon.shape[0])
dlat = dataset.createDimension('latitude',lat.shape[0])
dtime = dataset.createDimension('time',(mdend-mdini+1)*8)

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

# Set time values
dori = dt.datetime(1900,1,1).toordinal()
hori = (mdini - dori )*24
vtime[:] = range(hori,hori+(mdend-mdini+1)*24,3)


# --------------------------
# Process standard variables
# --------------------------
print('Processing standard variables :\n')
for tag in tags:

  ftag = tag[0]
  var = tag[1]
  units = tag[2]
  otag = tag[3]

  print('=>',ftag)

  full_data = []


  # Loop on days
  # ------------
  for jd in range(mdini,mdend+1):

    date = dt.datetime.fromordinal(jd) 
    print(date.strftime('%Y-%m-%d'),end='\r')

    year,mon,day = date.strftime('%Y'),date.strftime('%m'),date.strftime('%d')

    # Load variable
    fname = indir+'/'+name+'_'+str(year)+mon+'_'+ftag+'.nc'
    ds = xr.open_dataset(fname)
    long_name = ds[var].GRIB_name

    # Loop on records
    for rec in range(0,8):

      data = np.array(ds[var])[8*(int(day)-1)+rec,:,:]

      # Interpolate on model grid
      data = data.flatten()
      idata = griddata((met_lat,met_lon),data,(LAT,LON),method='linear').T

      idata[np.where(np.isnan(mask))] = np.nan

      full_data.append(idata)

  full_data = np.array(full_data)
  ds.close()


  # ---------------
  # Specific tuning
  # ---------------

  # Convention
  if ftag == 'surface_net_thermal_radiation' or ftag == 'surface_net_solar_radiation':
    full_data = -full_data

  # Joule to Watt
  if ftag == 'surface_net_solar_radiation' or tag[0] == 'surface_net_thermal_radiation':
    full_data = full_data/3600.

  # Store temperature to compute specific humidity
  if ftag == '2m_temperature':
    t2m = full_data

  # Store mean pressure to compute specific humidity
  if ftag == 'mean_sea_level_pressure':
    msl = full_data

  # Units convertion
  if ftag == 'total_precipitation':
    full_data = full_data/1000/3600  # from kg/m^2 (i.e., mm/hr) to m/s    

  # Compute specific humidity
  if ftag == '2m_relative_humidity':

    raw_data = full_data.copy()
    full_data = []

    for rec in range(0,raw_data.shape[0]):

      Td=t2m[rec,:,:].squeeze()-273.15 # K to deg C
      p=msl[rec,:,:].squeeze()/100  # Pa to mb

      e = 6.112*np.exp((17.67*Td)/(Td + 243.5)) # See ./README.md
      q = (0.622 * e)/(p - (0.378 * e))

      full_data.append(q)
    
    full_data = np.array(full_data)
    units = 'g kg-1'
    long_name = 'Specific humidity'



  # Write variable to NetCDF
  # ------------------------
  vdata = dataset.createVariable(var,np.float32,('time','latitude','longitude'),fill_value=-9999)
  vdata.units = units 
  vdata.long_name = long_name
  vdata[:] = full_data


  # Write to binary file
  # --------------------
  full_data.tofile(bindir+'/BC_'+otag+'_'+meteo_ini+'_'+meteo_end,format='float32')
  print('[FILE SAVED] '+bindir+'/BC_'+otag+'_'+meteo_ini+'_'+meteo_end+'\n')


  """
  # TEST 
  arr = full_data.flatten()
  print('Rec array shape', arr.shape)

  arr2 = np.fromfile(bindir+'/BC_'+otag+'_'+meteo_ini+'_'+meteo_end)
  arr2 = arr2.flatten()
  print('Read array shape', arr2.shape)
  """


# ------------
# Process wind 
# ------------

# Loop on days
# ------------

ufull_data = []
vfull_data = []

print('Processing wind variables :\n')
for jd in range(mdini,mdend+1):
  
  date = dt.datetime.fromordinal(jd)
  print(date.strftime('%Y-%m-%d'),end='\r')

  year,mon,day = date.strftime('%Y'),date.strftime('%m'),date.strftime('%d')

  # Load variable
  fname = indir+'/'+name+'_'+str(year)+mon+'_10m_wind_speed.nc'
  dsp = xr.open_dataset(fname)

  fname = indir+'/'+name+'_'+str(year)+mon+'_10m_wind_direction.nc'
  ddir = xr.open_dataset(fname)

  # Loop on records
  for rec in range(0,8):

     sdata = np.array(dsp['si10'])[8*(int(day)-1)+rec,:,:]
     ddata = np.array(ddir['wdir10'])[8*(int(day)-1)+rec,:,:]

     # Interpolate on model grid
     sdata = sdata.flatten()
     ddata = ddata.flatten()

     isdata = griddata((met_lat,met_lon),sdata,(LAT,LON),method='linear').T

     ddata = ddata*2*np.pi/360
     icos = griddata((met_lat,met_lon),np.cos(ddata),(LAT,LON),method='linear').T
     isin = griddata((met_lat,met_lon),np.sin(ddata),(LAT,LON),method='linear').T

     isdata[np.where(np.isnan(mask))] = np.nan

     ufull_data.append(isdata*icos)
     vfull_data.append(isdata*isin)

dsp.close()
ddir.close()

ufull_data = np.array(ufull_data)
vfull_data = np.array(vfull_data)

# Write to NetCDF file
# --------------------
vdata = dataset.createVariable('u10',np.float32,('time','latitude','longitude'),fill_value=-9999)
vdata.units = 'm s**-1'
vdata.long_name = '10 meter U wind component'
vdata[:] = ufull_data


vdata = dataset.createVariable('v10',np.float32,('time','latitude','longitude'),fill_value=-9999)
vdata.units = 'm s**-1'
vdata.long_name = '10 meter V wind component'
vdata[:] = vfull_data

# Write to binary file
# --------------------
ufull_data.tofile(bindir+'/BC_uwind_'+meteo_ini+'_'+meteo_end)
vfull_data.tofile(bindir+'/BC_vwind_'+meteo_ini+'_'+meteo_end)

print('')
print('[FILE SAVED] '+ncdir+'/'+oname+'\n')
dataset.close()


