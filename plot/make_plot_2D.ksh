#!/bin/ksh -x

# Config name as first argument
config=$1

# Launch make_plot_2D.py
#varlist={'so','thetao'}
#levlist={'0','1'}

varlist={'chl','thetao','no3','zoo','po4'}
levlist='8'


for var in $varlist; do
  for lev in $levlist; do
    echo 'Processing var:'$var' lev:'$lev
    python3 make_plot_2D.py $config $var $lev
  done
done



