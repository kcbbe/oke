
# IMPORTS
import argparse
import requests
from pathlib import Path
import yaml
import pandas as pd

def get_xml_from_pdf_papers(servername: str, portnumber: str, pmid: str):
            
    collect_errors = []


    with open(f"data/pdf_papers/{id}.pdf", "rb") as input:
        input_json = {"input": input.read()}

    response = requests.post(
        f'http://{servername}:{portnumber}/api/processFulltextDocument',
        files = input_json,
        timeout = 30
    )

    if response.status_code == 200:
    # TODO: monitor response.status_code
        with open(f"data/xml_papers/{id}.xml", "w") as output:
            output.write(response.text)

    else:
        collect_errors.append([pmid, response.status_code])
        # TODO: How to report errors? 
        error_code_to_text = {
            204: "Process was completed, but no content could be extracted and structured",
            400: "Wrong request, missing parameters, missing header",
            500: "Indicate an internal service error, further described by a provided message",
            503: "The service is not available, which usually means that all the threads are currently used"
        }
        # See here what the code means: https://grobid.readthedocs.io/en/latest/Grobid-service/#apiprocessfulltextdocument

    # TODO: notify user where file is saved. and how many were saved (len(collect_errors))
    if len(collect_errors) == 0:
        print("No errors occurred!")
    else:
        print(f"Error(s) occurred: {collect_errors}")

    # return error log
    return collect_errors

# MAIN
if __name__ == "__main__":
    print("Start of pdf2xml.py")

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

    # Create `xml_papers` directory, if it does not yet exists.
    Path("data/xml_papers/").mkdir(exist_ok = True)

    for id in pmids:
        if Path(f"data/xml_papers/{id}.xml").exists():
            # xml paper version for this `id` is already available on local drive.
            pass
        elif Path(f"data/pdf_papers/{id}.pdf").exists():
            # pdf needs to be transformed to xml.
            errors = get_xml_from_pdf_papers(
                servername = config["grobid_servername"],
                portnumber = config["grobid_portnumber"],
                pmid = id
            )
        else:
            # No paper was obtained for this `id`.
            pass

    # TODO: report `errors`
    print("End of pdf2xml.py")
