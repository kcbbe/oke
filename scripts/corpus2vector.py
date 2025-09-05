"""Transforms corpus into a vector that is saved as a pickle.


"""


# IMPORTS
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer # SBERT

# FUNCTIONS
def collect_arguments() -> argparse.Namespace:
    """Collect arguments from the command line."""
    parser = argparse.ArgumentParser(
        description = __doc__,
    )
    
    parser.add_argument(
        "-m",
        dest = "embedding_model",
        required = True,
        help = "Provide the name of the embedding model.",
        choices = ["sbert", "bow", "tf-idf", "transformer"],
        default = "sbert"
    )

    parser.add_argument(
        "-i",
        dest = "input_file",
        required = True,
        help = "Provide the name of the input file.",
    )

    return parser.parse_args()

def preprocess_corpus_for_embedder(serie: pd.Series, replace_abbr : dict = None) -> np.array:
    """Pre-process sentences (in pd.Series) to a list of sentences that is ready for an embedder."""
    # Replace abbreviated words (TODO: is this necessary though?)
    if isinstance(replace_abbr, dict):
        for k in replace_abbr.keys():
            # Replace `key` (e.g. "PD") with `value` (e.g. "parkinson's disease").
            serie = serie.str.replace(k, replace_abbr[k], case= True)

    # Make all sentence_text lower case & remove punctuations & turn `serie` (pd.Series) into a list
    list_sentences = serie.str.lower().str.strip('\[.*?\]').values

    return np.array(list_sentences)

# def main():
#     """
#     Needs an docstring
#     """

# MAIN
if __name__ == "__main__":
    print("Start of corpus2vector.py")

    # Collect arguments
    args = collect_arguments()

    # Load the input file
    df = pd.read_csv(
        f"data/corpus/{args.input_file}"
    )

    # Get input data into correct shape for the embedder
    list_sentences = preprocess_corpus_for_embedder(
        df['sentence_text'],
        replace_abbr= {"PD": "parkinson's disease"} # TODO: make this variable for the user to input? # NOTE: if PD is part of a longer abbreviation, like COPD, then this method has a problem..
    )

    # Load pre-trained model
    if args.embedding_model == 'sbert':
        model = SentenceTransformer('NeuML/pubmedbert-base-embeddings') # TODO: make this variable for when an new/better pretrained model becomes available

    # Apply model in order to encode sentences
    print(f"Start processing {list_sentences.shape[0]} sentences.")
    embeddings = model.encode(list_sentences)
    # TODO: multiprocessing: https://github.com/UKPLab/sentence-transformers/blob/master/examples/sentence_transformer/applications/computing-embeddings/computing_embeddings_multi_gpu.py

    # Create `vectors` directory, if it does not yet exists.
    Path("data/vectors/").mkdir(exist_ok = True)

    # Save the embeddings
    with open(f"data/vectors/embedding_{args.input_file.split('.')[0]}.pickle", "wb") as handle:
        pickle.dump(embeddings, handle)
    
    # Calculate cosine similarity scores
    model.similarity_fn_name = "cosine"
    similarities = model.similarity(embeddings, embeddings)

    # Save the similarity scores
    with open(f"data/vectors/similarity_{args.input_file.split('.')[0]}.pickle", "wb") as handle:
        pickle.dump(embeddings, handle)

    print("End of corpus2vector.py")
