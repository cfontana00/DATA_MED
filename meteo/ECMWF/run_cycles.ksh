#!/bin/ksh

# ------------------------------ #
# Routine to process meteo data  #
#   by looping through cycles    # 
# ------------------------------ #

# Read config as paramater
config=$1


# Load needed parameters
line=`cat ../../config/config_$config.json | grep meteo_ini \
	| sed s_'"'__g | sed s/':'/'='/ | sed s/,//`
eval $line

line=`cat ../../config/config_$config.json | grep n_cycle \
	| sed s_'"'__g | sed s/':'/'='/ | sed s/,//`
eval $line


line=`cat ../../config/config_$config.json | grep day_cycle \
	| sed s_'"'__g | sed s/':'/'='/ | sed s/,//`
eval $line

echo 'Initial date' $meteo_ini
echo 'Number of cycle' $n_cycle
echo 'Number of days per' $day_cycle
echo ''


# Loop on cycles
# --------------
let n_cycle=$n_cycle-1

for cycle in {0..$n_cycle};do

   # Define process parameters
   # -------------------------
   let end=$cycle*$day_cycle
   date_start=`date -d "$meteo_ini + $end days" +%Y-%m-%d`

   let end=$end+$day_cycle-1
   date_end=`date -d "$meteo_ini + $end days" +%Y-%m-%d`

   echo ""
   echo "###############################################"
   echo "# RUNNING CYCLE FROM $date_start to $date_end #"
   echo "###############################################"
   echo ""

   python3 process_data.py $config $date_start $date_end

done






