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
def start_session(login_credentials: dict):
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

# def get_concept_ids(session, payload, list_keywords):
#     payload['terms'] = ",".join(list_keywords)
#     results = session.post(
#     creds["ADDRESS"] + "concept/search/",
#     payload
# )


# APPENDIX
if __name__ == "__main__":
    print(__doc__)
else:
    print(f"Custom module '{__name__}' is imported successfully!")
