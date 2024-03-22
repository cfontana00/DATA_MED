#####################################
# Routine reading BOUSSOLE data     #
# and interpolating model variables #
#####################################

import numpy as np

from fun_gen import *
from fun_io import *
import sys,os




# Get args
# --------
config = sys.argv[1]  # Configuration name



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

     if year == '2022':
       year = '2021' # !!!!!!!!!!!!

     try:
       jd = dt.datetime.strptime(year+mon+day,'%Y%m%d').toordinal()
       jd = jd + float(line[5])/24.

       #                 Lon     Lat    Depth    Tchla
       data.append([jd,line[9],line[8],line[11],line[40]])

     except Exception as e :
       print(e)
       print('Error line',n,'\n')

data=np.array(data,dtype=float)


# Define model layer thicknesses
# ------------------------------
lon_mod,lat_mod,lev_mod=load_coords()

thick=[]
thick.append([0,lev_mod[1]])

for i in range(1,35):
  thick.append([lev_mod[i],lev_mod[i+1]]) 

thick = np.array(thick)


# Loop on days to create profiles
# --------------------------------
print('Processing day:\n')
for jd in range(jdini,jdend+1):

  # Get filename
  fname,dtag = get_filename(int(np.floor(jd)),ftag)
  print(dtag)
    
  profile=[]
  for t in thick:

                                                               
      # Select data for this layer                      # /!\ jdend + 23:59
    idx = np.where( ( data[:,0] >= jd) & (data[:,0] <= jd+0.99999)  &\
                      (data[:,3] >= t[0])  & (data[:,3] <= t[1]) ) 

    # Select data for this layer
    slc = data[idx]
 
    # Get model values
    # ----------------

    # Get interpolated model value
    for s  in slc:
      val  = get_model_val_3d(fname,vname,\
               lon_mod,lat_mod,lev_mod,\
                s[1],s[2],s[3])

      # Store data
      profile.append([s[3],val,s[4]])


  # Store profile
  if profile: 
    profile = np.array(profile)
    d = dt.datetime.fromordinal(int(np.floor(jd)))

    # Write data 
    np.savetxt(savedir+'/boussole_profile_'+d.strftime('%Y-%m-%d')+'.dat',profile)

    # Plot profile
    fig, ax = plt.subplots(1,1,figsize=(float(fig_prox), float(fig_proy)))


    plt.plot(profile[:,1],-profile[:,0],c=col1,marker='o',alpha=0.7,label='Model')
    plt.plot(profile[:,2],-profile[:,0],c=col2,marker='o',alpha=0.7,label='Data')
    plt.title('BOUSSOLE '+d.strftime('%Y-%m-%d'))

    plt.legend(loc='lower right')

    plt.xlabel(label+' ('+units+')')
    plt.ylabel("Depth (m)")

    savefig(savedir+'/boussole_profile_'+d.strftime('%Y-%m-%d')+'.'+fig_fmt)
    #plt.show()
















     



