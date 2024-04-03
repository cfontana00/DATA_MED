# --------------- #
# Read ADCP files #
# --------------- #

import warnings
warnings.simplefilter("ignore")

import numpy as np
import scipy.io as sio

data = sio.loadmat('data/data.mat')

print(data)


