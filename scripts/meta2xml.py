"""Download full scientific XMLs by using column `work_id` from the metadata CSV file.

This module downloads full scientific papers as XML by using the OpenAlex API by providing it with `work_id` that is found in the metadata CSV file for PMIDs.
After downloading, it reports which errors it encountered when failing to retrieve a XML.

Usage:
   python meta2xml.py -i pmids_in.csv -m efficient

Arguments:
    -c, --config_file
        Path to the configuration file (default: 'config.yaml')
    -i, --input_file
        Name of the input file, incl. its suffix.
    -m  --query_mode
        Query mode to use on OpenAlex. (default: 'efficient') Choose between 'efficient' or 'full' search. 'efficient' will only query PMIDs that are not present in destination folder, 'full' search will query all PMIDs provided in input file.

Input:
    A CSV file with one column header named 'pmid', were the values corresponds to its PubMed Identifier. And one column header named `work_id` with work ids from OpenAlex.
    A configuration file (config.yaml) is required. Please make sure the correct email address is in the configuration file (config.yaml).

Output:
    XMLs are downloaded to './data/xml_papers/'.
    It reports which errors it encountered when failing to retrieve a XML.
"""

# IMPORTS
import argparse
from pathlib import Path

import sys
import requests
import pandas as pd
import yaml
import time

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
        help = "Query mode to use on OpenAlex. (default: 'efficient') Choose between 'efficient' or 'full' search. 'efficient' will only query PMIDs that are not present in destination folder, 'full' search will query all PMIDs provided in input file.",
        choices = ['efficient', 'full'],
        default = 'efficient'
    )

    return parser.parse_args()

# Get XML files from list of PMIDs
def exclude_already_downloaded_pmids(pmids: list) -> list:
    """Exclude pmids of which the xmls are already downloaded."""
    try:
        # Compare local xmls with obtained pmids
        local_xmls = {f.stem for f in Path("data/xml_papers").iterdir() if f.suffixes[0] == ".xml"}
        old_pmids = pmids
        # Exclude pmids that are already in the local xml_directory
        pmids = list(set(pmids).difference(local_xmls))
        # Report how many pmids are already in the local xml_directory
        print(f"{round((len(old_pmids) - len(pmids)) / len(old_pmids) * 100, 2)}% ({len(old_pmids) - len(pmids)}/{len(old_pmids)}) papers are already found in the local xml_directory.")

    except FileNotFoundError:
        print("WARNING: Did not find 'data/xml_paper/' directory. If this is the first time running application that there is nothing to worry about. Else, check if set up is correct.")
        # Create `xml_papers` directory, if it does not yet exists.
        Path("data/xml_papers/").mkdir(exist_ok = True)

    return pmids


def get_xml_papers_from_url(work_ids: dict, YOUR_KEY: str, mode: str) -> list:
    """Download xml papers from (OpenAlex) work_ids.

    Take a dictionary of PMIDs and their corresponding work_ids as input,
    attempt to download the xmls (if it does not already exists), and save them to './data/xml_papers'.
    Collect error information of failed downloads.

    Args:
        work_ids (dict): PMID is key and work_id is value. For example: {'27634977': 'W2519408637' , ... }

    Returns:
        collect_errors (list): For example: [['pmid', 'error_code', 'error_message'], ['22420260', 403, 'Forbidden'], ...]
    """
    # Create `xml_papers` directory, if it does not yet exists.
    Path("data/xml_papers/").mkdir(exist_ok = True)

    # Collect results 
    collect_errors = [['pmid', 'error_code', 'error_message']]
    success_counter = 0
    success_session_counter = 0

    # Iterate
    for pmid in work_ids: 

        if mode == 'efficient':
            # Check if file already in output folder
            if Path(f"data/xml_papers/{pmid}.xml").exists():
                success_counter += 1

            # Else, download the file and save as `key`
            else:
                # build query url for OpenAlex (https://help.openalex.org/access/fulltext/)
                url = f"https://content.openalex.org/works/{work_ids[pmid]}.grobid-xml?api_key={YOUR_KEY}"

                # get response from OpenAlex
                with requests.Session() as session:
                    response = session.get(url)

                if response.status_code == 200:
                    with open(f"data/xml_papers/{pmid}.xml", "w", encoding="utf-8") as file:
                        # file.write(gzip.decompress(response.content)) 
                        file.write(response.content.decode("utf-8")) 
                    time.sleep(10)
                    # log success
                    success_counter += 1
                    success_session_counter += 1

                elif response.status_code == 404:
                    collect_errors.append([pmid, '404', response.content.decode("utf-8")])

                # TODO: code: 429 |text: Insufficient budget.

                else:
                    collect_errors.append([pmid, response.status_code, response.content.decode("utf-8")])

        elif mode == 'full':
            # Check if file already in output folder
            if Path(f"data/xml_papers/{pmid}.xml").exists():
                success_counter += 1

            # Else, download the file and save as `key`
            # build query url for OpenAlex (https://help.openalex.org/access/fulltext/)
            url = f"https://content.openalex.org/works/{work_ids[pmid]}.grobid-xml?api_key={YOUR_KEY}"

            # get response from OpenAlex
            with requests.Session() as session:
                response = session.get(url)

            if response.status_code == 200:
                with open(f"data/xml_papers/{pmid}.xml", "w", encoding="utf-8") as file:
                    # file.write(gzip.decompress(response.content)) 
                    file.write(response.content.decode("utf-8")) 
                time.sleep(10)
                # log success
                success_counter += 1
                success_session_counter += 1

            elif response.status_code == 404:
                collect_errors.append([pmid, '404', response.content.decode("utf-8")])

            else:
                collect_errors.append([pmid, response.status_code, response.content.decode("utf-8")])

    # Notify user where file is saved. and how many were saved (success_counter & len(collect_errors))
    print(f"{round(success_session_counter / len(work_ids) * 100, 2)}% ({success_session_counter}/{len(work_ids)}) papers are successful downloaded within this session.")
    print(f"{round(success_counter / len(work_ids) * 100, 2)}% ({success_counter}/{len(work_ids)}) papers were successful downloaded in total.")
    print("Please find the downloaded xml's in 'data/xml_papers/'")
    # return error log
    return collect_errors


def main():
    """Download full scientific papers in xml.

    This function is the main entry point of the meta2xml.py script.
    Collect arguments, retrieve PMIDs from the input file,
    exclude already downloaded PMIDs, retrieve xml URLs from the meta data file, and download the xmls.
    It also reports metrics and errors to log files.
    """
    print("Start of meta2xml.py")

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

    # Exclude pmids of which the xmls are already downloaded.
    if args.query_mode == 'efficient':
        pmids = exclude_already_downloaded_pmids(pmids)

    # Load meta data
    df_meta = pd.read_csv(
        f"data/meta/meta_{'_'.join(args.input_file.split('_')[1:])}", 
        index_col=0
    )

    # Print metrics of open acces (is_oa)
    print(f"{round(df_meta['is_oa'].value_counts()[True] / df_meta.shape[0] * 100, 2)}% ({df_meta['is_oa'].value_counts()[True]}/{df_meta.shape[0]}) are Open Access papers. (NOTE: the total here is from the 'meta_*.csv'. If this differs from the previous total, then these PMIDs were not found in the OpenAlex database.)")
    print(f"{round(df_meta['work_id'].isna().value_counts()[False] / df_meta['is_oa'].value_counts()[True] * 100, 2)}% ({df_meta['work_id'].isna().value_counts()[False]}/{df_meta['is_oa'].value_counts()[True]}) xml URLs are known.")

    # Create dict where pmid is key and work_id is value
    work_ids = df_meta.loc[
        ~df_meta['work_id'].isna(),            # Filter NaN away in column 'work_id'
        ['pmid','work_id']                     # Select 'pmid' and 'work_id'
    ].set_index('pmid').to_dict()['work_id']   # Set 'pmid' as index and turn pd.Series into a dictionary 
    # ].set_index('work_id').to_dict()['pmid']   # Set 'work_id' as index and turn pd.Series into a dictionary #TODO: REMOVE

    # Download xmls
    print("Trying to download listed work_ids")
    errors = get_xml_papers_from_url(work_ids, config["openalex_api_key"], args.query_mode)

    # error list to a pandas data frame
    df_errors = pd.DataFrame(errors[1:], columns= errors[0])

    # Save error report to file
    if df_errors.shape[0] > 1:
        Path("logs").mkdir(exist_ok = True)
        output_filename = f"logs/errors_meta2xml_{'_'.join(args.input_file.split('_')[1:])}"
        df_errors.to_csv(output_filename)
        print(f"Download error log is successfully written to '{output_filename}'")

    else:
        print("No error occurred when attempting to download xmls.")

    print("End of meta2xml.py")


# MAIN
if __name__ == "__main__":
    main()
