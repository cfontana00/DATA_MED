#!/bin/ksh

dnow=`date -d "today" +%Y-%m-%d`

echo `date`

for i in {0..5}; do
   dini=`date -d "today -$i days" +%Y-%m-%d`
   ./cpu2.slurm $dini > /home/cfontana/log/log_${dnow}_$dini 2>&1 
done

echo `date`
