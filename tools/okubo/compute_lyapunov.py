from matplotlib import pyplot as plt
from numba import njit
from numpy import arange, arctan2, empty, isnan, log, ma, meshgrid, ones, pi, zeros

from py_eddy_tracker import start_logger
from py_eddy_tracker.data import get_demo_path
from py_eddy_tracker.dataset.grid import GridCollection, RegularGridDataset

import numpy as np


start_logger().setLevel("ERROR")
from netCDF4 import Dataset


fname = '/home/fontana/DISK2TB/MODEL/OUTPUTS/ALBEDO/20150331/20150401_h-OGS--RFVL-MITgcmBFM-pilot8-b20150331_fc-v01.nc'

c = GridCollection.from_netcdf_cube(
    fname,
    "longitude",
    "latitude",
    "time",
    # To create U/V variable
    heigth=None,
)

ds = Dataset(fname,format='NETCDF4-CLASSIC')
lon = np.array(ds['longitude'])
lat = np.array(ds['latitude'])
u = np.array(ds['uo'][:,0,:,:]).squeeze()
v = np.array(ds['vo'][:,0,:,:]).squeeze()
ds.close()

LON,LAT = np.meshgrid(lon,lat)

f = c.filament(LON.reshape(-1),
               LAT.reshape(-1),
               u.T.reshape(-1),
               v.T.reshape(-1),
         10, nb_step=10, time_step=600, filament_size=6, rk4=True )



