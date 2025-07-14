#!/bin/bash

#SBATCH --job-name jennefer_sbert
#SBATCH --account kcbbe
#SBATCH --output test_corpus2vector.log
#SBATCH --chdir /homes/jbeenen/git-repo/master_graduation_project

#SBATCH --partition assemblix
#SBATCH --nodelist=assemblix2025
#SBATCH --time 15:00
#SBATCH --cpus-per-task 90
#SBATCH --mem=30G
#SBATCH --ntasks 1
#SBATCH --gres shard:32

log_file="logs/SLURM_test_corpus2vector.log"

date &> $log_file
srun ~/venv/graduation/bin/python scripts/corpus2vector.py -i df_xml2corpus_by_sentence_pmid_free_3600_250606.csv -m sbert &>> $log_file

# End
date &>> $log_file
echo "Experiment is finished."
