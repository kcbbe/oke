"""Search meta data of full scientific papers in OpenAlex.

This module searches for meta data of full scientific papers by searching the OpenAlex (https://openalex.org/) database for PMIDs. 
It reports were URLs are found for the PMIDs, and if it is a PDF download page or a general landing page.
An email address in the config file is required to get access to the polite pool.

Usage:
    TODO: python pmid2meta.py -c config.yaml -i pmids_in.csv -o pmids_out.csv

Arguments:
    -c, --config_file
        Path to the configuration file (default: 'config.yaml')
    -i, --input_file
        Name of the input file, incl. its suffix.
    -m  --query_mode
        Query mode to use on OpenAlex. (default: 'efficient') Choose between 'efficient' or 'full' search. 'efficient' will only query PMIDs that are not present in destination folder, 'full' search will query all PMIDs provided in input file.

Input:
    A CSV file with at least one column header named 'pmid', were the values corresponds to its PubMed Identifier.
    A configuration file (config.yaml) is required. Please make sure the correct email address is in the configuration file (config.yaml).

Output:
    It saves which URLs were found for the PMIDs, and if it is a PDF download page or a general landing page.
    It reports which errors it encountered when failing to retrieve a PDF.

"""

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
        "-i",
        dest = "input_file",
        required = True,
        help = "Provide the name of the input file.",
    )

    parser.add_argument(
        "-m",
        dest = "query_mode",
        required = True,
        help = "Query mode to use on OpenAlex. (default: 'efficient') Choose between 'efficient' or 'full' search. 'efficient' will only query PMIDs that are not present in destination folder, 'full' search will query all PMIDs provided in input file.",
        default = 'efficient'
    )

    return parser.parse_args()


def exclude_already_meta_searched_pmids(pmids):
    #TODO: """Exclude pmids of which the pmid meta data are already retrieved."""
    try:
        # Compare local pdfs with obtained pmids
        local_pdfs = {f.stem for f in Path("data/pdf_papers").iterdir() if f.suffixes[0] == ".pdf"}
        old_pmids = pmids
        # Exclude pmids that are already in the local pdf_directory
        pmids = list(set(pmids).difference(local_pdfs))
        # Report how many pmids are already in the local pdf_directory
        print(f"{len(old_pmids) - len(pmids)}/{len(old_pmids)} papers are already found in the local pdf_directory.")

    except FileNotFoundError:
        print("WARNING: Did not find 'data/pdf_paper/' directory. If this is the first time running application that there is nothing to worry about. Else, check if set up is correct.")
        # Create `pdf_papers` directory, if it does not yet exists.
        Path("data/pdf_papers/").mkdir(exist_ok = True)
        pass

    return pmids


# Get PDF URLs from list of PMIDs
def get_meta_for_pmids(pmids: list, email: str) -> dict:
    """Retrieve meta data of scientific papers of provided PMIDs.
    
    Provide a list with PMIDs (as strings) and an email address to get into the polite pool.
    Meta data is retrieved from OpenAlex (https://openalex.org/) and filtered on meta of interest.
    Metrics on how many PMIDs are open access are recorded and returned.
    
    Args:
        pmids (list): A list with PMIDs of interest. `pmids` must not contain numerical values. If it does, use the following code to turn them into strings: `[str(i) for i in pmids]`
        email (str): An email address of the user.

    Returns: TODO:
        pdf_collector (dict):
        landing_collector (dict):
        metrics (list):
    """

    # build query url for OpenAlex
    url = f"https://api.openalex.org/works?filter=pmid:{'|'.join(pmids)}&mailto={email}"

    # get response from OpenAlex
    with requests.Session() as session:
        response = session.get(url).json()

    # flow control: if an error occurred in the `get` statement.
    try:
        print(f'Successful query: response time {response["meta"]["db_response_time_ms"]}ms')
    except KeyError:
        print(f'ERROR in `get_pdf_urls_from_pmids`: A problem occurred in the `get` statement to OpenAlex. Please see the following error message:\n{response["error"]} {response["message"]}')
        sys.exit()

    # start collecting meta
    column_names = [
        "pmid",
        "doi",
        "pub_year",
        
        "is_oa",
        "landing_url",
        "pdf_url",
        "is_accepted",
        "is_published",
        "is_retracted",

        "cited_by_count",
        "referenced_count",
    ]

    df_chunk_meta = pd.DataFrame(columns= column_names)

    # iterate over found pmids
    for r in response["results"]:

        # # meta control:
        # pmid = r["ids"]["pmid"].split("/")[-1]
        try:
            doi = "/".join(r["doi"].split("/")[-2:])
        except AttributeError:
            doi = None
        # doi = "/".join(r["doi"].split("/")[-2:])
        # pub_year = r["publication_year"]

        # is_oa = r["primary_location"]['is_oa']
        # landing_url = r["primary_location"]['landing_page_url']
        # pdf_url = r["primary_location"]['pdf_url']
        # is_accepted = r["primary_location"]['is_accepted']
        # is_published = r["primary_location"]['is_published']
        # is_retracted = r['is_retracted']

        # cited_by_count = r["cited_by_count"]
        # referenced_count = r["referenced_works_count"]

        # place in a data frame
        df_part = pd.DataFrame(
            data= [[
                r["ids"]["pmid"].split("/")[-1],
                doi,
                r["publication_year"],

                r["primary_location"]['is_oa'],
                r["primary_location"]['landing_page_url'],
                r["primary_location"]['pdf_url'],
                r["primary_location"]['is_accepted'],
                r["primary_location"]['is_published'],
                r['is_retracted'],

                r["cited_by_count"],
                r["referenced_works_count"],
            ]],
            columns= column_names,
        )

        df_chunk_meta = pd.concat([df_chunk_meta, df_part], ignore_index= True)


        # # if pmid contains "beste_oa_location", try to collect pdf_url, else collect its landing_page_url
        # if r["best_oa_location"] is not None:
        #     if r["best_oa_location"]["pdf_url"] is not None:
        #         pdf_collector[pmid] = r["best_oa_location"]["pdf_url"]

        #     elif r["best_oa_location"]["pdf_url"] is None:
        #         landing_collector[pmid] = f'{r["best_oa_location"]["landing_page_url"]}'

    # # Report metrics
    # n_total_from_query = response["meta"]["count"]
    # proportion_open_access = sum([len(pdf_collector), len(landing_collector)])
    # proportion_pdf_url = len(pdf_collector)

    # metrics = [n_total_from_query, proportion_open_access, proportion_pdf_url]

    return df_chunk_meta #, metrics



def main():
    """Search meta data of full scientific papers in PDF.

    This function is the main entry point of the pmid2meta.py script.
    Collect arguments, load the configuration file, retrieve PMIDs from the input file,
    exclude PMIDs that are already in the meta data file, retrieve meta data and PDF URLs from OpenAlex.
    It also reports metrics and saves URLs and errors to log files.
    """
    print("Start of pmid2meta.py")

    # Collect arguments
    args = collect_arguments()

    # Load configuration file
    with open(args.config_file, 'r', encoding="utf-8") as stream:
        config = yaml.safe_load(stream)

    # Load pmid file
    pmids = pd.read_csv(
        f'data/pmids/{args.input_file}',
    ).loc[:,"pmid"].to_list()

    # Convert pmids `int` to `str`
    pmids = [str(i) for i in pmids]

    # Exclude pmids of which the pdfs are already downloaded.
    # TODO:
    if args.query_mode == 'efficient':
        pmids = exclude_already_meta_searched_pmids(pmids)

    # TODO: Try to have the following processes multiprocessed.
    # Collect pdf_urls and landing_urls
    total_metrics = [["total", "prop_open_access", "prop_pdf_url"], [0, 0, 0]]
    pdf_urls = dict()
    landing_urls = dict()
    meta = dict()
    errors = list()

    # TODO:TODO:TODO: `meta`

    # Get meta data from OpenAlex API (https://docs.openalex.org/)
    # data frame for collection
    column_names = [
        "pmid",
        "doi",
        "pub_year",
        
        "is_oa",
        "landing_url",
        "pdf_url",
        "is_accepted",
        "is_published",
        "is_retracted",

        "cited_by_count",
        "referenced_count",
    ]
    df_total_meta = pd.DataFrame(columns= column_names)

    # if pmids longer than 100 items
    if len(pmids) > 100:
        pmids_chunks = [pmids[i:i + 100] for i in range(0, len(pmids), 100)]

        for i, chunk in enumerate(pmids_chunks):
            # Wait 10 seconds to avoid penalties from OpenAlex
            if i != 0:
                print("Sleeping for 10 seconds to avoid penalties from OpenAlex")
                time.sleep(10)
            # Get meta data from OpenAlex
            print(f"Processing chunk {i+1}/{len(pmids_chunks)}")
            df_chunk_meta = get_meta_for_pmids(chunk, config["email_address"])
            
            df_total_meta = pd.concat([df_total_meta, df_chunk_meta], ignore_index= True)


            # # Collect pdf urls and landing urls
            # pdf_urls.update(pdfs)
            # landing_urls.update(landings)

            # # Update metrics
            # for i, met in enumerate(metrics):
            #     total_metrics[1][i] += met
            # for i in range(len(metrics)):
            #     total_metrics[1][i] += metrics[i]



    # if pmids is shorter than 100 items:
    else:
        # Get pdf urls from OpenAlex
        df_total_meta = get_meta_for_pmids(pmids, config["email_address"])
        
        # # Update metrics
        # for i, met in enumerate(metrics):
        #     total_metrics[1][i] += met

    # # Report metrics
    # n_total_from_query = total_metrics[1][0]
    # n_open_access = total_metrics[1][1]
    # n_pdf_url = total_metrics[1][2]
    # print("Total overview:")
    # print(f'{n_total_from_query} papers were processed by OpenAlex. (NOTE: Only papers of which no pdf is found in the pdf_directory are being processed in this script.)')
    # print(f'Proportion of PMIDs that returned an open access paper: {round(n_open_access / n_total_from_query * 100, 2)}% ({n_open_access}/{n_total_from_query})')
    # print(f'Proportion of Open Access PMIDs with PDF URLs: {round(n_pdf_url / n_open_access* 100, 2)}% ({n_pdf_url}/{n_open_access})')

    # Save meta data
    # NOTE: I choose to make separate 'meta files' for each experiment, so that it is logged which meta data was relevant at the time of the experiment
    # (in case the data ever changes on OpenAlex).
    Path("data/meta").mkdir(exist_ok = True)
    df_total_meta.to_csv(f"data/meta/meta_{'_'.join(args.input_file.split('_')[1:])}")


    # ## Prepare a list of urls for saving
    # all_urls = [['pmid', 'type', 'url']]
    # if len(pdf_urls) != 0:
    #     all_urls.extend([[k, 'pdf_url', pdf_urls[k]] for k in pdf_urls])
    # if len(landing_urls) != 0:
    #     all_urls.extend([[k, 'landing_url', landing_urls[k]] for k in landing_urls])

    # ## Save urls to file
    # print("Saving found urls")
    # output_file_name = f"logs/urls_pmid2pdf_{args.output_file}"
    # try:
    #     with open(output_file_name, "w", encoding="utf-8") as output:
    #         output.write(',\n'.join([str(line).strip("[]'").replace("'", "") for line in all_urls]))
    #     print(f"Url log is successfully written to '{output_file_name}'")

    # except FileNotFoundError:
    #     Path("logs").mkdir(exist_ok = True)
    #     with open(output_file_name, "w", encoding="utf-8") as output:
    #         output.write(',\n'.join([str(line).strip("[]'").replace("'", "") for line in all_urls]))
    #     print(f"Url log is successfully written to '{output_file_name}'")


    # TODO: further data exploration of the papers????????????

    print("End of pmid2meta.py")


# MAIN
if __name__ == "__main__":
    main()
