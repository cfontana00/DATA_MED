#########################################
# Routine to read river data and create 
# MITgcm input files                 
#########################################

import numpy as np
from datetime import datetime
from fun_gen import load_config
import sys


# Load parameters
# ---------------
try :
  load_config(sys.argv[1])
  from fun_gen import *
except Exception as e :
  print('Error in argument or config')
  print(e)
  exit()




# List to store all data
full=[]

# -------------
# FRENCH RIVERS
# -------------

# Loop on rivers
# --------------
for name in french_list:
 
  data=[]

  # Load file
  raw=np.loadtxt('data/'+name+'.csv',skiprows=1,dtype=str)

  # Loop on data
  for line in raw:
     line=line.replace('"','')
     line=line.split(",")

     jd=datetime.strptime(line[0],'%Y-%m-%dT00:00:00.000Z').toordinal()

     # Store data ( => QC ? )
     if jd >= jdini and jd <= jdend:
       data.append([jd,float(line[1])])

  # Store array    
  full.append([name,data])


# Print data
# ----------
for river in full:
 print(river)








