# ------------------------------------ #
# Read HF radars data and create plots #
# ------------------------------------ #

from fun_gen import *
from fun_io import *
import copernicusmarine
import os
import argparse
from netCDF4 import Dataset
import numpy as np
import datetime as dt
from scipy.interpolate import griddata
import cartopy.feature as cfeature
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.pyplot as plt
import matplotlib
import xarray as xr
import cmocean 

#matplotlib.use("Agg")



def get_radar_data(jd,hour):

  full_data = []
 
  """
  # Load CMEMS file
  # ---------------
  for tag in radarcmems:

    ds = Dataset(radardir+'/GL_TV_HF_HFR-'+tag+'-Total.nc')
    time = np.array(ds['TIME']).squeeze()

    dori = dt.datetime(1950,1,1).toordinal()
    time = time + dori
    jtime = np.floor(time)
    htime = np.floor((time-jtime)*24)

    idx = np.where( (jtime == jd) & (htime == hour) )

    try :
      idx = idx[0][0]

      lon = np.array(ds['LONGITUDE']).flatten()
      lat = np.array(ds['LATITUDE']).flatten()

      u = np.array(ds['EWCT'][idx,:,:]).squeeze().flatten()
      v = np.array(ds['NSCT'][idx,:,:]).squeeze().flatten()
      gdop_qc = np.array(ds['GDOP_QC'][idx,:,:]).squeeze().T.flatten()
      qc = np.array(ds['QCflag'][idx,:,:]).squeeze().T.flatten()
      ds.close()

      LON,LAT = np.meshgrid(lon,lat)
      LON,LAT = LON.flatten(),LAT.flatten()
    
      # Store data
      for n in range(0,LON.shape[0]):

        if u[n] > -999 and v[n] > -999 and gdop_qc[n] < 2 and qc[n] == 1 :
        #if u[n] > -999 and v[n] > -999 :
          full_data.append([LON[n],LAT[n],u[n],v[n]])

      print('\nData found for radar '+tag)
    
    except Exception as e:
      print(e)
      print('\nNo data found for radar '+tag)
      pass
  """
  # Read EuroGOOS radar
  # -------------------
  for tag in radareuro:


     #if 1 == 1: 
     try : 
       #ds = Dataset(diagdir+'/'+config+'/RADAR/DATA/'+tag+'.nc')
       ds = Dataset(radardir+'/'+tag+'.nc')

       time = np.array(ds['TIME']).flatten()
    
       dori = dt.datetime(1950,1,1).toordinal()
       time = time + dori
       jtime = np.floor(time)
       htime = np.floor((time-jtime)*24)

       #idx = np.where( (jtime == jd) & (htime == hour) )
       idx = np.where( (jtime == jd))

       #print(jtime,htime)
       #print(jd,hour)

       #idx = idx[0][0]

       lon = np.array(ds['LONGITUDE']).flatten()
       lat = np.array(ds['LATITUDE']).flatten()
       LON,LAT = np.meshgrid(lon,lat)
       LON,LAT = LON.flatten(),LAT.flatten()

       idx = np.array(idx).squeeze()

       u = np.array(ds['EWCT'][idx,:,:]).squeeze()
       v = np.array(ds['NSCT'][idx,:,:]).squeeze()

       u[u <= -999] = np.nan
       v[v <= -999] = np.nan

       # Mean daily value
       u = np.nanmean(u, axis=0)
       v = np.nanmean(v, axis=0)

       u = u.squeeze().T.flatten()
       v = v.squeeze().T.flatten()

       # Store data
       for n in range(0,LON.shape[0]):
         if u[n] > -999 and v[n] > -999 :
           full_data.append([LON[n],LAT[n],u[n],v[n]])
    
     except Exception as e:
       print(e)


  return np.array(full_data)



def argument():
    parser = argparse.ArgumentParser(description = '',formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(   '--config', '-c',
                                type = str,
                                required = True,
                                help ='Configuration name'
                        )
    return parser.parse_args()


# Get args
args = argument()
config = args.config  # Configuration name

# Load config
load_config(config)
from fun_gen import *

# Create arborescence
os.system('mkdir -p '+diagdir+'/'+config)
odir = diagdir+'/'+config+'/RADAR'
os.system('mkdir -p '+odir)

# Init plot
# ---------

# Load coords
lon_mod,lat_mod,lev = load_coords()
LON_MOD,LAT_MOD = np.meshgrid(np.array(lon_mod),np.array(lat_mod))
#LAT_MOD,LON_MOD = np.meshgrid(np.array(lat_mod),np.array(lon_mod))


# Load proj
exec('proj = ' + fig_proj)
cb_done = 'False'


# Init figure
extent = [lon_mod.min(),lon_mod.max(),lat_mod.min(),lat_mod.max()]


fig, (ax1, ax2) = plt.subplots(2, 1,figsize=(float(fig_sx), float(fig_sy)), subplot_kw={'projection': proj})

# Switch for colorbar
switch = 0

for ax in [ax1,ax2]:
  ax.set_extent(extent)

  land = cfeature.NaturalEarthFeature('physical', 'land', \
  scale=resol, facecolor=cfeature.COLORS['land'])

  ax.add_feature(land, facecolor='lightgrey')
  ax.add_feature(cfeature.BORDERS,edgecolor='darkgrey',zorder=2)
  ax.coastlines(resolution=resol, color='darkgrey', linestyle='-', alpha=1)
  gl = ax.gridlines(crs=proj, draw_labels=True,
  linewidth=0.2, color='gray', alpha=1., linestyle='-')
  gl.top_labels = True
  gl.left_labels = True
  gl.xlines = True
  gl.ylines = True
  gl.xformatter = LONGITUDE_FORMATTER
  gl.yformatter = LATITUDE_FORMATTER
  gl.xlabel_style = {'size': fig_tcklbl_size}
  gl.ylabel_style = {'size': fig_tcklbl_size}

# Find index to place scale
sub = 10 
tmp = lon_mod[::sub]-scale_lon 
idx_lon = np.where(abs(tmp) == np.amin(abs(tmp)))[0][0]
tmp = lat_mod[::sub]-scale_lat 
idx_lat = np.where(abs(tmp) == np.amin(abs(tmp)))[0][0]

tmp = LON_MOD[::sub,::sub].copy()
tmp[:] = np.nan
scale_x = np.zeros(LON_MOD[::sub,::sub].shape)
scale_y = np.zeros(LON_MOD[::sub,::sub].shape)
scale_x[idx_lat,idx_lon] = 0.5
scale_x[scale_x < 0.5] = np.nan 

# Plot scale
ax1.quiver(lon_mod[::sub],lat_mod[::sub],scale_x,scale_y,scale=15,zorder=10)
ax1.text(lon_mod[::sub][idx_lon],lat_mod[::sub][idx_lat]+0.04,'0.5 m.s$^{-1}$')


# Get outputs frequency
if freq == 'daily':
  hlim = 1
elif freq == 'hourly':
  hlim = 24

# Force hlim = 1
hlim = 1
  
# Loop on days
# ------------
for jd in range(jdini,jdend+1):

   d = dt.datetime.fromordinal(jd)
   dstr = d.strftime('%Y%m%d')

   # Loop on hours
   for hour in range(0,hlim):

     print('\n----------')
     print(dstr,hour)


     if 1 == 1: 
     #try:
     
       # Get radar data
       data = get_radar_data(jd,hour)

       # Interpolate on model grid
       lon,lat,u,v = data[:,0],data[:,1],data[:,2],data[:,3]


       iu = griddata((lat,lon),u,(LAT_MOD,LON_MOD),method='linear')
       iv = griddata((lat,lon),v,(LAT_MOD,LON_MOD),method='linear')


       # Get model values filename
       fname,dtag = get_filename(jd,'RFVL')

       mu = get_var_2D(jd,jdini,fname,'uo',hour,0)
       mv = get_var_2D(jd,jdini,fname,'vo',hour,0)

       # Plot velocities

       # Model
       # -----
       ax1.title.set_text('Model surface velocities (m.s$^{-1}$)')
       

       q1 = ax1.quiver(lon_mod[::sub],lat_mod[::sub],mu[::sub,::sub],mv[::sub,::sub],zorder=1,scale=15)


       # Plot norm
       norm = np.sqrt(np.square(mu)+np.square(mv))
       contours = np.arange(0.,0.8,0.1)
       c1 = ax1.contourf(lon_mod,lat_mod,norm,contours,cmap=cmocean.cm.speed,extend='max',zorder=0)
       if switch == 0:
         plt.colorbar(c1,pad=float(cb_pad_sat),fraction=float(cb_fraction_sat))

       ax2.title.set_text('HF radar - '+dstr+' '+str(hour).zfill(2)+'h')

       # Radars
       # ------
       q2 = ax2.quiver(lon_mod[::sub],lat_mod[::sub],iu[::sub,::sub],iv[::sub,::sub],zorder=1,scale=15)

       # Plot norm
       norm = np.sqrt(np.square(iu)+np.square(iv))

       #contours = np.arange(-1,1.1,0.1)
       #c2 = ax2.contourf(lon_mod,lat_mod,iu,contours,cmap=cmc.cm.vik,extend='max',zorder=0)

       c2 = ax2.contourf(lon_mod,lat_mod,norm,contours,cmap=cmocean.cm.speed,extend='max',zorder=0)

       if switch == 0:
         plt.colorbar(c2,pad=float(cb_pad_sat),fraction=float(cb_fraction_sat))
         switch = 1


       # Save figure 
       # -----------
       savefig(odir+'/'+dstr+'_'+str(hour).zfill(2)+'.'+fig_fmt)

       q1.remove()
       c1.remove()
       q2.remove()
       c2.remove()

     #except Exception as e:
     #  print(e)
     #  pass


     
