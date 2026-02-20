#/bin/ksh

#SBATCH --begin 03:00                
#SBATCH --nodes=1                    # 1 node
#SBATCH --ntasks-per-node=1         # 32 tasks per node
#SBATCH --time=2:00:00               # time limit: 1 hour
#SBATCH --error=myJob.err            # standard error file
#SBATCH --output=myJob.out           # standard output file
#SBATCH --account=PNRR_MER  # project account



dini=`date -d "-12 days" +"%Y-%m-%d"`


sbatch op.slurm $dini
