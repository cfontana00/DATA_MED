#!/bin/ksh

# Get config name
config=$1

# Get CMEMS data
cd datasets/CMEMS

for var in 'thetao' 'chl';do
  python get_data_sat.py -c $config -c $var -s CMEMS
  python interp_cmems.py -c $config -c $var -s CMEMS
done


# Do plots
cd ../../plot

for var in 'thetao' 'chl';do
  #python time_series_data_vs_sat.py -c $config -v $var -s CMEMS
  python plot_2D_data_vs_sat.py -c $config -v $var -s CMEMS
  python plot_sat_timeseries.py -c $config -v $var -s CMEMS
done


for var in 'chl' 'zooc' 'no3';do
  python make_plot_2D.py -c $config -v $var
done


# Do Argo
cd ../datasets/ARGO

python get_argo.py -c $config
python compare_argo.py -c $config


# Do Boussole
cd ../BOUSSOLE
python read_boussole.py -c $config


# Do Okubo
cd ../../tools/okubo/
source ~/venvs/ow2/bin/activate

python compute_okubo.py -c $config






