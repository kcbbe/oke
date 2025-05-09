
"""

https://github.com/TenWise-Dev/jrc-public/blob/main/lib/Tei2MaterialsMethods.py
"""

# IMPORTS
import argparse
from pathlib import Path
from bs4 import BeautifulSoup
import yaml
import pandas as pd

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

def get_body(xml):
    """
    Extracts the body of the xml file.
    """
    soup = BeautifulSoup(xml, 'lxml-xml')
    namespaces = {"TEI": "http://www.tei-c.org/ns/1.0"}

    # body = soup.find('body')
    # if body is None:
    # # Collect error message
    #     raise ValueError("No body found in the XML file.")
    return soup.select_one("TEI|body", namespaces=namespaces)

# MAIN
if __name__ == "__main__":
    print("Start of xml2vector.py")

    # Collect arguments
    args = collect_arguments()

    # Load configuration file
    with open(args.config_file, 'r', encoding="utf-8") as stream:
        config = yaml.safe_load(stream)

    # Load pmid file
    pmids = pd.read_csv(
        f'data/pmids/{args.input_file}'
    ).loc[:,"pmid"].to_list()

    # Create set of selected_xml_papers
    all_xml_papers = {int(file.stem) for file in Path("data/xml_papers/").iterdir()}
    selected_xml_papers = set(pmids).intersection(all_xml_papers)

    # Create `vectors` directory, if it does not yet exists.
    Path("data/vectors/").mkdir(exist_ok = True)


    # For each id in selected_xml_papers (TODO: MULTIPROCESSING, and in a separate function)
    for id in selected_xml_papers:
        if Path(f"data/xml_papers/{id}.xml").exists():
        
            # Load xml file
            with open(f"data/xml_papers/{id}.xml", 'r', encoding="utf-8") as file:
                get_body(file)