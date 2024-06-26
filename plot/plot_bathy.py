# --------------------------- #
# Routine to plot bathymetry  #
# --------------------------- #

import warnings
warnings.simplefilter("ignore")

import numpy as np
import argparse
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

from fun_gen import *
from fun_plot_2D import *
from fun_io import *
import matplotlib

matplotlib.use("Agg")
import cartopy.feature as cfeature
import cartopy.crs as ccrs
import cartopy

import cmocean
import cmcrameri



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


# Load coordinates
# ----------------
lon,lat,lev = load_coords()

xmin,xmax = np.amin(lon),np.amax(lon)
ymin,ymax = np.amin(lat),np.amax(lat)


# Load bathy file
etopo = xr.open_dataset(bathyfile)


# Load sliced variables.
lat = np.array(etopo.lat)
lon = np.array(etopo.lon)
topo = np.array(etopo.elevation)

"""
idy = np.where( (lat>=ymin) && (lat<=ymax))
idx = np.where( (lon>=xmin) nd (lon<=xmax))
print(idx)
print(idy)
lat = lat[idy]
lon = lon[idx]
topo = topo[idy,idx]

"""

# Create figure
exec('proj = ' + fig_proj)
extent = [xmin,xmax,ymin,ymax]
fig, ax = plt.subplots(1,1,figsize=(float(fig_sx), float(fig_sy)), subplot_kw={'projection': proj})
init_fig(ax,extent,proj)


# Plot bathy
topo[topo>0.]=0.
plot = ax.contourf(lon, lat, topo, 100, cmap=cmocean.cm.deep_r,
transform=ccrs.PlateCarree(), latlon=True, antialiased=False, vmin=-3000,vmax=0,
extend='min', alpha=1,zorder=1)

cb=plt.colorbar(plot,fraction=float(cb_fraction_2D),pad=float(cb_pad_2D),label="Depth (m)")

# Plot argo position
# ------------------
tag = ''
if argo_ds == 'bgc':
  tag = 'bio'

savedir = diagdir+'/'+config+'/ARGO'
ds = xr.open_dataset(savedir+'/'+tag+'argo.nc')

alat = np.array( ds['LATITUDE'])
alon = np.array(ds['LONGITUDE'])
num = np.array(ds['PLATFORM_NUMBER'])
cyc = np.array(ds['CYCLE_NUMBER'])

# Loop on floats
for n in np.unique(num):

  # Get all indexes
  idx = np.where( num == n )

  # Get data lon/lat
  n_lon = alon[idx]
  n_lat = alat[idx]
  n_cyc = cyc[idx]

  #plt.scatter(n_lon,n_lat,s=8,marker='.',color='r',linestyle='-')

# Plot eddy position
# ------------------
"""
eddy = np.loadtxt('/DISK2TB/DATA/eddy.dat').squeeze()
plt1 = plt.scatter(eddy[:,1],eddy[:,2],color='k',marker='.',s=8,facecolor='none',linestyle='-',linewidths=0.8,zorder=3)
plt1 = plt.scatter(eddy[0,1],eddy[0,2],color='k',marker='x',s=16,linestyle='-',linewidths=0.8,zorder=3)
plt1 = plt.plot(eddy[:,1],eddy[:,2],'k-',linewidth=0.8,zorder=3)
"""








# Save 
# ----
fname = bathyfile+'.'+fig_fmt
savefig(fname)















