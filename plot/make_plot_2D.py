# --------------------- #
#  2D plotting function #
# --------------------- #
import warnings
warnings.simplefilter("ignore")

from fun_gen import *
from fun_io import *
from fun_plot_2D import *
import sys,os
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



# Get args
# --------
config=sys.argv[1]  # Configuration name
var=sys.argv[2]     # Variable name
lev=sys.argv[3]     # Z-level


# Load parameters
# ---------------
load_config(config)
from fun_gen import *

# Load whales data
# ----------------
if with_whales:

  # Get whale position
  dtrack=np.loadtxt('/home/fontana/SONG/SICILIA/87780.dat')

  mon=dtrack[:,5].squeeze()
  day=dtrack[:,4].squeeze()
  year=dtrack[:,6].squeeze()

  mon=np.array(mon,dtype=int)
  day=np.array(day,dtype=int)
  year=np.array(year,dtype=int)

  # Compute julian day
  jd_w = []
  for i in range(0,year.shape[0]):
     d = dt.datetime(year[i],mon[i],day[i])
     jd_w.append(d.toordinal())

  # Compute mean position
  tlon = []
  tlat = []
  tjd = []

  for jd in np.unique(jd_w):
     
     idx = np.where( jd_w == jd)
     tlon.append(np.mean(dtrack[idx,1]))
     tlat.append(np.mean(dtrack[idx,0]))
     tjd.append(jd)

tlon = np.array(tlon)
tlat = np.array(tlat)
tjd = np.array(tjd)


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

 #for hour in range(12,13):
 for hour in range(0,24):
   # Get current variable parameters
   vname, ftag, cmap, islog, vmod, vmin, vmax, label, units\
        = load_variable(config,var)

   # Get filename
   fname,dtag = get_filename(jd,ftag)

   # Get 2D variable
   var2d = get_var_2D(fname,var,hour,lev)
   var2d = np.array(var2d)
   var2d[np.where(var2d > 999) ] = np.nan

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
     # Plot today position
     idx = np.where( tjd == jd )
     tw1 = plt.scatter(tlon[idx],tlat[idx],marker='o',color='r',s=56,transform=ccrs.PlateCarree(),zorder=9)

     # Plot last days position
     idx = np.where( tjd-jd >= -3 ) and np.where(tjd-jd <= 0)
     tw2 = ax.plot(tlon[idx],tlat[idx],'r-')



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
   
   if with_whales == 'True':
     ax.lines[0].remove()
     tw1.remove()



plt.close()

   

