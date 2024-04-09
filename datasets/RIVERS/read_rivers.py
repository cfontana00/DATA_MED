#########################################
# Routine to read river data and create 
# MITgcm input files                 
#########################################

import numpy as np
from datetime import datetime
from fun_gen import load_config
import sys,os


# Load parameters
# ---------------
load_config(sys.argv[1])
from fun_gen import *


# Convert river dates
# -------------------
rdini=datetime.strptime(river_ini,'%Y-%m-%d').toordinal()
rdend=datetime.strptime(river_end,'%Y-%m-%d').toordinal()


os.system('mkdir -p readyfiles')


# List to store all data
full=[]

# -------------
# FRENCH RIVERS
# -------------

# Loop on rivers
# --------------
print('Processing rivers')
for name in french_list:

  print('=>',name)

  data = []
  jd_old = -99

  # Load file
  try :
    raw=np.loadtxt('data_modif/'+name+'_modif.csv',skiprows=1,dtype=str)
    print('[FILE READ]','data_modif/'+name+'_modif.csv')
  except :
    raw=np.loadtxt('data/'+name+'.csv',skiprows=1,dtype=str)
    print('[FILE READ]','data/'+name+'.csv')


  # Loop on data
  for line in raw:

     line=line.replace('"','')
     line=line.split(",")

     jd=datetime.strptime(line[0],'%Y-%m-%dT00:00:00.000Z').toordinal()
  
     # Select interval
     if jd >= rdini and jd <= rdend:
    
       # Check for data continuity 
       if jd - jd_old != 1 and jd_old != -99 :
         print('ERROR ! Data are not continue at day',line[0])
         print('You must pre-processed data or check dates\n')
         exit()


       d=line[0].replace('-','')
       d=d.replace('.000Z','')

       data.append([d,line[1].replace('"','')])

       jd_old = jd

  # Write file
  # ----------
  data=np.array(data,dtype=str)
  np.savetxt('readyfiles/'+name+'.txt',data,fmt="%s %s")

  print('[FILE SAVED]','readyfiles/'+name+'.txt\n')

  

#---------------
# ITALIAN RIVERS
# --------------

for name in italian_list:
 print('=>',name)

 data = []
 jd_old = -99

 # Load file
 try :
   raw=np.loadtxt('data_modif/'+name+'_modif.csv',skiprows=19,delimiter=',',dtype=str)
   print('[FILE READ]','data_modif/'+name+'_modif.csv')
 except:
   raw=np.loadtxt('data/'+name+'.csv',skiprows=19,delimiter=',',dtype=str)
   print('[FILE READ]','data/'+name+'.csv')


 for line in raw:

   date=datetime.strptime(line[0],'%d/%m/%Y')
   jd=date.toordinal()

   # Select interval
   if jd >= rdini and jd <= rdend:
  
     # Check for data continuity 
     if jd - jd_old != 1 and jd_old != -99 or not line[1].isnumeric()  :
       print('ERROR ! Data are not continue at day',line[0])
       print('        Or non numeric value :',line[1])
       print('You must pre-processed data or check dates\n')
       exit()



     d=date.strftime('%Y%m%d')+'T00:00:00.000Z'

     #print(line[1])
     data.append([d,line[1]])
  
 # Write file
 # ----------
 data=np.array(data,dtype=str)
 np.savetxt('readyfiles/'+name+'.txt',data,fmt="%s %s")

 print('[FILE SAVED]','readyfiles/'+name+'.txt\n')





