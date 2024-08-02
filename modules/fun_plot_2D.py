# --------------------- #
# 2D Plotting functions #
# --------------------- #
from fun_gen import *
import cartopy.feature as cfeature
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.pyplot as plt


# -------------------- #
# Initialize 2D figure #
# -------------------- #
def init_fig(ax,extent,proj):

  from fun_gen import fig_sx,fig_sy,resol,fig_proj
  from fun_gen import fig_tcklbl_size

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





