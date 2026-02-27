import warnings
import sys
import os
import argparse
from glob import glob
from typing import Tuple, List, Optional, Dict, Any

import numpy as np
import xarray as xr
import datetime as dt
import cv2
import cartopy.feature as cfeature
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.colors as colors
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import matplotlib
matplotlib.use("Agg")
import cmocean
import cmcrameri

# --- Imports locaux ---
from fun_gen import *
from fun_io import *
from fun_plot_2D import *
from fun_meteo import load_meteo

def gkern(l: int, sig: float) -> np.ndarray:
    """
    Crée un noyau gaussien de taille `l` et d'écart-type `sig`.

    Args:
        l: Taille du noyau (côté carré).
        sig: Écart-type du noyau gaussien.

    Returns:
        Noyau gaussien normalisé.
    """
    ax = np.linspace(-(l - 1) / 2., (l - 1) / 2., l)
    gauss = np.exp(-0.5 * np.square(ax) / np.square(sig))
    kernel = np.outer(gauss, gauss)
    return kernel / np.sum(kernel)

def parse_arguments() -> argparse.Namespace:
    """Parse les arguments en ligne de commande."""
    parser = argparse.ArgumentParser(
        description='Script de comparaison modèle/satellite',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--config', '-c',
        type=str,
        required=True,
        help='Nom de la configuration'
    )
    parser.add_argument(
        '--variable', '-v',
        type=str,
        required=True,
        help='Variable : thetao ou chl'
    )
    parser.add_argument(
        '--satellite', '-s',
        type=str,
        required=True,
        help='Nom du satellite (ex: CMEMS)'
    )
    return parser.parse_args()

def load_variable_params(config: str, var: str) -> Tuple[str, str, str, bool, str, float, float, str, str]:
    """Charge les paramètres de la variable à tracer."""
    return load_variable(config, var)

def get_hour_range(var: str) -> List[int]:
    """Retourne la plage horaire en fonction de la variable."""
    if var == 'chl':
        return list(range(12, 13))
    elif var == 'thetao':
        return list(range(0, 1))
    else:
        raise ValueError(f"Variable {var} non supportée.")

def init_plot(ax: plt.Axes, extent: List[float], proj: ccrs.Projection) -> None:
    """Initialise un axe de figure avec la projection et l'étendue données."""
    ax.set_extent(extent, crs=proj)
    ax.coastlines()
    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.gridlines(draw_labels=True)
    ax.xaxis.set_major_formatter(LONGITUDE_FORMATTER)
    ax.yaxis.set_major_formatter(LATITUDE_FORMATTER)

def apply_mask(var2d: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Applique un masque à une variable 2D."""
    var2d = var2d + mask
    var2d[np.where(var2d == 0)] = np.nan
    return var2d

def plot_variable(
    ax: plt.Axes,
    lon: np.ndarray,
    lat: np.ndarray,
    var2d: np.ndarray,
    cmap: str,
    vmin: float,
    vmax: float,
    islog: bool,
    label: str,
    units: str,
    title: str,
    fig_title_size: int
) -> plt.QuadMesh:
    """Trace une variable 2D sur un axe donné."""
    if not islog:
        p = ax.pcolor(lon, lat, var2d, cmap=cmap, vmin=vmin, vmax=vmax, zorder=1)
    else:
        p = ax.pcolor(lon, lat, var2d, cmap=cmap, norm=colors.LogNorm(vmin=vmin, vmax=vmax), zorder=1)
    ax.set_title(title, fontsize=fig_title_size)
    return p

def save_time_series(time_series: List[List[float]], ddir: str) -> None:
    """Sauvegarde la série temporelle dans un fichier."""
    np.savetxt(os.path.join(ddir, 'time_series.dat'), np.array(time_series))

def main() -> None:
    # --- Parse arguments ---
    args = parse_arguments()
    config = args.config
    var = args.variable
    sat = args.satellite

    # --- Load config and params ---
    load_config(config)
    from fun_gen import *

    # --- Init plot params ---
    lower = (100 - 95) / 2
    upper = 100 - lower
    lon, lat, levels = load_coords()
    proj = eval(fig_proj)  # Attention: utiliser eval uniquement si fig_proj est sûr
    extent = [lon.min(), lon.max(), lat.min(), lat.max()]
    hours = get_hour_range(var)

    # --- Load mask ---
    with xr.open_dataset(maskfile) as ds:
        mask = np.array(ds['tmask'][0, :, :].squeeze(), dtype=float)
    mask[mask == 0] = np.nan
    mask[mask == 1] = 0

    # --- Init figure ---
    fig, (ax1, ax2) = plt.subplots(
        1, 2,
        figsize=(float(fig_sx_sat), float(fig_sy_sat)),
        subplot_kw={'projection': proj},
        constrained_layout=True
    )
    init_plot(ax1, extent, proj)
    init_plot(ax2, extent, proj)

    # --- Main loop ---
    time_series = []
    cb_done = False

    for jd in range(jdini, jdend + 1):
        vname, ftag, cmap, islog, vmod, vmin, vmax, label, units = load_variable_params(config, var)

        for hour in hours:
            # --- Load model data ---
            fname, dtag = get_filename(jd, ftag)
            if var == 'thetao':
                var2d = get_var_2D(jd, jdini, fname, var, hour, 1)
            elif var == 'chl':
                var2d = get_integre_2D(jd, jdini, fname, var, levels, hour)
            var2d = apply_mask(np.array(var2d), mask)

            # --- Load satellite data ---
            ddir = os.path.join(diagdir, config, sat, var, 'ITP_NC')
            fname = os.path.join(ddir, f'{var}_{dtag}.nc')
            sat2d = get_sat_2D(fname, var)
            sat2d = np.array(sat2d)
            sat2d[np.isnan(var2d)] = np.nan

            # --- Auto vmin/vmax if needed ---
            if vmod == 'auto':
                arr = var2d[~np.isnan(var2d)].flatten()
                if sat2d.size > 0:
                    sat_arr = sat2d[~np.isnan(sat2d)].flatten()
                    arr = np.concatenate([arr, sat_arr])
                vmin = np.percentile(arr, lower)
                vmax = np.percentile(arr, upper)

            # --- Plot model ---
            date = dt.datetime.fromordinal(jd)
            title = f'Model {date.strftime("%Y-%m-%d")} {hour:02d}h'
            p1 = plot_variable(ax1, lon, lat, var2d, cmap, vmin, vmax, islog, label, units, title, fig_title_size)

            # --- Plot satellite ---
            if var == 'thetao':
                sat2d = sat2d - 273.16  # Kelvin to C
            title = f'Satellite {date.strftime("%Y-%m-%d")} {hour:02d}h'
            p2 = plot_variable(ax2, lon, lat, sat2d, cmap, vmin, vmax, islog, label, units, title, fig_title_size)

            # --- Colorbar ---
            if not cb_done:
                cb = plt.colorbar(
                    p2,
                    extend='both',
                    fraction=float(cb_fraction_sat),
                    pad=float(cb_pad_sat),
                    label=f'{label} ({units})',
                    ax=ax2
                )
                cb.set_label(label=f'{label} ({units})', fontsize=cb_lbl_size_sat)
                cb.ax.tick_params(labelsize=cb_lbl_size_sat)
                if islog:
                    cb.ax.yaxis.set_minor_formatter(FormatStrFormatter('%.2f'))
                    cb.ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
                    cb.ax.tick_params(axis='both', which='both', labelsize=tck_size_ts)
                cb_done = True

            # --- Save plot ---
            savedir = os.path.join(ddir, 'PLOT')
            os.makedirs(savedir, exist_ok=True)
            fout = os.path.join(savedir, f'{dtag}{hour:02d}_{var}.{fig_fmt}')
            plt.savefig(fout)
            p1.remove()
            p2.remove()

            # --- Store time series ---
            idx_good = np.where((~np.isnan(sat2d)) & (~np.isnan(var2d)))
            idx_tot = np.where(~np.isnan(var2d))
            sat2d_good = sat2d[idx_good]
            var2d_good = var2d[idx_good]
            perc = float(len(sat2d_good)) / float(len(var2d[idx_tot]))
            time_series.append([jd, np.mean(var2d_good), np.mean(sat2d_good), perc])
            print(jd, np.mean(var2d_good), np.mean(sat2d_good), perc)

    # --- Save time series ---
    save_time_series(time_series, ddir)
    plt.close()

if __name__ == '__main__':
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        main()

