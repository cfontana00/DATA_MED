##################################
# Routine plotting profile plots #
##################################

from fun_gen import *
from fun_io import *
import numpy as np
import matplotlib.pyplot as plt


# -------------
# Plot profiles
# -------------
def plot_profiles(*arg):

  from fun_gen import fig_prox,\
                      fig_proy,\
                      col_phy,col_bcg,\
                      argo_ds
  
  if argo_ds == 'bgc':
    colors = col_bcg
  else: 
    colors = col_phy


  # Get number of profiles
  nprof = int((len(arg)-3)/3)
  fout = arg[0]
  time = arg[1]
  depth = arg[2]

  fig = plt.figure(figsize=(float(fig_prox), float(fig_proy)))

  # Create axes
  axes = []
  ax1 = fig.add_subplot(111)
  ax1.set_ylabel('Depth (m)')
  axes.append(ax1)

  for i in range(1,nprof):
    axes.append(ax1.twiny())

  # Plot
  for i in range(0,nprof):
    ax = axes[i]

    offset = 3+i*3
    model,data,label = arg[offset],arg[offset+1],arg[offset+2]

    ax.plot(model,depth,c=colors[i],label=label)
    ax.plot(data,depth,c=colors[i],marker='.',linestyle='None',alpha=0.5)

    ax.set_xlabel(label)
    ax.xaxis.label.set_color(colors[i])
    ax.tick_params(axis='x',colors=colors[i], which='both')

    if i == 0:
      ax.spines["bottom"].set_color(colors[i])
      ax.patch.set_alpha(0.0)

    if i > 0:
      ax.spines["top"].set_color(colors[i])

    if i > 1:
      ax.spines["top"].set_position(("axes", 1.0+i*0.04))
     
  plt.title(time)  

  # Save figure
  savefig(fout)
  print('')

  plt.close()


  




