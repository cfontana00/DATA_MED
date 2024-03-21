from fun_gen import load_config
from fun_io import *
from fun_plot_2D import *
import numpy as np
import sys

# ------------------------------------------
# Use: python3 my_new_routine.py config_name
# -----------------------------------------

# Load parameters
try :
  load_config(sys.argv[1])
  from fun_gen import *
except Exception as e :
  print('Error in argument/config')
  print(e)
  exit()

print("The initial julian day is",jdini)
print("The final julian day is",jdend)

# Load data
data=np.loadtxt("my_new_data.dat")
print('My data is',data)
print('-----------------------------')


# Load coordinates
lon,lat,levels = load_coords()


# Define model parameters
print('Load data ...\n')
varname = 'thetao'
level = 0


for jd in range(jdini,jdend):

  # Get filename
  fname,dtag = get_filename(jd,'TEMP')

  # Get 2D variable
  var2d = get_var_2D(fname,varname,level)

  # Get 3D variable
  var3d = get_var_3D(fname,varname)

  # Plot
  # ----
  print('Plot ...\n')
  exec('proj = ' + fig_proj)
  extent = [lon.min(),lon.max(),lat.min(),lat.max()]
  fig, ax = plt.subplots(1,1,figsize=(float(fig_sx), float(fig_sy)), subplot_kw={'projection': proj})
  init_fig(ax,extent,proj)

  plt.show()
  plt.close()

  break

print('To be continued ...')



