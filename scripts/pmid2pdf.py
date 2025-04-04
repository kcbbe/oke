
# IMPORTS
import sys
import argparse
from pathlib import Path
import yaml
import requests
import pandas as pd
from urllib.request import Request, urlopen
from urllib.error import HTTPError

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
        pdf_collector, landing_collector (both dict):
    """

    # flow control: pmids needs to contain strings, not numerical values.
    try:
        url = f"https://api.openalex.org/works?filter=pmid:{'|'.join(pmids)}&mailto={email}"
    except TypeError as e:
        # print(f"ERROR in `get_pdf_urls_from_pmids`: Likely the `pmids` list contains numeric representation. Please convert them to a string as mentioned in the docstring of this function.\n{e}")
        # sys.exit()
        pmids = [str(i) for i in pmids]
        url = f"https://api.openalex.org/works?filter=pmid:{'|'.join(pmids)}&mailto={email}"

    # get response from OpenAlex
    with requests.Session() as session:
        response = session.get(url).json()

    # flow control: if an error occurred in the `get` statement.
    try:
        print(f'Successfull query: response time {response["meta"]["db_response_time_ms"]}ms')
    except KeyError:
        print(f'ERROR in `get_pdf_urls_from_pmids`: A problem occurred in the `get` statement to OpenAlex. Please see the following error message:\n{response["error"]} {response["message"]}')
        sys.exit()

    # TODO: this needs a different filtering now.. (like best_open_version:acceptedOrPublished)
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

    # Load pmid file
    # with open(f'output/{config["output_pmids"]}_{config["experiment_name"]}.txt', 'r') as input:
    pmids = pd.read_csv(
        f'output/{config["output_pmids"]}_{config["experiment_name"]}.csv',
    ).loc[:,"pmid"].to_list()

# TODO:TODO:TODO:TODO:TODO:TODO:TODO:TODO:TODO:TODO:TODO:TODO:
# No more messages
# pdf_urls, landing_urls = get_pdf_urls_from_pmids(pmids, config["email_address"])
# Successfull query: response time 42ms
# Proportion of PMIDs that returned an open access paper: 100.0%
# Traceback (most recent call last):
#   File "<string>", line 1, in <module>
#   File "/homes/jbeenen/git-repo/master_graduation_project/scripts/pmid2pdf.py", line 59, in get_pdf_urls_from_pmids
#     if r["best_oa_location"]["pdf_url"] is not None:
#        ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^
# TypeError: 'NoneType' object is not subscriptable


    # Get PDF URLs from OpenAlex API (https://docs.openalex.org/)
    pdf_urls, landing_urls = get_pdf_urls_from_pmids(pmids, config["email_address"])
    # TODO: further data exploration of the papers???????????? ??????????? ?

    # Try to have the following processes multiprocessed.
    # TODO: Add a 'safepoint': pickle all input_json, `filename` = `pmid`
    # (is there a better way? I don't think a mysql is necessary since its just contains two columns (pmid, content)
    # (So that the documents remain accessible if it is ever removed from online)