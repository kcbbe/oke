"""Process scientific TEI XML papers into a CSV file containing the corpus on sentence level.

This module processes the XML files into a corpus of sentences, extracting and cleaning the text, removes references, and splits the text into sentences.
The resulting corpus is saved as a CSV file to the 'data/corpus/' directory.

Code inspired by:
https://github.com/TenWise-Dev/jrc-public/blob/main/lib/Tei2MaterialsMethods.py

Usage:
    python xml2corpus_by_sentence.py -i pmids_in.csv

Arguments:
    -i, input_file
        Name of the input file containing PMIDs.

Input:
    A CSV file with a column header named 'pmid', where the values corresponds to its PubMed Identifier.

Output:
    An CSV output file is generated.

    Example:

    ```
    paper_id,paper_name,head_id,head_name,paragraph_id,sentence_id,sentence_text\n
    0,17900545,0,title,0,0,EPIGALLOCATECHIN GALLATE (EGCG) POTENTIATES...\n
    ...,\n
    ```

"""

# IMPORTS
import argparse
import re
from pathlib import Path
import bs4
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

    return parser.parse_args()

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
    list_heads_and_paragraphs = [[title.name, [title.next]]]

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

        # Iterate over the paragraphs in the header
        for i_el, el in enumerate(element[1]):
            # If the element is a bs4.element.Tag, it is a header
            if isinstance(el, bs4.element.Tag):
                # Remove all references from the paragraph body
                # https://stackoverflow.com/questions/39885359/beautifulsoup-decompose
                for ref in el('ref'):
                    ref.decompose()

            # Ignore the first element of the header, which is the title (and is already clean as a string)
            elif isinstance(element[1], bs4.element.NavigableString):
                pass

            # Update the paragraph in the body list
            body[i_body][1][i_el] = el.text

    return body

def flatten_body(body: list, paper_id: int, name: str) -> pd.DataFrame:
    """
    Flattens a nested list representing the body of a document into a pandas DataFrame with sentence-level granularity.
    Each entry in the input list should represent a section or heading with associated paragraphs. The function processes this structure to produce a DataFrame where each row corresponds to a single sentence, annotated with identifiers for the paper, heading, paragraph, and sentence.
    
    Args:
        body (list): A list of tuples or lists, where each element contains a heading name and a list of paragraphs.
        paper_id (int): Identifier of the paper.
        name (str): Name of the paper.

    Returns:
        pandas.DataFrame: A DataFrame with the following columns:
            - head_id: Index of the heading within the body.
            - head_name: Name of the heading or section.
            - paragraph_id: Index of the paragraph within the heading.
            - sentence_text: The text of the sentence.
            - sentence_id: Index of the sentence within the paragraph.
            - paper_name: Name of the paper (requires 'name' variable in scope).
            - paper_id: Identifier of the paper (requires 'id' variable in scope).
    Notes:
        - Sentences are split using a regular expression that matches sentence-ending punctuation followed by whitespace.
        - Rows with empty paragraphs are removed.

    Example input:
        body = [
            ['Introduction', ['This is the first sentence. This is the second sentence.', 'This is the third sentence.']],
            ['Methods', ['This is a method.']]
        ]
        paper_id = 1
        name = 'example_paper'
    Example output:
        head_id  head_name    paragraph_id  sentence_text                sentence_id paper_name    paper_id
        0        Introduction 0             This is the first sentence.  0           example_paper        0
        0        Introduction 0             This is the second sentence. 1           example_paper        0
        1        Methods      0             This is a method.            0           example_paper        0
    """

    # Transform the body (list) into a dataframe
    df_body = pd.DataFrame(body, columns=['head_name', 'paragraph'])

    # Remove rows with no paragraphs
    df_body.loc[df_body['paragraph'].map(len) < 1, 'paragraph'] = None
    df_body = df_body.dropna(subset=['paragraph'])

    # Reset index and add the head_id to the dataframe
    df_body = df_body.reset_index(drop=True)
    df_body = df_body.reset_index(names='head_id')

    # Explode the paragraphs into separate rows and add the paragraph_id to the dataframe
    df_body = df_body.explode(['paragraph'])
    df_body['paragraph_id'] = df_body.groupby(['head_name']).cumcount()

    # Split the paragraph into sentences, explode them into separate rows and add the sentence_id to the dataframe
    # https://stackoverflow.com/questions/12680754/split-explode-pandas-dataframe-string-entry-to-separate-rows

    ### Start of regex that was generated by co-pilot ###
    # Regex to split sentences, but avoid splitting after common
    # personal/academic titles (e.g., "Dr.", "Mr.", etc.) and general abbreviations (e.g., "e.g.", "i.e.")
    titles = (
        r"(?:Mr|Mrs|Ms|Dr|Drs|Ing|Prof|Sr|Jr|St|Mt|Messrs|Mmes|Mme|M|"
        r"Msgr|Rev|Fr|Col|Gen|Lt|Maj|Capt|Sgt|Cpl|Pvt|Adm|Cmdr|Ens|"
        r"Ave|Rd|Blvd|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)"
    )
    abbrevs = r"(?:e\.g|i\.e|etc|vs|cf|al|Fig|fig|Eq|eq|Ref|ref|No|no|ca|esp|approx|resp|inc|ex|viz|esp|esp\.|ibid|op\.cit|loc\.cit|ed|eds|vol|pp|ch|sec|suppl|supp|add|trans|anon|n\.d|n\.p|n\.pag|l\.c|s\.v|s\.v\.v|ff|ff\.|Co)"
    # The negative lookbehind must be fixed-width, so we cannot use
    # variable-width lookbehinds in Python's regex engine.
    # Instead, split at sentence-ending punctuation followed by whitespace
    # and a capital letter, then post-process to merge splits after titles or abbreviations.
    regex = r"(?<=[.!?])\s+(?=[A-Z])"
    df_body['sentence_text'] = df_body['paragraph'].str.split(regex)
    # Post-process to merge sentences that were split after known titles or abbreviations
    def merge_abbrev_splits(sentences):
        if not isinstance(sentences, list):
            return sentences
        merged = []
        skip_next = False
        for i, sent in enumerate(sentences):
            if skip_next:
                skip_next = False
                continue
            if i > 0:
                prev = sentences[i-1].strip()
                # Check if previous sentence ends with a known title or abbreviation
                if re.search(rf"\b({titles}|{abbrevs})\.$", prev):
                    merged[-1] = merged[-1] + " " + sent
                    skip_next = False
                    continue
            merged.append(sent)
        return merged
    df_body['sentence_text'] = df_body['sentence_text'].apply(merge_abbrev_splits)
    ### End of regex that was generated by co-pilot ###

    # Explode the sentences into separate rows
    df_body = df_body.explode(['sentence_text'])

    ### Start of regex that was generated by co-pilot ###
    # Remove extra whitespace from the sentences
    df_body['sentence_text'] = df_body['sentence_text'].str.replace(r'\s+', ' ', regex=True).str.strip()
    # Remove whitespace before a punctuation mark
    df_body['sentence_text'] = df_body['sentence_text'].str.replace(r'\s+([.,!?;:])', r'\1', regex=True)
    ### End of regex that was generated by co-pilot ###

    # Add the sentence_id to the dataframe
    df_body['sentence_id'] = df_body.groupby(['paragraph']).cumcount()
    # Drop the paragraph column
    df_body = df_body.drop(columns=['paragraph'])
    # Add the paper_name to the dataframe
    df_body['paper_name'] = name
    # Add the paper_id to the dataframe
    df_body['paper_id'] = paper_id
    # Remove rows with empty sentences (these contain '')
    df_body = df_body.loc[df_body['sentence_text'] != '']
    # Return the dataframe
    return df_body

def main():
    """Process scientific TEI XML papers into a CSV file containing the corpus on sentence level.

    This function is the main entry point of the xml2corpus_by_sentence.py script.
    It processes the XML files into a corpus of sentences, extracting and cleaning the text, removes references, and splits the text into sentences.
    The resulting corpus is saved as a CSV file to the 'data/corpus/' directory.
    """
    print("Start of xml2corpus_by_sentence.py")

    # Collect arguments
    args = collect_arguments()

    # Load pmid file
    pmids = pd.read_csv(
        f'data/pmids/{args.input_file}'
    ).loc[:,"pmid"].to_list()

    # Create set of selected_xml_papers
    all_xml_papers = {int(file.stem) for file in Path("data/xml_papers/").iterdir()}
    selected_xml_papers = set(pmids).intersection(all_xml_papers)

    # Print the number of selected xml papers
    print(f"Proportion of pmid papers that will be parsed: {round(len(selected_xml_papers) / len(pmids) * 100, 2)}% ({len(selected_xml_papers)}/{len(pmids)})")

    # Create `vectors` directory, if it does not yet exists.
    Path("data/corpus/").mkdir(exist_ok = True)

    # Empty dataframe for collecting corpus
    df_corpus = pd.DataFrame(columns=["paper_id", "paper_name", "head_id", "head_name", "paragraph_id", "sentence_id", "sentence_text"])

    # For each paper_id in selected_xml_papers
    for paper_id, name in enumerate(selected_xml_papers):
        if Path(f"data/xml_papers/{name}.xml").exists():

            # Load xml file
            with open(f"data/xml_papers/{name}.xml", 'r', encoding="utf-8") as file:
                # Get the body of the xml file
                body = get_body(file)

            # Clean the paragraphs
            body = clean_paragraphs(body)

            # Flatten the body to a dataframe
            df_body = flatten_body(body, paper_id, name)

            # Append the dataframe to the corpus dataframe
            df_corpus = pd.concat([df_corpus, df_body], ignore_index=True)

    # Save to csv
    df_corpus.to_csv(f"data/corpus/corpus_{'_'.join(args.input_file.split('_')[1:])}", index=False)
    print(f"Corpus dataframe is successfully written to 'data/corpus/corpus_{'_'.join(args.input_file.split('_')[1:])}'")

    print("End of xml2corpus_by_sentence.py")

# MAIN
if __name__ == "__main__":
    main()
