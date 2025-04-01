"""
main.py

Please find documentation about TenWise Knowledge Map API, which is used in this script, here:
https://apimlqv2.tenwiseservice.nl/

Get full text from keywords
- Method 1: Select PMIDs from the TenWise PubMed 'MEDLINE abstracts' database by free search (not limited to concepts in the TenWise'Vocabulary' database).
- Method 2: Retrieve concept_ids of keywords from TenWise 'Vocabulary' database 
and then select PMIDs from the TenWise PubMed 'MEDLINE abstracts' database.
- Query TenWise PubMed database for full text of selected PMIDs.
1) vanuit keywords in `search_free`, of 2) vanuit concept_ids `search_concepts` uit de 'Vocabularies',
- Get PDF URLs from OpenAlex API (https://docs.openalex.org/)

??Reference to OpenAlex??

"""

# IMPORTS
# import json
import yaml
import functions as F
import sys
# import pandas as pd

# # Load configuration file
# with open('config.json', 'r', encoding="utf-8") as stream:
#     config = json.load(stream)

# Load configuration file
with open('config.yaml', 'r', encoding="utf-8") as stream:
    config = yaml.safe_load(stream)

# Connect to API
creds = F.get_credentials(config['path_to_credentials'])

# Start session #TODO: Create a class for the session?
session, payload = F.start_tenwise_session(creds)

# SEARCH
# Option 1) Get pmid ids on keywords "pesticides" and "Parkinson's disease"
if config["search_mode"].lower().strip() == "free":
    pmid_hits = F.search_free(
        session,
        payload,
        creds,
        config["free_search_terms"]
    )

# Option 2) Get pmid ids on concept_ids from TenWise vocabularies
# TODO: This option is not modifiable yet via config.yaml (hardcoded in function)
if config["search_mode"].lower().strip() == "concepts":
    pmid_hits = F.search_concepts(
        session,
        payload,
        creds,
        path_to_pesticide_ids = config["path_to_pesticide_ids"]
    )
else:
    print("Error in search_mode. Please change in 'config.yaml' variable 'search_mode' to either 'free' or 'concepts'.")
    sys.exit()

# Get PDF URLs from OpenAlex API (https://docs.openalex.org/)
pdf_urls, landing_urls = F.get_pdf_urls_from_pmids(pmid_hits, config["email_address"])
# TODO: further data exploration of the papers???????????? ??????????? ?

# TODO: Start up GROBID

### 

###
# pmid to pmcid
# https://pmc.ncbi.nlm.nih.gov/tools/id-converter-api/ (max. 200 per request)

# Via OpenAlex
# https://github.com/J535D165/pyalex

api_openalex = "https://api.openalex.org/"