"""Find PubMed Identifiers (PMIDs) based on provided free terms or fixed concepts.

This module finds relevant PMIDs on provided free terms or fixed concepts.
Start a session with the TenWise Knowledge Map API to find PMIDs:
1) Search on free text (e.g. "pesticides" and "Parkinson's disease")
2) Search on pre-defined concept_ids (e.g. "pesticides" and "Parkinson's disease")
Results are saved in a CSV file.

If search_mode is `free`, then a list only containing PMIDs is returned.
If search_mode is `concept`, then results include the following: pmid, hitnr, score.
Where 'pmid' are the PMIDs, 'hitnr' are number of unique concept_ids found in paper, and 'score' is the proportion of 'hitnr' to the total number of concept_ids requested.
See link for more information: https://apimlqv2.tenwiseservice.nl/html/all_help.html#conceptset-evidence

Usage:
    python concept2pmid.py -c config.yaml -n 1000 -m free -o pmids.csv

Arguments:
    -c, --config_file
        Path to the configuration file (default: 'config.yaml')
    -n, --nr_pmids
        Number of PMIDs to be returned (default: 1000)
    -m, --search_mode
        Search mode: 'free' or 'concept'.
    -o, --output_file
        Name of the output file, incl. its suffix.

Input:
    Please find search terms and concept_ids in the configuration file (config.yaml).
    A configuration file (config.yaml) is required. It contains the following keys:
    - path_to_concept_ids: Path to a file with concept_ids (tab-delimited)
    - free_search_terms: Search terms for free text search

Output:
    An comma separated values output file is generated.

    Example:
    
    ```
    pmid,\n
    34429776,\n
    6905769,\n
    ...,\n
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
def collect_arguments() -> argparse.Namespace:
    """Collect arguments from the command line."""
    parser = argparse.ArgumentParser(
        description = __doc__,
    )

    parser.add_argument(
        "-c",
        dest = "config_file",
        required = True,
        help = "Provide path to the configuration file (default: 'config.yaml')",
        default = "config.yaml"
    )

    parser.add_argument(
        "-n",
        dest = "nr_pmids",
        required = False,
        help = "Provide the number of PMIDs to be returned (default: 1000)",
        default = 1000,
        type = int
    )

    parser.add_argument(
        "-m",
        dest = "search_mode",
        required = True,
        help = "Provide the search mode: 'free' or 'concept'.",
    )

    parser.add_argument(
        "-o",
        dest = "output_file",
        required = True,
        help = "Provide the name of the file, incl. its suffix.",
    )

    return parser.parse_args()

# Get credentials
def get_credentials(path_to_text: str) -> dict:
    """Load a file with tab separated values from path_to_text and creates/returns a dictionary where the first column will be the key and the second column will be the value."""
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
    """Initialise a session by using the provided login_credentials and returns the started session and payload.
    
    Args:
        login_credentials (dict): Must contain following keys: 'APIKEY' and 'ADDRESS'.

    Returns:
        session (requests.Session): An API session. Provides cookie persistence, connection-pooling, and configuration.

    Returns:
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
    """Return PMIDs for from a free text search on the TenWise MEDLINE library.

    Search PMIDs in the TenWise MEDLINE library on provided free_terms.
    The search query (free_terms) can follow the same syntax as for a PubMed search.
    Numbers of PMIDs being returned is controlled by `retmax`.
    See link for more information: https://apimlqv2.tenwiseservice.nl/html/all_help.html#refset-free-search
    
    Args:
        session (requests.Session): An API session. Provide cookie persistence, connection-pooling, and configuration. (Created using `start_tenwise_session` function.)
        payload (dict): A payload for building queries. (Created using `start_tenwise_session` function.)
        credentials (dict): Must contain following keys: 'APIKEY' and 'ADDRESS'.
        free_terms (str): A query.
        retmax (int): Maximum number of PMIDs to return. (default: 50)

    Returns:
        hits_on_free_search (list): A list with PMIDs as strings. Example: ['32943485', '...']
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
# BIG TODO: MOVE CONCEPT_ID OF "PARKINSON'S DISEASE" TO data/concepts/concept_ids.txt so that all concept_ids are in one place. (and parkinson's disease is not hardcoded in the function)
# Optional TODO: this function should be split into two functions:
# 1) Finds the concept_ids of `search_terms` and appends it to a file (where the user can already have put concept_ids in)
# 2) Read in `concept_id_file` and query TenWise for PMIDs.
def search_concepts(session: requests.Session, payload: dict, credentials: dict, path_to_concept_ids: str, retmax: int):
    """Return PMIDs from TenWise Knowledge Map by searching on provided concept_ids.

    TODO:
    This includes 'parkinson' and concept_ids provided in path_to_concept_ids.

    Search PMIDs in the TenWise Knowledge Map by searching on provided concept_ids found in a file.
    This is a TXT file that is Tab-delimited where each line starts with the concept_id like so: `TWPHI_XXXXX \t name_pesticide`
    Numbers of PMIDs being returned is controlled by `retmax`.
    Results include the following: pmid, hitnr, score.
    Where 'pmid' are the PMIDs, 'hitnr' are number of unique concept_ids found in paper, and 'score' is the proportion of 'hitnr' to the total number of concept_ids requested.
    See link for more information: https://apimlqv2.tenwiseservice.nl/html/all_help.html#conceptset-evidence

    Args:
        session (requests.Session): An API session. Provide cookie persistence, connection-pooling, and configuration. (Created using `start_tenwise_session` function.)
        payload (dict): A payload for building queries. (Created using `start_tenwise_session` function.)
        credentials (dict): Must contain following keys: 'APIKEY' and 'ADDRESS'.
        path_to_concept_ids (str): Path to predefined concept_ids.
        retmax (int): Maximum number of PMIDs to return. (default: 50)

    Returns:
        hits_on_concept_ids (list): TODO: dit klopt niet: A list with PMIDs as strings. In example: ['32943485', '...']
    """
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


    # Get all pesticide concept_ids
    # Current format is tab-delimited: `TWPHI_XXXXX \t name_pesticide`
    pest_hits = pd.read_csv(
        path_to_concept_ids,
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

    # Collect concept_ids and metrics
    concept_ids = [str(d["pmid"]) for d in js['result']['evidence']]
    metrics_hitnr = [str(d["hitnr"]) for d in js['result']['evidence']]
    metrics_score = [str(d["score"]) for d in js['result']['evidence']]

    # This will become the header of column:
    concept_ids.insert(0, "pmid")
    metrics_hitnr.insert(0, "hitnr")
    metrics_score.insert(0, "score")

    # Combine concept_ids with metrics into one list
    hits_on_concept_ids = [str([concept_ids[i], metrics_hitnr[i], metrics_score[i]]).strip("[]'").replace("'", "") for i in range(len(concept_ids))]

    return hits_on_concept_ids

def main():
    """Find PubMed Identifiers (PMIDs) based on given free terms (`free`) or fixed concepts (`concept`).

    This function is the main entry point of the concept2pmid.py script.
    Start a session with the TenWise Knowledge Map API to find PMIDs:
    1) Search on free text (e.g. "pesticides" and "Parkinson's disease")
    2) Search on pre-defined concept_ids (e.g. "pesticides" and "Parkinson's disease")
    Results are saved in a CSV file.

    If search_mode is `free`, then a list only containing PMIDs is returned.
    If search_mode is `concept`, then results include the following: pmid, hitnr, score.
    Where 'pmid' are the PMIDs, 'hitnr' are number of unique concept_ids found in paper, and 'score' is the proportion of 'hitnr' to the total number of concept_ids requested.
    See link for more information: https://apimlqv2.tenwiseservice.nl/html/all_help.html#conceptset-evidence

    Results are saved in a CSV file.
        """
    print("Start of concept2pmid.py")

    # Collect arguments
    args = collect_arguments()
    print(f"Arguments: {args}")

    # Load configuration file
    with open(args.config_file, 'r', encoding="utf-8") as stream:
        config = yaml.safe_load(stream)

    # Get credentials
    creds = get_credentials(config['path_to_credentials'])

    # Start session
    session, payload = start_tenwise_session(creds)

    # SEARCH 
    # Option 1) Get pmid ids on keywords "pesticides" and "Parkinson's disease"
    # Optional TODO: This part needs to change so that it is modulair.
    if args.search_mode.lower().strip() == "free":
        pmid_hits = search_free(
            session,
            payload,
            creds,
            config["free_search_terms"],
            retmax = args.nr_pmids
        )

    # Option 2) Get pmid ids on concept_ids from TenWise vocabularies
    # Optional TODO: This option is not modifiable yet via config.yaml (atm hardcoded in function)
    elif args.search_mode.lower().strip() == "concept":
        pmid_hits = search_concepts(
            session,
            payload,
            creds,
            path_to_concept_ids = config["path_to_concept_ids"],
            retmax = args.nr_pmids
        )

    else:
        print("Error in search_mode. Please change in 'config.yaml' variable 'search_mode' to either 'free' or 'concept'.")
        sys.exit()

    # Save pmids to file
    output_file_name = f"data/pmids/{args.output_file}"
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

# MAIN
if __name__ == "__main__":
    main()
