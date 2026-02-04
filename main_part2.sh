#!/bin/bash

#SBATCH --job-name your_name_sbert
#SBATCH --account kcbbe
#SBATCH --chdir /homes/your_name/git-repo/

#SBATCH --output logs/SLURM_main_part2.log
#SBATCH --partition assemblix
#SBATCH --nodelist=assemblix2025
#SBATCH --time 5:00
#SBATCH --cpus-per-task 90
#SBATCH --mem=50G
#SBATCH --ntasks 1
#SBATCH --gres shard:32


# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# SETTINGS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
experiment_name="251013_pest_PD"
search_mode="free"  # "free" or "concept"
nr_pmids=1000

venv_path=~/venv/graduation_3_13_5
config_file="config.yaml"

sbert_model="NeuML/pubmedbert-base-embeddings"  # For other models, see https://huggingface.co/models?library=sentence-transformers&sort=trending&search=pubmed

# ~~~~~~~~~~~~~~~~~~~~~~~~~~	

log_file="logs/${experiment_name}_corpus_by_sentence2vector_a25.log"
full_exp_name="${search_mode}_${nr_pmids}_${experiment_name}"

# Message that script is in progress
echo "Busy with experiment: $full_exp_name"
echo "See log file for progress: $log_file"

source "$venv_path/bin/activate"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# PIPES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~		

# Get sentence embedding matrix and cosine similarity score matrix from corpus
date &> $log_file
srun python scripts/corpus_by_sentence2vector.py -c $config_file -i "corpus_$full_exp_name.csv" -m $sbert_model &>> $log_file

# Get a networkx graph from cosine similarity score matrix
date &>> $log_file
srun python scripts/similarity2graph.py -i "similarity_$full_exp_name.pickle" -t 0.75 -d 1.0 &>> $log_file

# ~~~~~~~~~~~~~~~~~~~~~~~~~~

# End
date &>> $log_file
echo "Experiment is finished."
