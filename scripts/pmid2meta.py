"""Search meta data of full scientific papers in OpenAlex.

This module searches for meta data of full scientific papers by searching the OpenAlex (https://openalex.org/) database for PMIDs. 
It reports were URLs are found for the PMIDs, and if it is a PDF download page or a general landing page.
An email address in the config file is required to get access to the polite pool.

Usage:
    python pmid2meta.py -c config.yaml -i pmids_in.csv -m efficient

Arguments:
    -c, --config_file
        Path to the configuration file (default: 'config.yaml')
    -i, --input_file
        Name of the input file, incl. its suffix.
    -m  --query_mode
        Query mode to use on OpenAlex. (default: 'efficient') Choose between 'efficient' or 'full' search. 'efficient' will only query PMIDs that are not present yet in the meta data file, 'full' search will query all PMIDs provided in input file.

Input:
    A CSV file with at least one column header named 'pmid', were the values corresponds to its PubMed Identifier.
    A configuration file (config.yaml) is required. Please make sure the correct email address is in the configuration file (config.yaml).

Output:
    It saves meta data of the PMIDs to './data/meta/'.

"""


# IMPORTS
import sys
import time
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
        "-i",
        dest = "input_file",
        required = True,
        help = "Provide the name of the input file.",
    )

    parser.add_argument(
        "-m",
        dest = "query_mode",
        required = True,
        help = "Query mode to use on OpenAlex. (default: 'efficient') Choose between 'efficient' or 'full' search. 'efficient' will only query PMIDs that are not present yet in the meta data file, 'full' search will query all PMIDs provided in input file.",
        choices = ['efficient', 'full'],
        default = 'efficient'
    )

    return parser.parse_args()

# Get PDF URLs from list of PMIDs
def get_meta_for_pmids(pmids: list, email: str) -> dict:
    """Retrieve meta data of scientific papers of provided PMIDs.
    
    Provide a list with PMIDs (as strings) and an email address to get into the polite pool.
    Meta data is retrieved from OpenAlex (https://openalex.org/) and filtered on meta of interest.
    Metrics on how many PMIDs are open access are recorded and returned.
    
    Args:
        pmids (list): A list with PMIDs of interest. `pmids` must not contain numerical values. If it does, use the following code to turn them into strings: `[str(i) for i in pmids]`
        email (str): An email address of the user.

    Returns:
        df_chunk_meta (pd.DataFrame): Data frame containing the following meta data: ["pmid", "doi", "pub_year", "is_oa", "landing_url", "pdf_url", "is_accepted", "is_published", "is_retracted", "cited_by_count", "referenced_count"]
    """

    # build query url for OpenAlex
    url = f"https://api.openalex.org/works?filter=pmid:{'|'.join(pmids)}&per-page=200&mailto={email}"

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

        # meta control:
        try:
            doi = r["doi"].split("doi.org/")[1]
        except AttributeError:
            doi = None

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

        # concatenate df_chunk_meta with new information
        df_chunk_meta = pd.concat([df_chunk_meta, df_part], ignore_index= True)

    return df_chunk_meta

def print_metrics(df: pd.DataFrame):
    """Print general metrics of pd.DataFrame that has columns 'is_oa' and 'pdf_url'."""
    n_total_from_query = df.shape[0]
    n_open_access = df['is_oa'].value_counts()[True]
    n_pdf_url = df['pdf_url'].isna().value_counts()[False]
    print("---Total overview:")
    print(f'{n_total_from_query} papers were processed by OpenAlex. (NOTE: Only papers of which no pdf is found in the pdf_directory are being processed in this script.)')
    print(f'Proportion of PMIDs that returned an open access paper: {round(n_open_access / n_total_from_query * 100, 2)}% ({n_open_access}/{n_total_from_query})')
    print(f'Proportion of Open Access PMIDs with PDF URLs: {round(n_pdf_url / n_open_access* 100, 2)}% ({n_pdf_url}/{n_open_access})')

def main():
    """Search meta data of full scientific papers in PDF.

    This function is the main entry point of the pmid2meta.py script.
    Collect arguments, load the configuration file, retrieve PMIDs from the input file,
    exclude PMIDs that are already in the meta data file, retrieve meta data from OpenAlex.
    It also reports metrics.
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
    if args.query_mode == 'efficient':
        # Read old meta file
        expected_output_filename = f"data/meta/meta_{'_'.join(args.input_file.split('_')[1:])}"
        try:
            df_old_meta = pd.read_csv(expected_output_filename, index_col=0)
            # Get `pmid` values
            existing_pmids = df_old_meta['pmid'].values
            old_pmids = pmids
            # Exclude pmids that are already in meta_*.csv
            pmids = list(set(pmids).difference(existing_pmids.astype(str)))
            # Report how many pmids are already in the local pdf_directory
            print(f"{len(old_pmids) - len(pmids)}/{len(old_pmids)} PMIDs are already found in '{expected_output_filename}'.")

        except FileNotFoundError:
            print(f"WARNING: Did not find '{expected_output_filename}'. Possibly did not make 'data/meta/' directory? Application will continue in 'full' `query_mode`.")
            args.query_mode = 'full'

    # Collect meta data from OpenAlex API (https://docs.openalex.org/)
    # Data frame for collecting:
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

        # for chunk in pmids_chunks list
        for i, chunk in enumerate(pmids_chunks):
            # Wait 10 seconds to avoid penalties from OpenAlex
            if i != 0:
                print("Sleeping for 10 seconds to avoid penalties from OpenAlex")
                time.sleep(10)
            # Get meta data from OpenAlex
            print(f"Processing chunk {i+1}/{len(pmids_chunks)}")
            df_chunk_meta = get_meta_for_pmids(chunk, config["email_address"])
            # Concatenate df_total_meta with new information
            df_total_meta = pd.concat([df_total_meta, df_chunk_meta], ignore_index= True)

    # if pmids is shorter than 100 items:
    else:
        # Get pdf urls from OpenAlex
        df_total_meta = get_meta_for_pmids(pmids, config["email_address"])

    # Print metrics
    print_metrics(df_total_meta)

    # If 'efficient', then append existing file
    if args.query_mode == 'efficient':
        df_total_meta = pd.concat([df_old_meta, df_total_meta], ignore_index= True)

    # Save meta data
    # NOTE: I choose to make separate 'meta files' for each experiment, so that it is logged which meta data was relevant at the time of the experiment
    # (in case the data ever changes on OpenAlex).
    print("Saving meta data")
    Path("data/meta").mkdir(exist_ok = True)
    output_filename = f"data/meta/meta_{'_'.join(args.input_file.split('_')[1:])}"
    df_total_meta.to_csv(output_filename)
    print(f"Meta data is successfully written to '{output_filename}'")

    print("End of pmid2meta.py")


# MAIN
if __name__ == "__main__":
    main()
