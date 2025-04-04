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
*Safe point*



??Reference to OpenAlex??

"""

# IMPORTS
import yaml
import functions as F
import sys

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
# TODO: This option is not modifiable yet via config.yaml (atm hardcoded in function)
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

# NOTE: capped for now! (This will return 3 pdf_urls)
pmid_hits = pmid_hits[:12]


# Get PDF URLs from OpenAlex API (https://docs.openalex.org/)
pdf_urls, landing_urls = F.get_pdf_urls_from_pmids(pmid_hits, config["email_address"])
# TODO: further data exploration of the papers???????????? ??????????? ?

# Try to have the following processes multiprocessed.
# TODO: Add a 'safepoint': pickle all input_json, `filename` = `pmid`
# (is there a better way? I don't think a mysql is necessary since its just contains two columns (pmid, content)
# (So that the documents remain accessible if it is ever removed from online)

# TODO: Check if GROBID is running
# if http://assemblix:8670/api/isalive == 'true':
# else:
# try: to start up GROBID via bash/sys`docker run --rm --init --ulimit core=0 -p 8670:8070 lfoppiano/grobid:0.8.1`
# except: error, sys.exit()

# TODO: Get GROBID in action
response = F.get_tei_from_pdf_urls(
    pdf_urls,
    servername = config["grobid_servername"],
    portnumber = config["grobid_portnumber"]
)

# How to parse TEI:
# For next https://github.com/TenWise-Dev/jrc-public/blob/main/lib/Tei2MaterialsMethods.py


### 

###
# pmid to pmcid
# https://pmc.ncbi.nlm.nih.gov/tools/id-converter-api/ (max. 200 per request)

# Via OpenAlex
# https://github.com/J535D165/pyalex

api_openalex = "https://api.openalex.org/"