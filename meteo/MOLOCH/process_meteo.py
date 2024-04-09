# ------------------------------------- #
# Process MOLOCH meteo files for MITgcm #
# ------------------------------------- #


import warnings
warnings.filterwarnings("ignore")

import numpy as np

from fun_gen import *
from fun_io import *
import sys,os
from glob import glob
import datetime as dt
import xarray as xr
from netCDF4 import Dataset


# Get args
# --------
config = sys.argv[1]  # Configuration name

# Load config file
# ----------------
load_config(config)
from fun_gen import *


# Create output directory
# -----------------------
savedir = meteodir + '/readyfiles'
os.system('mkdir -p ' + savedir)


# Date conversion
# ---------------
mdini = datetime.strptime(meteo_ini,'%Y-%m-%d').toordinal()
mdend = datetime.strptime(meteo_end,'%Y-%m-%d').toordinal()
print('Processing data from',meteo_ini,'to',meteo_end,'\n')


# Nomenclature
# ------------
nom = []

# -------------------------------------------------------------------------------------
#            In-tag       In-var     Out_var
# -------------------------------------------------------------------------------------
nom.append([ 'pmsl'    , 'prmsl'  ,  'msl' ])     # Pressure Reduced to MSL
nom.append([ 'dswrf'   , 'dswrf'  ,  'p3111' ])   # Downward short-wave radiation flux 
#nom.append([ '' , '',  'p3112' ])            # Downward long-wave radiation flux
nom.append([ 'rh2m'    , 'r2'     ,  'r' ])       # 2 metre relative humidity
nom.append([ 't2m'     , 't2m'     ,  't2m' ])    # 2 metre temperature
nom.append([ 'clct'    , 'clct'   ,  'tcc' ])     # Total Cloud Cover 
nom.append([ 'apcp'    , 'unknown',  'tp' ])      # Total precipitation
nom.append([ 'wind10m' , 'u10'    ,  'u10' ])     # 10 metre U wind component
nom.append([ 'wind10m' , 'v10'    ,  'v10' ])     # 10 metre V wind component
# -------------------------------------------------------------------------------------


# Get dimensions size
# -------------------
fname = glob(meteodir+'/*.nc')[0]
ds = xr.open_dataset(fname)
lon = ds['longitude']
lat = ds['latitude']
time = ds['time']

slon = lon.shape[0]
slat = lat.shape[0]

ds.close()



# Loop on days
# ------------
for jd in range(mdini,mdend+1):


   # Define time parameters
   # -----------------------
   d = dt.datetime.fromordinal(jd)
   year,mon,day = d.strftime('%Y'),d.strftime('%m'),d.strftime('%d')
   doy = int(d.strftime('%j'))

   print(year,mon,day)


   if doy == 1 :
     year = int(year)-1
     istart = 8760-24
     iend = 8760
   else :
     istart = (doy-1)*24
     iend = (doy)*24

   # !!!!!!!!!!!!!!
   # REDUCE LON LAT


   # Open file to write
   # ------------------
   dtag = str(year)+mon+day
   fout = savedir + '/'+ dtag + '00_mol02ecm.nc'
   dataset = Dataset( fout ,'w',format='NETCDF3_CLASSIC')

   dlon = dataset.createDimension('longitude',slon)
   dlat = dataset.createDimension('latitude',slat)
   dtime= dataset.createDimension('time',24)


   # Create variables & set attributes
   # ---------------------------------
   vlon = dataset.createVariable('longitude',np.float32,('longitude'))
   vlon.units="degrees east"
   vlon.long_name="Longitude of considered cell"
   vlon[:] = lon

   vlat = dataset.createVariable('latitude',np.float32,('latitude'))
   vlat.units="degrees north"
   vlat.long_name="Latitude of considered cell"
   vlat[:] = lat

   vtime = dataset.createVariable('time',np.float32,('time'))
   vtime.units="hours since 1900-01-01 00:00:00.0"
   vtime.long_name="time"
   vtime.calendar = "gregorian"
   vtime[:] = time[istart:iend]


   # Loop on variables
   # -----------------
   for tags in nom:

     intag = tags[0]
     invar = tags[1]
     ovar = tags[2]

     #print(intag,invar,ovar)

     # Read data
     # ---------
     fname = meteodir+'/moloch_'+str(year)+'_'+intag+'.nc'
     ds = xr.open_dataset(fname)
     data = ds[invar][istart:iend,:,:]
     ds.close()

     # Write data
     # ----------
     vdata = dataset.createVariable(ovar,np.float32,('time','latitude','longitude'),fill_value=-9999)
     try :
       vdata.units = data.units
     except : 
       pass

     if intag != "apcp":
       vdata.long_name = data.long_name
     else:
       vdata.long_name = 'Total Precipitation'

     vdata[:] = data[:,:,:]

   dataset.close()
   print("[SAVED NC]",fout,'\n')


     






























