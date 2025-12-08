"""Create a networkx graph from a provided similarity matrix.

This module loads a pickled similarity matrix file ('similarity_*.pickle'), 
filters on edges with a similarity score equal or higher than provided edge threshold, 
removes duplicated sentences based on provided duplicates threshold, 
creates a networkx graph from the filtered similarity matrix,
and saves the graph as a pickled file.

Usage:
    python similarity2graph.py -i similarity_$full_exp_name.pickle -t 0.75 -d 1.0

Arguments:
    -i, --input_file
        Name of the input file containing the similarity matrix ('similarity_*.pickle').
    -t, --edge_threshold
        Edge threshold. Only sentences with at least one similarity score equal or higher than this threshold is kept, and edges with lower similarity score than threshold are removed.
    -d, --duplicates_threshold
        Duplicates threshold. Only one sentence is kept of duplicated sentences in the corpus.

Input:
    A pickled similarity matrix file ('similarity_*.pickle'). Where for each sentence per row the cosine similarity score is calculated for each sentence in columns.

Output:
    A pickled networkx graph file ('graph_thres_<edge_threshold>_<full_exp_name>.pickle').
"""


# IMPORTS
import argparse
from pathlib import Path

import pickle
import numpy as np
import pandas as pd

import torch
import networkx as nx


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
        help = "Provide the name of the input file ('similarity_*.pickle').",
    )

    parser.add_argument(
        "-t",
        dest = "edge_threshold",
        type = float,
        required = True,
        default = 0.75,
        help = "Provide the edge threshold. Only sentences with at least one similarity score equal or higher than this threshold is kept, and edges with lower similarity score than threshold are removed.",
    )

    parser.add_argument(
        "-d",
        dest = "duplicates_threshold",
        type = float,
        default = 1.0,
        help = "Provide the duplicates threshold. Only one sentence is kept of duplicated sentences in the corpus.",
    )

    return parser.parse_args()

def get_duplicates_dataframe(similarity_matrix: torch.Tensor, threshold: float) -> pd.DataFrame:
    """Return a similarity dataframe that only contains duplicates, 
    where duplicates are defined as sentences with a similarity score equal or higher than provided threshold."""
    # Substract 2 from the similarity score that matched itself, so that it turns the value to -1.
    df_duplicates = pd.DataFrame(
        np.subtract(
            similarity_matrix,
            np.identity(similarity_matrix.shape[0]) *2
        )
    )

    # Drop columns and rows without duplicates (defined by the threshold)
    df_duplicates = df_duplicates[df_duplicates >= threshold].dropna(axis=0, how='all')
    df_duplicates = df_duplicates[df_duplicates >= threshold].dropna(axis=1, how='all')

    # if df_duplicates is empty (and therefore there are no duplicates)
    if len(df_duplicates.index) == 0:
        # raise an error
        raise ValueError("No duplicates found in provided pd.DataFrame!")

    return df_duplicates

def get_duplicates_clusters(df_duplicates: pd.DataFrame) -> dict:
    """Return a dictionary where the kept 'unique sentence index' (=key) references to the duplicate index in a list (=values)."""
    # Create a dict with indexes on sentences with a duplicate.
    potential_duplicates = df_duplicates.index
    duplicate_dict = {}

    # Iterate over potential duplicates list
    while len(potential_duplicates) != 0:

        # Look at first item
        idx = potential_duplicates[0]

        # For idx in list, find other idx that have same sentence.
        cluster = df_duplicates.loc[idx, ~df_duplicates.loc[idx].isna()].index

        # Store 'unique' idx in as key, and store 'duplicate' idx as values
        duplicate_dict[idx] = cluster.to_list()

        # Remove duplicate index and first item from potential_duplicates. (This will shorten the loop)
        potential_duplicates = potential_duplicates[~potential_duplicates.isin(cluster)]
        potential_duplicates = potential_duplicates[1:]

    return duplicate_dict

def delete_for_torch_tensor(x: torch.Tensor, row_exclude, axis: int = 0) -> torch.Tensor:
    """Return a new torch.Tensor with sub-arrays along a provided axis deleted.
    
    Parameters:
        x (torch.Tensor): Input tensor.

        row_exclude (list) : slice, array-like of ints or bools
        Indicate indices of sub-arrays to remove along the specified axis.

        axis (int): default = 0
        The axis along which to delete the subarray defined by row_exclude. 
    """
    # get indexes of interest (all indexes - indexes to remove)
    all_indexes = np.arange(x.shape[axis])
    indexes_of_interest = np.delete(all_indexes, row_exclude)

    # select rows and columns of interest (thus removing `indexes to remove`)
    if axis == 0:
        x = x[indexes_of_interest]
    if axis == 1:
        x = x[:, indexes_of_interest]

    return x

def remove_duplicates(similarity_matrix: pd.DataFrame, dupli_dict: dict) -> pd.DataFrame:
    """Return a similarity matrix (pd.DataFrame) without duplicates based on provided duplicate dictionary."""
    # Create a flat list with indexes on sentences with a duplicate.
    duplicate_to_remove = [item for layer in dupli_dict.values() for item in layer]
    print(f"Number of indexes to remove: {len(set(duplicate_to_remove))}")

    # Drop duplicates from `similarity` (both rows and columns)
    print(f"Similarities shape with duplicates: {similarity_matrix.shape}")
    # similarity_matrix = delete_for_torch_tensor(similarity_matrix, duplicate_to_remove, axis=0)
    # similarity_matrix = delete_for_torch_tensor(similarity_matrix, duplicate_to_remove, axis=1)

    similarity_matrix.drop(duplicate_to_remove, axis=0, inplace=True)
    similarity_matrix.drop(duplicate_to_remove, axis=1, inplace=True)

    print(f"Similarities shape without duplicates: {similarity_matrix.shape}")

    return similarity_matrix

def save_duplicate_dict(dupli_dict: dict, filename: str):
    """Save duplicate dictionary as .csv file."""
    # Save `duplicate_dict` as .csv
    # (This is important, because if the 'duplicate' is a hit, we need to find it back in the corpus. Also if the hit occurs multiple times in the corpus.)
    # Create `duplicates` directory, if it does not yet exists.
    Path("data/vectors/duplicates").mkdir(exist_ok = True)

    df_duplicate_dict = pd.DataFrame(
        dupli_dict.values(),
        index= dupli_dict.keys(),
    )
    df_duplicate_dict.index.name = "kept"
    df_duplicate_dict.to_csv(f"data/vectors/duplicates/{filename}.csv")
    print(f"Duplicate dictionary was been saved to '{f'data/vectors/duplicates/{filename}.csv'}'")

def filter_similarity_matrix(matrix: torch.Tensor, edge_threshold: float, ) -> pd.DataFrame:
    """Return a compressed similarity matrix (pd.DataFrame) where only sentences with at least one similarity score equal or higher than `edge_threshold` is kept, and edges with lower similarity score than `edge_threshold` are removed (set to NaN)."""
    ### Filter on edges that are equal to or larger than `threshold`
    # To similarity into a DataFrame
    # and substract 2 from its own similarity score so that it is '-1' (=not equal in semantic meaning) instead of '1' (=equal).
    df_similarity_pre = pd.DataFrame(matrix - (np.identity(matrix.shape[0]) *2))

    # Get indexes of sentences above `threshold`
    idx_above_thres = df_similarity_pre[df_similarity_pre.max(axis=0) >= edge_threshold].index

    # Select only nodes that are assigned to a cluster
    similarity_weights = df_similarity_pre.loc[idx_above_thres, idx_above_thres]

    print(f"Data filtered to {similarity_weights.shape[0] / matrix.shape[0]:.4f}")

    # Remove edge values with weights smaller than `threshold`
    similarity_weights[similarity_weights < edge_threshold] = np.nan

    # Fraction of NaN in matrix
    temp = ~similarity_weights.isna()
    print(f"Edge list ({temp.sum().sum()}) filtered to {temp.sum().sum() / similarity_weights.shape[0] **2:.4f}")

    return similarity_weights

def get_graph(similarity_scores: pd.DataFrame):
    """This function is computational expensive. It is advised to remove edges that have a lower similarity score than a certain threshold,
    before passing the similarity_scores dataframe to this function."""
    # Transform wide dataframe to long dataframe to make it compatible with networkx module
    similarity_scores = similarity_scores.reset_index()
    similarity_scores = pd.melt(similarity_scores, id_vars= ['index']).dropna(axis=0)
    similarity_scores = similarity_scores.rename(columns={"index": "source", "variable": "target", "value": "weight"})

    # Create graph (on CPU power)
    G = nx.from_pandas_edgelist(
        similarity_scores,
        "source",
        "target",
        "weight"
    )
    print(G)

    return G

def main():
    """Create a networkx graph from a provided similarity matrix.

    This function is the main entry point of the similarity2graph.py script.
    It loads a pickled similarity matrix file ('similarity_*.pickle'), 
    filters on edges with a similarity score equal or higher than provided edge threshold, 
    removes duplicated sentences based on provided duplicates threshold, 
    creates a networkx graph from the filtered similarity matrix,
    and saves the graph as a pickled file.
    """
    print("Start of similarity2graph.py")

    # Collect arguments
    args = collect_arguments()

    # Load similarity scores
    with open(f"data/vectors/{args.input_file}", 'rb') as handle:
        similarities = pickle.load(handle)

    # Remove duplicates from similarity score,
    # and save a dictionary with removed sentences.
    try:
        duplicate_dict = get_duplicates_clusters(
            get_duplicates_dataframe(
                torch.round(similarities, decimals=4), # similarities is round to 4 decimals to compensate float point errors.
                threshold= args.duplicates_threshold
            )
        )

        # # similarities as Tensor
        # similarities = remove_duplicates(
        #     similarities,
        #     duplicate_dict,
        # )

        # similarities as pd.DataFrame
        similarities = remove_duplicates(
            pd.DataFrame(similarities),
            duplicate_dict,
        )

        # Save `duplicate_dict` as .csv
        save_duplicate_dict(
            duplicate_dict,
            f"dict_{'_'.join(args.input_file.split('_')[1:]).split('.', maxsplit=1)[0]}"
        )
        # TODO: print where dict was saved to

    except ValueError:
        print("WARNING: A ValueError was raised. If the error is: 'No duplicates found in provided pd.DataFrame!', then there is no worries and the script will continue without any problems.")

    # Filter on edges that are equal to or larger than `edge_threshold`
    similarity_weights = filter_similarity_matrix(
        similarities,
        args.edge_threshold
    )

    # Get graph
    print('Create graph')
    G = get_graph(similarity_weights)
    print("Successfully created graph")

    # Save Graph
    # Create `graphs` directory, if it does not yet exists.
    Path("data/graphs/").mkdir(exist_ok = True)

    # Save graph
    print(f"Start saving graph as 'data/graphs/graph_thres_{'_'.join(str(args.edge_threshold).split('.'))}_{'_'.join(args.input_file.split('.')[0].split('_')[1:])}.pickle'")
    with open(f"data/graphs/graph_thres_{"_".join(str(args.edge_threshold).split("."))}_{"_".join(args.input_file.split(".")[0].split("_")[1:])}.pickle", "wb") as handle:
        pickle.dump(G, handle)

    print(f"Graph is successfully written to 'data/graphs/graph_thres_{'_'.join(str(args.edge_threshold).split('.'))}_{'_'.join(args.input_file.split('.')[0].split('_')[1:])}.pickle'")
    print("End of similarity2graph.py")


# MAIN
if __name__ == "__main__":
    main()
