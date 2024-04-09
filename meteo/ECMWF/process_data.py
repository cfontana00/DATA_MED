# --------------------------------#
# Download ECMWF atmospheric data #
# --------------------------------#
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


# Get args
# --------
config=sys.argv[1]  # Configuration name

indir = diagdir+'/'+config+'/METEO'

ncdir = diagdir+'/'+config+'/METEO/ITP_NC' 
os.system('mkdir -p '+ncdir)


# Load lon/lat
# ------------
lon,lat,levels = load_coords()


# Define parameters
# -----------------
mdini = dt.datetime.strptime(meteo_ini,'%Y-%m-%d').toordinal()
mdend = dt.datetime.strptime(meteo_end,'%Y-%m-%d').toordinal()

name = 'reanalysis-cerra-single-levels'

tags = []      # File tag                Variable name    'Units'      Output tag        
tags.append(['2m_temperature',               't2m'     ,  'degK'      ,'tag'  ])
#tags.append(['2m_relative_humidity',         'r2'      ,        ,'tag'  ])
#tags.append(['surface_net_solar_radiation',  'ssr'     ,   'W.m-2'     , 'tag'  ])

# Load meteo lon/lat
# ------------------
fname = glob(indir+'/*2m_temperature*')[0]
ds = xr.open_dataset(fname)
met_lon = np.array(ds['longitude']).flatten()
met_lat = np.array(ds['latitude']).flatten()
ds.close()

# Mesh model lon/lat
LAT,LON = np.meshgrid(lat,lon)



print('Processing data :\n')

switch = 0


# Initialize NetCDF file for writing
# -----------------------------------
meteo_ini = meteo_ini.replace('-','') 
meteo_end = meteo_end.replace('-','') 

fname = name + '_'+ meteo_ini +'_'\
                  + meteo_end +'.nc'

# Open file
dataset = Dataset(ncdir+'/'+fname,'w',format='NETCDF3_CLASSIC')

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
vtime[:] = range(0,(mdend-mdini+1)*8)



# Process standard variables
# --------------------------
for tag in tags:

  ftag = tag[0]
  var = tag[1]
  otag = tag[2]
  units = tag[3]

  print('=>',ftag)

  full_data = []


  # Loop on days
  # ------------
  for jd in range(mdini,mdend+1):

    date = dt.datetime.fromordinal(jd) 
    print(date.strftime('%Y-%m-%d'))

    year,mon,day = date.strftime('%Y'),date.strftime('%m'),date.strftime('%d')

    # Load variable
    fname = indir+'/'+name+'_'+str(year)+mon+'_'+ftag+'.nc'
    ds = xr.open_dataset(fname)

    # Loop on records
    for rec in range(0,8):

      data = np.array(ds[var])[8*int(day)+rec,:,:]

      # Interpolate on model grid
      data = data.flatten()
      idata = griddata((met_lat,met_lon),data,(LAT,LON),method='linear') 
      full_data.append(idata.T)

  full_data = np.array(full_data)
  ds.close()


  # Specific tuning
  #if tag[0] == 'surface_net_solar_radiation':
  #  full_data = full_data/3600.
  #  print('HERE')


  # Write variable to NetCDF
  # ------------------------
  vdata = dataset.createVariable(var,np.float32,('time','latitude','longitude'),fill_value=-9999)
  vdata.units = units 
  print(var)
  vlat.long_name = ds[var].GRIB_name

  vdata[:] = full_data



dataset.close()


    












   





'''

    for var in [ '10m_wind_direction', '10m_wind_speed', '2m_relative_humidity','surface_latent_heat_flux', 'surface_net_solar_radiation', 'surface_net_thermal_radiation','surface_pressure', 'surface_sensible_heat_flux', 'surface_solar_radiation_downwards','surface_thermal_radiation_downwards', 'time_integrated_surface_direct_short_wave_radiation_flux', 'total_cloud_cover','2m_temperature', 'evaporation', 'mean_sea_level_pressure','total_precipitation',  '2m_temperature']:


'''


