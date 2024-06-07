import warnings
warnings.simplefilter("ignore")

from fun_gen import *
from fun_io import *
from fun_plot_2D import *
import sys,os
from glob import glob

import numpy as np
from numpy import array as npa
from scipy.interpolate import griddata
import datetime as dt
from netCDF4 import Dataset

import cartopy.feature as cfeature
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")

import cmocean
import cmcrameri


# Get args
# --------
config=sys.argv[1]  # Configuration name


# Load parameters
# ---------------
load_config(config)
from fun_gen import *

os.system('mkdir -p '+modis_dir)


# Initialize plot
# ---------------

# Load lon/lat
# ------------
lon_mod,lat_mod,levels = load_coords()

# Load proj
# ---------
exec('proj = ' + fig_proj)

# Init figure
# -----------
lon_min,lon_max = lon_mod.min(),lon_mod.max()
lat_min,lat_max = lat_mod.min(),lat_mod.max()

extent = [lon_min,lon_max,lat_min,lat_max]
fig, ax = plt.subplots(1,1,figsize=(float(fig_sx), float(fig_sy)), subplot_kw={'projection': proj})
init_fig(ax,extent,proj)

# Loop on tags
# ------------
#for tag in ['OC','SST','KD490']: 
for tag in ['KD490']: 

  print('Processing',tag,'from',date_ini,'to',date_end)

  if tag == 'OC':
     var = 'chlor_a'
     long_name = 'Chlorophyll a'
     units = 'mg.m**-3'
     ftag = 'OC'

  elif tag == 'SST':
     var = 'sst'
     long_name = 'Sea Surface Temperature'
     units = 'degC'
     ftag = 'SST'

  elif tag == 'KD490':
     var = 'Kd_490'
     long_name = 'Attenuation coefficient'
     units = 'm**-1'
     ftag = 'OC'

  # Create output directory
  os.system('mkdir -p '+modis_dir+'/'+tag)
  os.system('mkdir -p '+modis_dir+'/'+tag+'/ITP_NC')

  # Loop on days
  # ------------
  for jd in range(jdini,jdend+1):


     d = dt.datetime.fromordinal(jd)   
     dstr = d.strftime('%Y%m%d')

     # Search for data
     flist = glob(modis_dir+'/'+ftag+'/*'+dstr+'*'+ftag+'*')

     # Load data
     fdata,flon,flat,fqual = [],[],[],[]
     for f in flist:
        ds = Dataset(f,format='NETCDF4-CLASSIC')
 
        if tag == 'SST':
          fqual = ds['geophysical_data/qual_sst'][:,:]

        tmp = ds['geophysical_data/'+var][:,:]
        print()

        try : 
          tmp[np.where(fqual != 0)] = -9999
        except:
          pass

        fdata.append(tmp)
           
        flat.append(ds['navigation_data/latitude'][:])
        flon.append(ds['navigation_data/longitude'][:])
        ds.close()


     data = npa([])
     lon = npa([])
     lat = npa([])

     # Concatenate data
     for i in range(0,len(flist)):
        data = np.concatenate((data,npa(fdata[i]).flatten()))
        lon = np.concatenate((lon,npa(flon[i]).flatten()))
        lat = np.concatenate((lat,npa(flat[i]).flatten()))


     # Interpolate on model grid
     LON,LAT = np.meshgrid(lon_mod,lat_mod)


     data[ np.where(data < -999)] = np.nan
     idx_lon = npa( np.where(lon > lon_min-1) and np.where(lon < lon_max+1)).squeeze()
     idx_lat = npa( np.where(lat > lat_min-1) and np.where(lat < lat_max+1)).squeeze()

     idx = np.concatenate((npa(idx_lon),idx_lat))
     data,lon,lat = data[idx],lon[idx],lat[idx]

     try:
       idata = griddata((lon,lat),data,(LON,LAT),method='linear')

       dori = dt.datetime(1900,1,1).toordinal()
       time = np.array([(jd - dori )*24])

       # Save NetCDF
       fname = modis_dir+'/'+tag+'/ITP_NC/'+var+'_'+dstr+'.nc'
       write_nc(fname,time,lon_mod,lat_mod,var,idata,long_name,units)

     except Exception as e:
       print('INTERP FAILED')
       print(e)



