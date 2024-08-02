# ------------------- #
# Plot AIS trajectory #
# ------------------- #
import warnings
warnings.simplefilter("ignore")

from fun_io import *
from fun_plot_2D import *

import os
import datetime as dt
import numpy as np
from numpy import array
from scipy import interpolate

import cartopy.feature as cfeature
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")

from netCDF4 import Dataset
import cmcrameri as cmc



# Convert name
# ------------
def convert(s):

    # initialization of string to ""
    new = ""

    # traverse in the string
    for x in s:
        new += x.decode('UTF-8')

    # return string
    return new




# Load config
config = 'ALBEDO'
load_config(config)
from fun_gen import *

# Create directories
savedir = diagdir+'/'+config+'/AIS_DENS/'
os.system('mkdir -p '+savedir)


# Inititialize map
# ----------------

# Load lon/lat
mlon,mlat,levels = load_coords()
t = 'Name (date)\n------\n'

# Load proj
exec('proj = ' + fig_proj)
cb_done = 'False'

# Init figure
lon_min,lon_max,lat_min,lat_max = 8,10.5,42.5,mlat.max()
extent = [lon_min,lon_max,lat_min,lat_max]
fig, ax = plt.subplots(1,1,figsize=(float(fig_sx), float(fig_sy)), subplot_kw={'projection': proj})
init_fig(ax,extent,proj)


# Load eddy position and interpolate hourly
pos = np.loadtxt('/DISK2TB/DATA/eddy.dat').squeeze()

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

elon = flon(x_new).squeeze()
elat = flat(x_new).squeeze()


# Load whales data
# ----------------
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





# Load AIS density data
# ---------------------
ds = Dataset('/home/fontana/DISK2TB/DATA/AIS/Cargo_Ships_2015_04.nc',format='NETCDF4-CLASSIC')
cargo = array(ds['DEFAULT'])
dlon = array(ds['longitude'])
dlat = array(ds['latitude'])
ds.close()

ds = Dataset('/home/fontana/DISK2TB/DATA/AIS/Passenger_Ships_2015_04.nc',format='NETCDF4-CLASSIC')
person = array(ds['DEFAULT'])
ds.close()

ds = Dataset('/home/fontana/DISK2TB/DATA/AIS/Tankers_2015_04.nc',format='NETCDF4-CLASSIC')
tankers = array(ds['DEFAULT'])
ds.close()

density = cargo + person + tankers
#density[density==0]=np.nan


#plt.pcolor(dlon,dlat,density,norm=colors.LogNorm(vmin=0.01,vmax=5),cmap=cmc.cm.oslo_r)

plt.pcolor(dlon,dlat,density,vmin=0.0,vmax=2.5,cmap=cmc.cm.acton_r)
cb = plt.colorbar(extend='both',fraction=float(cb_fraction_2D),
        pad=float(cb_pad_2D),label='Boats Density (hrs.km$^{-2}$)')


idx_old = 0

# Loop on days
# ------------
for jd in range(jdini,jdini+19):


   d = dt.datetime.fromordinal(jd)
   dtag = d.strftime('%Y%m%d')

   # Plot eddy position
   # ------------------
   idx = np.where(tjd==jd)

   s1 = ax.scatter(pos[idx,1],pos[idx,2],color='r',facecolor='none',
             marker='o',s=1200,zorder=3)

   s2 = ax.scatter(pos[idx,1],pos[idx,2],color='r',alpha=0.5,
             marker='o',s=1200,zorder=3)


   for hour in range(0,24):

     tag = 'ais_'+dtag+'_'+str(hour).zfill(2)

     htag = d.strftime('%Y%m%d')+str(hour).zfill(2) 

     # Plot eddy position
     # ------------------

     # Get eddy position

     """
     # Hourly
     diff = abs(x_new - (float(jd)+float(hour)/24.))
     idx = np.where(diff == np.amin(diff))

     ilon = elon[idx]
     ilat = elat[idx]

     s1 = ax.scatter(ilon,ilat,color='r',
             marker='o',s=1200,facecolor='none',alpha=0.4,zorder=3)
     """

     # Plot AIS density map
     # --------------------



     # Plot whales position
     # --------------------
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

     plt.title(d.strftime('%Y-%m-%d '+str(hour).zfill(2)+'h')
)

     
     fout = savedir+tag+'.'+fig_fmt
     savefig(fout)

     # Remove points
     try :
       tw1.remove()
     except :
       pass
     #tw2[0].remove()

     idx_old = idx



   s2.remove()
    

     

     




























