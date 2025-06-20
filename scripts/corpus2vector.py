"""Transforms corpus into a vector that is saved as a pickle.


"""


# IMPORTS
import argparse
from pathlib import Path
import pandas as pd

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
        choices = ["sent2vec", "bow", "tf-idf", "transformer"],
        default = "sent2vec"
    )

    parser.add_argument(
        "-i",
        dest = "input_file",
        required = True,
        help = "Provide the name of the input file.",
    )

    return parser.parse_args()


def main():
    """
    Needs an docstring
    """

# MAIN
if __name__ == "__main__":
    print("Start of corpus2vector.py")

    # Collect arguments
    args = collect_arguments()

    # Load the input file
    df = pd.read_csv(
        f"data/corpus/{args.input_file}"
    )


    print("End of corpus2vector.py")
