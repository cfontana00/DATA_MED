#!/bin/ksh

#SBATCH --nodes=1                    # 1 node
#SBATCH --ntasks-per-node=1         # 32 tasks per node
#SBATCH --time=1:00:00               # time limit: 1 hour
#SBATCH --error=myJob.err            # standard error file
#SBATCH --output=myJob.out           # standard output file
#SBATCH --account=PNRR_MER  # project account


# Date de début et de fin
start_date="2026-02-10"
end_date="2026-02-10"

current_date="$start_date"

while [ "$(date -d "$current_date" +%Y%m%d)" -le "$(date -d "$end_date" +%Y%m%d)" ]
do

 for domain in LIG ION GOT NAD SAD SAR TYR;do

    # Affichage au format YYYY_MM_DD
    date=`date -d "$current_date" +%Y-%m-%d`
    echo $date

    ./job.slurm $date $domain
 done

    # Passage au jour suivant
    current_date=$(date -d "$current_date +1 day" +%Y-%m-%d)
done
