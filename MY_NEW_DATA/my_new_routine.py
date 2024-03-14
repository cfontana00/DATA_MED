from fun_gen import load_config
import numpy as np
import sys

# ------------------------------------------
# Use: python3 my_new_routine.py config_name
# -----------------------------------------

# Load parameters
try :
  load_config(sys.argv[1])
  from fun_gen import *
except :
  print('Error in argument/config')
  exit()

print("The initial day is",jdini)

# Load data
data=np.loadtxt("my_new_data.dat")
print('My data is',data)

# To be continued ...



