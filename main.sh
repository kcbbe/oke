#!/usr/bin/bash

# Please find documentation about TenWise Knowledge Map API, which is used in this script, here:
# https://apimlqv2.tenwiseservice.nl/

# Get full text from keywords
# - Method 1: Select PMIDs from the TenWise PubMed 'MEDLINE abstracts' database by free search (not limited to concepts in the TenWise'Vocabulary' database).
# - Method 2: Retrieve concept_ids of keywords from TenWise 'Vocabulary' database 
# and then select PMIDs from the TenWise PubMed 'MEDLINE abstracts' database.
# - Query TenWise PubMed database for full text of selected PMIDs.
# 1) vanuit keywords in `search_free`, of 2) vanuit concept_ids `search_concepts` uit de 'Vocabularies',
# - Get PDF URLs from OpenAlex API (https://docs.openalex.org/)

# ??Reference to OpenAlex??


# Settings
log_file="test_250705_1"
config_file="config.yaml"

# Make `logs/` directory (if it does not already exists)
mkdir -p logs/

# TODO: start by appending log with datetime

# Get concept_ids from TenWise database
# ~/venv/graduation/bin/python scripts/term2concept.py -c $config_file &>> logs/$log_file.log

# Get PMIDs from querying TenWise database (find the search settings in the configuration file)
~/venv/graduation/bin/python scripts/concept2pmid.py -c $config_file &> logs/$log_file.log

# Get PDFs by searching pdf_urls in OpenAlex on PMIDs
~/venv/graduation/bin/python scripts/pmid2pdf.py -c $config_file &>> logs/$log_file.log

# Get XMLs from PDFs using GROBID
~/venv/graduation/bin/python scripts/pdf2xml.py -c $config_file &>> logs/$log_file.log



# # Run Snakemake application
# snakemake -s main.smk --cores 3 &> logs/snakemake_run.log
