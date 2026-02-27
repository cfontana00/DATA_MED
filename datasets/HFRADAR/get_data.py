# ----------------------- #
# Download HF radars data #
# ----------------------- #

from fun_gen import *
from fun_io import *
import copernicusmarine 
import os
import argparse
import xarray as xr
import requests
from requests.auth import HTTPBasicAuth
from io import BytesIO
from netCDF4 import Dataset



def argument():
    parser = argparse.ArgumentParser(description = '',formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(   '--config', '-c',
                                type = str,
                                required = True,
                                help ='Configuration name'
                        )
    return parser.parse_args()

                           
# Get args
args = argument()
config = args.config  # Configuration name

# Load config
load_config(config)
from fun_gen import *

# Create dirs
os.makedirs(diagdir+'/'+config+'/RADAR/DATA',exist_ok=True)
os.makedirs(radardir,exist_ok=True)


# Get CMEMS username
usr = os.getenv('COPERNICUSMARINE_SERVICE_USERNAM')

# Create directory

"""
# Get CMEMS files
# ---------------
query_metadata = copernicusmarine.get(dataset_id='cmems_obs-ins_glo_phy-cur_nrt_radar-total_irr', dry_run=True,username='cfontana3')

os.system('rm -f files.txt')

# Loop on tags
for tag in ['TirLig']:
  os.system('echo history/GL_TV_HF_HFR-'+tag+'-Total.nc >> files.txt')
  os.system('rm -f '+radardir+'/GL_TV_HF_HFR-'+tag+'-Total.nc')

# Download files
copernicusmarine.get(dataset_id='cmems_obs-ins_glo_phy-cur_nrt_radar-total_irr', 
                     file_list="files.txt",
                     username=usr,
                     output_directory = radardir,
                     no_directories=True
                     )


os.system('rm -f files.txt')


print('\nFiles downloaded in '+radardir )
os.system('ls '+radardir)
"""

# Get EuroGoos file
# -----------------
print("Processing EuroGoos")
for tag in radareuro :
 
  try:
    print(tag)

    ds = xr.open_dataset('https://thredds.hfrnode.eu:8443/thredds/dodsC/'+tag,decode_times=True)

    subset = ds[['EWCT','NSCT']].sel(TIME=slice(date_ini, date_end))
  #subset = ds[['EWCT','NSCT']].sel(TIME=slice("2017-01-01","2017-02-01"))
    #fname = diagdir+'/'+config+'/RADAR/DATA/'+tag+'.nc'
    fname = radardir+'/'+tag+'.nc'
    subset.to_netcdf(fname)

    print(fname)
    print('\n[FILE SAVED] '+fname) 
  except:
    print("[FAILED] ",fname )  
    


