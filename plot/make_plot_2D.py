# --------------------- #
#  2D plotting function #
# --------------------- #
import warnings
warnings.simplefilter("ignore")

from fun_gen import *
from fun_io import *
from fun_plot_2D import *
import sys,os,argparse
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
    parser.add_argument(   '--level',"-l",
                                type = str,
                                required = True,
                                help = 'model level number')
    return parser.parse_args()



# Get args
# --------
args = argument()
config = args.config  # Configuration name
var = args.variable   # Variable name
lev = args.level   # Level number


# Load parameters
# ---------------
load_config(config)
from fun_gen import *

# Load whales data
# ----------------
if with_whales:

  dtrack = np.loadtxt('/home/fontana/SONG/SICILIA/87780.dat',dtype=str)

  wlon = np.array(dtrack[:,1],dtype=float).squeeze()
  wlat = np.array(dtrack[:,0],dtype=float).squeeze()


  hour = dtrack[:,2].squeeze()
  mon = dtrack[:,5].squeeze()
  day = dtrack[:,4].squeeze()
  year = dtrack[:,6].squeeze()

  # Compute julian day
  wtag = []
  for i in range(0,year.shape[0]):
     wtag.append(year[i]+mon[i]+day[i]+hour[i])

  wtag = np.array(wtag,dtype=str)



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
cb_done = 'False'

# Init figure
# -----------
extent = [lon.min(),lon.max(),lat.min(),lat.max()]
fig, ax = plt.subplots(1,1,figsize=(float(fig_sx), float(fig_sy)), subplot_kw={'projection': proj})
init_fig(ax,extent,proj)


# Loop on files
# -------------
print('Processing')
for jd in range(jdini,jdend+1):

 for hour in range(12,13):
 #for hour in range(0,24):


   # Get current variable parameters
   vname, ftag, cmap, islog, vmod, vmin, vmax, label, units\
        = load_variable(config,var)

   # Get filename
   fname,dtag = get_filename(jd,ftag)
   htag = dtag+str(hour).zfill(2)

   # Get 2D variable
   var2d = get_var_2D(fname,var,hour,lev)
   var2d = np.array(var2d)
   var2d[np.where(var2d > 999) ] = np.nan


   #if var == 'zooc':
   #  var2d = var2d/12. # !!!!! To remove for next simus

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


   # Plot currents
   if with_currents == 'True':

   #if 1 == 2:
     vname, ftag, cmap, islog, vmod, vmin, vmax, label, units\
           = load_variable(config,'uo')

     # Get filename
     fname,dtag = get_filename(jd,ftag)

     # Get 2D variable
     u = get_var_2D(fname,'uo',hour,0)
     v = get_var_2D(fname,'vo',hour,0)

     sub = 10

     lons,lats = lon[::sub],lat[::sub]
     us,vs = npa(u[::sub,::sub]),npa(v[::sub,::sub])

     norm = np.sqrt(np.square(us)+np.square(vs))

     us[np.where(norm < 0.1)] = np.nan
     vs[np.where(norm < 0.1)] = np.nan

     q = ax.quiver(lons,lats,us,vs,color='k',edgecolor='k',linewidth=.2,scale=18,zorder=4,width=0.002)

   # Plot whales
   if with_whales == 'True':

     try :
       idx = np.where( wtag == htag )

       if len(idx[0]) == 0 :
          idx = idx_old

       tw1 = plt.scatter(wlon[idx[0][0]],wlat[idx[0][0]],marker='o',color='deepskyblue',s=56,transform=ccrs.PlateCarree(),zorder=9)

       # Plot last days position
       last = idx[-1][0]
       tw2 = ax.plot(wlon[last-5:last+1],wlat[last-5:last+1],color='deepskyblue',linestyle='-',alpha=0.8,zorder=9)
     except:
       pass




   # Title
   date = dt.datetime.fromordinal(jd)
   y,m,d = date.strftime('%Y'),date.strftime('%m'),date.strftime('%d')

   title = y+'-'+m+'-'+d+' '+str(hour).zfill(2)+'h'
   plt.title(title)

   # Save file
   # ---------
   os.system('mkdir -p '+savedir)

   plt.draw()

   fout = savedir+'/'+dtag+str(hour).zfill(2)+'_'+var+'.'+fig_fmt
   savefig(fout)

   p.remove()

   if with_currents == 'True':
     q.remove()
   
   # Remove whale if any points
   try :
     tw1.remove()
   except :
     pass


   idx_old = idx




plt.close()

   

