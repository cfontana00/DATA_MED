# -------------------------------- #
# Compare whale parameters to eddy #
# -------------------------------- #
import warnings
warnings.simplefilter("ignore")

from matplotlib import pyplot as plt
from fun_gen import load_config
from fun_io import savefig
from fun_whales import get_whale_pos
import argparse
import datetime as dt
import haversine as hs
from scipy.stats import linregress


def argument():
    parser = argparse.ArgumentParser(description = '',formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(   '--config', '-c',
                                type = str,
                                required = True,
                                help ='Configuration name'
                                )
    return parser.parse_args()

# Get args
args = argument()
config = args.config  # Configuration name


# Load config file
# ----------------
load_config(config)
from fun_gen import *


# Load eddy file
eddy = np.loadtxt(trans_file).squeeze()

# Load whale tracks
tjd,tlon,tlat = get_whale_pos('87780')


# Loop on days
# ------------
dist = []

for jd in range(jdini,jdend+1):

   d = dt.datetime.fromordinal(jd)
   dtag = d.strftime('%Y%m%d')

   # Get eddy position
   try : 
  
     idx = np.array( np.where( eddy[:,0].squeeze() == int(dtag) ))
     elon,elat = eddy[idx,1],eddy[idx,2]

     idx = np.where( tjd == jd )
     wlon2,wlat2 = tlon[idx],tlat[idx]
     wlon1,wlat1 = tlon[idx[0]-1],tlat[idx[0]-1]

     # Compute distance to eddy
     loc1 = (elat,elon)
     loc2 = (wlat2,wlon2)

     edist = hs.haversine(loc1,loc2)

     # Compute swum distance
     loc1 = (wlat1,wlon1)
     loc2 = (wlat2,wlon2)
 
     wdist =  hs.haversine(loc1,loc2)

     dist.append([np.log(edist),wdist])

   except Exception as e:
     #print(e)
     pass

dist = np.array(dist)


# Make plot
# ---------

print(dist)

fig,ax = plt.subplots(1,1,figsize=(6,6))

ax.scatter(dist[:,0],dist[:,1],marker='o',s=60,edgecolor='k',facecolor='none')

plt.xlabel('Logarithm of the daily distance to the eddy')
plt.ylabel('Daily distance swum (km)')

reg = linregress(dist[:,0],dist[:,1])

r = str(np.round(reg.rvalue,decimals=3))
p = str(reg.pvalue)

slope = reg.slope
inter = reg.intercept
xmin,xmax = np.amin(dist[:,0]),np.amax(dist[:,0])
ymin = xmin*slope+inter
ymax = xmax*slope+inter


plt.plot([xmin,xmax],[ymin,ymax],color='gray')
N = str(dist[:,0].shape[0])
plt.text(2.5,160,'N = '+N+'\nR = '+r+'\np < 1e-4',bbox=dict(color='lightgrey'),fontsize=12)

plt.ylim([0,190])


np.savetxt('test.dat',dist)

fname = diagdir+'/'+config+'/whale_dist.tiff'
savefig(fname)


















