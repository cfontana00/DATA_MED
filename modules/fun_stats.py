import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy import stats
from scipy.stats import gaussian_kde
import json
import os
import datetime as dt


def compute_stats(var2d, sat2d, jd, var_name, units, output_dir):
    """
    Compute validation statistics between model and satellite data.
    
    Parameters
    ----------
    var2d : np.ndarray - Model 2D field (NaN = masked)
    sat2d : np.ndarray - Satellite 2D field on same grid (NaN = masked)
    output_dir : str   - Directory to save outputs
    var_name : str     - Variable name for plot titles
    units : str        - Units for axis labels
    """

    date = dt.datetime.fromordinal(jd)
    y,m,d = date.strftime('%Y'),date.strftime('%m'),date.strftime('%d')        
    dtag = y+'-'+m+'-'+d

    # -------------------------------------------------------
    # 1. Mask: only keep pixels valid in BOTH arrays
    # -------------------------------------------------------
    mask = np.isfinite(var2d) & np.isfinite(sat2d)
    mod  = var2d[mask].flatten()
    sat  = sat2d[mask].flatten()
    n    = len(mod)
    print(f"Valid pixels: {n}")

    # -------------------------------------------------------
    # 2. Compute statistics
    # -------------------------------------------------------
    bias  = np.mean(mod - sat)
    mae   = np.mean(np.abs(mod - sat))
    rmse  = np.sqrt(np.mean((mod - sat)**2))
    r, p  = stats.pearsonr(mod, sat)

    # Willmott Index of Agreement
    obs_mean = np.mean(sat)
    d = 1 - (np.sum((mod - sat)**2) /
             np.sum((np.abs(mod - obs_mean) + np.abs(sat - obs_mean))**2))

    # STD ratio
    std_mod = np.std(mod)
    std_sat = np.std(sat)
    std_ratio = std_mod / std_sat

    # Centered RMSE (for Taylor diagram)
    crmse = np.sqrt(rmse**2 - bias**2)

    # Kling-Gupta Efficiency
    kge = 1 - np.sqrt((r - 1)**2 + (std_ratio - 1)**2 + (bias / obs_mean)**2)

    # Murphy Skill Score (reference = satellite mean)
    ss = 1 - (rmse**2 / np.mean((sat - obs_mean)**2))

    # -------------------------------------------------------
    # 3. Save statistics to JSON
    # -------------------------------------------------------
    stats_dict = {
        'n_valid_pixels' : int(n),
        'bias'           : round(float(bias),   4),
        'mae'            : round(float(mae),    4),
        'rmse'           : round(float(rmse),   4),
        'crmse'          : round(float(crmse),  4),
        'pearson_r'      : round(float(r),      4),
        'pearson_p'      : round(float(p),      6),
        'willmott_d'     : round(float(d),      4),
        'std_model'      : round(float(std_mod),4),
        'std_sat'        : round(float(std_sat),4),
        'std_ratio'      : round(float(std_ratio),4),
        'kge'            : round(float(kge),    4),
        'skill_score'    : round(float(ss),     4),
    }

    json_path = os.path.join(output_dir, 'validation_stats.json')
    with open(json_path, 'w') as f:
        json.dump(stats_dict, f, indent=4)
    print(f"Stats saved → {json_path}")
    print(json.dumps(stats_dict, indent=4))

    # -------------------------------------------------------
    # 4. Plots
    # -------------------------------------------------------

    # --- 4a. PDF comparison ---
    print('PDF')
    fig, ax = plt.subplots(figsize=(7, 5))
    kde_mod = gaussian_kde(mod)
    kde_sat = gaussian_kde(sat)
    x_range = np.linspace(min(mod.min(), sat.min()),
                          max(mod.max(), sat.max()), 300)
    ax.plot(x_range, kde_sat(x_range), color='steelblue',  lw=2, label='Satellite')
    ax.plot(x_range, kde_mod(x_range), color='darkorange', lw=2, label='Model')
    ax.fill_between(x_range, kde_sat(x_range), kde_mod(x_range),
                    alpha=0.15, color='gray')
    ax.set_xlabel(f'{var_name} ({units})')
    ax.set_ylabel('Density')
    ax.set_title('PDF comparison – Model vs Satellite')
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, 'pdf_comparison_'+dtag+'.png'), dpi=150)
    plt.close(fig)

    # --- 4b. Scatter plot model vs satellite ---
    print('SCATTER')
    """
    fig, ax = plt.subplots(figsize=(6, 6))
    xy  = np.vstack([sat, mod])
    z   = gaussian_kde(xy)(xy)          # density for coloring
    idx = z.argsort()
    ax.scatter(sat[idx], mod[idx], c=z[idx], s=2, cmap='viridis')
    lims = [min(sat.min(), mod.min()), max(sat.max(), mod.max())]
    ax.plot(lims, lims, 'r--', lw=1.5, label='1:1')
    ax.set_xlabel(f'Satellite {var_name} ({units})')
    ax.set_ylabel(f'Model {var_name} ({units})')
    ax.set_title('Scatter plot – Model vs Satellite')
    ax.text(0.05, 0.95,
            f'r={r:.2f}  RMSE={rmse:.2f}  Bias={bias:.2f}',
            transform=ax.transAxes, va='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, 'scatter_'+dtag+'.png'), dpi=150)
    plt.close(fig)
    """

    # --- 4c. Bias spatial map ---
    print('BIAS')
    bias_map = var2d - sat2d        # keeps NaN where either is masked
    fig, ax = plt.subplots(figsize=(6, 5))
    vabs = np.nanpercentile(np.abs(bias_map), 95)
    im = ax.imshow(bias_map, cmap='RdBu_r', vmin=-vabs, vmax=vabs,
                   origin='lower')
    plt.colorbar(im, ax=ax, label=f'Bias ({units})')
    ax.set_title('Spatial bias (Model − Satellite)')
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, 'bias_map_'+dtag+'.png'), dpi=150)
    plt.close(fig)

    # --- 4d. Taylor Diagram ---
    print('TAYLOR')
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={'projection': 'polar'})
    ax.set_thetamax(180)
    # reference point (satellite)
    theta_ref = np.arccos(1.0)
    ax.plot(theta_ref, std_sat, 'b*', ms=12, label='Satellite (ref)')
    # model point
    theta_mod = np.arccos(np.clip(r, -1, 1))
    ax.plot(theta_mod, std_mod, 'ro', ms=10, label=f'Model (r={r:.2f})')
    # reference std arc
    arc = np.linspace(0, np.pi, 100)
    ax.plot(arc, np.full_like(arc, std_sat), 'b--', lw=1)
    # CRMSE arc
    crmse_arc = np.linspace(0, 2 * np.pi, 200)
    ax.plot(crmse_arc,
            np.sqrt(std_sat**2 + std_mod**2 - 2*std_sat*std_mod*np.cos(crmse_arc)),
            'g:', lw=1, label=f'cRMSE={crmse:.2f}')
    ax.set_xlabel('Correlation')
    ax.set_title('Taylor Diagram', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, 'taylor_diagram_'+dtag+'.png'), dpi=150)
    plt.close(fig)

    print(f"Plots saved in → {output_dir}/")
    return stats_dict
