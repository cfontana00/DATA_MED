# --------------------- #
#  2D plotting function #
# --------------------- #
import warnings
warnings.simplefilter("ignore")

import shutil

import gc, types
from fun_gen import *
from fun_io import *
from fun_plot_2D import *
from fun_meteo import load_meteo
import sys,os,argparse
from glob import glob
import subprocess
import matplotlib.colors as mcolors
import pickle


import numpy as np
from numpy import array as npa
import xarray as xr
import datetime as dt
#import cv2

import cartopy.feature as cfeature
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib
matplotlib.use("Agg")
import matplotlib.colors as colors
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter,FixedLocator,NullFormatter,LogLocator,FuncFormatter,MaxNLocator,StrMethodFormatter,MultipleLocator,ScalarFormatter
from matplotlib.gridspec import GridSpec,GridSpecFromSubplotSpec,GridSpecFromSubplotSpec

import cmocean
import json
import glob

import io 
import cProfile


def _noop(*args, **kwargs):
    return None

def _identity(x):
    return x

class NoLambdaPickler(pickle.Pickler):
    def reducer_override(self, obj):
        # __name__ == '<lambda>' distingue les vraies lambdas des fonctions nommées
        if callable(obj) and getattr(obj, '__name__', None) == '<lambda>':
            return (_identity, (_noop,))  # reconstruit comme _identity(_noop) = _noop
        return NotImplemented




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

# Load domain map
with open("../config/domains.json") as f:
    domain_map = json.load(f)

domains = domain_map["domains"]
up = domains[config[0:3]]["parent"]


# Load eventually CMEMS model data
if up == 'CMEMS':

  pars = np.loadtxt('../config/cmems_'+config+'.dat',dtype=str)

  # Loop on variables
  for par in pars:
    if par[0] == var:
      break

  cvar = par[4]

  fname = os.path.join(diagdir,config,sat,var,'model_cmems.nc')
  ds = xr.open_dataset(fname)
  uplon = ds['longitude']
  uplat = ds['latitude']
  upvar = ds[var]
  ds.close()

  label3 = "CMEMS"

else:
  label3 = "Regional MER" 



ddir = os.path.join(diagdir,config,sat,var,'ITP_NC')
savedir = ddir+'/PLOT'
os.makedirs(savedir, exist_ok=True)

# Load lon/lat
# ------------
lon,lat,levels = load_coords()

# Load mask
mask = xr.open_dataset(maskfile)['tmask']
mask = np.array(mask[0,:,:].squeeze(),dtype=float)
mask[np.where(mask==0)] = np.nan
mask[np.where(mask==1)] = 0
sy,sx = mask.shape

# Compute layer thickness
ds = xr.open_dataset(maskfile)
depth = ds["depth"].values[:7]

interfaces = np.concatenate([
    [0.0],
    (depth[:-1] + depth[1:]) / 2,
])
thickness = np.diff(interfaces)
thickness = np.append(thickness, depth[6] - (depth[5] + depth[6]) / 2)




# Load proj
# ---------
exec('proj = ' + fig_proj)
cb_done = 'False'

# Init figure
# -----------
extent = [lon.min(),lon.max(),lat.min(),lat.max()]

plt.figure(1)

layout = domains[config[0:3]]["display"]["layout"]
cb_fraction = domains[config[0:3]]["display"]["cb_fraction"]

if layout == 'horizontal':
  nrows, ncols ,orientation = 1,3,'vertical'
else:
  nrows, ncols ,orientation = 3,1,'horizontal'

# Get vmin/vmax
#print('BEFORE')
#vmin,vmax = get_clim(jdini,jdend,config,var,sat)
#print('AFTER')
#exit()



fig, (ax1, ax2, ax3) = plt.subplots(nrows,ncols,figsize=(float(fig_sx_sat), float(fig_sy_sat)), subplot_kw={'projection': proj},constrained_layout=True)


"""
if nrows == 3:
    fig.set_constrained_layout_pads(hspace=0.05)
else:
    fig.set_constrained_layout_pads(wspace=0.05)
"""

init_fig(ax1,extent,proj)
init_fig(ax2,extent,proj)
init_fig(ax3,extent,proj)


"""
for i, ax in enumerate(fig.axes):
    print(f"ax[{i}] type : {type(ax)}")
    print(f"ax[{i}] projection : {getattr(ax, 'projection', 'N/A')}")
"""

time_series = []

if var == 'chl':
  hours = range(12,13)
elif var == 'thetao':
  hours = range(0,1)

# Initialize array for vmin/vmax
arr = [np.nan]

# Loop on files
# -------------
print('Processing')

# Get current variable parameters
vname, ftag, cmap, islog, vmod, vmin, vmax, label, units\
       = load_variable(config,var)

for jd in range(jdini,jdend+1):
#for jd in range(jdini,jdini+1):
 
 for hour in hours:

   # PLOT MODEL
   # ----------

   # Get filename
   fname,dtag = get_filename(jd,ftag)

   # Get upper coords
   if up != 'CMEMS':
     maskfileup = maskfile.replace(config[0:3].lower(),up.lower())
     ds = xr.open_dataset(maskfileup)
     uplon = np.array(ds['longitude'])
     uplat = np.array(ds['latitude'])
     ds.close()


   # Get 2D variable
   if var == 'thetao':

     #var2d = get_var_2D(jd,jdini,fname,var,hour,1) # !!!!
     var2d = get_var_sst(jd,jdini,fname,var,hour,thickness) # !!!!

     var2d = np.array(var2d)
     percentile = 99

     # Get upper grid if HR
     if up != 'CMEMS':
       fup = fname.replace(config[0:3],up)
       up2d = get_regional_2D(jd,jdini,fup,var,hour,0) # !!!!
       up2d = np.array(up2d)


   elif var == 'chl':

     #var2d = get_integre_2D(jd,jdini,fname,var,levels,hour)
     var2d = get_var_2D(jd,jdini,fname,var,hour,1) # !!!!

     var2d = np.array(var2d)
     percentile = 99

     # Get upper grid if HR
     if up != 'CMEMS':
       fup = fname.replace(config[0:3],up)
       up2d = get_regional_2D(jd,jdini,fup,var,hour,0) # !!!!
       up2d = np.array(up2d)
   
        

   # Get upper grid
   if up == 'CMEMS':
     up2d = upvar[jd-jdini,:,:].squeeze()

     # Remove coastal zone
     #mask = var2d.copy()
     #kernel = gkern(int(glength),int(gsigma))

     # TO CHANGE !!!!!
     #mask = cv2.dilate(mask, kernel, iterations=1)


   var2d = var2d+mask # faster than where
   var2d[np.where(var2d == 0 )] = np.nan

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
      arr = np.concatenate([arr,var2d[idx].flatten()])


      #try :
      if 1 == 1:
        idx = np.where( ~np.isnan(sat2d) )
        arr = np.concatenate([arr,sat2d[idx].flatten()])
      #except:
      #  pass

      if cb_done == 'False':
        # Percentile for vmin/vmax
        lower = (100 - percentile) / 2
        upper = 100 - lower

        arr = arr[~np.isnan(arr)]

        vmin = np.percentile(arr, lower)
        vmax = np.percentile(arr, upper)

    
   if not islog :      
     p1 = ax1.pcolor(lon,lat,var2d,cmap=cmap,vmin=vmin,vmax=vmax,zorder=1)
     p2 = ax2.pcolor(uplon,uplat,up2d,cmap=cmap,vmin=vmin,vmax=vmax,zorder=1)
     p3 = ax3.pcolor(lon,lat,sat2d,cmap=cmap,vmin=vmin,vmax=vmax,zorder=1)
   else:
     p1 = ax1.pcolor(lon,lat,var2d,cmap=cmap,norm=colors.LogNorm(vmin=vmin,vmax=vmax),zorder=1)
     p2 = ax2.pcolor(uplon,uplat,up2d,cmap=cmap,norm=colors.LogNorm(vmin=vmin,vmax=vmax),zorder=1)
     p3 = ax3.pcolor(lon,lat,sat2d,cmap=cmap,norm=colors.LogNorm(vmin=vmin,vmax=vmax),zorder=1)

   # Title
   date = dt.datetime.fromordinal(jd)
   y,m,d = date.strftime('%Y'),date.strftime('%m'),date.strftime('%d')

   title = 'High Resolution MER '+y+'-'+m+'-'+d+' '+str(hour).zfill(2)+'h'
   #ax1.title.set_text(title,fontsize=fig_lbl_size)
   ax1.set_title(title,fontsize=fig_title_size)

   title = label3+' '+y+'-'+m+'-'+d+' '+str(hour).zfill(2)+'h'
   ax2.set_title(title,fontsize=fig_title_size)

   title = 'Satellite '+y+'-'+m+'-'+d+' '+str(hour).zfill(2)+'h'
   ax3.set_title(title,fontsize=fig_title_size)



   if cb_done == 'False': # plot cb only once

     norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
     sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
     cb = plt.colorbar(p3,extend='both',fraction=float(cb_fraction),pad=float(cb_pad_sat),\
              label=label+' ('+units+')',ax=ax3,orientation=orientation)
     #cb = fig.colorbar(sm, cax=cax, label=label+' ('+units+')')
     cb.set_label(label=label+' ('+units+')',fontsize=cb_lbl_size_sat)
     cb.ax.tick_params(labelsize=cb_lbl_size_sat)

     cb.ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.2f}'))

     if var == 'chl':
       tick_values = np.logspace(np.log10(vmin), np.log10(vmax), num=5)
       cb.ax.yaxis.set_minor_formatter(NullFormatter())
       cb.ax.yaxis.set_major_formatter(NullFormatter())
       cb.ax.xaxis.set_minor_formatter(NullFormatter())
       cb.ax.xaxis.set_major_formatter(NullFormatter())

       cb.set_ticks(tick_values)
       cb.set_ticklabels([f'{v:.2f}' for v in tick_values]) 


     cb_done = 'True'

   else: # just adjust vmin/vmax
     pass
     #cb.mappable.set_clim(vmin, vmax)  

   # Add mention if data are not available
   if data_sat == 0 :
      ax3.text(0.1,0.5,'No data available yet',transform=ax3.transAxes,va='center',ha='left',fontsize=12)



   # Save file
   # ---------
   #plt.draw()

   fig._pcm = [p1, p2, p3]
   fig._cbar = cb
   fout = savedir+'/'+dtag+str(hour).zfill(2)+'_'+var+'.pkl'


   
   """
   for obj in gc.get_referrers(fig):
    pass  # pas utile

   # Chercher toutes les lambdas dans les attributs de chaque axe
   for i, ax in enumerate(fig.axes):
    for attr_name in dir(ax):
        try:
            attr = getattr(ax, attr_name)
            if isinstance(attr, types.LambdaType):
                print(f"ax[{i}].{attr_name} -> lambda")
            if isinstance(attr, list):
                for j, item in enumerate(attr):
                    if isinstance(item, types.LambdaType):
                        print(f"ax[{i}].{attr_name}[{j}] -> lambda")
                    if hasattr(item, '__dict__'):
                        for k, v in item.__dict__.items():
                            if isinstance(v, types.LambdaType):
                                print(f"ax[{i}].{attr_name}[{j}].{k} -> lambda")
        except Exception:
            pass

   """


   fig._pcm = [p1, p2, p3]
   fig._cbar = cb
   fout = savedir+'/'+dtag+str(hour).zfill(2)+'_'+var+'.pkl'

   total, used, free = shutil.disk_usage("/")
   if free / 1e6 < 700:
     print(f"No space left on the device ({free:.0f} Mo free) — exiting")
     break
   

   with open(fout, "wb") as f:
         NoLambdaPickler(f, protocol=5).dump(fig)


   #fout = savedir+'/'+dtag+str(hour).zfill(2)+'_'+var+'.'+fig_fmt
   #savefig(fout)
   #plt.savefig('test.jpg', bbox_inches='tight', dpi=150, pil_kwargs={'quality': 95})

   p1.remove()
   p2.remove()
   p3.remove()


   # Store time series
   # -----------------

   idx_good = np.where( (~np.isnan(sat2d)) & (~np.isnan(var2d)) )
   idx_tot = np.where( ~np.isnan(var2d) )

   sat2d = sat2d[idx_good]
  
   # Keep only corresponding data
   if data_sat == 1:
     var2d = np.array(var2d)[idx_good]
     up2d = np.array(up2d)[idx_good]

   #if up == 'CMEMS':
   upmean = np.nanmean(up2d)
   #else:
   #  upmean = np.nan

   idx_good = np.array(idx_good)
   idx_tot = np.array(idx_tot)

   perc = 1
   if data_sat == 1: 
     perc = float(idx_good.shape[1])/float(idx_tot.shape[1])

   time_series.append([jd,np.nanmean(var2d),np.mean(sat2d),upmean,perc])
   print(jd,np.nanmean(var2d),np.mean(sat2d),upmean,perc)


# Get final vmin/vmax
lower = (100 - percentile) / 2
upper = 100 - lower


arr = arr[~np.isnan(arr)]
global_vmin = np.percentile(arr, lower)
global_vmax = np.percentile(arr, upper)
del arr

# Reload all figures
pkl_files = sorted(glob.glob(savedir+"/*.pkl"))

# Load all figures and collect clims
for path in pkl_files:
    with open(path, "rb") as f:
        fig = pickle.load(f)

        for pcm in fig._pcm:
            pcm.set_clim(global_vmin, global_vmax)

        fig._cbar.update_normal(fig._pcm[0])

        for i in range(0,3):
          ax = fig.axes[i]
          gl = ax.gridlines(draw_labels=True, linewidth=0.2, color='gray', linestyle='-')
          gl.top_labels = False
          gl.right_labels = False
          gl.xformatter = LONGITUDE_FORMATTER
          gl.yformatter = LATITUDE_FORMATTER

        fig.canvas.draw()

        out = path.replace(".pkl", ".jpg")
        fig.savefig(out, dpi=int(fig_res), bbox_inches="tight")
        print('[SAVED FIG]',out)
        plt.close(fig)
        del fig

        # Erase pickle file
        os.remove(path)



# Save time series 
np.savetxt(ddir+'/time_series.dat',np.array(time_series))

plt.close()


if data_sat != 1:
  exit(2)

