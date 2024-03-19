# ----------------- #
# General functions #
# ----------------- #

import numpy as np
from datetime import datetime
import json
import os


# ------------------------------ #
# Function loading configuration #
# ------------------------------ #
def load_config(config):

  # Load configuration file
  # -----------------------
  DIR=os.getenv('DATA_MED_DIR')
  with open(DIR+'config/config_'+config+'.json') as file:
    data = json.load(file)
    file.close()

    # Read entries
    # ------------
    for key in data.keys():
       if key != '_____':
         exec( key + " = data['"+key+"']")
         exec("globals()[f'"+key+"']  =  data['"+key+"']")

    # Date conversion
    # ---------------
    global jdini,jdend
    jdini=datetime.strptime(data["date_ini"],'%Y-%m-%d').toordinal()
    jdend=datetime.strptime(data["date_end"],'%Y-%m-%d').toordinal()

  print('=> Config file loaded')
  print('---------------------\n')


# ---------------------------------- #
# END Function loading configuration #
# ---------------------------------- #



# -------------------------- #
# Function loading variables #
# -------------------------- #
def load_variable(config,var):
 
   # Load file
   DIR=os.getenv('DATA_MED_DIR')
   pars=np.loadtxt(DIR+'config/variables_mit_'+config+'.dat',dtype=str)

   # Loop on variables
   for par in pars:
     if par[0] == var:
       break

   return par[0],\
          par[1],\
          par[2],\
          json.loads(par[3].lower()),\
          par[4],float(par[5]),\
          float(par[6]),\
          par[7],\
          par[8]





# ------------------------------ #
# END Function loading variables #
# ------------------------------ #











