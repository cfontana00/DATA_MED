# --------------------- #
#  2D plotting function #
# --------------------- #
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
import cv2


def gkern(l, sig):
    """\
    creates gaussian kernel with side length `l` and a sigma of `sig`
    """
    ax = np.linspace(-(l - 1) / 2., (l - 1) / 2., l)
    gauss = np.exp(-0.5 * np.square(ax) / np.square(sig))
    kernel = np.outer(gauss, gauss)
    return kernel / np.sum(kernel)



# Get args
# --------
config=sys.argv[1]  # Configuration name
var=sys.argv[2]     # Variable name
sat=sys.argv[3]     # Dataset dir


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
   if var != 'chl':
     var2d = get_var_2D(fname,var,hour,3) # !!!!
     var2d = np.array(var2d)

   else:
     var2d = get_integre_2D(fname,var,levels,hour)
     var2d = np.array(var2d)


     # Remove coastal zone
     mask = var2d.copy()

     mask[np.where(~np.isnan(mask))] = 0
     mask[np.where(np.isnan(mask)) ] = 1
  
     #kernel = np.ones((35,35))
     kernel = gkern(40,20)

     mask = cv2.dilate(mask, kernel, iterations=1)

     var2d[mask > 0] = np.nan

   # Load data for SST correction
   if var == 'thetao':
     t2m = load_meteo(config,jd,'t2m')


   # Title
   date = dt.datetime.fromordinal(jd)
   y,m,d = date.strftime('%Y'),date.strftime('%m'),date.strftime('%d')


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

   # Save file
   # ---------
   savedir = ddir+'/PLOT'
   os.system('mkdir -p '+savedir)


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
   print(jd,np.mean(var2d),np.mean(sat2d),perc)



plt.close()

   

