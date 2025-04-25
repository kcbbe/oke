"""
Reads pmids from the 'experiment' csv file,
Checks if the corresponding pdf files are available in the `data/pdf_papers/` directory,
If the pdf files are available, it checks if the corresponding xml files are already available in the `data/xml_papers/` directory.
If the xml files are not available, it process the pdf files into xml files using the GROBID server.
"""
# work on error reporting


# IMPORTS
import argparse
from pathlib import Path
import requests
import yaml
import pandas as pd

def get_xml_from_pdf_papers(servername: str, portnumber: str, pmid: str):
    # TODO: docstring
    """
    Transforms a single pdf into a single xml

    Args:
        servername (str): The name of the server where GROBID is running.
        portnumber (str): The port number where GROBID is running.
        pmid (str): The pmid of the paper to be transformed.

    Returns:
        collect_errors (list): A list of errors that occurred during the transformation.
    """
    

    # Read pdf
    with open(f"data/pdf_papers/{id}.pdf", "rb") as input:
        input_json = {"input": input.read()}

    # Let GROBID process pdf into xml
    response = requests.post(
        f'http://{servername}:{portnumber}/api/processFulltextDocument',
        files = input_json,
        timeout = 30
    )

    # Check if the response is successful and save the xml file
    if response.status_code == 200:
        with open(f"data/xml_papers/{id}.xml", "w") as output:
            output.write(response.text)

    # if the response is not successful return the error code
    else:
        # See here what the code means: https://grobid.readthedocs.io/en/latest/Grobid-service/#apiprocessfulltextdocument
        error_code_to_text = {
            204: "Process was completed, but no content could be extracted and structured",
            400: "Wrong request, missing parameters, missing header",
            500: "Indicate an internal service error, further described by a provided message",
            503: "The service is not available, which usually means that all the threads are currently used"
        }

        collect_errors = [
            pmid,
            response.status_code,
            error_code_to_text.get(response.status_code, "Error code not included in error_code_to_text dictionary"),
            response.text
        ]

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
        "-i",
        dest = "input_file",
        required = True,
        help = "Provide the name of the input file.",
    )

    args = parser.parse_args()

    return args

# MAIN
if __name__ == "__main__":
    print("Start of pdf2xml.py")

    # Collect arguments
    args = collect_arguments()

    # # Collect arguments
    # parser = argparse.ArgumentParser(
    #     description = __doc__,
    #     # formatter_class = argparse.RawDescriptionHelpFormatter
    # )
    # parser.add_argument(
    #     "-c",
    #     dest = "config_file",
    #     required = True,
    #     help = "Provide path to the configuration file (default: 'config.yaml')",
    #     default = "config.yaml"
    # )
    # args = parser.parse_args()

    # Load configuration file
    with open(args.config_file, 'r', encoding="utf-8") as stream:
        config = yaml.safe_load(stream)

    # Load pmid file
    pmids = pd.read_csv(
        f'data/pmids/{args.input_file}'
    ).loc[:,"pmid"].to_list()

    # Create `xml_papers` directory, if it does not yet exists.
    Path("data/xml_papers/").mkdir(exist_ok = True)


# TODO: Check if GROBID is running
# if http://assemblix:8670/api/isalive == 'true':
# else:
# try: to start up GROBID via bash/sys`docker run --rm --init --ulimit core=0 -p 8670:8070 lfoppiano/grobid:0.8.1`
# except: error, sys.exit()


    # For each pmid (TODO: MULTIPROCESSING)
    total_metrics = [["xml_count", "pdf_count", "none_count"], [0, 0, 0]]
    errors = [["pmid", "error_code", "error_text", "error_message"]]

    for id in pmids:
        if Path(f"data/xml_papers/{id}.xml").exists():
            # xml paper version for this `id` is already available on local drive.
            total_metrics[1][0] += 1
            pass

        elif Path(f"data/pdf_papers/{id}.pdf").exists():
            # pdf needs to be transformed to xml.
            err = get_xml_from_pdf_papers(
                servername = config["grobid_servername"],
                portnumber = config["grobid_portnumber"],
                pmid = id
            )

            # append the list of errors
            if err is not None:
                errors.append(err)

            total_metrics[1][1] += 1

        else:
            # No paper was obtained for this `id`.
            total_metrics[1][2] += 1
            pass

    # Report total_metrics
    print("Total overview:")
    print(f"Ideally, {len(pmids)} pmids should be processed")
    print(f"Proportion of pmids missing an xml file and pdf files: {round(total_metrics[1][2] / len(pmids) * 100, 2)}% ({total_metrics[1][2]}/{len(pmids)})")
    print(f"Proportion of already existing xml files: {round(total_metrics[1][0] / len(pmids) * 100, 2)}% ({total_metrics[1][0]}/{len(pmids)})")
    print(f"Proportion of pdf files attempted to be transformed into xml files: {round(total_metrics[1][1] / len(pmids) * 100, 2)}% ({total_metrics[1][1]}/{len(pmids)})")
    # print(f"Total metrics: {total_metrics[1][0]} xml files, {total_metrics[1][1]} pdf files, {total_metrics[1][2]} none files")

    # Report errors
    if len(errors) > 1:
        print(f"Proportion of successful transformations: {round((total_metrics[1][1] - (len(errors) - 1))/ total_metrics[1][1] * 100, 2)}% ({total_metrics[1][1] - (len(errors) - 1)}/{total_metrics[1][1]})")
        # print(f"Number of errors during 'pdf to xml' transformation: {len(errors) - 1}")
        # print(f"Number of successful transformations: {total_metrics[1][1] - (len(errors) - 1)}")

        # Save error report to file
        output_file_name = f"logs/errors_pdf2xml_{args.input_file}"
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
        print("All pdf files were successfully transformed into xml files. No errors occurred.")

    print("End of pdf2xml.py")

# How to parse TEI:
# For next https://github.com/TenWise-Dev/jrc-public/blob/main/lib/Tei2MaterialsMethods.py
