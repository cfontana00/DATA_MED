from fun_io import get_cmems_model,write_nc_cmems
from fun_gen import load_config,load_variable
import sys
import xarray as xr
from scipy.interpolate import griddata
import datetime as dt
import os


config = sys.argv[1]
var = sys.argv[2]

load_config(config)
from fun_gen import *

os.makedirs(diagdir+'/'+config, exist_ok=True)
os.makedirs(diagdir+'/'+config+'/CMEMS/', exist_ok=True)
os.makedirs(diagdir+'/'+config+'/CMEMS/'+var, exist_ok=True)

# Load variable parameters
# ------------------------
vname, ftag, cmap, islog, vmod, vmin, vmax, label, units\
        = load_variable(config,var)



# Load lon/lat
# ------------
lon,lat,levels = load_coords()
LON_MOD,LAT_MOD = np.meshgrid(np.array(lon),np.array(lat))
extent = [lon.min(),lon.max(),lat.min(),lat.max()]

get_cmems_model(config,extent,var)

# Interpolate on MER grid
cdir = os.path.join(diagdir,config,'CMEMS',var)

ds = xr.open_dataset(cdir+'/model_cmems.nc')
clon = ds['longitude']
clat = ds['latitude']
cvar = ds[var]
ds.close()


LON,LAT = np.meshgrid(clon,clat)
LON,LAT = LON.flatten(),LAT.flatten()

full_data = []

dori = dt.datetime(1900,1,1).toordinal()
time = np.zeros(6)
i = 0
for jd in range(jdini,jdend+1):

  if var == 'thetao':
    data = np.array(cvar[(jd-jdini)*24,:,:]).squeeze().flatten()
  elif var == 'chl':
    data = np.array(cvar[(jd-jdini),3,:,:]).squeeze().flatten()

  idata = griddata((LON,LAT),data.T,(LON_MOD,LAT_MOD),method='nearest')
  full_data.append(idata)
  time[i] = (jd - dori )*24
  i += 1



full_data = np.array(full_data)

# Save file
# ---------
fname = cdir+'/model_cmems.nc'
os.remove(fname)
write_nc_cmems(fname,time,lon,lat,var,full_data,label,units)



