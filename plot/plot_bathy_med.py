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
#extent = [3,16,34.91,44.8]
extent = [-5.5,16,34.91,44.8]
fig, ax = plt.subplots(1,1,figsize=(3,3), subplot_kw={'projection': proj})

ax.set_extent(extent)

land = cfeature.NaturalEarthFeature('physical', 'land', \
scale=resol, facecolor=cfeature.COLORS['land'])

ax.add_feature(land, facecolor='lightgrey')
ax.add_feature(cfeature.BORDERS,edgecolor='darkgrey',linewidth=0.5,zorder=2)
ax.coastlines(resolution='50m', color='darkgrey',linewidth=0.5, linestyle='-', alpha=1)


# Plot model domain
plt.plot([xmin, xmax,xmax,xmin, xmin], [ymin, ymin, ymax, ymax, ymin],
         color='red', linewidth=1)


# Plot bathy
#topo[topo>0.]=0.
#plot = ax.contourf(lon, lat, topo, 100, cmap=cmocean.cm.deep_r,
#transform=ccrs.PlateCarree(), latlon=True, antialiased=False, vmin=-3000,vmax=0,
#extend='min', alpha=1,zorder=1)

#cb=plt.colorbar(plot,fraction=float(cb_fraction_2D),pad=float(cb_pad_2D),label="Depth (m)")

# Save 
# ----
fname = diagdir+'/'+config+'/'+'map_med.'+fig_fmt
savefig(fname)















