# ------------- #
# Plot AIS data #
# ------------- #
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

density = []

for year in ['2015','2024']:
  # Load AIS data
  # -------------
  ds = Dataset('/home/fontana/DISK2TB/DATA/AIS_DIFF/Cargo_Ships_'+year+'_04.nc',format='NETCDF4-CLASSIC')
  cargo = array(ds['DEFAULT'])
  dlon = array(ds['longitude'])
  dlat = array(ds['latitude'])
  ds.close()

  ds = Dataset('/home/fontana/DISK2TB/DATA/AIS_DIFF/Passenger_Ships_'+year+'_04.nc',format='NETCDF4-CLASSIC')
  person = array(ds['DEFAULT']) 
  ds.close()

  ds = Dataset('/home/fontana/DISK2TB/DATA/AIS_DIFF/Tankers_'+year+'_04.nc',format='NETCDF4-CLASSIC')
  tankers = array(ds['DEFAULT']) 
  ds.close()

  data = cargo + person + tankers
  data[data>20] = 0 

  density.append(data)


density = array(density)

print(2015,np.mean(density[0]))
print(2024,np.mean(density[1]))

diff = density[1]-density[0]

print(np.mean(diff)/np.mean(density[0])*100)




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


plt.pcolor(dlon,dlat,diff,vmin=-1,vmax=1,cmap=cmc.cm.roma_r)
cb = plt.colorbar(extend='both',fraction=float(cb_fraction_2D),
        pad=float(cb_pad_2D),label='Boats Density (hrs.km$^{-2}$)')


savefig('/home/fontana/DISK2TB/DATA/AIS_DIFF/diff.tiff')


















