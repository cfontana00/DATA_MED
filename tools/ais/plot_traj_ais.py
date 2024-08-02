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
savedir = diagdir+'/'+config+'/AIS_TRAJ/'
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
wlon = []
wlat = []
wjd = []

for jd in np.unique(jd_w):

   idx = np.where( jd_w == jd)
   wlon.append(np.mean(dtrack[idx,1]))
   wlat.append(np.mean(dtrack[idx,0]))
   wjd.append(jd)

wlon = np.array(wlon)
wlat = np.array(wlat)
wjd = np.array(wjd)





# Loop on days
# ------------
for jd in range(jdini,jdini+10):


   d = dt.datetime.fromordinal(jd)
   dtag = d.strftime('%Y%m%d')


   for hour in range(0,24):

     # Plot eddy position
     # ------------------

     # Get eddy position
     diff = abs(x_new - (float(jd)+float(hour)/24.))
     idx = np.where(diff == np.amin(diff))

     ilon = elon[idx]
     ilat = elat[idx]

     s1 = ax.scatter(ilon,ilat,color='r',
             marker='o',s=1200,alpha=0.4,zorder=3)

     #s2 = plt.scatter(eddy[-last,1],eddy[-last,2],color='k',
     #       marker='o',facecolor='none',s=300,zorder=3)


     # Plot boats positions
     # --------------------
     tag = 'ais_'+dtag+'_'+str(hour).zfill(2)

     # Load data 
     # ---------

     tag_tmp = '202407'+dtag[6:8]+'_'+str(hour).zfill(2)
     dtag_tmp = '202407'+dtag[6:8]


     ds = Dataset('/DISK2TB/AIS/files/'+dtag_tmp+'/ais_'+tag_tmp+'.nc','r')

     lon = np.array(ds['longitude'])
     lat = np.array(ds['latitude'])

     mlon,mlat = array(mlon),array(mlat)


     idx = np.where( (lon > lon_min) \
             & (lon < lon_max) \
             & (lat > lat_min) \
             & (lat < lat_max) )

     lon,lat = lon[idx],lat[idx]
     ship = np.array(ds['ship'])[idx]
     mmsi = np.array(ds['mmsi'])[idx]
     time = np.array(ds['time'])[idx]

     ds.close()


     # Loop on boats
     pos = []
     plist = []
     pold = []
     btag = []
     for boat in np.unique(mmsi):

        idx = np.where(boat == mmsi) 

        blon = np.mean(lon[idx])
        blat = np.mean(lat[idx])

        dist = np.sqrt( (blon - ilon)**2 + (blat - ilat)**2   )

        #name = str(convert(ship[idx][0]))[0:5]+str(convert(ship[idx][0]))[-1]
        long_name = str(convert(ship[idx][0])).strip()
        name = str(convert(ship[idx][0]))[0:5]+str(convert(ship[idx][0]))[7:8]

        color = 'g'
        if dist < 0.3 and dist >= 0.1:
           color = 'orange'
        elif dist < 0.1:
           color = 'r'
           t += long_name+' ('+d.strftime('%m/%d ')+str(hour).zfill(2)+'h)\n'
     
        # Plot positions
        p = plt.plot(blon,blat,color=color,marker='o',alpha=0.3,zorder=3)
        plist.append(p)

        # Plot track
        try:
          
            idx = np.array(np.where(boat == old_pos[:,0]))
            olon = old_pos[idx[0],1][0]
            olat = old_pos[idx[0],2][0]
            p = plt.plot([blon,olon],[blat,olat],color='k',linewidth=0.5,alpha=0.3)
            pold.append(p)

        except Exception as e :
            #print(e)
            pass

    

        pos.append([boat,blon,blat])



        if dist < 1 :
          tname = plt.text(blon,blat,name,color='r',fontsize=6)
          btag.append(tname)
     
     
     text = plt.text(10.75,42.6,t,color='r')


     # Plot whales position
     # --------------------
     # Plot today position
     idx = np.where( wjd == jd )
     tw1 = plt.scatter(wlon[idx],wlat[idx],marker='o',color='b',s=56,transform=ccrs.PlateCarree(),zorder=9)

     # Plot last days position
     idx = np.where( wjd-jd >= -3 ) and np.where(wjd-jd <= 0)
     tw2 = ax.plot(wlon[idx],wlat[idx],'b-')


     plt.title(d.strftime('%Y-%m-%d '+str(hour).zfill(2)+'h')
)


     fout = savedir+tag+'.'+fig_fmt
     savefig(fout)

     # Remove points
     tw1.remove()
     tw2[0].remove()



     s1.remove()
    
     for p in plist:
        p[0].remove()
    
     for p in pold:
        p[0].remove()


     text.remove()

     try: 
       tmp.remove()
     except:
       pass

     for b in btag:
       b.remove()

     old_pos = np.array(pos)

     

     




























