#########################################
# Routine to read river data and create 
# MITgcm input files                 
#########################################

import numpy as np
from datetime import datetime
from fun_gen import load_config

global jdini

# Load parameters
load_config()
from fun_gen import *


# List to store all data
full=[]

# -------------
# FRENCH RIVERS
# -------------
rlist=['rhone','var','argens']

# Loop on rivers
# --------------
for name in rlist:
 
  data=[]

  # Load file
  raw=np.loadtxt(name+'.csv',skiprows=1,dtype=str)

  for line in raw:
      line=line.replace('"','')
      line=line.split(",")

      d=datetime.strptime(line[0],'%Y-%m-%dT00:00:00.000Z')
      jd=d.toordinal()

      # Store data => QC ?
      if jd >= jdini and jd <= jdend:
        data.append([jd,float(line[1])])

  # Store array    
  full.append([name,data])

  print(full)








