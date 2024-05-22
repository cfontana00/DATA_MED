###########################################
# Routine to compute Okubo Weis parameter #
###########################################
#   ^
#  /!\ THIS ROUTINE DOES NOT USE fun_io FUNCTIONS
# / ! \  PROBLEM OF COMPATIBILITY, NEED A VIRTUAL ENV
# -----

from matplotlib import pyplot as plt
from numpy import arange, ma, where, array
from fun_gen import *
from fun_plot_2D import *
#from fun_io import *
from netCDF4 import Dataset

from py_eddy_tracker import data
from py_eddy_tracker.dataset.grid import RegularGridDataset
from py_eddy_tracker.observations.observation import EddiesObservations

import datetime as dt
from glob import glob
import sys


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
savedir = diagdir+'/'+config+'/OKUBO'
os.system('mkdir -p '+savedir)


for jd in range(jdini,jdend+1):

   for hour in range(0,1):

    try:
      d = dt.datetime.fromordinal(jd)
      dtag = d.strftime('%Y%m%d')


      fname = glob(outdir+'/'+dtag+'*RFVL*')[0]

      g = RegularGridDataset(fname,"longitude","latitude")

      dataset = Dataset(fname,format='NETCDF4-CLASSIC')
 
      u = dataset['uo'][hour,0,:,:].squeeze()
      v = dataset['vo'][hour,0,:,:].squeeze()
      lon = dataset['longitude']
      lat = dataset['latitude']

      u[np.where(u>9999)] = np.nan
      v[np.where(v>9999)] = np.nan

      u_x = g.compute_stencil(u)
      u_y = g.compute_stencil(u, vertical=True)


      v_x = g.compute_stencil(v)
      v_y = g.compute_stencil(v, vertical=True)

      ow = g.vars["ow"] = (u_x - v_y) ** 2 + (v_x + u_y) ** 2 - (v_x - u_y) ** 2



      exec('proj = ' + fig_proj)
      extent = [np.amin(lon),np.amax(lon),np.amin(lat),np.amax(lat)]
      fig, ax = plt.subplots(1,1,figsize=(float(fig_sx), float(fig_sy)), subplot_kw={'projection': proj})
      init_fig(ax,extent,proj)

      p = plt.pcolor(lon,lat,ow,cmap='bwr',vmin=-3e-9,vmax=3e-9,zorder=1)
      #plt.colorbar()

      sub = 8

      lons,lats = lon[::sub],lat[::sub]
      us,vs = array(u[::sub,::sub]),array(v[::sub,::sub])

      norm = np.sqrt(np.square(us)+np.square(vs))

      us[np.where(norm < 0.1)] = np.nan
      vs[np.where(norm < 0.1)] = np.nan

      q = ax.quiver(lons,lats,us,vs,color='k',edgecolor='k',linewidth=.1,scale=22,zorder=4,width=0.001)

      # Tune 
      cb = plt.colorbar(extend='both',fraction=float(cb_fraction_2D),pad=float(cb_pad_2D),\
                label='Okubo Weis')

      plt.title(dtag+' '+str(hour).zfill(2)+'h')

      # Save
      fout = fname.replace("RFVL","OKWSh"+str(hour).zfill(2))
      print(fout)
      fout = fout.replace("nc",fig_fmt)
      fout = os.path.basename(fout)
      fout = savedir +'/'+ fout

      if tight == "True" :
        plt.savefig(fout,bbox_inches='tight',dpi=int(fig_res))
      else:
        plt.savefig(fout,dpi=int(fig_res))

      print('[SAVED FIG] '+fout)

      plt.close()

    except:
      pass







