################################
# Functions for meteo routines #
################################
from netCDF4 import Dataset
import datetime as dt
import numpy as np
import os




# Write NetCDF file
# -----------------
def write_nc_meteo(fname,mdini,mdend,lon,lat,var,data,long_name,units):


  # Open file
  dataset = Dataset(fname,'w',format='NETCDF4_CLASSIC')

  # Create dimension
  dlon = dataset.createDimension('longitude',lon.shape[0])
  dlat = dataset.createDimension('latitude',lat.shape[0])
  dtime = dataset.createDimension('time',(mdend-mdini+2)*8)

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

  dori = dt.datetime(1900,1,1).toordinal()
  hori = (mdini - dori )*24
  time = range(hori,hori+(mdend-mdini+2)*24,3)


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




# Load meteo variables through already 
#       interpolated fields
# ------------------------------------
def load_meteo(config,jd,var):

   from fun_gen import meteo_ini,day_cycle,n_cycle,diagdir

   # Get file tag

   tags = []      # File tag                  Variable name            
   # ------------------------------------------------------
   tags.append(['2m_temperature',                 't2m'    ])
   tags.append(['mean_sea_level_pressure',        'msl'    ])
   tags.append(['2m_relative_humidity',           'r2'     ])
   tags.append(['surface_net_solar_radiation',    'ssr'    ])
   tags.append(['surface_net_thermal_radiation',  'str'    ])
   tags.append(['total_precipitation',            'tp'     ])
   tags.append(['uwind',                          'u10'     ])
   tags.append(['vwind',                          'v10'     ])

   tags = np.array(tags)
   idx = np.where(tags[:,1] == var)

   tag = tags[idx,0][0][0]

   # Get filename
   idir = os.path.join(diagdir,config,'METEO','ITP_NC')

   # Meteo start
   mdini = dt.datetime.strptime(meteo_ini,'%Y-%m-%d').toordinal()

   # Concerned cycle start
   jdlist = np.arange(mdini,mdini+n_cycle*day_cycle,day_cycle)

   idx = np.amax(np.where(jdlist <= jd))

   dstart = dt.datetime.fromordinal(jdlist[idx])
   dend = dt.datetime.fromordinal(jdlist[idx]+day_cycle-1)

   delta = jd-jdlist[idx]

   tstart = dstart.strftime('%Y%m%d')
   tend = dend.strftime('%Y%m%d')

   dtag = tstart+'_'+tend

   fname = idir+'/reanalysis-cerra-single-levels_'+tag+'_'+dtag+'.nc'


   ds = Dataset(fname,format='NETCDF4-CLASSIC')
   arr = ds[var][delta*8,:,:].squeeze()
   ds.close()

   return arr

