"""

"""
# IMPORTS
import sys
import argparse
from pathlib import Path
import yaml
import requests
import pandas as pd


# FUNCTIONS
# Get credentials
def get_credentials(path_to_text: str) -> dict:
    """
    Loads a file (path_to_text) with tab separated values and creates/returns a dictionary. 
    The first column will be the key, second column will be the value.
    """
    try:
        with open(path_to_text) as file:
            lines = file.readlines()
            list_credentials = [l.strip('\n').split('\t') for l in lines]
            dict_credentials = {l[0]: l[1] for l in list_credentials}
    except FileNotFoundError:
        print("ERROR: Entered file not found (maybe there's a typo?): ", path_to_text)
        sys.exit()
    print("Loaded credentials")
    return dict_credentials

# Start session and get a payload
def start_tenwise_session(login_credentials: dict):
    """
    Start a session with requests.Sessions() using the provided login_credentials, returns the session and a template payload.
    
    Args:
        login_credentials (dict): Must contain following keys: 'APIKEY', 'ADDRESS'.

    Returns:
        session (requests): API session. Provides cookie persistence, connection-pooling, and configuration.
        payload (dict): A payload template for building queries.
    """
    
    session = requests.Session()
    session.headers['referer'] = login_credentials["ADDRESS"].removesuffix("api/mlquery/") # NOTE: 'referer' is not a typo. Please ignore cSpell.
    session.get(login_credentials["ADDRESS"] + "start/")
    payload = {
        'apikey': login_credentials["APIKEY"],
        'csrfmiddlewaretoken': session.cookies.get_dict()['csrftoken']
    }

    return session, payload

# Search method 1: Search on PubMed concepts
def search_free(session, payload, credentials, free_terms):
    # TODO: docstring

    ### PUBMED USING FREE SEARCH (TODO: 'define free_search')
    payload['terms'] = free_terms
    results = session.post(
        credentials["ADDRESS"] + "refset/free_search",
        payload
    )

    js = results.json()
    hits_on_free_search = js['result']['pmids']

    # js['result'] =
    # >  parkinson"  , 'hitnr': 126, 'pmids': ['32943485', '...']
    # >  parkinson's", 'hitnr': 866, 'pmids': ['37354828',
    # NOTE: I expected 'parkinson' to have more hits, since it would include "parkinson's"?

    return hits_on_free_search

# Search method 2: Search on pre-defined alias of TenWise
def search_concepts(session, payload, credentials, path_to_pesticide_ids):
    # TODO: docstring
    
    ### PUBMED USING KMAP
    # Get all Parkinsons Disease concept_ids
    payload['terms'] = "parkinson"
    # payload['terms'] = "parkinson's" # NOTE: this returns an error: "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near \'s\')\' at line 1"
    payload['wildcard'] = 'true'

    results = session.post(
        credentials["ADDRESS"] + "concept/search/",
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
        path_to_pesticide_ids,
        header = None,
        sep = "\t"
        ).iloc[:,0].to_list()

    # payload['concept_ids'] = 'TWDIS_17683'
    payload['concept_ids'] = ",".join([*park_hits, *pest_hits])
    results = session.post(
        credentials["ADDRESS"] + "conceptset/evidence/",
        # creds["ADDRESS"] + "conceptset/hits/",
        payload
    )
    js = results.json()
    hits_on_concept_ids = [str(d["pmid"]) for d in js['result']['evidence']]
    # > ['3262231', ...] pmids

    return hits_on_concept_ids

# MAIN
if __name__ == "__main__":

    # Collect arguments
    parser = argparse.ArgumentParser(
        description = __doc__,
        # formatter_class = argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-c",
        dest = "config_file",
        required = True,
        help = "Provide path to the configuration file (default: 'config.yaml')",
        default = "config.yaml"
    )
    args = parser.parse_args()

    # Load configuration file
    with open(args.config_file, 'r', encoding="utf-8") as stream:
        config = yaml.safe_load(stream)

    # Get credentials
    creds = get_credentials(config['path_to_credentials'])

    # Start session
    session, payload = start_tenwise_session(creds)

    # SEARCH TODO: This part needs to change so that it is modulair.
    # Option 1) Get pmid ids on keywords "pesticides" and "Parkinson's disease"
    if config["search_mode"].lower().strip() == "free":
        pmid_hits = search_free(
            session,
            payload,
            creds,
            config["free_search_terms"]
        )

    # Option 2) Get pmid ids on concept_ids from TenWise vocabularies
    # TODO: This option is not modifiable yet via config.yaml (atm hardcoded in function)
    elif config["search_mode"].lower().strip() == "concepts":
        pmid_hits = search_concepts(
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

    try:
        with open(f"output/{config['output_pmids']}_{config['experiment_name']}.txt", "w") as output:
            output.write(',\n'.join(pmid_hits))
    except FileNotFoundError:
        Path("output").mkdir(exist_ok = True)
        with open(f"output/{config['output_pmids']}_{config['experiment_name']}.txt", "w") as output:
            output.write(',\n'.join(pmid_hits))
    print("End of concept2pmid.py")
