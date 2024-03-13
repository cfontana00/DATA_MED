from fun_gen import load_config
import numpy as np

# Load parameters
load_config()
from fun_gen import *

print("The initial day is",jdini)

# Load data
data=np.loadtxt("my_new_data.dat")
print('My data is',data)

# To be continued ...



