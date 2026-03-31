################################
# Create maps for all  domains #
################################

from fun_plot_2D import *
import xarray as xr
import numpy as np
from numpy import array as npa
                                
import cartopy.feature as cfeature
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.colors as colors
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.image as mpimg

from PIL import Image
from glob import glob


domains = [os.path.basename(f) for f in glob("/home/cfontana/meshmasks/*.nc")]


# Create full map
# ---------------

plt.figure(1)

fig, ax = plt.subplots(1,1,figsize=(8, 8), subplot_kw={'projection': ccrs.PlateCarree()},constrained_layout=True)


ax.set_extent([5.5,22,34.5,46.05])

land = cfeature.NaturalEarthFeature('physical', 'land', \
scale='50m', facecolor=cfeature.COLORS['land'])

ax.add_feature(land, facecolor='lightgrey')
ax.add_feature(cfeature.BORDERS,edgecolor='darkgrey',zorder=2)
ax.coastlines(resolution='50m', color='darkgrey', linestyle='-', alpha=1)
gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
linewidth=0.2, color='gray', alpha=1., linestyle='-')
gl.top_labels = True
gl.left_labels = True
gl.xlines = True
gl.ylines = True
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.xlabel_style = {'size': 12}
gl.ylabel_style = {'size': 12}

# First loop to plot all domains
# ------------------------------
for domain in domains:
  ds = xr.open_dataset('/home/cfontana/meshmasks/'+domain,engine="netcdf4")

  lon = np.array(ds['longitude'])
  lat = np.array(ds['latitude'])
  m = np.array(ds['tmask'][0,:,:].squeeze())

  c = ax.contour(lon, lat, m,
                    levels=[0.5],
                    colors=['gray'],
                    linewidths=2,
                   transform=ccrs.PlateCarree())


  #ax.text(lon.min(),lat.min(),domain)

fig.canvas.draw() 

xlim = ax.get_xlim()
ylim = ax.get_ylim()

#img = mpimg.imread('/home/cfontana/MAPS/labels.png')
#ax.imshow(img, extent=[xlim[0], xlim[1], ylim[0], ylim[1]],
 #         transform=ccrs.PlateCarree(), zorder=5, origin='upper')



# Loop on domains to plot one by one
# ----------------------------------
for domain in domains:

  print(domain)
  
  # Load mask file
  ds = xr.open_dataset('/home/cfontana/meshmasks/'+domain,engine="netcdf4")

  lon = np.array(ds['longitude'])
  lat = np.array(ds['latitude'])

  rect = Rectangle(
    (lon.min(), lat.min()),      
    lon.max()-lon.min(),           
    lat.max()-lat.min(),            
    facecolor='red',
    alpha=0.6,     
    transform=ccrs.PlateCarree()
)
  ax.add_patch(rect)

  domain = domain.upper()
  domain = domain.replace('.NC','.jpg')
  
  plt.draw()

  plt.savefig('/home/cfontana/MAPS/'+domain,bbox_inches='tight',dpi=200)
  #plt.savefig('/home/cfontana/MAPS/'+domain,dpi=200)

  rect.remove()

  # Composite au niveau pixel (pas de coordonnées géo !)
  base = Image.open('/home/cfontana/MAPS/'+domain).convert('RGBA')
  labels = Image.open('/home/cfontana/MAPS/labels.png').convert('RGBA')

  # Redimensionne labels si nécessaire
  if labels.size != base.size:
    labels = labels.resize(base.size, Image.LANCZOS)

  # Colle les labels par-dessus
  base.paste(labels, (0, 0), labels)  # utilise le canal alpha comme masque
  base.convert('RGB').save('/home/cfontana/MAPS/'+domain)







