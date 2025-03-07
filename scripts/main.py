"""
main.py

Please find documentation about TenWise Knowledge Map API here:
https://apimlqv2.tenwiseservice.nl/
"""

# IMPORTS
import json
import functions as F

# Load configuration file
with open('config.json', 'r', encoding="utf-8") as stream:
    config = json.load(stream)

# Connect to API
creds = F.get_credentials(config['path_to_credentials'])

# Start session
session, payload = F.start_session(creds)

# TODO: Get full text from keywords 'pesticides' and 'Parkinsons disease'
# How to retrieve concept_ids? (Parkinsons Disease (TWDIS_06685))
# Get all Parkinsons Disease concept_ids
payload['terms'] = "Parkinson"
payload['wildcard'] = 'true'

results = session.post(
    creds["ADDRESS"] + "concept/search/",
    payload
)

js = results.json()
hits = list(js['result']['hits'].keys())
# NOTE: Disease concepts start with "TWDIS", therefore hits are filtered on "TWDIS": https://apimlqv2.tenwiseservice.nl/html/all_help.html#vocabularies
park_hits = [h for h in hits if h[:5] == 'TWDIS']

# TODO: Get all pesticides concept_ids

# NOTE: "Parkinsons Disease" id is not queried the same way CXCR3 is queried.. 
# list_keywords = ["Parkinsons", "CXCR3"]
# list_keywords = ["Cholesterol", "CXCR3"]
# payload['terms'] = ",".join(list_keywords)

# payload['terms'] = "CXCR3"


# payload['terms'] = "CXCR"
payload['wildcard'] = 'true'

results = session.post(
    creds["ADDRESS"] + "concept/search/",
    payload
)

js = results.json()
hits = list(js['result']['hits'].keys())





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
