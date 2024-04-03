# ------------------------------------- #
# Process MOLOCH meteo files for MITgcm #
# ------------------------------------- #


import warnings
warnings.filterwarnings("ignore")

import numpy as np

from fun_gen import *
from fun_io import *
import sys,os


# Get args
# --------
config = sys.argv[1]  # Configuration name

# Load config file
# ----------------
load_config(config)
from fun_gen import *


# Create output directory
# -----------------------
os.system('mkdir -p '+meteodir+'/readyfiles')


# Date conversion
# ---------------
mdini = datetime.strptime(meteo_ini,'%Y-%m-%d').toordinal()
mdend = datetime.strptime(meteo_end,'%Y-%m-%d').toordinal()

# Nomenclature
# ------------
nom = []

# -------------------------------------------------------------------------------------
#            In-tag       In-var     Out_var
# -------------------------------------------------------------------------------------
nom.append([ 'pmsl'    , 'prmsl'  ,  'msl' ])     # Pressure Reduced to MSL
nom.append([ 'dswrf'   , 'dswrf'  ,  'p3111' ])   # Downward short-wave radiation flux 
#nom.append([ '' , '',  'p3112' ])            # Downward long-wave radiation flux
nom.append([ 'rh2m'    , 'r2'     ,  'r' ])       # 2 metre relative humidity
nom.append([ 't2m'     , 't2'     ,  't2m' ])     # 2 metre temperature
nom.append([ 'clct'    , 'clct'   ,  'tcc' ])     # Total Cloud Cover 
nom.append([ 'apcp'    , 'unknown',  'tp' ])      # Total precipitation
nom.append([ 'wind10m' , 'u10'    ,  'u10' ])     # 10 metre U wind component
nom.append([ 'wind10m' , 'v10'    ,  'v10' ])     # 10 metre U wind component
# -------------------------------------------------------------------------------------



# Loop on days
# ------------
for jd in range(mdini,mdend+1):

   # Loop on variables
   # -----------------
   for tags in nom:
     intag = tags[0]
     invar = tags[1]
     ovar = tags[2]


     print(intag,invar,ovar)
     exit()
     






























