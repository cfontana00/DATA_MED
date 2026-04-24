#!/bin/ksh

rm monitor.log

while [ 1 -eq 1 ];do

   echo `date` >> monitor.log
   echo `df -h` >> monitor.log
   echo `free -h` >> monitor.log
   echo ' ' >> monitor.log

   sleep 5 
done
