# ------------------------------------ #
#  Verticlal section plotting function #
# ------------------------------------ #
from fun_gen import *
from fun_io import *
from fun_plot_2D import init_fig
import sys,os
from glob import glob
import warnings
warnings.filterwarnings("ignore")

import numpy as np
from scipy.interpolate import griddata as gd
import xarray as xr
import datetime as dt

import cartopy.feature as cfeature
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")

from cmcrameri import cm
import cmocean


# Get args
# --------
config = sys.argv[1]  # Configuration name
var = sys.argv[2]     # Variable name
ori = sys.argv[3]     # Orientation (horizontal/vertical)
strpos = sys.argv[4]     # Slice position

pos = float(strpos)

# Exemple for Med sea
# -------------------
# python3 make_plot_section.py NWMED thetao horizontal 43
# python3 make_plot_section.py NWMED thetao vertical 9


# Load config file
# ----------------
load_config(config)
from fun_gen import *


# Get current variable parameters
vname, ftag, cmap, islog, vmod, vmin, vmax, label, units\
        = load_variable(config,var)

# Load lon/lat
# ------------
lon,lat,levels = load_coords()

levels = -np.flip(levels)


# Get parameters
# --------------
if ori == "horizontal": 

 lim1,lim2 = float(sec_lon1),float(sec_lon2)
 coord=lon
 idfix = np.amax ( np.where(  lat <= pos  )) 

else: 

 lim1,lim2 = float(sec_lat1),float(sec_lat2)
 coord=lat
 idfix = np.amax ( np.where(  lon <= pos  )) 

dep = float(sec_dep)

idmin = np.amin ( np.where(  coord >= lim1 ))
idmax = np.amax ( np.where(  coord <= lim2  ))
zmax = np.amin ( np.where( levels >= -dep )  )

resH,resV = float(sec_resH),float(sec_resV)


# Create diagnostic arborescence
vdir = create_arbo(config,var,'SECTION')
odir = vdir+'/'+ori+'_'+strpos+'_'+str(lim1)+'_'+str(lim2)
os.system('mkdir -p '+odir)



# ------------------- #
# Plot section on map #
# ------------------- #

# Init fig
fname = odir+'/map.'+fig_fmt

if not os.path.isfile(fname): # Skip if file already exist

  exec('proj = ' + fig_proj)
  extent = [lon.min(),lon.max(),lat.min(),lat.max()]
  fig, ax = plt.subplots(1,1,figsize=(float(fig_sx), float(fig_sy)), subplot_kw={'projection': proj})

  init_fig(ax,extent,proj)

  pos = float(pos)
  if ori == "horizontal": 
    plt.plot([lim1,lim2],[pos,pos],'r-')
  else:
    plt.plot([pos,pos],[lim1,lim2],'r-')

  savefig(fname)

  plt.close()



# ------------ #
# Plot section #
# ------------ #

icoord = np.arange(coord[0],coord[-1],0.01)
icoord = coord[idmin:idmax]
ilev =  np.arange(levels[zmax],levels[-1],resV)



# Loop on files
# -------------
print('\nProcessing')
for jd in range(jdini,jdend+1):

  for hour in range(0,1):  
    # Get var
    fname,dtag = get_filename(jd,ftag)
    var3d = get_var_3D(fname,hour,var)

    if ori == "horizontal":
      sec = var3d[:,idfix,idmin:idmax]
    else:
      sec = var3d[:,idmin:idmax,idfix]

    fig, ax = plt.subplots(1,1,figsize=(float(fig_secx), float(fig_secy)))
    sec = np.flip(sec)
    sec = np.fliplr(sec)

    # Interpolate data
    X,Y = np.meshgrid(coord[idmin:idmax],levels)  
    X,Y = X.flatten(),Y.flatten()
    sec = sec.flatten()

    sec[sec > 10000]=np.nan

    XI,YI = np.meshgrid(icoord,ilev)
    isec = gd((X,Y),sec,(XI,YI))


    p = plt.pcolor(XI,YI,isec,cmap=cmap,vmin=vmin,vmax=vmax)
    cb= plt.colorbar(p,extend='both',fraction=float(cb_fraction_sec),\
          pad=float(cb_pad_sec),label=label+' ('+units+')')


    plt.ylabel("Depth (m)")

    if ori == 'horizontal':
      plt.xlabel("Longitude (°)")
    else:
      plt.xlabel("Latitude (°)")

    # Title
    date = dt.datetime.fromordinal(jd)
    y,m,d = date.strftime('%Y'),date.strftime('%m'),date.strftime('%d')

    title = y+'-'+m+'-'+d+' '+str(hour).zfill(2)+'h'
    plt.title(title)

    savefig( odir+'/'+dtag+str(hour).zfill(2)+'_'+var+'.'+fig_fmt)
    #plt.show()
    plt.close()






















