"""Transforms corpus into a vector that is saved as a pickle.


"""


# IMPORTS
import argparse
from pathlib import Path
import pandas as pd
# import re
import pickle


from sentence_transformers import SentenceTransformer # SBERT
# https://github.com/MartinoMensio/spacy-sentence-bert

# universal-sentence-encoder This should be better than BERT? https://research.google/blog/advances-in-semantic-textual-similarity/
# https://github.com/MartinoMensio/spacy-universal-sentence-encoder

# bert roberta combi
# https://colab.research.google.com/github/keras-team/keras-io/blob/master/examples/nlp/ipynb/sentence_embeddings_with_sbert.ipynb

# pegasus

# sent2vect met spacy
# https://stackoverflow.com/questions/61133531/how-does-spacy-generate-vectors-for-phrases

# https://codesphere.com/articles/best-open-source-sentence-embedding-models

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

def preprocess_corpus_for_embedder(serie: pd.Series, replace_abbr : dict = None) -> list:
    """Pre-process sentences (in pd.Series) to a list of sentences that is ready for an embedder for sentence similarity analysis. 
    """
    # Replace abbreviated words (TODO: is this necessary though?)
    if isinstance(replace_abbr, dict):
        for k in replace_abbr.keys():
            # Replace `key` (e.g. "PD") with `value` (e.g. "parkinson disease").
            serie = serie.str.replace(k, replace_abbr[k], case= True)
    # Make all sentence_text lower case & remove puntuations & turn `serie` (pd.Series) into a list
    list_sentences = serie.str.lower().str.strip('\[.*?\]').values

    return list_sentences


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
        replace_abbr= {"PD": "parkinson's disease"}
    )
    # list_sentences = df['sentence_text'].values

    # Load pre-trained model
    if args.embedding_model == 'sbert':
        model = SentenceTransformer('NeuML/pubmedbert-base-embeddings')
        # model = SentenceTransformer('all-MiniLM-L6-v2')

    # Apply model to encode sentences
    # TODO: Placed limit while in testing phase
    # list_sentences = list_sentences[:1000]
    print(f"Start processing {list_sentences.shape[0]} sentences.")
    embeddings = model.encode(list_sentences)

    # Create `vectors` directory, if it does not yet exists.
    Path("data/vectors/").mkdir(exist_ok = True)

    # Save TODO: while building code
    with open(f"data/vectors/{args.input_file.split('.')[0]}.pickle", "wb") as handle:
        pickle.dump(embeddings, handle)
    
    # Add corpus_id to vector
    # corpus_id consist out of the following:
    # [paper_id, head_id, paragraph_id, sentence_id]
    # TODO: Does it matter from which corpus it came from? (if yes, then we need to take that into account as well)

    # Save as a pickle


    print("End of corpus2vector.py")
