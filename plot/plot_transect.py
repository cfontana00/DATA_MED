# ------------------------------------ #
#  Verticlal section plotting function #
# ------------------------------------ #
import warnings
warnings.filterwarnings("ignore")

from fun_gen import *
from fun_io import *
from fun_plot_2D import init_fig
import sys,os,argparse
from glob import glob

import numpy as np
from scipy.interpolate import griddata as gd
from scipy import interpolate
import xarray as xr
import datetime as dt

import cartopy.feature as cfeature
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdates

matplotlib.use("Agg")

import cmocean
import cmcrameri


def argument():
    parser = argparse.ArgumentParser(description = '',formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(   '--config', '-c',
                                type = str,
                                required = True,
                                help ='Configuration name'
                                )
    parser.add_argument(   '--variable',"-v",
                                type = str,
                                required = True,
                                help = 'variable : thetao or chl')
    return parser.parse_args()


# Get args
# --------
args = argument()
config = args.config    # Configuration name
var = args.variable     # Variable name


# Load config file
# ----------------
load_config(config)
from fun_gen import *


# Get current variable parameters
vname, ftag, cmap, islog, vmod, vmin, vmax, label, units\
        = load_variable(config,var)

# Create arborescence
os.system('mkdir -p '+diagdir+'/'+config+'/TRANSECT/')
os.system('mkdir -p '+diagdir+'/'+config+'/TRANSECT/'+trans_name)

odir = diagdir+'/'+config+'/TRANSECT/'+trans_name+'/'+var
os.system('mkdir -p '+odir)



# Load lon/lat
# ------------
lon,lat,levels = load_coords()

# Load transect position file
# ---------------------------
pos = np.loadtxt(trans_file)


# ------------- #
# Plot transect #
# ------------- #
zmax = np.amin ( np.where( levels >= trans_depth )  )

resV = trans_resV
ilev =  np.arange(levels[0],levels[zmax],resV)
ilon = ilev.copy()
ilat = ilev.copy()

# Interpolate transect
tdini = datetime.strptime(trans_ini,'%Y-%m-%d').toordinal()
tdend = datetime.strptime(trans_end,'%Y-%m-%d').toordinal()


tjd = []
for p in pos:
  tjd.append(datetime.strptime(str(int(p[0])),'%Y%m%d').toordinal())

tjd = np.array(tjd)


idx = np.where( (tjd[:] >= tdini) & (tjd[:] <= tdend+2))

idx = np.array(idx).squeeze()


flon = interpolate.interp1d(range(tdini,tdend+1), pos[idx,1].squeeze() )
flat = interpolate.interp1d(range(tdini,tdend+1), pos[idx,2].squeeze() )

x_new = np.arange(tdini,tdend,1/24.)


tlon = flon(x_new).squeeze()
tlat = flat(x_new).squeeze()

trans = []


#for i in range(0,tlon.shape[0]):
#  print(x_new[i],tlon[i])
#exit()
 

# Loop on files
# -------------
print('\nProcessing')
for jd in range(tdini,tdend):

  # Get var
  fname,dtag = get_filename(jd,ftag)

  print('\n')
  print(dtag)
  print(fname)


  for hour in range(0,24):

    # Get transect position
    diff = abs(x_new - (float(jd)+float(hour)/24.))

    idx = np.where(diff == np.amin(diff))

    ilon[:] = tlon[idx]
    ilat[:] = tlat[idx]

    val = get_model_val_3d(fname,hour,vname,\
               lon,lat,levels,\
                 ilon,ilat,ilev)

    if vname == 'zooc':  # !!!!! TEMPORARY FIX
       val = val/12.

    #print(ilon[0],ilat[0],val[30])

    trans.append(val)


trans = np.array(trans)

#print(trans)


# Plot transect
# -------------
fig, ax = plt.subplots(1,1,figsize=(float(fig_secx), float(fig_secy)))


xticks = x_new - dt.datetime(1970,1,1).toordinal()

YI,XI = np.meshgrid(-np.flip(ilev),xticks)
trans = np.flip(trans)
trans = np.flipud(trans)


p = plt.pcolor(XI,YI,trans,cmap=cmap,vmin=vmin,vmax=vmax)
cb= plt.colorbar(p,extend=cb_extend,fraction=float(cb_fraction_sec),\
        pad=float(cb_pad_sec),label=label+' ('+units+')')

# Tune graph
loc = mdates.AutoDateLocator()
ax.xaxis.set_major_locator(loc)
ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(loc))



plt.ylabel("Depth (m)")
plt.xlabel("Date")


savefig(odir+'/transect'+'.'+fig_fmt)
plt.close()


