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
import subprocess


import numpy as np
from numpy import array as npa
import xarray as xr
import datetime as dt
#import cv2

import cartopy.feature as cfeature
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.colors as colors
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter,FixedLocator,NullFormatter,LogLocator,FuncFormatter,MaxNLocator,StrMethodFormatter,MultipleLocator,ScalarFormatter
import matplotlib
matplotlib.use("Agg")

import cmocean

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

# Load mask
mask = xr.open_dataset(maskfile)['tmask']
mask = np.array(mask[0,:,:].squeeze(),dtype=float)
mask[np.where(mask==0)] = np.nan
mask[np.where(mask==1)] = 0
sy,sx = mask.shape

# Loop on files
# -------------
print('Processing')

for jd in range(jdini,jdend+1):


 # Get current variable parameters
 vname, ftag, cmap, islog, vmod, vmin, vmax, label, units\
       = load_variable(config,var)
 
 for hour in hours:

   # PLOT MODEL
   # ----------

   # Get filename
   fname,dtag = get_filename(jd,ftag)

   # Get 2D variable
   if var == 'thetao':

     var2d = get_var_2D(jd,jdini,fname,var,hour,1) # !!!!
     var2d = np.array(var2d)
     percentile = 95

   elif var == 'chl':

     var2d = get_integre_2D(jd,jdini,fname,var,levels,hour)
     var2d = np.array(var2d)
     percentile = 98

     # Remove coastal zone
     #mask = var2d.copy()
   
     kernel = gkern(int(glength),int(gsigma))

     # TO CHANGE !!!!!
     #mask = cv2.dilate(mask, kernel, iterations=1)


   var2d = var2d+mask # faster than where
   var2d[np.where(var2d == 0 )] = np.nan

   #var2d[np.where(var2d == 0 )] = np.nan # quick fix

   ddir = os.path.join(diagdir,config,sat,var,'ITP_NC')
   fname = ddir+'/'+var+'_'+dtag+'.nc'

   data_sat = 0
   try:

     sat2d = get_sat_2D(fname,var)
     sat2d = np.array(sat2d)
  
     if var == 'thetao':
        sat2d = sat2d - 273.15

     data_sat = 1

   except:
     sat2d = var2d.copy()
     sat2d[:] = np.nan

   #sat2d[np.where(mask == 0 )] = np.nan
   sat2d[np.where( np.isnan(var2d))] = np.nan 

   # PLOT DATA
   # ---------
   # Plot
   if vmod == 'auto' :


      # Search min/max in data
      var2d[np.where(var2d) == 0] = np.nan
      idx = np.where( ~np.isnan(var2d) )
      arr = var2d[idx].flatten()


      #try :
      if 1 == 1:
        idx = np.where( ~np.isnan(sat2d) )
        arr = np.concatenate([arr,sat2d[idx].flatten()])
      #except:
      #  pass

      # Percentile for vmin/vmax
      lower = (100 - percentile) / 2
      upper = 100 - lower

      vmin = np.percentile(arr, lower)
      vmax = np.percentile(arr, upper)

      #print("MIN",vmin)


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

   if not islog :      
     p2 = ax2.pcolor(lon,lat,sat2d,cmap=cmap,vmin=vmin,vmax=vmax,zorder=1)

   else:
     p2 = ax2.pcolor(lon,lat,sat2d,cmap=cmap,norm=colors.LogNorm(vmin=vmin,vmax=vmax),zorder=1)


   if cb_done == 'False': # plot cb only once

     cb = plt.colorbar(p2,extend='both',fraction=float(cb_fraction_sat),pad=float(cb_pad_sat),\
              label=label+' ('+units+')',ax=ax2)
     cb.set_label(label=label+' ('+units+')',fontsize=cb_lbl_size_sat)
     cb.ax.tick_params(labelsize=cb_lbl_size_sat)

     cb.ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.2f}'))

     if var == 'chl':
       tick_values = np.logspace(np.log10(vmin), np.log10(vmax), num=5)
       cb.ax.yaxis.set_minor_formatter(NullFormatter())
       cb.ax.yaxis.set_major_formatter(NullFormatter())

       cb.set_ticks(tick_values)
       cb.set_ticklabels([f'{v:.2f}' for v in tick_values]) 


     cb_done = 'True'

   else: # just adjust vmin/vmax
     cb.mappable.set_clim(vmin, vmax)  


   # Add mention if data are not available
   if data_sat == 0 :
      ax2.text(0.1,0.5,'No data available yet',transform=ax2.transAxes,va='center',ha='left',fontsize=12)


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
  
   # Keep only corresponding data
   if data_sat == 1:
     var2d = np.array(var2d)[idx_good]

   idx_good = np.array(idx_good)
   idx_tot = np.array(idx_tot)

   perc = 1
   if data_sat == 1: 
     perc = float(idx_good.shape[1])/float(idx_tot.shape[1])

   time_series.append([jd,np.nanmean(var2d),np.mean(sat2d),perc])
   print(jd,np.nanmean(var2d),np.mean(sat2d),perc)

# Save time series 
np.savetxt(ddir+'/time_series.dat',np.array(time_series))


plt.close()

   

