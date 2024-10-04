###########################################
# Routine to compute Okubo Weis parameter #
###########################################
#   ^
#  /!\ THIS ROUTINE DOES NOT USE fun_io FUNCTIONS
# / ! \  PROBLEM OF COMPATIBILITY, NEED A VIRTUAL ENV
# -----

from matplotlib import pyplot as plt
from numpy import arange, ma, where, array
from fun_gen import load_config
from fun_plot_2D import *
#from fun_io import *
from netCDF4 import Dataset

from py_eddy_tracker import data
from py_eddy_tracker.dataset.grid import RegularGridDataset
from py_eddy_tracker.observations.observation import EddiesObservations

import datetime as dt
from glob import glob
import sys
import cv2
import cmcrameri as cmc


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

   for hour in range(0,24):

    good = False
      

    while good == False: 
     try:
      d = dt.datetime.fromordinal(jd)
      dtag = d.strftime('%Y%m%d')


      fname = glob(outdir+'/'+dtag+'*RFVL*')[0]

      g = RegularGridDataset(fname,"longitude","latitude")

      dataset = Dataset(fname,format='NETCDF4-CLASSIC')
 
      u = dataset['uo'][hour,0,:,:].squeeze()
      v = dataset['vo'][hour,0,:,:].squeeze()
      lon = np.array(dataset['longitude'])
      lat = np.array(dataset['latitude'])


      LON,LAT = np.meshgrid(lon,lat)

      sub = 8
      '''
      lons = lon[::sub]
      lats = lat[::sub]
      us = u[::sub,::sub]
      vs = v[::sub,::sub]
      '''

      u[np.where(u>9999)] = np.nan
      v[np.where(v>9999)] = np.nan


      #u_x = g.compute_stencil(u)
      #u_y = g.compute_stencil(u, vertical=True)

      #v_x = g.compute_stencil(v)
      #v_y = g.compute_stencil(v, vertical=True)


      #ow = g.vars["ow"] = (u_x - v_y) ** 2 + (v_x + u_y) ** 2 - (v_x - u_y) ** 2


      exec('proj = ' + fig_proj)
      #extent = [np.amin(lon),np.amax(lon),np.amin(lat),np.amax(lat)]
      #extent = [8,10.05,42.5,43.5]
      extent = [7,11,42.1,44]
      fig, ax = plt.subplots(1,1,figsize=(5,4), subplot_kw={'projection': proj})

      ax.set_extent(extent)

      land = cfeature.NaturalEarthFeature('physical', 'land', \
      scale=resol, edgecolor='k', facecolor=cfeature.COLORS['land'])

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
      gl.xlabel_style = {'size': 8 }
      gl.ylabel_style = {'size': 8}


      # Process data
      #ow = np.array(ow)
      #idx = np.where( (LON > 9.7) | (LON < 10.5) | \
      #        (LAT > 43.7) | (LAT < 43.05))

      #ow[idx] = np.nan
      #ow[np.where(ow<2e-9)] = np.nan
      
      #ow[np.where(ow>2.5e-9)] = 1
      #ow[np.where(np.abs(ow)<2.e-9)] = np.nan


      #p = plt.pcolor(lon,lat,ow,cmap='bwr',vmin=-4e-9,vmax=4e-9,zorder=1)
      #p = plt.contour(lon,lat,ow,20,colors='k',zorder=2)
      #plt.colorbar()


      lons,lats = lon[::sub],lat[::sub]
      us,vs = array(u[::sub,::sub]),array(v[::sub,::sub])

      norm = np.sqrt(np.square(us)+np.square(vs))

      us[np.where(norm < 0.1)] = np.nan
      vs[np.where(norm < 0.1)] = np.nan

      # Plot vector
      #q = ax.quiver(lons,lats,us,vs,color='k',edgecolor='k',linewidth=0.5,scale=12,zorder=4,width=0.005,headlength=5)
      q = ax.quiver(lons,lats,us,vs,color='k',edgecolor='k',linewidth=0.5,scale=12,zorder=4,width=0.002,headlength=5)
      #q = ax.quiver(lons,lats,us,vs,color='k',edgecolor='k',linewidth=0.5,scale=15,zorder=4,width=0.002,headlength=5)

      # Plot norm
      contours = np.arange(0.,0.8,0.1)
      ct = ax.contourf(lons,lats,norm,contours,cmap=cmc.cm.buda_r,extend='max')
      plt.colorbar(ct,pad=0.14,fraction=0.04,
              label='Surface velocity (m.s$^{-1}$)',
              orientation='horizontal')

      # Plot scale
      #ax.quiver([9.15],[42.55],[0.6],[0],edgecolor='k',linewidth=0.5,scale=15,width=0.005,headlength=5,zorder=100)
      #plt.text(9.11,42.57,'0.6 m.s$^{-1}$',fontsize=8)

      # Plot eddy position
      eddy = np.loadtxt('/DISK2TB/DATA/eddy.dat')
      idx = np.where(eddy[:,0] <= float(dtag))
      idx = np.array(idx)


      #plt1 = plt.plot(eddy[idx,1],eddy[idx,2],'ko',markersize=1,linewidth=2,zorder=3)
      #plt2 = plt.plot(eddy[idx,1].flatten(),eddy[idx,2].flatten(),'k-',linewidth=0.7,zorder=5)
      #plt3 = plt.plot(eddy[idx[-1][-1],1],eddy[idx[-1][-1],2],'ko', markerfacecolor='none',zorder=3)

      # Tune 
      #cb = plt.colorbar(extend='both',fraction=float(cb_fraction_2D),pad=float(cb_pad_2D),\
      #          label='Okubo Weiss')

      plt.title(dtag+' '+str(hour).zfill(2)+'h',fontsize=10)

      ax.set_xticklabels(ax.get_xticks(), fontsize=2)
      ax.set_yticklabels(ax.get_yticks(), fontsize=8)


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

      #plt.show()
      plt.close()
      
      good = True
   
     except Exception as e:
      print(e)
      pass







