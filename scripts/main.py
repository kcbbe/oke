"""
main.py
"""

# IMPORTS
import json
import support_module as S

# Load configuration file
with open('config.json', 'r', encoding="utf-8") as stream:
    config = json.load(stream)

# Connect to API
creds = S.get_credentials(config['path_to_credentials']) # NOTE: ATM just "path_to_credentials": "path/to/credentials"

# Start session
session, payload = S.start_session(creds)


# Example (https://apimlqv2.tenwiseservice.nl/html/pythonexample.html)
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
