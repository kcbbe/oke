#!/bin/bash

#SBATCH --job-name jennefer_sbert
#SBATCH --account kcbbe
#SBATCH --output logs/corpus2vector.log
#SBATCH --chdir /homes/jbeenen/git-repo/master_graduation_project

#SBATCH --partition assemblix
#SBATCH --nodelist=assemblix2025
#SBATCH --time 15:00
#SBATCH --cpus-per-task 90
#SBATCH --mem=50G
#SBATCH --ntasks 1
#SBATCH --gres shard:32

# Settings
experiment_name="250606"
search_mode="free"  # "free" or "concept"
nr_pmids=3600
embedding_model="sbert"  # "sbert" "sentence-transformers" "Universal Sentence Encoder" "sent2vec" or "sentence-transformers/all-MiniLM-L12-v2"

log_file="logs/${experiment_name}_corpus2vector_a25.log"
full_exp_name="${search_mode}_${nr_pmids}_${experiment_name}"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~	

# Message that script is in progress
echo "Busy with experiment: $full_exp_name"
echo "See log file for progress: $log_file"

# # Get sentence embedding matrix and cosine similarity score matrix from corpus
# date &> $log_file
# srun ~/venv/graduation/bin/python scripts/corpus2vector.py -i "corpus_$full_exp_name.csv" -m sbert &>> $log_file

# Get a networkx graph from cosine similarity score matrix
date &> $log_file
# date &>> $log_file
~/venv/graduation/bin/python scripts/cos_sim2graph.py -i "similarity_$full_exp_name.pickle" -t 0 &>> $log_file


# End
date &>> $log_file
echo "Experiment is finished."
