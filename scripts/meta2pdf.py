"""Download full scientific PDFs by using column `pdf_urls` from the metadata CSV file.

This module downloads full scientific papers as PDF by using the URLs provided in the metadata CSV file for PMIDs.
After downloading, it reports which errors it encountered when failing to retrieve a PDF.

Usage:
   python meta2pdf.py -i pmids_in.csv -m efficient

Arguments:
    -i, --input_file
        Name of the input file, incl. its suffix.
    -m  --query_mode
        Query mode to use on OpenAlex. (default: 'efficient') Choose between 'efficient' or 'full' search. 'efficient' will only query PMIDs that are not present in destination folder, 'full' search will query all PMIDs provided in input file.

Input:
    A CSV file with at least one column header named 'pmid', were the values corresponds to its PubMed Identifier.
    A configuration file (config.yaml) is required. Please make sure the correct email address is in the configuration file (config.yaml).

Output:
    PDFs are downloaded to './data/pdf_papers/'.
    It reports which errors it encountered when failing to retrieve a PDF.

.. note::

    It is possible that the PDF file actually contains a different type of file. This will be reported as an error when parsing the PDFs with GROBID (see the next pipe pdf2xml.py).
"""

# IMPORTS
import argparse
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import pandas as pd

# FUNCTIONS
def collect_arguments() -> argparse.Namespace:
    """Collect arguments from the command line."""
    parser = argparse.ArgumentParser(
        description = __doc__,
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
        choices = ['efficient', 'full'],
        default = 'efficient'
    )

    return parser.parse_args()


def exclude_already_downloaded_pmids(pmids):
    """Exclude pmids of which the pdfs are already downloaded."""
    try:
        # Compare local pdfs with obtained pmids
        local_pdfs = {f.stem for f in Path("data/pdf_papers").iterdir() if f.suffixes[0] == ".pdf"}
        old_pmids = pmids
        # Exclude pmids that are already in the local pdf_directory
        pmids = list(set(pmids).difference(local_pdfs))
        # Report how many pmids are already in the local pdf_directory
        print(f"{round((len(old_pmids) - len(pmids)) / len(old_pmids) * 100, 2)}% ({len(old_pmids) - len(pmids)}/{len(old_pmids)}) papers are already found in the local pdf_directory.")

    except FileNotFoundError:
        print("WARNING: Did not find 'data/pdf_paper/' directory. If this is the first time running application that there is nothing to worry about. Else, check if set up is correct.")
        # Create `pdf_papers` directory, if it does not yet exists.
        Path("data/pdf_papers/").mkdir(exist_ok = True)

    return pmids


def get_pdf_papers_from_url(pdf_urls: dict):
    """Download pdf papers from pdf_urls.

    Take a dictionary of PMIDs and their corresponding PDF URLs as input,
    attempt to download the PDFs (if it does not already exists), and save them to './data/pdf_papers'.
    Collect error information of failed downloads.

    Args:
        pdf_urls (dict): PMID is key and pdf_url is value. For example: {'25461413': 'https://www.sciencedirect.com/... , ... }

    Returns:
        collect_errors (list): For example: [['pmid', 'error_code', 'error_message'], ['22420260', 403, 'Forbidden'], ...]
    """

    # Collect results
    collect_errors = [['pmid', 'error_code', 'error_message']]
    success_counter = 0
    success_session_counter = 0

    # Iterate
    for pdf_key in pdf_urls:

        # Check if file already in output folder
        if Path(f"data/pdf_papers/{pdf_key}.pdf").exists():
            success_counter += 1

        # Else, download the file and save as `key`
        else:
            # NOTE: Proof-of-Principle for using 'https://sci-hub.box/' for finding pdf_url proved successfull.
            # Tested with `pmid = 19270050`
            # 1) send a request for 'https://sci-hub.box/{doi}' {'https://sci-hub.box/10.1093/aje/kwp006'}
            # 2) in HTML of response (input_json['output'] in our case) search for 'src=' till '.pdf' {'https://moscow.sci-hub.box/3311/b17f96702a17d5ef66accdfaf05105ac/costello2009.pdf'}
            # 3) next response is the pdf!
            # NOTE: We should notify alexandra@dns.cymru and request if they are okay with us scraping their server.
            # NOTE: I'm unsure if this is ethical...

            # This should help to by pass bot checks
            req = Request(
                url = pdf_urls[pdf_key].replace(' ', '%20'), # Replace ' ' with '%20' in the URL if applicable.
                headers = {"User-Agent": "Mozilla/6.0"}
            )
            try:
                input_json = {"output" : urlopen(req).read()}

                # Save as pdf
                with open(f"data/pdf_papers/{pdf_key}.pdf", "wb") as output:
                    output.write(input_json["output"])

                success_counter += 1
                success_session_counter += 1

            except HTTPError as error:
                collect_errors.append([pdf_key, error.code, error.msg])

            except URLError as error:
                collect_errors.append([pdf_key, '404', error.reason.strerror])

    # Notify user where file is saved. and how many were saved (success_counter & len(collect_errors))
    print(f"{round(success_session_counter / len(pdf_urls) * 100, 2)}% ({success_session_counter}/{len(pdf_urls)}) papers are successful downloaded within this session.")
    print(f"{round(success_counter / len(pdf_urls) * 100, 2)}% ({success_counter}/{len(pdf_urls)}) papers were successful downloaded in total.")
    print("Please find the downloaded pdf's in 'data/pdf_papers/'")
    # return error log
    return collect_errors



def main():
    """Download full scientific papers in PDF.

    This function is the main entry point of the meta2pdf.py script.
    Collect arguments, retrieve PMIDs from the input file,
    exclude already downloaded PMIDs, retrieve PDF URLs from the meta data file, and download the PDFs.
    It also reports metrics and errors to log files.
    """
    print("Start of meta2pdf.py")

    # Collect arguments
    args = collect_arguments()

    # Load pmid file
    pmids = pd.read_csv(
        f'data/pmids/{args.input_file}',
    ).loc[:,"pmid"].to_list()

    # Convert pmids `int` to `str`
    pmids = [str(i) for i in pmids]

    # Exclude pmids of which the pdfs are already downloaded.
    if args.query_mode == 'efficient':
        pmids = exclude_already_downloaded_pmids(pmids)

    # Load meta data
    df_meta = pd.read_csv(
        f"data/meta/meta_{'_'.join(args.input_file.split('_')[1:])}", 
        index_col=0
    )

    # Print metrics of open acces (is_oa)
    print(f"{round(df_meta['is_oa'].value_counts()[True] / df_meta.shape[0] * 100, 2)}% ({df_meta['is_oa'].value_counts()[True]}/{df_meta.shape[0]}) are Open Access papers. (NOTE: the total here is from the 'meta_*.csv'. If this differs from the previous total, then these PMIDs were not found in the OpenAlex database.)")
    print(f"{round(df_meta['pdf_url'].isna().value_counts()[False] / df_meta['is_oa'].value_counts()[True] * 100, 2)}% ({df_meta['pdf_url'].isna().value_counts()[False]}/{df_meta['is_oa'].value_counts()[True]}) PDF URLs are known.")

    # Create dict where pmid is key and pdf_url is value
    pdf_urls = df_meta.loc[
        ~df_meta['pdf_url'].isna(),            # Filter NaN away in column 'pdf_url'
        ['pmid','pdf_url']                     # Select 'pmid' and 'pdf_url'
    ].set_index('pmid').to_dict()['pdf_url']   # Set 'pmid' as index and turn pd.Series into a dictionary

    # Download PDFs
    print("Trying to download listed PDF_URLs")
    errors = get_pdf_papers_from_url(pdf_urls)

    # error list to a pandas data frame
    df_errors = pd.DataFrame(errors[1:], columns= errors[0])

    # Save error report to file
    if df_errors.shape[0] > 1:
        Path("logs").mkdir(exist_ok = True)
        output_filename = f"logs/errors_meta2pdf_{'_'.join(args.input_file.split('_')[1:])}"
        df_errors.to_csv(output_filename)
        print(f"Download error log is successfully written to '{output_filename}'")

    else:
        print("No error occurred when attempting to download PDFs.")

    print("End of meta2pdf.py")


# MAIN
if __name__ == "__main__":
    main()
