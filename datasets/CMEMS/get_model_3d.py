from fun_gen import load_config,load_variable
import copernicusmarine
import sys,os
import numpy as np


# Get parameters
config = sys.argv[1]
var = sys.argv[2]

# Load config
load_config(config)
from fun_gen import *

# Create directories
os.makedirs(diagdir+'/'+config, exist_ok=True)
os.makedirs(diagdir+'/'+config+'/CMEMS/', exist_ok=True)
os.makedirs(diagdir+'/'+config+'/CMEMS/'+var, exist_ok=True)

# Load lon/lat
# ------------
lon,lat,levels = load_coords()
LON_MOD,LAT_MOD = np.meshgrid(np.array(lon),np.array(lat))
extent = [lon.min(),lon.max(),lat.min(),lat.max()]

# Get CMEMS products name
usr = os.getenv('COPERNICUSMARINE_SERVICE_USERNAM')
pswd = os.getenv('COPERNICUSMARINE_SERVICE_PASSWORD')

pars = np.loadtxt('config/cmems_'+config+'.dat',dtype=str)

# Loop on variables
for par in pars:
  if par[0] == var:
    break

ds_id = par[5]
cvar = par[6]

outdir = os.path.join(diagdir,config,'CMEMS',cvar)


copernicusmarine.subset(
        dataset_id = ds_id,
        minimum_longitude = extent[0],
        maximum_longitude = extent[1],
        minimum_latitude = extent[2],
        maximum_latitude = extent[3],
        maximum_depth = 300,
        start_datetime = date_ini,
        end_datetime = date_end,
        variables = [cvar],
        output_directory = outdir,
        output_filename = 'model_cmems_3d.nc',
        overwrite=True,
        username = usr,
        password = pswd
    )

print('[FILE SAVED]',outdir+'/model_cmems_3d.nc')




