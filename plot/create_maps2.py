from fun_plot_2D import *
import xarray as xr
import numpy as np
import cartopy.feature as cfeature
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.pyplot as plt
from PIL import Image
from glob import glob
from shapely.geometry import Point
from shapely.ops import unary_union
from shapely.prepared import prep

domains = [os.path.basename(f) for f in glob("/home/cfontana/meshmasks/*.nc")]


def load_mask(ds):
    for varname in ['mask', 'tmask', 'nav_msk', 'fmask']:
        if varname in ds:
            mask = np.array(ds[varname])
            while mask.ndim > 2:
                mask = mask[0]
            return mask
    for varname in ds.data_vars:
        if varname not in ('longitude', 'latitude', 'lon', 'lat', 'nav_lon', 'nav_lat'):
            mask = np.array(ds[varname])
            while mask.ndim > 2:
                mask = mask[0]
            if mask.ndim == 2:
                return mask
    raise ValueError("No mask variable found in dataset.")


# Préparer la géométrie terre une seule fois
land_shp = shpreader.natural_earth(resolution='50m', category='physical', name='land')
land_geom = unary_union(list(shpreader.Reader(land_shp).geometries()))
prepared_land = prep(land_geom.buffer(0.2))


def mask_for_contour(lon, lat, mask):
    """
    Met à 1 les cellules qui sont 0 parce que c'est la terre (pas hors domaine).
    Ainsi contour ne trace que la frontière du domaine en mer.
    """
    mask_out = mask.copy().astype(float)
    rows, cols = np.where(mask == 0)
    for r, c in zip(rows, cols):
        if prepared_land.contains(Point(lon[c], lat[r])):
            mask_out[r, c] = 1  # terre → même valeur que mer active
    return mask_out


def make_base_map():
    fig, ax = plt.subplots(1, 1, figsize=(8, 8),
                           subplot_kw={'projection': ccrs.PlateCarree()},
                           constrained_layout=True)
    ax.set_extent([5.5, 22, 34.5, 46.05])
    land = cfeature.NaturalEarthFeature('physical', 'land', scale='50m',
                                        facecolor=cfeature.COLORS['land'])
    ax.add_feature(land, facecolor='lightgrey')
    ax.add_feature(cfeature.BORDERS, edgecolor='darkgrey', zorder=2)
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
    return fig, ax


def draw_contour(ax, lon, lat, mask_c):
    mask_padded = np.pad(mask_c, 1, mode='constant', constant_values=0)
    dlon = lon[1] - lon[0]
    dlat = lat[1] - lat[0]
    lon_padded = np.concatenate([[lon[0] - dlon], lon, [lon[-1] + dlon]])
    lat_padded = np.concatenate([[lat[0] - dlat], lat, [lat[-1] + dlat]])
    ax.contour(lon_padded, lat_padded, mask_padded,
               levels=[0.5],
               colors=['gray'],
               linewidths=2,
               transform=ccrs.PlateCarree())


# Load all data once + precalculate mask for contour
print("Chargement des masques...")
all_data = []
for domain in domains:
    ds = xr.open_dataset('/home/cfontana/meshmasks/' + domain, engine="netcdf4")
    lon = np.array(ds['longitude'])
    lat = np.array(ds['latitude'])
    mask = load_mask(ds)
    print(f"  {domain}: calcul du masque contour...")
    mask_c = mask_for_contour(lon, lat, mask)
    all_data.append((domain, lon, lat, mask, mask_c))


# First map: all contours together
fig, ax = make_base_map()
for domain, lon, lat, mask, mask_c in all_data:
    draw_contour(ax, lon, lat, mask_c)
plt.savefig('/home/cfontana/MAPS/ALL_DOMAINS.jpg', bbox_inches='tight', dpi=200)
plt.close(fig)


# Second loop: one map per domain
for domain, lon, lat, mask, mask_c in all_data:
    print(domain)

    fig, ax = make_base_map()

    # Red fill for current domain
    ax.contourf(lon, lat, mask,
                levels=[0.5, 1.5],
                colors=['red'],
                alpha=0.4,
                transform=ccrs.PlateCarree())

    # All contours (frontière marine uniquement)
    for _, l, la, m, mc in all_data:
        draw_contour(ax, l, la, mc)

    domain_out = domain.upper().replace('.NC', '.jpg')
    plt.savefig('/home/cfontana/MAPS/' + domain_out, bbox_inches='tight', dpi=200)
    plt.close(fig)

    # Composite with labels overlay
    base = Image.open('/home/cfontana/MAPS/' + domain_out).convert('RGBA')
    labels = Image.open('/home/cfontana/MAPS/labels.png').convert('RGBA')
    if labels.size != base.size:
        labels = labels.resize(base.size, Image.LANCZOS)
    base.paste(labels, (0, 0), labels)
    base.convert('RGB').save('/home/cfontana/MAPS/' + domain_out)
