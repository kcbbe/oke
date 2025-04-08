"""
concept2pmid.py

Find PMIDs based on given concepts.

Output:
    An output file is generated in

    Example:
    ```
    pmid,
    34429776,
    6905769,
    ...,
    ```
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
        session (requests.Session): API session. Provides cookie persistence, connection-pooling, and configuration.
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
def search_free(session: requests.Session, payload: dict, credentials: dict, free_terms: str, retmax: int):
    """
    Return PMIDs for from a free text search on the TenWise MEDLINE library.
    See link for more information: https://apimlqv2.tenwiseservice.nl/html/all_help.html#refset-free-search
    
    Args:
        session (requests.Session): API session. Provides cookie persistence, connection-pooling, and configuration. Created using `start_tenwise_session` function.
        payload (dict): A payload template for building queries. Created using `start_tenwise_session` function.
        credentials (dict): Must contain following keys: 'APIKEY', 'ADDRESS'.
        free_terms (str): A search query like used in the PubMed search bar.
        retmax (int): Maximum number of PMIDs to return.

    Returns:
        hits_on_free_search (list): A list with PMIDs as strings. In example: ['32943485', '...']
    """
    payload['terms'] = free_terms
    payload['retmax'] = str(retmax)
    results = session.post(
        credentials["ADDRESS"] + "refset/free_search",
        payload
    )

    js = results.json()
    # js['result'] =
    # >  parkinson"  , 'hitnr': 126, 'pmids': ['32943485', '...']
    # >  parkinson's", 'hitnr': 866, 'pmids': ['37354828', '...']
    # NOTE: I expected 'parkinson' to have more hits, since it would include "parkinson's" but "parkinsonism" as well?
    
    # Get list with PMIDs
    hits_on_free_search = js['result']['pmids']
    
    # Add "pmid" at the beginning of list. ("pmid" will become the header of a column)
    hits_on_free_search.insert(0, "pmid")

    # Report number of hits
    print(f"Query '{js['result']['query']}' generated {js['result']['hitnr']} PMID hits.")

    return hits_on_free_search

# Search method 2: Search on pre-defined alias of TenWise
# TODO: this function should be split into two functions. 
# 1) Finds the concept_ids of `search_terms` and appends it to a file (where the user can already have put concept_ids in)
# 2) Read in `concept_id_file` and query TenWise for PMIDs.
def search_concepts(session: requests.Session, payload: dict, credentials: dict, path_to_pesticide_ids: str, retmax: int):
    """
    Return PMIDs from TenWise Knowledge Map by searching on provided concept_ids.
    This includes 'parkinson' and concept_ids provided in path_to_pesticide_ids.

    See link for more information: https://apimlqv2.tenwiseservice.nl/html/all_help.html#conceptset-evidence

    Args:
        session (requests.Session): API session. Provides cookie persistence, connection-pooling, and configuration. Created using `start_tenwise_session` function.
        payload (dict): A payload template for building queries. Created using `start_tenwise_session` function.
        credentials (dict): Must contain following keys: 'APIKEY', 'ADDRESS'.
        path_to_pesticide_ids (str): Path to predefined concept_ids.
        retmax (int): Maximum number of PMIDs to return.

    Returns:
        hits_on_concept_ids (list): A list with PMIDs as strings. In example: ['32943485', '...']
    """
    
    ### PUBMED USING KMAP
    # Get all Parkinsons Disease concept_ids
    payload['terms'] = "parkinson"
    payload['wildcard'] = 'true'

    results = session.post(
        credentials["ADDRESS"] + "concept/search/",
        payload
    )
    payload['wildcard'] = 'false' # <- Turn off wildcard (cleaning after myself)

    js = results.json()

    # Get the one concept_id for "parkinson's disease"
    park_hit = [k for k, v in js['result']['hits'].items() if v[0].lower() == "parkinson's disease"]
    # NOTE: Disease concepts start with "TWDIS", therefore hits are filtered on "TWDIS": https://apimlqv2.tenwiseservice.nl/html/all_help.html#vocabularies
    # park_hits = [h for h in hits if h[:5] == 'TWDIS'] # ['TWDIS_03314', 'TWDIS_03315', ...]
    

    # Get all pesticide concept_ids
    # Current format is tab-delimited: `TWPHI_XXXXX \t name_pesticide`
    pest_hits = pd.read_csv(
        path_to_pesticide_ids,
        header = None,
        sep = "\t"
        ).iloc[:,0].to_list()

    # Combine both concept_ids
    payload['concept_ids'] = ",".join([*park_hit, *pest_hits])
    payload['retmax'] = str(retmax)
    results = session.post(
        credentials["ADDRESS"] + "conceptset/evidence/",
        # creds["ADDRESS"] + "conceptset/hits/",
        payload
    )
    js = results.json()
    concept_ids = [str(d["pmid"]) for d in js['result']['evidence']]
    metrics_hitnr = [str(d["hitnr"]) for d in js['result']['evidence']]
    metrics_score = [str(d["score"]) for d in js['result']['evidence']]

    # This will become the header of column:
    concept_ids.insert(0, "pmid")
    metrics_hitnr.insert(0, "hitnr")
    metrics_score.insert(0, "score")

    # hits_on_concept_ids = [[concept_ids[i], metrics_hitnr[i], metrics_score[i]] for i in range(len(concept_ids))]

    hits_on_concept_ids = [str([concept_ids[i], metrics_hitnr[i], metrics_score[i]]).strip("[]'").replace("'", "") for i in range(len(concept_ids))]

    return hits_on_concept_ids

# MAIN
if __name__ == "__main__":
    print("Start of concept2pmid.py")

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
            config["free_search_terms"],
            retmax = config["bruto_nr_pmids"]
        )

    # Option 2) Get pmid ids on concept_ids from TenWise vocabularies
    # TODO: This option is not modifiable yet via config.yaml (atm hardcoded in function)
    elif config["search_mode"].lower().strip() == "concept":
        pmid_hits = search_concepts(
            session,
            payload,
            creds,
            path_to_pesticide_ids = config["path_to_pesticide_ids"],
            retmax = config["bruto_nr_pmids"]
        )

    else:
        print("Error in search_mode. Please change in 'config.yaml' variable 'search_mode' to either 'free' or 'concept'.")
        sys.exit()

    # Save pmids to file
    output_file_name = f"data/pmids/{config['output_pmids']}_{config['experiment_name']}.csv"
    try:
        with open(output_file_name, "w", encoding="utf-8") as output:
            output.write(',\n'.join(pmid_hits))
        print(f"PMIDs were successfully written to '{output_file_name}'")

    except FileNotFoundError:
        Path("data/pmids").mkdir(exist_ok = True)
        with open(output_file_name, "w", encoding="utf-8") as output:
            output.write(',\n'.join(pmid_hits))
        print(f"PMIDs were successfully written to '{output_file_name}'")

    print("End of concept2pmid.py")
