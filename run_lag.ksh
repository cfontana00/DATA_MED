#!/bin/ksh

dini=`date -d "-8 days" +"%Y-%m-%d"`


./op.slurm $dini
