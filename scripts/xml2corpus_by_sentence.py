
"""

https://github.com/TenWise-Dev/jrc-public/blob/main/lib/Tei2MaterialsMethods.py
"""

# IMPORTS
import argparse
from pathlib import Path
# from bs4 import BeautifulSoup
import bs4
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

def get_body(xml) -> list:
    """
    Extracts the body of the xml file.

    Returns:
        list: A list of all headers and paragraphs in the xml file.

    """
    # Load the xml file into BeautifulSoup
    soup = bs4.BeautifulSoup(xml, 'lxml-xml')
    
    # Get title and create a list to collect all headers and paragraphs
    title = soup.find('title')
    list_heads_and_paragraphs = [[title.name, title.next]]

    # Get all headers and paragraphs
    heads = soup.find_all('head')
    for head in heads:
        # head_and_para = [[head.next, el] for el in head.next_siblings if el.name == 'p']
        paragraphs = [el for el in head.next_siblings if el.name == 'p']
        list_heads_and_paragraphs.append([head.next, paragraphs])

    # Return the list of headers and paragraphs
    return list_heads_and_paragraphs

def clean_paragraphs(body: list) -> list:
    """
    Cleans the paragraphs by removing all references and turns bs4.element.Tag into strings.

    Args:
        body (list): A list of all headers and paragraphs in the xml file.

    Returns:
        list: A list of all headers and paragraphs in the xml file without references.

    """
    # Remove all references from the paragraph body and turn bs4.element.Tag into a string.
    

    # Iterate over the header list
    for i_body, element in enumerate(body):
        # Ignore the first element of the header, which is the title (and is already clean as a string)
        if isinstance(element[1], bs4.element.NavigableString):
            element[1] = element[1].text
        # If the element is a bs4.element.Tag, it is a header
        elif isinstance(element[1], list):
            # Iterate over the paragraphs in the header
            for i_el, el in enumerate(element[1]):
                if isinstance(el, bs4.element.Tag):
                    # Remove all references from the paragraph body
                    # https://stackoverflow.com/questions/39885359/beautifulsoup-decompose
                    for ref in el('ref'):
                        ref.decompose()

                # Update the paragraph in the body list
                body[i_body][1][i_el] = el.text

                # else:
                #     # If the element is not a bs4.element.Tag, it is already a string
                #     continue
    # Iterate over the body list and clean each paragraph


    # for i in range(len(body)):
    #     # Ignore the first element of the body, which is the title (and is already clean as a string)
    #     if isinstance(body[i][1], bs4.element.NavigableString):
    #         body[i][1] = body[i][1].text

    #     # elif isinstance(body[i][1], bs4.element.Tag):
    #     elif isinstance(body[i][1], list):
    #         for el in body[i][1]:
    #             if isinstance(el[i][1], bs4.element.Tag):
    #                 for ref in el[i][1]('ref'):
    #                     ref.decompose()
    #                 el[i][1] = el[i][1].text

    return body


# TODO: Collect header names of the xml file and plot their frequency


# MAIN
if __name__ == "__main__":
    print("Start of xml2corpus_by_sentence.py")

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
    Path("data/corpus/").mkdir(exist_ok = True)

    # # Collect header names of the xml file and plot their frequency
    # collect_header_names = pd.DataFrame(columns=["id", "header_name"])

    # For each id in selected_xml_papers (TODO: MULTIPROCESSING, and in a separate function)
    # Empty dataframe for collecting corpus
    df_corpus = pd.DataFrame(columns=["paper_id", "paper_name", "head_id", "head_name", "paragraph_id", "sentence_id", "sentence_text"])

    for id in selected_xml_papers:
        if Path(f"data/xml_papers/{id}.xml").exists():
        
            # Load xml file
            with open(f"data/xml_papers/{id}.xml", 'r', encoding="utf-8") as file:

                # Get the body of the xml file
                body = get_body(file)
                
                # # Remove all references from the paragraph body and turn bs4.element.Tag into a string.
                # # https://stackoverflow.com/questions/39885359/beautifulsoup-decompose
                body = clean_paragraphs(body)

                # Transform the body (list) into a dataframe
                df_body = pd.DataFrame(body, columns=['head_name', 'paragraphs'])

    #             # Add the head_id to the dataframe (TODO: Maybe groupby not needed)
    #             df_body['head_id'] = df_body.groupby(['head_name']).cumcount()

    #             # Explode the paragraphs into separate rows and add the paragraph_id to the dataframe
    #             df_body = df_body.explode(['paragraphs'])
    #             df_body['paragraph_id'] = df_body.groupby(['head_name']).cumcount()

    #             # Split the paragraph into sentences
    #             # https://stackoverflow.com/questions/12680754/split-explode-pandas-dataframe-string-entry-to-separate-rows
    #             # TODO: current regex is generated by copilot. It appears to be OK, but check it to be sure!
    #             df_body['sentence'] = df_body['paragraph'].str.split(r"(?<=[.!?]) +")
    #             df_body = df_body.explode(['sentence'])

    #             # test.iloc[1,1]

    #             print(body)

    #             # for i in range(len(body)):
    #             #     for ref in body[i][1]('ref'):
    #             #         try:
    #             #             ref.decompose()
    #             #         except TypeError:
    #             #             # The first element of the body is not a bs4.element.Tag but a string, thus it cannot be decomposed, thus it will throw this error
    #             #             continue



    #             # TODO: Check out what this code was about:
    #             # header_names = [header.next.lower() for header in headers if 'bs4.element.NavigableString' in str(type(header.next))]
    #             # ids = [id] * len(header_names)
    #             # # Create dataframe
    #             # df = pd.DataFrame({"id": ids, "header_name": header_names})
    #             # # Append to the dataframe
    #             # collect_header_names = pd.concat([collect_header_names, df], ignore_index=True)

    # # Save to csv
    # collect_header_names.to_csv(f"logs/headers_xml2corpus_by_sentence_{args.input_file}", index=False)

    #             # 

    #             # # Collect header names of the xml file and plot their frequency
    #             # for header in headers:
