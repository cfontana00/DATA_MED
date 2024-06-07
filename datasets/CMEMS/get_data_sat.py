#############################
# Routine to get CMEMS data #
#############################
import warnings
warnings.simplefilter("ignore")
from fun_gen import *
from fun_io import *
import os
import sys
import copernicusmarine
import datetime as dt


# Get args
# --------
config = sys.argv[1]  # Configuration name
var = sys.argv[2]  # Configuration name



# Load parameters
# ---------------
load_config(config)
from fun_gen import *

# Create arborescence
# -------------------
vdir = create_arbo(config,var,'CMEMS')
datadir = diagdir+'/'+config+'/CMEMS/data'
os.system('mkdir -p '+datadir)

usr = os.getenv('COPERNICUSMARINE_SERVICE_USERNAM')
pswd = os.getenv('COPERNICUSMARINE_SERVICE_PASSWORD')

# Load coordinates
# ----------------
lon,lat,lev = load_coords()

# Load CMEMS parameters
# ---------------------
pars = np.loadtxt('../../config/cmems_'+config+'.dat',dtype=str)

# Loop on variables
for par in pars:
  if par[0] == var:
    break

ds_id = par[1]
cvar = par[2]

if var == 'chl':
  cvar = ['CHL','KD490']
else :
  cvar = [cvar]


print('Downloading CMEMS products :',ds_id)
print('=> Variable',cvar,'\n')

copernicusmarine.subset(
        dataset_id = ds_id,
        minimum_longitude = lon.min()-1,
        maximum_longitude = lon.max()+1,
        minimum_latitude = lat.min()-1,
        maximum_latitude = lat.max()+1,
        start_datetime = date_ini,
        end_datetime = date_end,
        #variables = cvar,
        output_directory = datadir,
        output_filename = ds_id+'.nc',
        username = usr,
        password = pswd,
        force_download = 'true'
    )

print('')
print('[FILE SAVED ]',datadir+'/'+ds_id+'.nc')




