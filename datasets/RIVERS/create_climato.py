#########################################
# Create rivers climato
#########################################

import numpy as np
from datetime import datetime
from fun_gen import load_config
import sys,os


# Get args
# --------
config = sys.argv[1]  # Configuration name

# Load config file
# ----------------
load_config(config)
from fun_gen import *


print(french_list)
