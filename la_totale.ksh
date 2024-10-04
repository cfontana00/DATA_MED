###############
# LA TOTALE ! #
###############

#!/bin/ksh

set -x

# Get config name
config=$1


# Get CMEMS data
cd datasets/CMEMS

for var in 'thetao' 'chl';do
  python3 get_data_sat.py -c $config -v $var 
  python3 interp_cmems.py -c $config -v $var
done


# Do plots
cd ../../plot

for var in 'thetao' 'chl';do
  python3 time_series_data_vs_sat.py -c $config -v $var -s CMEMS
  python3 plot_2D_data_vs_sat.py -c $config -v $var -s CMEMS
  python3 plot_sat_timeseries.py -c $config -v $var -s CMEMS
done


#for var in 'chl' 'zooc' 'no3';do
#  python3 make_plot_2D.py -c $config -v $var
#done


# Do Argo
cd ../datasets/ARGO

python3 get_argo.py -c $config
python3 compare_argo.py -c $config


# Do Boussole
cd ../BOUSSOLE
python3 read_boussole.py -c $config


# Do Okubo
#cd ../../tools/okubo/
#source ~/venvs/ow2/bin/activate

#python3 compute_okubo.py -c $config






