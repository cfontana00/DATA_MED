# --------------------- #
#  2D plotting function #
# --------------------- #
from fun_gen import *
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
from cmcrameri import cm
import cmocean




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

# Create arborescence
os.system('mkdir -p '+diagdir+'/PLOT_2D')
os.system('mkdir -p '+diagdir+'/PLOT_2D/'+var)

# Initialize plot
# ---------------

# Load lon/lat
# ------------
fname=glob(outdir+'/*.nc')[0]
ds=xr.open_dataset(fname)
lon=ds['longitude']
lat=ds['latitude']
ds.close()

# Load proj
# ---------
exec('proj = ' + fig_proj)

# Init figure
# -----------
fig, ax = plt.subplots(1,1,figsize=(float(fig_sx), float(fig_sy)), subplot_kw={'projection': proj})
ax.set_extent([lon.min(),lon.max(),lat.min(),lat.max()])


# Tune figure
# -----------
resol = '10m'
land = cfeature.NaturalEarthFeature('physical', 'land', \
    scale=resol, edgecolor='k', facecolor=cfeature.COLORS['land'])

ax.add_feature(land, facecolor='lightgrey')
ax.add_feature(cfeature.BORDERS,edgecolor='darkgrey',zorder=2)
#ax.gridlines(draw_labels=True)
ax.coastlines(resolution=resol, color='darkgrey', linestyle='-', alpha=1)
gl = ax.gridlines(crs=proj, draw_labels=True,
linewidth=0.2, color='gray', alpha=1., linestyle='-')
gl.top_labels = True
gl.left_labels = True
gl.xlines = True
gl.ylines = True
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.xlabel_style = {'size': fig_tcklbl_size}
gl.ylabel_style = {'size': fig_tcklbl_size}



# Loop on files
# -------------
print('Processing')
for jd in range(jdini,jdend+1):

   # Get filename
   dobj = dt.datetime.fromordinal(jd)
   dtag = dobj.strftime('%Y%m%d')
   fname = glob(outdir+'/'+dtag+'_h-OGS--'+ftag+'-MITgcmBFM-pilot8-b*_fc-v01.nc' )[0]
   print(dtag)
  
   # Open file
   ds = xr.open_dataset(fname)
   var2d = ds[var][23,int(lev),:,:].squeeze() 
   ds.close()

   # Plot
   if vmod == 'auto' :
      p = plt.pcolor(lon,lat,var2d,cmap=cmap,zorder=1)
      cb = plt.colorbar(p,fraction=float(cb_fraction),pad=float(cb_pad))
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
   savedir=diagdir+'/PLOT_2D/'+var+'/LEV'+lev.zfill(2)
   os.system('mkdir -p '+savedir)

   plt.draw()
   plt.savefig(savedir+'/'+dtag+'_'+var+'.'+fig_fmt,dpi=int(fig_res)) 

   # Do any actions on the colorbar object (e.g. remove it)
   #cb.remove()

   p.remove()


   #plt.close()

   






















