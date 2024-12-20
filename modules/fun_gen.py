# ----------------- #
# General functions #
# ----------------- #

from fun_io import load_coords
import numpy as np
from datetime import datetime
import json
import os


# ------------------------------ #
# Function loading configuration #
# ------------------------------ #
def load_config(config):
    
 try :
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
     jdini = datetime.strptime(data["date_ini"],'%Y-%m-%d').toordinal()
     jdend = datetime.strptime(data["date_end"],'%Y-%m-%d').toordinal()

     # Define boundary limits
     # ----------------------
     lon,lat,lev = load_coords() 
     global ibmin,ibmax,jbmin,jbmax

     # Default limites
     ibmin = 0
     ibmax = lon.shape[0]
     jbmin = 0
     jbmax = lat.shape[0]

     # Define boundaries
     if rm_boundary == 'yes':

        for tag in boundary:
           if tag == 'W':
             ibmin = damping
             
           if tag == 'E':
             ibmax = ibmax-damping

           if tag == 'S':
             jbmin = damping

           if tag == 'N':
             jbmax = jbmax-damping


   os.system('mkdir -p '+diagdir)
   os.system('mkdir -p '+diagdir+'/'+config)

   print('----------------------------------')
   print('=> Config file '+config+' loaded')
   print('----------------------------------\n')

 except Exception as e :
  print('Error in argument or config')
  print(e)
  exit()




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
   
   #print('----------------')
   #print('Variable :',var)
   #print('cmap :',par[2])
   #print('log :',par[3])
   #print('min/max mode :',par[4])
   #print('vmin :',par[5])
   #print('vmax :',par[6])
   #print('----------------\n')


   return par[0],\
          par[1],\
          par[2],\
          json.loads(par[3].lower()),\
          par[4],float(par[5]),\
          float(par[6]),\
          par[7].replace('_',' '),\
          par[8]

# ------------------------------ #
# END Function loading variables #
# ------------------------------ #



# -----------------------------
# Create arborescence for diags
# -----------------------------
def create_arbo(config,var,name):

  #Config dir
  os.system('mkdir -p '+diagdir)
  os.system('mkdir -p '+diagdir+'/'+config)
  os.system('mkdir -p '+diagdir+'/'+config+'/'+name)

  # Variable dir
  vdir = diagdir+'/'+config+'/'+name+'/'+var
  os.system('mkdir -p '+vdir)

  return vdir

# -----------------------------












