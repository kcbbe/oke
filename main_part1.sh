#!/usr/bin/bash

# Please find documentation about TenWise Knowledge Map API, which is used in this script, here:
# https://apimlqv2.tenwiseservice.nl/

# Get a corpus by sentences from full text of PubMed papers.
# - Query TenWise PubMed database in search for relevant PMIDs.
# -- Method 1 (free): Select PMIDs from the TenWise PubMed 'MEDLINE abstracts' database by free search (not limited to concepts in the TenWise'Vocabulary' database).
# -- Method 2 (concept): Retrieve concept_ids of keywords from TenWise 'Vocabulary' database and then select PMIDs from the TenWise PubMed 'MEDLINE abstracts' database.
# - Get PDF URLs from OpenAlex API (https://docs.openalex.org/)

# ??Reference to OpenAlex??


# Settings
experiment_name="251013_pest_PD"
search_mode="free"  # "free" or "concept"
nr_pmids=1000


config_file="config.yaml"

log_file="logs/${experiment_name}.log"
full_exp_name="${search_mode}_${nr_pmids}_${experiment_name}"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~	

# Message that script is in progress
echo "Busy with experiment: $full_exp_name"
echo "See log file for progress: $log_file"

# Make `logs/` directory (if it does not already exists)
mkdir -p logs/

# Get PMIDs from querying TenWise database (find the search settings in the configuration file)
date &> $log_file
~/venv/graduation_3_13_5/bin/python scripts/concept2pmid.py -c $config_file -n $nr_pmids -m $search_mode -o "pmid_$full_exp_name.csv" &>> $log_file

# # Get metadata by searching PMIDs in OpenAlex
date &>> $log_file
~/venv/graduation_3_13_5/bin/python scripts/pmid2meta.py -c $config_file -i "pmid_$full_exp_name.csv" -m "efficient" &>> $log_file

# # Get PDFs by searching pdf_urls from metadata
date &>> $log_file
~/venv/graduation_3_13_5/bin/python scripts/meta2pdf.py -i "pmid_$full_exp_name.csv" -m "full" &>> $log_file

# # Get XMLs from PDFs using GROBID
date &>> $log_file
~/venv/graduation_3_13_5/bin/python scripts/pdf2xml.py -c $config_file -i "pmid_$full_exp_name.csv" &>> $log_file

# # Get corpus dataframe from XMLs
date &>> $log_file
~/venv/graduation_3_13_5/bin/python scripts/xml2corpus_by_sentence.py -i "pmid_$full_exp_name.csv" &>> $log_file

# # Get corpus vectors from corpus dataframe
# NOTE: This part runs on assemblix25
# see 'corpus2vector.sh'


# End
date &>> $log_file
echo "Experiment $full_exp_name has finished."
echo "NOTE: Run 'sbatch main_part2.sh' to get the vector embeddings, similarity scores, and a networkx graph."
