# ------------------------- #
# Routine to get Argo data  #
# ------------------------- #
import warnings
warnings.simplefilter("ignore")
import numpy as np

from fun_gen import *
from fun_io import *
from fun_plot_2D import *
import sys,os
import datetime as dt
import xarray as xr
import datetime as dt

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
ds = xr.open_dataset(savedir+'/argo.nc')

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



  full_data = []
  full_val = []

  for var in ['PSAL_ADJUSTED','TEMP_ADJUSTED']:

    if var == 'PSAL_ADJUSTED':
       mod_var = 'so'
    elif var == 'TEMP_ADJUSTED':
       mod_var = 'thetao'

    # Get data
    data = ds[var][idx]

    # Get current variable parameters
    vname, ftag, cmap, islog, vmod, vmin, vmax, label, units\
        = load_variable(config,mod_var)

    # Convert date
    dstr = str(time[idx][0])

    print('Float',pnum,'cycle',pcyc)

    date = dt.datetime.strptime(dstr,'%Y-%m-%dT%H:%M:%S.000000000')
    jd = date.toordinal()

    hours,mnt = date.strftime('%H'),date.strftime('%M')
    hours = int(np.round(float(hours)+float(mnt)/60.))


    # Get filename
    fname,dtag = get_filename(int(np.floor(jd)),ftag)


    # Interpolate model on data
    try :
      val  = get_model_val_3d(fname,hours,vname,\
               lon_mod,lat_mod,lev_mod,\
                 data_lon,data_lat,data_pres)
    except Exception as e :
      print('Interp failed')
      print(e)
      val = data_lon
      val[:] = np.nan

   

    full_val.append(val)
    full_data.append(data)


  full_val = np.array(full_val)
  full_data = np.array(full_data)

  # Plot profile
  # ------------

  fig = plt.figure(figsize=(float(fig_prox), float(fig_proy)))
  ax1 = fig.add_subplot(111)
  ax2 = ax1.twiny()

  psal,temp = full_val[0],full_val[1]

  # Plot model
  ax1.plot(psal,-data_pres,c=col2,label='Salinity')
  ax2.plot(temp,-data_pres,c=col3,label='Temperature')

  psal,temp = full_data[0],full_data[1]

  # Plot data
  ax1.plot(psal,-data_pres,c=col2,marker='.',linestyle='None',alpha=0.5)
  ax2.plot(temp,-data_pres,c=col3,marker='.',linestyle='None',alpha=0.5)


  ax1.set_xlabel('Salinity')
  ax1.set_ylabel('Depth (m)')
  ax1.xaxis.label.set_color(col2)
  ax1.spines["bottom"].set_color(col2)
  ax1.tick_params(axis='x',colors=col2, which='both')
  ax1.patch.set_alpha(0.0)

  ax2.set_xlabel('Temperature (°C)')
  ax2.xaxis.label.set_color(col2)
  ax2.spines["top"].set_color(col3)
  ax2.xaxis.label.set_color(col3)
  ax2.tick_params(colors=col3, which='both')


  plt.title(ptime)



  # Save figure
  # -----------
  os.system('mkdir -p '+savedir+'/'+str(pnum))

  fout = savedir+'/'+pnum+'/profile_'+pcyc+'.'+fig_fmt
  savefig(fout)
  print('')

  plt.close()

  exit()


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
   fout = savedir+'/'+str(n)+'/map'+'.'+fig_fmt
   savefig(fout)

   plt.close()


  
  














