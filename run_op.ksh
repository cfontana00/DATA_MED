#!/bin/ksh

dini=`date -d "-1 days" +"%Y-%m-%d"`


./op.slurm $dini
