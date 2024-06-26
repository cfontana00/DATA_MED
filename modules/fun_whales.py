# -------------------------------- #
# Functions related to whales data #
# -------------------------------- #
import numpy as np
import datetime as dt


# Compute whale daily position
# ----------------------------
def get_whale_pos(tag):

  # Get whale position
  dtrack=np.loadtxt('/home/fontana/SONG/SICILIA/'+tag+'.dat')

  mon=dtrack[:,5].squeeze()
  day=dtrack[:,4].squeeze()
  year=dtrack[:,6].squeeze()

  mon=np.array(mon,dtype=int)
  day=np.array(day,dtype=int)
  year=np.array(year,dtype=int)

  # Compute julian day
  jd_w = []
  for i in range(0,year.shape[0]):
     d = dt.datetime(year[i],mon[i],day[i])
     jd_w.append(d.toordinal())

  # Compute mean position
  tlon = []
  tlat = []
  tjd = []

  for jd in np.unique(jd_w):

     idx = np.where( jd_w == jd)
     tlon.append(np.mean(dtrack[idx,1]))
     tlat.append(np.mean(dtrack[idx,0]))
     tjd.append(jd)


  tjd = np.array(tjd)
  tlon = np.array(tlon)
  tlat = np.array(tlat)

  return tjd,tlon,tlat





