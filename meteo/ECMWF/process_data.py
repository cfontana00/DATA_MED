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
from fun_meteo import *
import xarray as xr
from scipy.interpolate import griddata


# Get args
# --------
config = sys.argv[1]  # Configuration name

# Load config file
# ----------------
load_config(config)
from fun_gen import *


# Try to read date as parameters
# ------------------------------
try : 
  arg_ini = sys.argv[2]
  arg_end = sys.argv[3]

  # Define parameters
  # -----------------
  mdini = dt.datetime.strptime(arg_ini,'%Y-%m-%d').toordinal()
  mdend = dt.datetime.strptime(arg_end,'%Y-%m-%d').toordinal()

except :
  print('No date arguments given')
  print('=> Saving all in one file\n')

  # Define parameters
  # -----------------
  mdini = dt.datetime.strptime(meteo_ini,'%Y-%m-%d').toordinal()
  mdend = dt.datetime.strptime(meteo_end,'%Y-%m-%d').toordinal()




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
  print('---------------')

  full_data = []

  # Tag for file name
  tag_ini = dt.datetime.fromordinal(mdini)
  tag_ini = tag_ini.strftime('%Y%m%d')

  tag_end = dt.datetime.fromordinal(mdend)
  tag_end = tag_end.strftime('%Y%m%d')


  # Loop on days
  # ------------
  for jd in range(mdini,mdend+2):

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

      #idata[np.where(np.isnan(mask))] = np.nan

      full_data.append(idata)

  full_data = np.array(full_data,dtype='float32')
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
    
    full_data = np.array(full_data,dtype='float32')
    units = 'g kg-1'
    long_name = 'Specific humidity'



  # Write variable to NetCDF
  # ------------------------
  oname = name +'_'+ftag+ '_'+ tag_ini +'_'\
                  + tag_end +'.nc'
  write_nc_meteo(ncdir+'/'+oname,mdini,mdend,lon,lat,var,full_data,long_name,units)

  # TEST !!!!!!!
  #if ftag == '2m_temperature':
  #    full_data = full_data[0:2,:,:]

  # Write to binary file
  # --------------------
  full_data.tofile(bindir+'/BC_'+otag+'_'+tag_ini+'_'+tag_end,format='float32')
  print('[FILE SAVED] '+bindir+'/BC_'+otag+'_'+tag_ini+'_'+tag_end+'\n')

  ''' 
  data = np.fromfile(bindir+'/BC_'+otag+'_'+meteo_ini+'_'+meteo_end,dtype='float32')
  nrec = int(data.shape[0]/(336*784))
  data = data.reshape([nrec,336,784])
  print(nrec,data[3,100,100])
  exit()
  '''


# ------------ #
# Process wind #
# ------------ #

# Loop on days
# ------------

ufull_data = []
vfull_data = []

print('Processing wind variables :\n')
print('---------------------------\n')
for jd in range(mdini,mdend+2):
  
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

     #isdata[np.where(np.isnan(mask))] = np.nan

     ufull_data.append(isdata*icos)
     vfull_data.append(isdata*isin)

dsp.close()
ddir.close()

ufull_data = np.array(ufull_data,dtype='float32')
vfull_data = np.array(vfull_data,dtype='float32')

# Write to NetCDF file
# --------------------

# U10
units = 'm s**-1'
long_name = '10 meter U wind component'
oname = name +'_uwind_'+ tag_ini +'_'\
                  + tag_end +'.nc'

print('DATE',mdini,mdend)
write_nc_meteo(ncdir+'/'+oname,mdini,mdend,lon,lat,'u10',ufull_data,long_name,units)

# V10
long_name = '10 meter V wind component'
oname = name +'_vwind_'+ tag_ini +'_'\
                  + tag_end +'.nc'

write_nc_meteo(ncdir+'/'+oname,mdini,mdend,lon,lat,'v10',vfull_data,long_name,units)


# Write to binary file
# --------------------
ufull_data.tofile(bindir+'/BC_uwind_'+tag_ini+'_'+tag_end,format='float32')
print('[FILE SAVED] '+bindir+'/BC_uwind_'+tag_ini+'_'+tag_end)

vfull_data.tofile(bindir+'/BC_vwind_'+tag_ini+'_'+tag_end,format='float32')
print('[FILE SAVED] '+bindir+'/BC_vwind_'+tag_ini+'_'+tag_end)
