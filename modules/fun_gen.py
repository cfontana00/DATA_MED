# ----------------- #
# General functions #
# ----------------- #

import numpy as np
from datetime import datetime
import json


# ------------------------------
# Function loading configuration
# ------------------------------
def load_config(config):

  # Load configuration file
  # -----------------------
  with open('../../config/config_'+config+'.json') as file:
    data = json.load(file)
    file.close()

    # Read entries
    # ------------
    for key in data.keys():
       if key != '_____':
         exec( key + " = data['"+key+"']")
         exec("globals()[f'"+key+"']  =  data['"+key+"']")
         #print(key,'=',data[key])

    # Date conversion
    # ---------------
    global jdini,jdend
    jdini=datetime.strptime(data["date_ini"],'%Y-%m-%d').toordinal()
    jdend=datetime.strptime(data["date_end"],'%Y-%m-%d').toordinal()

  print('=> Config file loaded')
  print('')

