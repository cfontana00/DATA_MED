# --------------------- #
#  2D plotting function #
# --------------------- #
import warnings
warnings.simplefilter("ignore")

from fun_gen import *
from fun_io import *
from fun_plot_2D import *
from fun_meteo import load_meteo
import sys,os,argparse
from glob import glob

import numpy as np
from numpy import array as npa
import xarray as xr
import datetime as dt
import cv2

import cartopy.feature as cfeature
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.colors as colors
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import matplotlib
matplotlib.use("Agg")

import cmocean
import cmcrameri

def gkern(l, sig):
    """\
    creates gaussian kernel with side length `l` and a sigma of `sig`
    """
    ax = np.linspace(-(l - 1) / 2., (l - 1) / 2., l)
    gauss = np.exp(-0.5 * np.square(ax) / np.square(sig))
    kernel = np.outer(gauss, gauss)
    return kernel / np.sum(kernel)


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
    parser.add_argument(   '--satellite',"-s",
                                type = str,
                                required = True,
                                help = 'satellite : ex CMEMS')
    return parser.parse_args()



# Get args
# --------
args = argument()
config = args.config    # Configuration name
var = args.variable     # Variable name
sat = args.satellite    # Dataset dir



# Load parameters
# ---------------
load_config(config)
from fun_gen import *

# Create diagnostic arborescence
#null = create_arbo(config,var,'PLOT_SAT')
#os.system('mkdir -p '+savedir)

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

plt.figure(1)

fig, (ax1, ax2) = plt.subplots(1,2,figsize=(float(fig_sx_sat), float(fig_sy_sat)), subplot_kw={'projection': proj},constrained_layout=True)
init_fig(ax1,extent,proj)
init_fig(ax2,extent,proj)

time_series = []

if var == 'chl':
  hours = range(12,13)
elif var == 'thetao':
  hours = range(0,1)

# Loop on files
# -------------
print('Processing')
for jd in range(jdini,jdend+1):

 for hour in hours:
   # Get current variable parameters
   vname, ftag, cmap, islog, vmod, vmin, vmax, label, units\
        = load_variable(config,var)


   # PLOT MODEL
   # ----------

   # Get filename
   fname,dtag = get_filename(jd,ftag)


   # Get 2D variable
   if var == 'thetao':

     var2d = get_var_2D(fname,var,hour,1) # !!!!
     var2d = np.array(var2d)

   elif var == 'chl':
     var2d = get_integre_2D(fname,var,levels,hour)
     var2d = np.array(var2d)


     # Remove coastal zone
     mask = var2d.copy()

     mask[np.where(~np.isnan(mask))] = 0
     mask[np.where(np.isnan(mask)) ] = 1
  
     #kernel = np.ones((35,35))
     kernel = gkern(int(glength),int(gsigma))

     mask = cv2.dilate(mask, kernel, iterations=1)

     var2d[mask > 0] = np.nan


   # Plot
   if vmod == 'auto' :
      # !!! TO CHANGE
      p1 = ax1.pcolor(lon,lat,var2d,cmap=cmap,zorder=1)
      #cb = plt.colorbar(p,fraction=float(cb_fraction),pad=float(cb_pad))
   else:

      if not islog :      
        p1 = ax1.pcolor(lon,lat,var2d,cmap=cmap,vmin=vmin,vmax=vmax,zorder=1)
      else:
        p1 = ax1.pcolor(lon,lat,var2d,cmap=cmap,norm=colors.LogNorm(vmin=vmin,vmax=vmax),zorder=1)


   # Title
   date = dt.datetime.fromordinal(jd)
   y,m,d = date.strftime('%Y'),date.strftime('%m'),date.strftime('%d')

   title = 'Model '+y+'-'+m+'-'+d+' '+str(hour).zfill(2)+'h'
   #ax1.title.set_text(title,fontsize=fig_lbl_size)
   ax1.set_title(title,fontsize=fig_title_size)


   # PLOT DATA
   # ---------
   ddir = os.path.join(diagdir,config,sat,var,'ITP_NC')
   fname = ddir+'/'+var+'_'+dtag+'.nc'
   sat2d = get_sat_2D(fname,var)
   sat2d = np.array(sat2d)

   if var == 'chl':
     sat2d[mask>0] = np.nan


   # Apply correction to sst

   if var == 'thetao':
      sat2d = sat2d - 273.16   # Kelvin to C

      #t2m = np.array(t2m) - 273.16
      #idx = np.where(sat2d<9999)
      #bias = np.mean(sat2d[idx]-t2m[idx])
      #print(bias)

      sat2d = sat2d # SST correction


   if not islog :      
     p2 = ax2.pcolor(lon,lat,sat2d,cmap=cmap,vmin=vmin,vmax=vmax,zorder=1)
     #p2 = ax2.pcolor(lon,lat,sat2d-t2m,cmap=cmap,zorder=1)
   else:
     p2 = ax2.pcolor(lon,lat,sat2d,cmap=cmap,norm=colors.LogNorm(vmin=vmin,vmax=vmax),zorder=1)


   if cb_done == 'False': # plot cb only once
      cb = plt.colorbar(p2,extend='both',fraction=float(cb_fraction_sat),pad=float(cb_pad_sat),\
              label=label+' ('+units+')',ax=ax2)
      cb.set_label(label=label+' ('+units+')',fontsize=cb_lbl_size_sat)
      cb.ax.tick_params(labelsize=cb_lbl_size_sat)

      cb_done = 'True'

      if islog : 
         cb.ax.yaxis.set_minor_formatter(FormatStrFormatter('%.2f'))
         cb.ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

         cb.ax.tick_params(axis='both', which='both', labelsize=tck_size_ts)


   # Tune


   # Title
   title = 'Satellite '+y+'-'+m+'-'+d+' '+str(hour).zfill(2)+'h'
   plt.title(title,fontsize=fig_title_size)

   # Save file
   # ---------
   savedir = ddir+'/PLOT'
   os.system('mkdir -p '+savedir)

   plt.draw()

   fout = savedir+'/'+dtag+str(hour).zfill(2)+'_'+var+'.'+fig_fmt
   savefig(fout)

   p1.remove()
   p2.remove()

   # Store time series
   # -----------------

   idx_good = np.where( (~np.isnan(sat2d)) & (~np.isnan(var2d)) )
   idx_tot = np.where( ~np.isnan(var2d) )

   sat2d = sat2d[idx_good]
   var2d = np.array(var2d)[idx_good]

   idx_good = np.array(idx_good)
   idx_tot = np.array(idx_tot)

   perc = float(idx_good.shape[1])/float(idx_tot.shape[1])

   time_series.append([jd,np.mean(var2d),np.mean(sat2d),perc])
   #print(jd,np.mean(var2d),np.mean(sat2d),perc)



# Save time series 
np.savetxt(ddir+'/time_series.dat',np.array(time_series))


plt.close()

   

