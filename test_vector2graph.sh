#!/bin/bash

#SBATCH --job-name jennefer_networkx
#SBATCH --account kcbbe
#SBATCH --output test_vector2graph.log
#SBATCH --chdir /homes/jbeenen/git-repo/master_graduation_project

#SBATCH --partition assemblix
#SBATCH --nodelist=assemblix2025
#SBATCH --time 15:00
#SBATCH --cpus-per-task 90
#SBATCH --mem=30G
#SBATCH --ntasks 1
#SBATCH --gres shard:32

log_file="logs/SLURM_test_vector2graph.log"

date &> $log_file
srun ~/venv/graduation/bin/python scripts/vector2graph.py &>> $log_file

# End
date &>> $log_file
echo "Experiment is finished."