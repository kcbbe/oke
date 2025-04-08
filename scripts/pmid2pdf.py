
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


    # start collecting pdf urls
    pdf_collector = dict()
    landing_collector = dict()

    for r in response["results"]:
        pmid = r["ids"]["pmid"].split("/")[-1]

        if r["best_oa_location"] is not None:
            if r["best_oa_location"]["pdf_url"] is not None:
                pdf_collector[pmid] = r["best_oa_location"]["pdf_url"]

            # TODO: Troubleshoot when `pdf_url` is None, how to extract a pdf in an alternative way:
            # if pdf_url is empty, try to retrieve pdf by trying tricks on landing_page_url
            elif r["best_oa_location"]["pdf_url"] is None:
                if r["best_oa_location"]["landing_page_url"].split("/")[-1][:3] == "PMC":
                    landing_collector[pmid] = f'{r["best_oa_location"]["landing_page_url"]}/pdf' # TODO: Check if this can be added to pdf_collector instead?
                else:
                    landing_collector[pmid] = f'{r["best_oa_location"]["landing_page_url"]}'


    # TODO: this needs a different filtering now.. (like best_open_version:acceptedOrPublished)
    n_total_from_query = response["meta"]["count"]
    # n_pdf = len(pdf_collector)
    # n_landing = len(landing_collector)
    print(f'Proportion of PMIDs that returned an open access paper: {round(sum([len(pdf_collector), len(landing_collector)]) / n_total_from_query * 100, 2)}% ({sum([len(pdf_collector), len(landing_collector)])}/{n_total_from_query})')
    print(f'Proportion of Open Access PMIDs with PDF URLs: {round(len(pdf_collector) / sum([len(pdf_collector), len(landing_collector)]) * 100, 2)}% ({len(pdf_collector)}/{sum([len(pdf_collector), len(landing_collector)])})')

    return pdf_collector, landing_collector

# TODO: this can be multiprocessed..
def get_pdf_papers_from_url(pdf_urls: dict):
    """
    """

    # Collect results
    collect_errors = []
    success_counter = 0

    # Create `pdf_papers` directory, if it does not yet exists.
    Path("data/pdf_papers/").mkdir(exist_ok = True)

    # Iterate
    for pdf_key in pdf_urls:

        # Check if file already in output folder
        if Path(f"data/pdf_papers/{pdf_key}.pdf").exists():
            success_counter += 1

        # Else, download the file and save as `key`
        else:
            # This should help to by pass bot checks
            req = Request(
                url = pdf_urls[pdf_key],
                headers = {"User-Agent": "Mozilla/6.0"}
            )
            try:
                input_json = {"output" : urlopen(req).read()}
                success_counter += 1

                # Save pdf
                with open(f"data/pdf_papers/{pdf_key}.pdf", "wb") as output:
                    output.write(input_json["output"])

            except HTTPError as e:
                collect_errors.append([pdf_key, e.code, e.msg])

    # TODO: notify user where file is saved. and how many were saved (success_counter & len(collect_errors))
    print(f"Proportion of successful downloads: {round(success_counter / len(pdf_urls) * 100, 2)}% ({success_counter}/{len(pdf_urls)})")
    
    # return error log
    return collect_errors

# MAIN
if __name__ == "__main__":
    print("Start of pmid2pdf.py")

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
    pmids = pd.read_csv(
        f'data/pmids/{config["output_pmids"]}_{config["experiment_name"]}.csv',
    ).loc[:,"pmid"].to_list()

    # convert pmids `int` to `str`
    pmids = [str(i) for i in pmids]

    # Exclude pmids of which the pdfs are already downloaded. TODO: this needs to be communicated with user!
    try:
        local_pdfs = {f.stem for f in Path("data/pdf_papers").iterdir() if f.suffixes[0] == ".pdf"}
        pmids = list(set(pmids).difference(local_pdfs))
    except FileNotFoundError:
        print("WARNING: Did not find 'data/pdf_paper/ directory. If this is the first time running application that there is nothing to worry about. Else, check if set up is correct.'")
        pass

    # Get PDF URLs from OpenAlex API (https://docs.openalex.org/)
    pdf_urls, landing_urls = get_pdf_urls_from_pmids(pmids, config["email_address"])
    # TODO: further data exploration of the papers???????????? ??????????? ?

    # TODO: Try to have the following processes multiprocessed.
    errors = get_pdf_papers_from_url(pdf_urls)

    # TODO: report `errors`

    print("End of pmid2pdf.py")
