# --------------------- #
# 2D Plotting functions #
# --------------------- #
from fun_gen import *
from fun_io import get_filename,get_var_2D,get_integre_2D,get_sat_2D
import cartopy.feature as cfeature
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.pyplot as plt
import numpy as np
import os

# -------------------- #
# Initialize 2D figure #
# -------------------- #
def init_fig(ax,extent,proj):

  from fun_gen import fig_sx,fig_sy,resol,fig_proj
  from fun_gen import fig_tcklbl_size

  ax.set_extent(extent)

  land = cfeature.NaturalEarthFeature('physical', 'land', \
  scale=resol, facecolor=cfeature.COLORS['land'])

  ax.add_feature(land, facecolor='lightgrey')
  ax.add_feature(cfeature.BORDERS,edgecolor='darkgrey',zorder=2)
  ax.coastlines(resolution=resol, color='darkgrey', linestyle='-', alpha=1)
  gl = ax.gridlines(crs=proj, draw_labels=True,
  linewidth=0.2, color='gray', alpha=1., linestyle='-')
  gl.top_labels = False
  gl.right_labels = False
  gl.left_labels = True
  gl.xlines = True
  gl.ylines = True
  gl.xformatter = LONGITUDE_FORMATTER
  gl.yformatter = LATITUDE_FORMATTER
  gl.xlabel_style = {'size': fig_tcklbl_size}
  gl.ylabel_style = {'size': fig_tcklbl_size}




# ------------- #
# Get vmin/vmax #
# ------------- #
def get_clim(jdini,jdend,config,var,sat):

  from fun_gen import diagdir
  from fun_io import load_coords

  lon,lat,levels = load_coords()
  
  # Initialize globla array
  arr = [np.nan]

  # Load variable parameters
  vname, ftag, cmap, islog, vmod, vmin, vmax, label, units\
       = load_variable(config,var)

  ddir = os.path.join(diagdir,config,sat,var,'ITP_NC')


  if var == 'chl':
    hour = 12
  elif var == 'thetao':
    hour = 0

  # Loop on days
  for jd in range(jdini,jdend+1):

    print(jd)
    # Get filename
    fname,dtag = get_filename(jd,ftag)

    ddir = os.path.join(diagdir,config,sat,var,'ITP_NC')
    sat2d = get_sat_2D(ddir+'/'+var+'_'+dtag+'.nc',var)

    if var == 'thetao':
      var2d = get_var_2D(jd,jdini,fname,var,hour,1) # !!!!
      sat2d = sat2d - 273.15
      percentile = 95

    elif var == 'chl':
      var2d = get_integre_2D(jd,jdini,fname,var,levels,hour)
      percentile = 98


    var2d = np.array(var2d[::4])
    sat2d = np.array(sat2d[::4])

    arr = np.concatenate([arr,var2d.flatten()])
    arr = np.concatenate([arr,sat2d.flatten()])

  arr = arr[~np.isnan(arr)]
  lower = (100 - percentile) / 2
  upper = 100 - lower

  vmin = np.percentile(arr, lower)
  vmax = np.percentile(arr, upper)

  return vmin,vmax




     
     

     





 










