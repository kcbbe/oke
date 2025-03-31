"""
main.py

Please find documentation about TenWise Knowledge Map API, which is used in this script, here:
https://apimlqv2.tenwiseservice.nl/

Get full text from keywords
- Method 1: Select PMIDs from the TenWise PubMed 'MEDLINE abstracts' database by free search (not limited to concepts in the TenWise'Vocabulary' database).
- Method 2: Retrieve concept_ids of keywords from TenWise 'Vocabulary' database 
and then select PMIDs from the TenWise PubMed 'MEDLINE abstracts' database.
- Query TenWise PubMed database for full text of selected PMIDs.
1) vanuit keywords in `free_search`, of 2) vanuit concept_ids uit de 'Vocabularies',
- Get PDF URLs from OpenAlex API (https://docs.openalex.org/)

??Reference to OpenAlex??

"""

# IMPORTS
import json
import functions as F
import pandas as pd

# Load configuration file
with open('config.json', 'r', encoding="utf-8") as stream:
    config = json.load(stream)

# Connect to API
creds = F.get_credentials(config['path_to_credentials'])

# Start session #TODO: Create a class for the session?
session, payload = F.start_tenwise_session(creds)

### Get full text from keywords "pesticides" and "Parkinson's disease"
### PUBMED USING FREE SEARCH (TODO: 'define free_search')
payload['terms'] = "(pesticide OR pesticides) AND parkinson's"
results = session.post(
    creds["ADDRESS"] + "refset/free_search",
    payload
)

js = results.json()
hits_on_free_search = js['result']['pmids']

# js['result'] =
# >  parkinson"  , 'hitnr': 126, 'pmids': ['32943485', '...']
# >  parkinson's", 'hitnr': 866, 'pmids': ['37354828',
# NOTE: I expected 'parkinson' to have more hits, since it would include "parkinson's"?


### PUBMED USING KMAP
# Get all Parkinsons Disease concept_ids
payload['terms'] = "parkinson"
# payload['terms'] = "parkinson's" # NOTE: this returns an error: "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near \'s\')\' at line 1"
payload['wildcard'] = 'true'

results = session.post(
    creds["ADDRESS"] + "concept/search/",
    payload
)
payload['wildcard'] = 'false' # <- Turn off wildcard (cleaning after myself)

js = results.json()
hits = list(js['result']['hits'].keys())
# NOTE: Disease concepts start with "TWDIS", therefore hits are filtered on "TWDIS": https://apimlqv2.tenwiseservice.nl/html/all_help.html#vocabularies
park_hits = [h for h in hits if h[:5] == 'TWDIS'] # ['TWDIS_03314', 'TWDIS_03315', ...]


# Get all pesticide concept_ids
# Current format is tab-delimited: `TWPHI_XXXXX \t name_pesticide`
pest_hits = pd.read_csv(
    config["path_to_pesticide_ids"],
    header = None,
    sep = "\t"
    ).iloc[:,0].to_list()

# payload['concept_ids'] = 'TWDIS_17683'
payload['concept_ids'] = ",".join([*park_hits, *pest_hits])
results = session.post(
    creds["ADDRESS"] + "conceptset/evidence/",
    # creds["ADDRESS"] + "conceptset/hits/",
    payload
)
js = results.json()
hits_on_concept_ids = [str(d["pmid"]) for d in js['result']['evidence']]
# > ['3262231', ...] pmids



# Get PDF URLs from OpenAlex API (https://docs.openalex.org/)
pdf_urls, landing_urls = F.get_pdf_urls_from_pmids(hits_on_concept_ids, config["email_address"])
# TODO: further data exploration of the papers?

# TODO: Start up GROBID

### 

###
# pmid to pmcid
# https://pmc.ncbi.nlm.nih.gov/tools/id-converter-api/ (max. 200 per request)

# Via OpenAlex
# https://github.com/J535D165/pyalex

api_openalex = "https://api.openalex.org/"