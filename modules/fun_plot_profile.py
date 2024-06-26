##################################
# Routine plotting profile plots #
##################################

from fun_gen import *
from fun_io import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


# -------------
# Plot profiles
# -------------
def plot_profiles(*arg):

  from fun_gen import fig_prox,\
                      fig_proy,\
                      col_phy,col_bcg,\
                      argo_ds,\
                      fig_fmt
  
  if argo_ds == 'bgc':
    colors = col_bcg
  else: 
    colors = col_phy


  # Get number of profiles
  nprof = int((len(arg)-6)/3)
  savedir = arg[0]
  tag = arg[1]
  pnum = arg[2]
  pcyc = arg[3]
  time = arg[4]
  depth = arg[5]

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

    offset = 6+i*3
    model,data,label = arg[offset],arg[offset+1],arg[offset+2]

    # Plot curves
    ax.plot(model,depth,c=colors[i],zorder=2)
    ax.plot(data,depth,c=colors[i],marker='.',linestyle='None',alpha=1,zorder=2)

    # Plot for legend
    ax.plot(model,depth,c='k',label='Model',zorder=1)
    ax.plot(data,depth,c='k',marker='.',linestyle='None',alpha=1,label='Data',zorder=1)


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

  plt.legend() 
  plt.title(time)  
  plt.suptitle('Float '+str(pnum)+' - profile '+pcyc,y=1.05)  

  # Save figure
  fout = savedir+'/'+tag+str(pnum)+'/profile_'+pcyc+'.'+fig_fmt

  savefig(fout)
  print('')

  plt.close()


  

# Plot error profile with standard deviation
# ------------------------------------------
def plot_error_histo(savedir,dstep,mean,std,varname,units,color):

  from fun_gen import fig_prox,\
                      fig_proy,\
                      tck_size_prof,\
                      fig_fmt

  mean = np.array(mean).squeeze()
  std = np.array(std).squeeze()

  fig = plt.figure(figsize=(float(fig_prox), float(fig_proy)))
  ax = fig.add_subplot(111)

  y_val = []
  for n in range(0,dstep.shape[0]-1):
     y_val.append((dstep[n]+dstep[n+1])/2)

  y_val = np.array(y_val)

  ax.scatter(mean,y_val,marker='o',color=color,linestyle='None',s=10,alpha=0.8)
  ax.errorbar(mean,y_val, xerr=std,  capsize=4,linestyle='None' ,lolims=True, color=color,alpha=0.4)

  plt.title('Mean Absolute Error')
  ax.set_ylabel('Depth (m)')
  if varname == 'Salinity':
    ax.set_xlabel(varname)
  else:
    ax.set_xlabel(varname+' ('+units+')')

  #ax.set_xticklabels(ax.get_xticks(), fontsize=tck_size_prof)
  #ax.set_yticklabels(ax.get_yticks(), fontsize=tck_size_prof)
  ax.tick_params(axis='both', which='major', labelsize=tck_size_prof)

  ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: '{:,.2f}'.format(x)))

  xmin, xmax = ax.get_xlim()
  #plt.xlim(0,xmax)  
  plt.ylim(np.amin(dstep),np.amax(dstep))

  savefig(savedir+'/error_'+varname+'.'+fig_fmt)





