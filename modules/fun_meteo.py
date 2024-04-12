################################
# Functions for meteo routines #
################################
from netCDF4 import Dataset
import datetime as dt
import numpy as np




# Write NetCDF file
# -----------------
def write_nc_meteo(fname,lon,lat,var,data,long_name,units):

  from fun_gen import meteo_ini,meteo_end

  mdini = dt.datetime.strptime(meteo_ini,'%Y-%m-%d').toordinal()
  mdend = dt.datetime.strptime(meteo_end,'%Y-%m-%d').toordinal()


  # Open file
  dataset = Dataset(fname,'w',format='NETCDF4_CLASSIC')

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

  dori = dt.datetime(1900,1,1).toordinal()
  hori = (mdini - dori )*24
  time = range(hori,hori+(mdend-mdini+1)*24,3)


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





