"""Transform a sentence-based corpus into vectors and calculate similarity scores.

This module embeds a sentence-based corpus by transforming it into vectors with SBERT and calculate cosine similarity scores between the sentence vectors.
Both the embedded sentences and cosine similarity scores are saved as a pickle.
  
Usage:
    python corpus_by_sentence2vector.py -i corpus_free_3600_250606.csv -m NeuML/pubmedbert-base-embeddings
  
Arguments:
    -c, --config_file
        Path to the configuration file (default: 'config.yaml')
    -i, --input_file
        Name of the input file containing the corpus. The column name containing the sentences should be "sentence_text".
    -m, --sbert_model
        Name of an SBERT supported model. (default: 'NeuML/pubmedbert-base-embeddings') For other models, see https://huggingface.co/models?library=sentence-transformers&sort=trending&search=pubmed
    
Input:
    A CSV file with a column header named 'sentence_text', where each row contains a single sentence.

Output:
    Two pickled matrixes:
    1) [embedding_*.pickle] Where each sentence per row is represented by an n-dimensional vector in columns.
    2) [similarity_*.pickle] Where for each sentence per row the cosine similarity score is calculated for each sentence in columns.
"""


# IMPORTS
import argparse
from pathlib import Path
import pickle
import yaml
import pandas as pd
from pandas.errors import EmptyDataError
import numpy as np
from sentence_transformers import SentenceTransformer


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
        dest = "sbert_model",
        default = 'NeuML/pubmedbert-base-embeddings',
        help = "Provide the name of the SBERT transformer model.",
    )

    return parser.parse_args()

def csv_to_dict(path_to_csv: str) -> dict:
    """Read csv and transform it into a dictionary where the first column will be the key and the second column the value."""
    df = pd.read_csv(path_to_csv, header= None, index_col= 0)

    return df[1].to_dict()

def preprocess_corpus_for_embedder(serie: pd.Series, replace_abbr: dict = None) -> np.array:
    """Pre-process sentences (in pd.Series) to a list of sentences that is ready for an embedder."""
    # Replace abbreviated words
    if isinstance(replace_abbr, dict):
        for k in replace_abbr.keys():
            # Replace `key` (e.g. "PD") with `value` (e.g. "parkinson's disease").
            serie = serie.str.replace(k, replace_abbr[k], case= True)

    # Make all sentence_text lower case & remove punctuations & turn `serie` (pd.Series) into a list
    list_sentences = serie.str.lower().str.strip('[].,;:*?!\\/').values

    return np.array(list_sentences)

def main():
    """Transform a sentence-based corpus into vectors and calculate similarity scores.

    This function is the main entry point of the corpus_by_sentence2vector.py script.
    It embeds a sentence-based corpus by transforming it into vectors with SBERT and calculate cosine similarity scores between the sentence vectors.
    Both the embedded sentences and cosine similarity scores are saved as a pickle.
    """
    print("Start of corpus_by_sentence2vector.py")

    # Collect arguments
    args = collect_arguments()

    # Load the input file
    df = pd.read_csv(
        f"data/corpus/{args.input_file}"
    )

    # Load pre-trained model
    model = SentenceTransformer(args.sbert_model)

    # Load configuration file
    with open(args.config_file, 'r', encoding="utf-8") as stream:
        config = yaml.safe_load(stream)

    # Load expected abbreviations in text
    try:
        dict_abbr = csv_to_dict(config["path_to_abbr"])
    except EmptyDataError:
        print("WARNING: Provided CSV with abbreviations appears to be empty. If this is correct, then there's no worries.")
        dict_abbr = None
    except FileNotFoundError:
        print(f"WARNING: Provided CSV with abbreviations was not found! If this is correct, then there's no worries. If it failed, check the config file if path is correct. The script will continue without correction. Current script is executed from {Path.cwd()}")
        dict_abbr = None

    # Get input data into correct shape for the embedder
    # NOTE: This step is not really needed, though I think it will reduce the 'noise' in the data.
    list_sentences = preprocess_corpus_for_embedder(
        df['sentence_text'],
        replace_abbr= dict_abbr # NOTE: if PD is part of a longer abbreviation, like COPD, then this method has a problem..
    )

    # Embed sentences
    print(f"Start processing {list_sentences.shape[0]} sentences.")
    embeddings = model.encode(
        list_sentences,
        device= ["cuda:0"] # NOTE: Currently single gpu. See following for multiprocessing: https://www.sbert.net/examples/sentence_transformer/applications/computing-embeddings/README.html#multi-process-multi-gpu-encoding
    )

    # Create `vectors` directory, if it does not yet exists.
    Path("data/vectors/").mkdir(exist_ok = True)

    # Save the embeddings
    with open(f"data/vectors/embedding_{'_'.join(args.input_file.split('.')[0].split('_')[1:])}.pickle", "wb") as handle:
        pickle.dump(embeddings, handle)

    # Calculate cosine similarity scores
    model.similarity_fn_name = "cosine"
    similarities = model.similarity(embeddings, embeddings)

    # Save the similarity scores
    with open(f"data/vectors/similarity_{'_'.join(args.input_file.split('.')[0].split('_')[1:])}.pickle", "wb") as handle:
        pickle.dump(similarities, handle)

    print("End of corpus_by_sentence2vector.py")


# MAIN
if __name__ == "__main__":
    main()
