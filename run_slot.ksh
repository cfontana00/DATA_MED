#!/bin/ksh

dnow=`date -d "today" +%Y-%m-%d`
#dnow=`date -d "today -1 days" +%Y-%m-%d`

# Loop on days
for i in {1..6}; do

   dini=`date -d "today -$i days" +%Y-%m-%d`

   # Launch processes on slots
   while [ 1 -eq 1 ];do

     # Count number of runningn process
     count=`ps -u cfontana | grep op.slurm | wc -l`

     if [ $count -lt 2 ];then
      ./op.slurm $dini > /home/cfontana/log/log_${dnow}_$dini 2>&1 &
      echo "Run "$dini" launched"
      break
     else
      sleep 5
     fi
   done

date
  
done

