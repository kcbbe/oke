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
session, payload = F.start_session(creds)

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
# NOTE: Ready to retrieve full text?


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


# TODO: Get all pesticide concept_ids
# Current format is: `TWPHI_XXXXX \t name_pesticide`
pest_hits = pd.read_csv(
    config["path_to_pesticide_ids"],
    header = None,
    sep = "\t"
    ).iloc[:,0].to_list()

# TODO: Not sure if my conceptset/evidence/ output is correct.. (Think so!)
# payload['concept_ids'] = 'TWDIS_17683'
payload['concept_ids'] = ",".join([*park_hits, *pest_hits])
results = session.post(
    creds["ADDRESS"] + "conceptset/evidence/",
    # creds["ADDRESS"] + "conceptset/hits/",
    payload
)
js = results.json()
hits_on_concept_ids = [d["pmid"]for d in js['result']['evidence']]
# > ['3262231', ...] pmids


# TODO: Where can I extract the PMC ids?
# NOTE: Pesticides TW_ids: https://ironman.tenwisedev.nl/public/all_pesticide_concept_ids.txt
# NOTE: (Once pesticides are added) Ready to retrieve full text?

###

#############################################################################
####### Example (https://apimlqv2.tenwiseservice.nl/html/pythonexample.html)
### Get the relations for 2 concepts ###
# In this case we look at relations with
# CXCR3 (HGNC:4540) and Parkinsons Disease (TWDIS_06685)
# These are referred to as the subjects.

payload['concept_ids_subject'] = "HGNC:4540,TWDIS_06685"
results = session.post(
    creds["ADDRESS"] + "conceptset/relations/",
    payload
)

js = results.json()
relations = js['result']['relations']

### Get all ids and names for which a relation is found ###
# These are referred to as the "object"
# This is done by the annotation method

object_ids = {x['object']:1 for x in relations}
ids = ["HGNC:4540","TWDIS_06685"] + list(object_ids.keys())
payload['concept_ids'] = ",".join(ids)
results = session.post(creds["ADDRESS"] + "conceptset/annotation/",
                       payload)
js = results.json()
annotation = js['result']['annotation']

### Print out some details for each relation ###
print("\t".join(['Subject','Object','Score','Overlap']))

for relation in relations:
    if relation['score'] >100:
        if relation['overlap'] > 10:
            print("\t".join([
                annotation[relation['subject']]['name'][0],
                annotation[relation['object']]['name'][0],
                str(relation['score']),
                str(relation['overlap'])
              ]
            )
)
