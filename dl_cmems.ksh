#!/bin/ksh
#dini=`date +%Y-%m-%d` !!!!!!!!!!!!!!!!!!
dini=`date -d "$dini -0 days" +"%Y-%m-%d"`
dout=`echo $dini | sed s/-//g`
dend=`date -d "$dini +5 days" +"%Y-%m-%d"`

echo "Download for "$dini 

. /home/cfontana/.cron_env

export PYTHONPATH=$PYTHONPATH:/home/cfontana/DATA_MED/modules/
export DATA_MED_DIR=/home/cfontana/DATA_MED/

source /home/cfontana/venv/c/bin/activate


# Loop on domains
for domain in LIG ION NAD SAD SAR TYR SIC ;do
   
   config=${domain}_$dini
   mkdir -p ~/DIAGS/$config
   mkdir -p ~/DIAGS/$config/CMEMS

   # Create config files
   cat config/config_$domain.json | sed -e s/DINI/$dini/g |\
                                        sed -e s/DOUT/$dout/  |\
                                        sed -e s/DEND/$dend/  |\
                                        sed -e s/FREQ/hourly/  \
      > config/config_$config.json

   cp config/cmems_DOMAIN.dat config/cmems_$config.dat
   cp config/variables_mit_DOMAIN.dat config/variables_mit_$config.dat


  # Loop on variables
  for var in thetao chl;do
    mkdir -p ~/DIAGS/$config/CMEMS/$var
    python datasets/CMEMS/get_model.py ${domain}_$dini $var
  done

done
   
