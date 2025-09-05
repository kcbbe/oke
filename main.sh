#!/usr/bin/bash

# Please find documentation about TenWise Knowledge Map API, which is used in this script, here:
# https://apimlqv2.tenwiseservice.nl/

# Get full text from keywords
# - Query TenWise PubMed database for full text of selected PMIDs.
# -- Method 1: Select PMIDs from the TenWise PubMed 'MEDLINE abstracts' database by free search (not limited to concepts in the TenWise'Vocabulary' database).
# -- Method 2: Retrieve concept_ids of keywords from TenWise 'Vocabulary' database 
# and then select PMIDs from the TenWise PubMed 'MEDLINE abstracts' database.
# - Get PDF URLs from OpenAlex API (https://docs.openalex.org/)

# ??Reference to OpenAlex??


# Settings
experiment_name="250606"
search_mode="free"  # "free" or "concept"
nr_pmids=3600

# # Settings
# experiment_name="250425_testing_grobid_lite"
# search_mode="concept"  # "free" or "concept"


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
~/venv/graduation/bin/python scripts/concept2pmid.py -c $config_file -n $nr_pmids -m $search_mode -o "pmid_$full_exp_name.csv" &>> $log_file

# # Get PDFs by searching pdf_urls in OpenAlex on PMIDs
date &>> $log_file
~/venv/graduation/bin/python scripts/pmid2pdf.py -c $config_file -i "pmid_$full_exp_name.csv" -o "$full_exp_name.csv" &>> $log_file

# # Get XMLs from PDFs using GROBID
date &>> $log_file
~/venv/graduation/bin/python scripts/pdf2xml.py -c $config_file -i "pmid_$full_exp_name.csv" &>> $log_file

# # Get corpus dataframe from XMLs
date &>> $log_file
~/venv/graduation/bin/python scripts/xml2corpus_by_sentence.py -i "pmid_$full_exp_name.csv" &>> $log_file

# # Get corpus vectors from corpus dataframe
# NOTE: This part runs on assemblix25
# see 'corpus2vector.sh'


# End
date &>> $log_file
echo "Experiment $full_exp_name finished."
echo "NOTE: Run 'corpus2vectors.sh' to get the embedding and similarity scores."
