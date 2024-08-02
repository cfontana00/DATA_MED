# --------------------------------#
# Download ECMWF atmospheric data #
# --------------------------------#
import warnings
warnings.filterwarnings("ignore")

import sys,os,argparse
import numpy as np
import cdsapi
from fun_gen import *
from fun_io import *


def argument():
    parser = argparse.ArgumentParser(description = '',formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(   '--config', '-c',
                                type = str,
                                required = True,
                                help ='Configuration name'
                                )
    return parser.parse_args()


# Get args
# --------
args = argument()
config = args.config  # Configuration name


# Load config file
# ----------------
load_config(config)
from fun_gen import *


# Load lon/lat
# ------------
lon,lat,levels = load_coords()

yini,mini,dini = meteo_ini.split('-')
yend,mend,dend = meteo_end.split('-')

yini,mini = int(yini),int(mini)
yend,mend = int(yend),int(mend)


name = 'reanalysis-cerra-single-levels'

# Create output directory
# -----------------------
os.system('mkdir -p '+diagdir+'/'+config)
savedir= diagdir+'/'+config+'/METEO'
os.system('mkdir -p '+savedir)


latmax,latmin = str(np.amax(lat)+1),str(np.amin(lat)-1)
lonmax,lonmin = str(np.amax(lon)+1),str(np.amin(lon)-1)

area = "'"+latmax+"/"+lonmin+"/"+latmin+"/"+lonmax+"'"


c = cdsapi.Client()


# Loop on years 
# -------------
for year in range(int(yini),int(yend)+1):

  # Define months array
  if yini == yend :
    months = range(mini,mend+1)
  else :
    if year == yini :
       months = range(mini,13)
    elif year == yend :
       months = range(1,mend+1)


  for mon in range(np.amin(months),np.amax(months)+1):

    mon = str(mon).zfill(2)

    for var in ['10m_wind_direction','10m_wind_speed',\
            '2m_temperature','2m_relative_humidity',\
            'surface_net_solar_radiation','surface_net_thermal_radiation',\
            'mean_sea_level_pressure','total_precipitation']:

    #for var in ['10m_wind_speed']:

     oname = savedir+'/'+name+'_'+str(year)+mon+'_'+var+'.nc'

     c.retrieve(
      name,
      {
         'variable':  var ,
        'level_type': 'surface_or_atmosphere',
        'data_type': 'reanalysis',
        'product_type': 'forecast',
        'year': str(year),
        'month': mon,
        'day': [
            '01', '02', '03',
            '04', '05', '06',
            '07', '08', '09',
            '10', '11', '12',
            '13', '14', '15',
            '16', '17', '18',
            '19', '20', '21',
            '22', '23', '24',
            '25', '26', '27',
            '28', '29', '30',
            '31',
        ],
        'time': [
            '00:00', '03:00', '06:00',
            '09:00', '12:00', '15:00',
            '18:00', '21:00',
        ],
        'leadtime_hour': '1',
        'format': 'netcdf',
    },
    oname)


     # Crop file
     # ---------
     os.system('ncks -O -d x,'+imin+','+imax+' -d y,'+jmin+','+jmax+' '+oname+' '+oname)

     print('\n[DOWNLOADED]',oname,'\n')


