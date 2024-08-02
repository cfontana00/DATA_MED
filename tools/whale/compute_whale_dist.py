# -------------------------------- #
# Compare whale parameters to eddy #
# -------------------------------- #
import warnings
warnings.simplefilter("ignore")

from matplotlib import pyplot as plt
from fun_gen import load_config
from fun_io import savefig,get_filename,get_model_val_3d
from fun_whales import get_whale_pos
import argparse
import datetime as dt
import haversine as hs
from scipy.stats import linregress
from astral import moon
import cmcrameri as cmc
from sklearn.cluster import KMeans





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

# Load coordinates
# ----------------
lon_mod,lat_mod,lev_mod = load_coords()


# Load eddy file
eddy = np.loadtxt(trans_file).squeeze()

# Load whale tracks
tjd,tlon,tlat = get_whale_pos('87780')

# Get variable parameters
vname, ftag, cmap, islog, vmod, vmin, vmax, label, units\
        = load_variable(config,'zooc')



# Loop on days
# ------------
pos = []
dist = []
mday = []
lday = []

for jd in range(jdini,jdend+1):

   d = dt.datetime.fromordinal(jd)
   fname,dtag = get_filename(jd,ftag)


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

     #if moon.phase(d) < 27:
     dist.append([np.log(edist),wdist])
     pos.append([wlon2,wlat2])
     lday.append(jd)
      
     # Get moon day
     mday.append(moon.phase(d))


   except Exception as e:
     print(e)
     pass

dist = np.array(dist)
pos = np.array(pos)

# Compute Kmeans
kmeans = KMeans(n_clusters=2)

data = np.zeros([dist.shape[0],2])
data[:,0] = dist[:,0]/np.max(dist[:,0])
data[:,1] = dist[:,1]/np.max(dist[:,1])

kmeans.fit(data)
label = kmeans.predict(data)





# Make plot
# ---------
color='k' 
s=80
marker='s'


fig,ax = plt.subplots(1,1,figsize=(6,6))

np.savetxt(diagdir+'/ALBEDO/all.dat',dist)


for l in [0,1]:
   idx = np.where(label==l)
   x = dist[idx,0].squeeze()
   y = dist[idx,1].squeeze()

   plt.scatter(x,y,marker=marker,s=s,
               facecolor='none',edgecolor='k',label='Cluster '+str(l))
   marker='o'
 

   np.savetxt(diagdir+'/ALBEDO/cluster'+str(l)+'.dat',np.dstack((x,y)).squeeze())







plt.legend()

"""
# Plot new moon days
for i in range(0,dist[:,0].shape[0]):

    
    # Get zooplankton value
    try:
   
      fname,dtag = get_filename(lday[i],ftag)

      if mday[i] > 27:
        pos[i,0] = pos[i,0]+0.05

      color =  get_model_val_3d(fname,0,'zooc',\
               lon_mod,lat_mod,lev_mod,\
                 pos[i,0],pos[i,1],np.array([15.0]))

      color /= 12
      #print(pos[i,0],dtag,color,mday[i])

    except Exception as e:
      #print(e)
      color = 'grey'
      pass

    #cmap=cmc.cm.broc

    color='k' 
    s=80
    marker='s'
    if label[i] == 0:
      marker = 'o'

    #plt.text(dist[i,0],dist[i,1],str(np.round(mday[i],decimals=2)))

    plt.scatter(dist[i,0],dist[i,1],marker=marker,s=s,
               facecolor='none',edgecolor='k')

    plt.scatter(dist[i,0],dist[i,1],marker=marker,s=s,c=color,
            #vmin=.8737614,vmax=2.05833689,cmap=cmap,zorder=2)
            vmin=1.4737614,vmax=2.05833689,cmap=cmap,
               facecolor='none',edgecolor='k')

    if mday[i] < 7: 
       ax.scatter(dist[i,0],dist[i,1],marker='o',s=s,
               edgecolor='k',facecolor='none',zorder=2)
    else:
       ax.scatter(dist[i,0],dist[i,1],marker='o',s=s,
               edgecolor='r',facecolor='none',zorder=2)

    if color == 'grey':
       ax.scatter(dist[i,0],dist[i,1],marker='x',s=50,color='w',zorder=2)
"""

plt.plot([4,4],[0,250],'k:',color='grey',linewidth=0.8)
plt.plot([0,10],[50,50],'k:',color='grey',linewidth=0.8)
plt.text(2.1,40,'First quarter',fontsize=12)

#plt.colorbar() 
plt.xlabel('Logarithm of the daily distance to the eddy')
plt.ylabel('Daily distance swum (km)')

reg = linregress(dist[:,0],dist[:,1])

r = f'{reg.rvalue:.2f}'
p = str(reg.pvalue)
print('p=',p)

slope = reg.slope
inter = reg.intercept
xmin,xmax = np.amin(dist[:,0]),np.amax(dist[:,0])
ymin = xmin*slope+inter
ymax = xmax*slope+inter

plt.plot([xmin,xmax],[ymin,ymax],color='gray',zorder=0)
N = str(dist[:,0].shape[0])
#plt.text(2.2,180,'N = '+N+'\nR = '+r+'\np < 1e-6',bbox=dict(color='lightgrey'),fontsize=12)

plt.ylim([0,210])
plt.xlim([2,7])


fname = diagdir+'/'+config+'/whale_dist.tiff'
savefig(fname)


















