#!/bin/ksh

#SBATCH --nodes=1                    # 1 node
#SBATCH --ntasks-per-node=1         # 32 tasks per node
#SBATCH --time=3:00:00               # time limit: 1 hour
#SBATCH --error=myJob.err            # standard error file
#SBATCH --output=myJob.out           # standard output file
#SBATCH --account=PNRR_MER  # project account
#SBATCH --mem=8G      # ou plus selon la taille des données


export COLUMNS=120
export LINES=40


#dini=$1
#domain=$2
#get_radar=$3

dini='2026-02-08'
dout=`echo $dini | sed s/-//g`
dend=`date -d "$dini +5 days" +"%Y-%m-%d"`

run_cmems_thetao=0
run_cmems_chl=0
run_argo=1
run_radar=0
run_static=1

# Get radar data for all domains

switch_radar=0

# Loop on domain
# --------------
#for domain in LIG ION GOT NAD SAD SAR TYR ;do
for domain in LIG ;do

   echo "PROCESSING "$domain
   echo "_______________ "

   
   config=${domain}_$dini

   lower=`echo "$domain" | awk '{print tolower($0)}'`

   # Run hourly diags
   # ----------------

   # Create config files
   set -x

   cat config/config_$domain.json | sed -e s/DINI/$dini/g |\
	                                  sed -e s/DOUT/$dout/  |\
	                                  sed -e s/DEND/$dend/  |\
				          sed -e s/FREQ/hourly/  \
	> config/config_$config.json


   cp config/cmems_DOMAIN.dat config/cmems_$config.dat
   cp config/variables_mit_DOMAIN.dat config/variables_mit_$config.dat

   if [ $run_radar -eq 1 -a $switch_radar -eq 0 ];then
     python datasets/HFRADAR/get_data.py -c $config
     switch_radar=1
   fi 

   if [ $run_cmems_thetao -eq 1 ];then

     # Run diags
     cd datasets/CMEMS
     python get_data_sat.py -c $config -v thetao
     python interp_cmems.py -c $config -v thetao
     cd ../../plot
     python plot_2D_data_vs_sat.py -c $config -v thetao -s CMEMS
     python plot_sat_timeseries.py -c $config -v thetao -s CMEMS

     cd ..
   fi

   if [ $run_radar -eq 1 ];then  
     # Run radars diags
     cd datasets/HFRADAR
     python read_radar.py -c $config

     cd ../..
   fi

   # Run daily diags
   # ---------------

   cat config/config_$domain.json | sed -e s/DINI/$dini/g |\
	                                  sed -e s/DOUT/$dout/  |\
	                                  sed -e s/DEND/$dend/  |\
				          sed -e s/FREQ/daily/  \
	> config/config_$config.json

   if [ $run_cmems_chl -eq 1 ];then

     # Run Chl CMEMS
     cd datasets/CMEMS

     python get_data_sat.py -c $config -v chl
     python interp_cmems.py -c $config -v chl
     cd ../../plot

     python plot_2D_data_vs_sat.py -c $config -v chl -s CMEMS
     python plot_sat_timeseries.py -c $config -v chl -s CMEMS

     cd ..
   fi




   if [ $run_argo -eq 1 ];then
     # Run Argo diags
     source ~/venv/a/bin/activate > /dev/null

     # Physical
     sed -i 's/daily/hourly/' config/config_$config.json

     cd datasets/ARGO

     srun --unbuffered --pty python get_argo.py -c $config

     if [ $? -eq 0 ];then
       echo "ARGO FOUND"
       python compare_argo.py -c $config
     fi


     cd ../../

     # Biogeochemical
     sed -i 's/phy/bgc/' config/config_$config.json

     cd datasets/ARGO

     python get_argo.py -c $config

     if [ $? -eq 0 ];then
       echo "BIOARGO FOUND"
       python compare_argo.py -c $config
     fi


     cd ../../
   fi


   # PREPARE STATIC FILES
   # --------------------

   if [ $run_static -eq 1 ];then
     source ~/venv/c3/bin/activate > /dev/null
     diagdir='/leonardo_scratch/large/userexternal/cfontan1/DIAGS/'$config
     static=$diagdir/static_$config
     mkdir $static
 
     # Copy files

     # CMEMS
     for var in thetao chl;do 

       dir=$diagdir'/CMEMS/'$var'/ITP_NC'
       i=1
       for file in `ls $dir'/PLOT/'`;do
         cp $dir'/PLOT/'$file $static/${var}_$i.jpg
         let i=$i+1	
       done

      cp $dir/'time_series.jpg' $static/"time_series_$var.jpg"
      python plot/resize.py $static/"time_series_$var.jpg" 0.3

     done


     # RADAR

     dir=$diagdir'/RADAR/'
     i=1
     for file in `ls $dir/*.jpg`;do
       cp $file $static/radar_$i.jpg
       let i=$i+1
     done


     # ARGO 
     dir=$diagdir/ARGO/
  
      
     for file in `ls -d $dir/bio*/`;do
       file=`basename $file`
       num=`echo $file | sed s/bio//`
       mv $dir/bio$num/* $dir/$num
     done


     i=1
     for adir in `ls -d $dir/*/`;do
       for file in `ls $adir/profile*`;do	   

         cp $file $static/argo_$i.jpg
         python plot/resize.py $static/argo_$i.jpg 0.2

         echo "argo_$i.jpg"
         let i=$i+1
       done
     done > $static/list.txt$

     cp $dir/map.jpg $static
     python plot/resize.py $static/map.jpg 0.35
	   
     # Cleaning
     #rm config/config_$config.json
     #rm config/cmems_$config.dat
     #rm config/variables_mit_$config.dat

     # Send data to server
     scp -r $static yulpa175555@webhost03.yulpa.io:/datas/yulpa175555/sites/merval.eg2.fr/htdocs/DIAGS

   fi

done






