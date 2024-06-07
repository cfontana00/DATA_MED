####################################
# Compare computed runoffs to data #
####################################

import warnings
warnings.simplefilter("ignore")
import numpy as np
from datetime import datetime
from fun_gen import load_config
import sys,os
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdates
matplotlib.use("Agg")

from fun_io import savefig



# Get args
# --------
config = sys.argv[1]  # Configuration name

# Load config file
# ----------------
load_config(config)
from fun_gen import *


# Convert river dates
# -------------------
rdini = datetime.strptime(river_ini,'%Y-%m-%d').toordinal()
rdend = datetime.strptime(river_end,'%Y-%m-%d').toordinal()

# Create arborescence
os.system('mkdir -p '+diagdir+'/'+config)
odir = diagdir+'/'+config+'/RIVERS'
os.system('mkdir -p '+odir)




# Loop on rivers
# --------------
for name in french_list:
 
  data = []
  comp = []

  raw=np.loadtxt('data/'+name+'.csv',skiprows=1,dtype=str)
  print('[FILE READ]','data/'+name+'.csv')

  # Loop on data
  for line in raw:

    line=line.replace('"','')
    line=line.split(",")

    jd=datetime.strptime(line[0],'%Y-%m-%dT00:00:00.000Z').toordinal()

    # Select interval
    if jd >= rdini and jd <= rdend:

      data.append([jd,line[1].replace('"','')])


  # COMPUTED
  # --------
  raw=np.loadtxt('computed/'+name+'.txt',skiprows=1,dtype=str)
  print('[FILE READ]','computed/'+name+'.txt')


  # Loop on data
  for line in raw:

     jd = datetime.strptime(line[0],'%Y%m%dT00:00:00.000Z').toordinal()
     ratio,offset = 1,0
     if name == 'Var':
        ratio,offset = 1,1
     comp.append([jd,ratio*float(line[1])+offset])


  data = np.array(data,dtype=float)
  comp = np.array(comp,dtype=float)

   
  fig, ax = plt.subplots(1,1,figsize=(6,6))

  plt.plot(data[:,0],data[:,1],'r-',linewidth=0.5,label='Data')
  plt.plot(data[:,0],data[:,1],'ro',markersize=2)

  plt.plot(comp[:,0],comp[:,1],'b-',linewidth=0.5,label='Computed')
  plt.plot(comp[:,0],comp[:,1],'bo',markersize=.55)

  plt.legend()

  loc = mdates.AutoDateLocator()
  ax.xaxis.set_major_locator(loc)
  ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(loc))

  fname = odir +'/'+name+'.jpg'
  savefig(fname)

  plt.close()








# Loop on  rivers
# ---------------
for name in italian_list:

  data = []
  comp = []

  # DATA
  # ----
  raw=np.loadtxt('data/'+name+'.csv',skiprows=19,dtype=str)
  print('[FILE READ]','data/'+name+'.csv')

  # Loop on data
  for line in raw:

     line = line.split(',')

     jd = datetime.strptime(line[0],'%d/%m/%Y').toordinal()
     if jd >= rdini and jd <= rdend:
       try:
         exec('runoff = '+line[1]+'.'+line[2])
         data.append([jd,runoff])
       except:
         data.append([jd,np.nan])
         pass


  # COMPUTED
  # --------
  raw=np.loadtxt('computed/'+name+'.txt',skiprows=1,dtype=str)
  print('[FILE READ]','computed/'+name+'.txt')

   
  # Loop on data
  for line in raw:

     jd = datetime.strptime(line[0],'%Y%m%dT00:00:00.000Z').toordinal()
     comp.append([jd,line[1]])


  data = np.array(data,dtype=float)
  comp = np.array(comp,dtype=float)


  fig, ax = plt.subplots(1,1,figsize=(6,6))

  plt.plot(data[:,0],data[:,1],'r-',linewidth=0.5,label='Data')
  plt.plot(data[:,0],data[:,1],'ro',markersize=2)

  plt.plot(comp[:,0],comp[:,1],'b-',linewidth=0.5,label='Computed')
  plt.plot(comp[:,0],comp[:,1],'bo',markersize=.55)

  plt.legend()

  loc = mdates.AutoDateLocator()
  ax.xaxis.set_major_locator(loc)
  ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(loc))

  fname = odir +'/'+name+'.jpg'
  savefig(fname)

  plt.close()






