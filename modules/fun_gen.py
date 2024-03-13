import numpy as np
from datetime import datetime
import json



# Function loading configuration
# ------------------------------
def load_config():

  global jdini
  global jdend
  global outdir
  global french_list

  # Load configuration file
  with open('../config.par') as file:
    data = json.load(file)
    file.close()

    # General
    jdini=datetime.strptime(data["date_ini"],'%Y-%m-%d').toordinal()
    jdend=datetime.strptime(data["date_end"],'%Y-%m-%d').toordinal()
    outdir=data["outdir"]

    # Rivers
    french_list=data["french_list"]

    

