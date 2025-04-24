
# IMPORTS
import sys
import time
import argparse
from pathlib import Path
import yaml
import requests
import pandas as pd
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

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

    # try:
    url = f"https://api.openalex.org/works?filter=pmid:{'|'.join(pmids)}&mailto={email}"
    # except TypeError as e:
    #     # print(f"ERROR in `get_pdf_urls_from_pmids`: Likely the `pmids` list contains numeric representation. Please convert them to a string as mentioned in the docstring of this function.\n{e}")
    #     # sys.exit()
    #     pmids = [str(i) for i in pmids]
    #     url = f"https://api.openalex.org/works?filter=pmid:{'|'.join(pmids)}&mailto={pmids}"

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
                landing_collector[pmid] = f'{r["best_oa_location"]["landing_page_url"]}'


    # Report metrics
    n_total_from_query = response["meta"]["count"]
    proportion_open_access = sum([len(pdf_collector), len(landing_collector)])
    proportion_pdf_url = len(pdf_collector)

    # print(f'{len(pmids)} papers were processed by OpenAlex. (NOTE: Only papers of which no pdf is found in the pdf_directory are being processed in this script.)')
    # print(f'Proportion of PMIDs that returned an open access paper: {round(sum([len(pdf_collector), len(landing_collector)]) / n_total_from_query * 100, 2)}% ({sum([len(pdf_collector), len(landing_collector)])}/{n_total_from_query})')
    # print(f'Proportion of Open Access PMIDs with PDF URLs: {round(len(pdf_collector) / sum([len(pdf_collector), len(landing_collector)]) * 100, 2)}% ({len(pdf_collector)}/{sum([len(pdf_collector), len(landing_collector)])})')

    metrics = [n_total_from_query, proportion_open_access, proportion_pdf_url]

    return pdf_collector, landing_collector, metrics

# TODO: this can be multiprocessed..
def get_pdf_papers_from_url(pdf_urls: dict):
    """
    Download pdf papers from pdf_urls.

    Args:
        pdf_urls (dict): PMID is key and pdf_url is value. For example: {'25461413': 'https://www.sciencedirect.com/... , ... }

    Returns:
        collect_errors (list): For example: [['pmid', 'error_code', 'error_message'], ['22420260', 403, 'Forbidden'], ...]
    """

    # Collect results
    collect_errors = [['pmid', 'error_code', 'error_message']]
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

            except URLError as e:
                collect_errors.append([pdf_key, '404', e.reason.strerror])

    # TODO: notify user where file is saved. and how many were saved (success_counter & len(collect_errors))
    print(f"Proportion of successful downloads: {round(success_counter / len(pdf_urls) * 100, 2)}% ({success_counter}/{len(pdf_urls)})")
    print("Please find the downloaded pdf's in 'data/pdf_papers/'")
    # return error log
    return collect_errors

def collect_arguments():
    """
    Collects arguments from the command line.
    """
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

    parser.add_argument(
        "-i",
        dest = "input_file",
        required = True,
        help = "Provide the name of the input file.",
    )

    args = parser.parse_args()

    return args

# MAIN
if __name__ == "__main__":
    print("Start of pmid2pdf.py")

    # Collect arguments
    args = collect_arguments()

    # Load configuration file
    with open(args.config_file, 'r', encoding="utf-8") as stream:
        config = yaml.safe_load(stream)

    # Load pmid file
    pmids = pd.read_csv(
        f'data/pmids/{args.input_file}',
    ).loc[:,"pmid"].to_list()

    # convert pmids `int` to `str`
    pmids = [str(i) for i in pmids]

    # Exclude pmids of which the pdfs are already downloaded. TODO: this needs to be communicated with user!
    try:
        local_pdfs = {f.stem for f in Path("data/pdf_papers").iterdir() if f.suffixes[0] == ".pdf"}
        old_pmids = pmids
        pmids = list(set(pmids).difference(local_pdfs))
        print(f"{len(old_pmids) - len(pmids)}/{len(old_pmids)} papers are already found in the local pdf_directory.")
    except FileNotFoundError:
        print("WARNING: Did not find 'data/pdf_paper/ directory. If this is the first time running application that there is nothing to worry about. Else, check if set up is correct.'")
        pass

    # TODO: Try to have the following processes multiprocessed.
    # Collect pdf_urls and landing_urls
    pdf_urls = dict()
    landing_urls = dict()
    total_metrics = [["total", "prop_open_access", "prop_pdf_url"], [0, 0, 0]]
    errors = list()

    # Get PDF URLs from OpenAlex API (https://docs.openalex.org/)
    # if pmids longer than 100 items
    if len(pmids) > 100:
        pmids_chunks = [pmids[i:i + 100] for i in range(0, len(pmids), 100)]

        for i, chunk in enumerate(pmids_chunks):
            # Wait 10 seconds to avoid penalties from OpenAlex
            if i != 0:
                print("Sleeping for 10 seconds to avoid penalties from OpenAlex")
                time.sleep(10)
            print(f"Processing chunk {i+1}/{len(pmids_chunks)}")
            pdfs, landings, metrics = get_pdf_urls_from_pmids(chunk, config["email_address"])
            pdf_urls.update(pdfs)
            landing_urls.update(landings)
            for i in range(len(metrics)):
                total_metrics[1][i] += metrics[i]

    else:
        pdf_urls, landing_urls, metrics = get_pdf_urls_from_pmids(pmids, config["email_address"])
        for i in range(len(metrics)):
                total_metrics[1][i] += metrics[i]

    # TODO: Report metrics
    n_total_from_query = total_metrics[1][0]
    n_open_access = total_metrics[1][1]
    n_pdf_url = total_metrics[1][2]
    print("Total overview:")
    print(f'{n_total_from_query} papers were processed by OpenAlex. (NOTE: Only papers of which no pdf is found in the pdf_directory are being processed in this script.)')
    print(f'Proportion of PMIDs that returned an open access paper: {round(n_open_access / n_total_from_query * 100, 2)}% ({n_open_access}/{n_total_from_query})')
    print(f'Proportion of Open Access PMIDs with PDF URLs: {round(n_pdf_url / n_open_access* 100, 2)}% ({n_pdf_url}/{n_open_access})')

    # Save urls
    all_urls = [['pmid', 'type', 'url']]
    if len(pdf_urls) != 0:
        all_urls.extend([[k, 'pdf_url', pdf_urls[k]] for k in pdf_urls])
    if len(landing_urls) != 0:
        all_urls.extend([[k, 'landing_url', landing_urls[k]] for k in landing_urls])

    print("Saving found urls")
    output_file_name = f"logs/urls_pmid2pdf_{args.output_file}"
    try:
        with open(output_file_name, "w", encoding="utf-8") as output:
            output.write(',\n'.join([str(line).strip("[]'").replace("'", "") for line in all_urls]))
        print(f"Url log is successfully written to '{output_file_name}'")

    except FileNotFoundError:
        Path("logs").mkdir(exist_ok = True)
        with open(output_file_name, "w", encoding="utf-8") as output:
            output.write(',\n'.join([str(line).strip("[]'").replace("'", "") for line in all_urls]))
        print(f"Url log is successfully written to '{output_file_name}'")

    # Attempt to retrieve pdf_url from landing_url:
    print("Trying to retrieve pdf_url from landing_url")
    # extend a PMC url with '/pdf':
    extra_pdf_urls = {k: landing_urls[k] + "/pdf" for k in landing_urls if landing_urls[k].split("/")[-1][:3] == "PMC"}

    # # add all landing_urls:
    # extra_pdf_urls = {k: landing_urls[k] for k in landing_urls}
    pdf_urls.update(extra_pdf_urls)
    print(f"{len(extra_pdf_urls)} urls that potentially link to a pdf were added to pdf_urls list")
          
    # Download PDFs
    print("Trying to download listed PDFs")
    errors = get_pdf_papers_from_url(pdf_urls)

    # Save error report to file
    if len(errors) > 1:
        output_file_name = f"logs/errors_pmid2pdf_{args.output_file}"
        try:
            with open(output_file_name, "w", encoding="utf-8") as output:
                output.write(',\n'.join([str(line).strip("[]'").replace("'", "") for line in errors]))
            print(f"Error log is successfully written to '{output_file_name}'")

        except FileNotFoundError:
            Path("logs").mkdir(exist_ok = True)
            with open(output_file_name, "w", encoding="utf-8") as output:
                output.write(',\n'.join([str(line).strip("[]'").replace("'", "") for line in errors]))
            print(f"Error log is successfully written to '{output_file_name}'")
    else:
        print("No error occurred")


    # TODO: Write collected pdf_urls and landing_urls to somewhere.
    

    # TODO: further data exploration of the papers???????????? ??????????? ?

    print("End of pmid2pdf.py")
