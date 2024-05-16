# ------------------------- #
# Routine to get Argo data  #
# ------------------------- #
import warnings
warnings.simplefilter("ignore")
import numpy as np

from fun_gen import *
from fun_io import *
from fun_plot_2D import *
from fun_plot_profile import *
import sys,os
import xarray as xr
import datetime as dt
from datetime import datetime

from mpl_toolkits.axes_grid1 import host_subplot
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")



# Get args
# --------
config = sys.argv[1]  # Configuration name


# Load config file
# ----------------
load_config(config)
from fun_gen import *

# Create arborescence
# -------------------
os.system('mkdir -p '+diagdir)
os.system('mkdir -p '+diagdir+'/'+config)
savedir = diagdir+'/'+config+'/ARGO'
os.system('mkdir -p '+savedir)

# Load coordinates
# ----------------
lon_mod,lat_mod,lev_mod=load_coords()


# Load data
# ---------
savedir = diagdir+'/'+config+'/ARGO'
ds = xr.open_dataset(savedir+'/bioargo.nc')

lat = np.array( ds['LATITUDE'])
lon = np.array(ds['LONGITUDE'])
time = np.array(ds['TIME'])
num = np.array(ds['PLATFORM_NUMBER'])
cyc = np.array(ds['CYCLE_NUMBER'])
pres = np.array(ds['PRES_ADJUSTED'])


time = np.array(time,dtype=str)


# Define profiles position
# ------------------------

lon_uni = np.unique(lon)
print(lon_uni.shape[0],'profiles found\n')


# Loop on profiles
# ----------------
print('Processing\n')
for plon in lon_uni:

  # Get all indexes
  idx = np.where( lon == plon )

  # Get data lon/lat
  data_lon = lon[idx]
  data_lat = lat[idx]
  data_pres = pres[idx]

  pnum = str(num[idx][0])
  pcyc = str(cyc[idx][0])
  ptime = str(time[idx][0])


  print('Float',pnum,'cycle',pcyc)


  full_data = []
  full_val = []

  for var in ['CHLA','PSAL_ADJUSTED','TEMP_ADJUSTED']:

    if var == 'CHLA':
       mod_var = 'chl'
    elif var == 'PSAL_ADJUSTED':
       mod_var = 'so'
    elif var == 'TEMP_ADJUSTED':
       mod_var = 'thetao'

    # Get data
    data = ds[var][idx]

    # Get current variable parameters
    vname, ftag, cmap, islog, vmod, vmin, vmax, label, units\
        = load_variable(config,mod_var)

    # Convert date
    dstr = str(time[idx][0]).replace(':00.000000000','')
    date = dt.datetime.strptime(dstr,'%Y-%m-%dT%H:%M')
    jd = date.toordinal()
 
    hours,mnt = date.strftime('%H'),date.strftime('%M')
    hours = int(np.round(float(hours)+float(mnt)/60.))


    # Get filename
    fname,dtag = get_filename(int(np.floor(jd)),ftag)


    # Interpolate model on data
    val  = get_model_val_3d(fname,hours,vname,\
               lon_mod,lat_mod,lev_mod,\
                 data_lon,data_lat,data_pres)

    full_val.append(val)
    full_data.append(data)


  full_val = np.array(full_val)
  full_data = np.array(full_data)

  # Plot profile
  # ------------
  mchl,mpsal,mtemp = full_val[0],full_val[1],full_val[2]
  dchl,dpsal,dtemp = full_data[0],full_data[1],full_data[2]

  os.system('mkdir -p '+savedir+'/bio_'+str(pnum))
  fout = savedir+'/bio_'+str(pnum)+'/profile_'+pcyc+'.'+fig_fmt

  ptime = ptime.replace(':00.000000000','')
  plot_profiles(fout,ptime,-data_pres,\
               mchl,dchl,'Chlorophyll (mg.m$^{-3}$)',\
               mpsal,dpsal,'Salinity',\
               mtemp,dtemp,'Temperature (°C)')




# Plot trajectories
# -----------------

print('Plot trajectories ...')

# Loop on Argo float
for n in np.unique(num):

   print(n)

   # Load proj
   exec('proj = ' + fig_proj)

   # Initialize map
   extent = [lon_mod.min(),lon_mod.max(),lat_mod.min(),lat_mod.max()]
   fig, ax = plt.subplots(1,1,figsize=(float(fig_sx), float(fig_sy)), subplot_kw={'projection': proj})
   init_fig(ax,extent,proj)

   # Get all indexes
   idx = np.where( num == n )

   plon = np.unique( lon[idx])
   plat = np.unique( lat[idx])
   txt = np.unique(cyc[idx])

   plt.plot(plon,plat,marker='+',linestyle='-')

   for i in [0,plon.shape[0]-1]:
     plt.text(plon[i],plat[i],str(txt[i]),fontsize=8)

   # Save figure
   fout = savedir+'/bio_'+str(n)+'/map'+'.'+fig_fmt
   savefig(fout)

   plt.close()




