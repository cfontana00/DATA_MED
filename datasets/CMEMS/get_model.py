from fun_io import get_cmems_model
from fun_gen import load_config
import sys


config = sys.argv[1]
var = sys.argv[2]

load_config(config)
from fun_gen import *

os.makedirs(diagdir+'/'+config, exist_ok=True)
os.makedirs(diagdir+'/'+config+'/CMEMS/', exist_ok=True)
os.makedirs(diagdir+'/'+config+'/CMEMS/'+var, exist_ok=True)

# Load lon/lat
# ------------
lon,lat,levels = load_coords()
extent = [lon.min(),lon.max(),lat.min(),lat.max()]

get_cmems_model(config,extent,var)
