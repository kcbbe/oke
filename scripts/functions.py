# MODULE
"""
functions.py: A collection of supporting functions.

INITIALISATION
* get_credentials
"""
# IMPORTS
import requests
import sys

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

# Get PDF URLs from list of PMIDs TODO: Refactor: separate OpenAlex query from PDF retrieval (that would be a nicer design pattern)
def get_pdf_urls_from_pmids(pmids: list, email: str) -> dict:
    """
    Retrieve URLs where PDF files are hosted of provided PubMed ids.
    This is done by sending a 'get' request to the OpenAlex API:
    https://docs.openalex.org/ (also see https://openalex.org/)
    
    Args:
        email (str): email address of user.
        pmids (list): list with PubMed ids of interest. `pmids` must not contain numerical values. If it does, use the following code to turn them into strings: `[str(i) for i in pmids]`

    Returns:
        collection (dict):
    """

    # flow control: pmids needs to contain strings, not numerical values.
    try:
        # TODO: refactor long line to make it more readable
        url = f"https://api.openalex.org/works?filter=pmid:{'|'.join(pmids)},best_open_version:acceptedOrPublished&select=ids,best_oa_location,open_access&mailto={email}"
    except TypeError as e:
        print(f"ERROR in `get_pdf_urls_from_pmids`: Likely the `pmids` list contains numeric representation. Please convert them to a string as mentioned in the docstring of this function.\n{e}")
        sys.exit()

    # get response from OpenAlex
    with requests.Session() as session:
        response = session.get(url).json()

    # flow control: if an error occurred in the `get` statement.
    try:
        print(f'Successfull query: response time {response["meta"]["db_response_time_ms"]}ms')
    except KeyError:
        print(f'ERROR in `get_pdf_urls_from_pmids`: A problem occurred in the `get` statement to OpenAlex. Please see the following error message:\n{response["error"]} {response["message"]}')
        sys.exit()

    print(f'Proportion of PMIDs that returned an open access paper: {round(response["meta"]["count"] / len(pmids) * 100, 2)}%')

    # start collecting pdf urls
    pdf_collector = dict()
    landing_collector = dict()

    for r in response["results"]:
        pmid = r["ids"]["pmid"].split("/")[-1]

        if r["best_oa_location"]["pdf_url"] is not None:
            pdf_collector[pmid] = r["best_oa_location"]["pdf_url"]

        # TODO: Troubleshoot when `pdf_url` is None, how to extract a pdf in an alternative way:
        # if pdf_url is empty, try to retrieve pdf by trying tricks on landing_page_url
        elif r["best_oa_location"]["pdf_url"] is None:
            if r["best_oa_location"]["landing_page_url"].split("/")[-1][:3] == "PMC":
                landing_collector[pmid] = f'{r["best_oa_location"]["landing_page_url"]}/pdf' # TODO: Check if this can be added to pdf_collector instead?
            else:
                landing_collector[pmid] = f'{r["best_oa_location"]["landing_page_url"]}'

    print(f'Proportion of Open Access PMIDs with PDF URLs: {round(len(pdf_collector) / response["meta"]["count"] * 100, 2)}%')

    return pdf_collector, landing_collector

# APPENDIX
if __name__ == "__main__":
    print(__doc__)
else:
    print(f"Custom module '{__name__}' is imported successfully!")
