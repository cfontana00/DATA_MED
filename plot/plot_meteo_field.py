# ----------------- #
# Plot meteo fields #
# ----------------- #

import warnings
warnings.simplefilter("ignore")

from fun_gen import *
from fun_io import *
from fun_plot_2D import *
from fun_meteo import load_meteo
import sys,os
from glob import glob

import numpy as np
from numpy import array as npa
import xarray as xr
import datetime as dt

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
config = sys.argv[1]  # Configuration name
var = sys.argv[2]     # Variable name

# Load parameters
# ---------------
load_config(config)
from fun_gen import *


odir = os.path.join(diagdir,config,'METEO/PLOT')
os.system('mkdir -p '+odir)

odir = os.path.join(diagdir,config,'METEO/PLOT',var)
os.system('mkdir -p '+odir)

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


# Get current variable parameters
vname, ftag, cmap, islog, vmod, vmin, vmax, label, units\
      = load_variable(config,var)

# Loop on files
# -------------
print('Processing')
for jd in range(jdini,jdend+1):

    # Date tag
    dobj = dt.datetime.fromordinal(jd)
    dtag = dobj.strftime('%Y%m%d')


    # Load meteo file
    var2d = load_meteo(config,jd,var)

    extent = [lon.min(),lon.max(),lat.min(),lat.max()]


    # Plot
    if vmod == 'auto' :
      # !!! TO CHANGE
      p = plt.pcolor(lon,lat,var2d,cmap=cmap,zorder=1)
      #cb = plt.colorbar(p,fraction=float(cb_fraction),pad=float(cb_pad))
    else:

      if not islog :
        p = plt.pcolor(lon,lat,var2d,cmap=cmap,vmin=vmin,vmax=vmax,zorder=1)
      else:
        p = plt.pcolor(lon,lat,var2d,cmap=cmap,norm=colors.LogNorm(vmin=vmin,vmax=vmax),zorder=1)

    if cb_done == 'False': # plot cb only once
        cb = plt.colorbar(extend='both',fraction=float(cb_fraction_2D),pad=float(cb_pad_2D),\
                label=label+' ('+units+')')
        cb_done = 'True'


    # Title
    date = dt.datetime.fromordinal(jd)
    y,m,d = date.strftime('%Y'),date.strftime('%m'),date.strftime('%d')

    title = y+'-'+m+'-'+d
    plt.title(title)

    # Save file
    # ---------
    plt.draw()

    fout = odir+'/'+dtag+'_'+var+'.'+fig_fmt
    savefig(fout)

    # Erase pcolor plot
    p.remove()

plt.close()

