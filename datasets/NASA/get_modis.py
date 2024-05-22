#############################
# Routine to get MODIS data #
#############################


import numpy as np
import os


# Get args
# --------
config=sys.argv[1]  # Configuration name


# Load parameters
# ---------------
load_config(config)
from fun_gen import *

os.system('mkdir -p '+modis_dir)


# Loop on days
for jd in range(jdini,jdend+1):
 
    # Get date
    d = dt.datetime.fromordinal(jd)
    year = d.strftime('%Y')
    doy = d.strftime('%j').zfill(3)

    # Download
    # !!!! TO FINISH !!!!!






