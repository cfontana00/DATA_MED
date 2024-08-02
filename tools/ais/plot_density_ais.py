# -------------------- #
# Plot AIS density map #
# -------------------- #
import warnings
warnings.simplefilter("ignore")


from fun_io import *
from fun_plot_2D import *

import numpy as np
from numpy import array
import cartopy.feature as cfeature
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")

from netCDF4 import Dataset

import cmcrameri as cmc




# Load config
load_config('ALBEDO')
from fun_gen import *


# Load AIS data
# -------------
ds = Dataset('/home/fontana/DISK2TB/DATA/AIS/Cargo_Ships_2015_04.nc',format='NETCDF4-CLASSIC')
cargo = array(ds['DEFAULT'])
dlon = array(ds['longitude'])
dlat = array(ds['latitude'])
ds.close()

ds = Dataset('/home/fontana/DISK2TB/DATA/AIS/Passenger_Ships_2015_04.nc',format='NETCDF4-CLASSIC')
person = array(ds['DEFAULT']) 
ds.close()

ds = Dataset('/home/fontana/DISK2TB/DATA/AIS/Tankers_2015_04.nc',format='NETCDF4-CLASSIC')
tankers = array(ds['DEFAULT']) 
ds.close()

density = cargo + person + tankers

# Initialize plot
# ---------------

# Load lon/lat
# ------------
lon,lat,levels = load_coords()

# Load proj
# ---------
exec('proj = ' + fig_proj)
cb_done = 'False'

# Init figure
# -----------
extent = [lon.min(),lon.max(),lat.min(),lat.max()]
fig, ax = plt.subplots(1,1,figsize=(float(fig_sx), float(fig_sy)), subplot_kw={'projection': proj})
init_fig(ax,extent,proj)


density[density==0]=np.nan

plt.pcolor(dlon,dlat,density,norm=colors.LogNorm(vmin=0.01,vmax=5),cmap=cmc.cm.buda_r)
cb = plt.colorbar(extend='both',fraction=float(cb_fraction_2D),
        pad=float(cb_pad_2D),label='Boats Density (hrs.km$^{-2}$)')


# Plot eddy position
# ------------------
eddy = np.loadtxt('/DISK2TB/DATA/eddy.dat').squeeze()
last = 2
tag = str(eddy[-last,0])

# Plot track
plt1 = plt.scatter(eddy[12:-last+1,1],eddy[12:-last+1,2],
           color='k',marker='.',s=8,facecolor='none',linestyle='-',linewidths=0.8,zorder=3)
plt.plot(eddy[12:-last+1,1],eddy[12:-last+1,2],'k-',linewidth=0.8,zorder=3)


# Plot zone
plt.scatter(eddy[-last,1],eddy[-last,2],color='r',
           marker='o',s=300,alpha=0.4,zorder=3)

plt.scatter(eddy[-last,1],eddy[-last,2],color='k'
           ,marker='o',facecolor='none',s=300,zorder=3)

plt.title(tag[0:4]+'-'+tag[4:6]+'-'+tag[6:8])



savefig('/home/fontana/DISK2TB/DATA/AIS/plot.tiff')


















