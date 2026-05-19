#!/bin/ksh

dnow=`date -d "today" +%Y-%m-%d`
#dnow=`date -d "today -1 days" +%Y-%m-%d`

switch=0


# RUN FULL VALIDATION
# -------------------

# Loop on days
#for i in {3..6}; do
for i in 0 7; do

   dini=`date -d "today -$i days" +%Y-%m-%d`

   # Launch processes on slots
   while [ 1 -eq 1 ];do

     # Count number of runningn process
     count=`ps -u cfontana | grep op.slurm | wc -l`

     if [ $count -lt 2 ];then

      ./op.slurm $dini > /home/cfontana/log/log_${dnow}_$dini 2>&1 &
      echo "Run "$dini" launched"
   
      # Introduce a lag to shift runs
      if [ $switch -eq 0 ];then
        sleep 1200
        switch=1
      fi

      break


     else
      sleep 5
     fi
   done

date


done


# RUN ARGO VALIDATION
# -------------------
  
for i in {1..6}; do

  dini=`date -d "today -$i days" +%Y-%m-%d`

  # Count number of runningn process
  count=`ps -u cfontana | grep argo.slurm | wc -l`

  if [ $count -lt 2 ];then

    ./argo.slurm $dini > /home/cfontana/log/argo_${dnow}_$dini 2>&1 &
    echo "Run "$dini" launched"

  fi

done
