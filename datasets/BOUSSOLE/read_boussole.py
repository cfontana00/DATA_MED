#####################################
# Routine reading BOUSSOLE data     #
# and interpolating model variables #
#####################################
import warnings
warnings.simplefilter("ignore")
import numpy as np

from fun_gen import *
from fun_io import *
import sys,os,argparse

import matplotlib
matplotlib.use("Agg")

def argument():
    parser = argparse.ArgumentParser(description = '',formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(   '--config', '-c',
                                type = str,
                                required = True,
                                help ='Configuration name'
                                )
    return parser.parse_args()


# Get args
# --------
args = argument()
config = args.config  # Configuration name


# Load config file
# ----------------
load_config(config)
from fun_gen import *

# Create diagnostic arborescence
os.system('mkdir -p '+diagdir)
os.system('mkdir -p '+diagdir+'/'+config)
savedir = diagdir+'/'+config+'/BOUSSOLE'
os.system('mkdir -p '+savedir)


# Get current variable parameters
vname, ftag, cmap, islog, vmod, vmin, vmax, label, units\
        = load_variable(config,'chl')


# Read file
# ---------
data=[]

with open('data/Boussole-pig-maj20240116.csv') as fd:
 for n, line in enumerate(fd):
   if n > 5: 
     line = line.split(',')
   
     day = str(line[2]).zfill(2) 
     mon = str(line[3]).zfill(2)
     year = line[4]
     hour = str(int(float(line[5])))

     try:
       jd = dt.datetime.strptime(year+mon+day,'%Y%m%d').toordinal()
       jd = jd + float(line[5])/24.

       #                 Lon     Lat    Depth    Tchla
       data.append([jd,line[9],line[8],line[11],line[40]])

     except Exception as e :
       print(e)
       print('Error line',n,'\n')

data=np.array(data,dtype=float)


# Load coordinates
# ----------------
lon_mod,lat_mod,lev_mod=load_coords()

# Loop on days to create profiles
# --------------------------------
print('Processing day:\n')
for jd in range(jdini,jdend+1):

    
   profile=[]
                                                               
   # Select data for                         # /!\ jdend + 23:59
   idx = np.where( ( data[:,0] >= jd) & (data[:,0] <= jd+0.99999))  

   idx =  np.array(idx) 

   # Get model values
   # ----------------
   if idx.any() : 

     d = dt.datetime.fromordinal(int(np.floor(jd)))
     print('Data found on',d.strftime('%Y-%m-%d'))

     # Get filename
     fname,dtag = get_filename(int(np.floor(jd)),ftag)

     # Select data for this layer
     slc = data[idx].squeeze()
     slc = np.flipud(slc)

     # Get interpolated model value
     val  = get_model_val_3d(fname,0,vname,\
               lon_mod,lat_mod,lev_mod,\
                 slc[:,1],slc[:,2],slc[:,3])

     # Store data
     profile.append([slc[:,3],val[:],slc[:,4]])
     profile = np.array(profile).squeeze().T


     # Store profile

     # Write data 
     np.savetxt(savedir+'/boussole_profile_'+d.strftime('%Y-%m-%d')+'.dat',profile)

     # Plot profile
     fig, ax = plt.subplots(1,1,figsize=(float(fig_prox), float(fig_proy)))

     plt.plot(profile[:,1],-profile[:,0],c='g',marker='o',alpha=0.7,label='Model')
     plt.plot(profile[:,2],-profile[:,0],c='g',marker='s',alpha=0.7,label='Data')

     plt.title('BOUSSOLE '+d.strftime('%Y-%m-%d'))

     plt.legend(loc='lower right')

     plt.xlabel(label+' ('+units+')')
     plt.ylabel("Depth (m)")

     savefig(savedir+'/boussole_profile_'+d.strftime('%Y-%m-%d')+'.'+fig_fmt)
     #plt.show()

     print('')


