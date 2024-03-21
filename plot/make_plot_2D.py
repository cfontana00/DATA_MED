# --------------------- #
#  2D plotting function #
# --------------------- #
from fun_gen import *
from fun_io import *
from fun_plot_2D import *
import sys,os
from glob import glob

import numpy as np
import xarray as xr
import datetime as dt

import cartopy.feature as cfeature
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import cmocean
import cmcrameri



# Get args
# --------
config=sys.argv[1]  # Configuration name
var=sys.argv[2]     # Variable name
lev=sys.argv[3]     # Z-level


# Load parameters
# ---------------
try :
  load_config(config)
  from fun_gen import *
except Exception as e :
  print('Error in argument or config')
  print(e)
  exit()

# Get current variable parameters
vname, ftag, cmap, islog, vmod, vmin, vmax, label, units\
        = load_variable(config,var)

# Create diagnostic arborescence
vdir = create_arbo(config,var,'PLOT_2D')

savedir= vdir+'/LEV'+lev.zfill(3)
os.system('mkdir -p '+savedir)

# Initialize plot
# ---------------

# Load lon/lat
# ------------
lon,lat,levels = load_coords()

# Load proj
# ---------
exec('proj = ' + fig_proj)

# Init figure
# -----------
extent = [lon.min(),lon.max(),lat.min(),lat.max()]
fig, ax = plt.subplots(1,1,figsize=(float(fig_sx), float(fig_sy)), subplot_kw={'projection': proj})
init_fig(ax,extent,proj)


# Loop on files
# -------------
print('Processing')
for jd in range(jdini,jdend+1):

   # Get filename
   fname,dtag = get_filename(jd,ftag)

   # Get 2D variable
   var2d = get_var_2D(fname,var,lev)

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

      if jd == jdini: # plot cb only once
        cb = plt.colorbar(extend='both',fraction=float(cb_fraction_2D),pad=float(cb_pad_2D),\
                label=label+' ('+units+')')

   # Save file
   # ---------
   os.system('mkdir -p '+savedir)

   plt.draw()

   fout = savedir+'/'+dtag+'_'+var+'.'+fig_fmt
   savefig(fout)

   p.remove()


plt.close()

   

