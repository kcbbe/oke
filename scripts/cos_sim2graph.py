
# import
import argparse
from pathlib import Path

import pickle
import numpy as np
import pandas as pd

import networkx as nx


# settings
# edge_threshold = 0.75
# similarity_file = "similarity_corpus_free_3600_250606.pickle"


# FUNTIONS
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

    parser.add_argument(
        "-t",
        dest = "threshold",
        type = float,
        help = "Provide the edge threshold. Only sentences with at least one similarity score equal or higher than this threshold is kept, and edges with lower similarity score than threshold are removed.",
    )

    return parser.parse_args()

def get_graph(similarity_scores: pd.DataFrame):
    """This function is computational expensive. It is advised to remove edges that have a lower similarity score than a certain threshold,
    before passing the similarity_scores dataframe to this function.
    The smaller the `scaler` the larger the distance between the nodes will be plot."""
    # Transform wide dataframe to long dataframe to make it compatible with networkx module
    similarity_scores = similarity_scores.reset_index()
    similarity_scores = pd.melt(similarity_scores, id_vars= ['index']).dropna(axis=0)
    similarity_scores = similarity_scores.rename(columns={"index": "source", "variable": "target", "value": "weight"})
    # TODO: remove edges that are the same (A-B and B-A) (ONLY IF IT IMPROVES COMPUTATIONAL TIME)

    G = nx.from_pandas_edgelist(
        similarity_scores,
        "source",
        "target",
        "weight"
    )
    print(G)

    return G


# MAIN
if __name__ == "__main__":
    print("Start of cos_sim2graph.py")

    # Collect arguments
    args = collect_arguments()

    # Load cosine similarity scores
    with open(f"data/vectors/{args.input_file}", 'rb') as handle:
        similarities = pickle.load(handle)



    # ### Remove duplets
    # # Get duplet dictionary
    # duplet_dict = get_duplets_clusters(
    #     get_duplets_dataframe(
    #         similarities,
    #         threshold= duplicate_threshold
    #     )
    # )

    # # Create a list with indexes on sentences with a duplet.
    # duplet_to_remove = [item for layer in duplet_dict.values() for item in layer]
    # print(f"Number of indexes to remove: {len(duplet_to_remove)}")

    # # get indexes of interest (all indexes - indexes to remove)
    # all_indexes = np.arange(similarities.shape[0])
    # vector_ids = np.delete(all_indexes, duplet_to_remove)

    # # Drop duplets from `similarity` (both rows and columns)
    # print(f"Similarities shape with duplets: {similarities.shape}")
    # similarities = delete_for_torch_tensor(similarities, duplet_to_remove, axis=0)
    # similarities = delete_for_torch_tensor(similarities, duplet_to_remove, axis=1)
    # print(f"Similarities shape without duplets: {similarities.shape}")


    ### Filter on edges that are equal to or larger than `threshold`
    # To similarity into a DataFrame 
    # and substract 2 from its own similarity score so that it is '-1' (=not equal in semantic meaning) instead of '1' (=equal).
    df_similarity_pre = pd.DataFrame(similarities - (np.identity(similarities.shape[0]) *2))

    # Get indexes of sentences above `threshold`
    idx_above_thres = df_similarity_pre[df_similarity_pre.max(axis=0) >= args.threshold].index.to_list()

    # Select only nodes that are assigned to a cluster
    similarity_weights = df_similarity_pre.iloc[idx_above_thres, idx_above_thres]

    print(f"Data compressed by {similarity_weights.shape[0] / similarities.shape[0]:.4f}")

    # Remove edge values with weights smaller than `threshold`
    similarity_weights[similarity_weights < args.threshold] = np.nan

    # Fraction of NaN in matrix
    print(f"Edge list compressed to {1-(similarity_weights.isna().sum().sum() / similarity_weights.shape[0] **2):.4f}")



    ### Get graph
    print('generate graph')

    G = get_graph(similarity_weights)
    print("created graph")


    ### Save Graph
    # Create `graphs` directory, if it does not yet exists.
    Path("data/graphs/").mkdir(exist_ok = True)


    # Save TODO: while building code
    # print(f'Start saving graph as "data/graphs/{save_filename}.pickle"')
    # with open(f"data/graphs/{save_filename}.pickle", "wb") as handle:
    #     pickle.dump(G, handle)
    # TODO: Remove block below and activate block above.
    print(f'Start saving graph as "/students/2022-2023/master/spacey/jennefer/master_thesis/graphs/graph_thres_{"_".join(str(args.threshold).split("."))}_{"_".join(args.input_file.split(".")[0].split("_")[1:])}.pickle"')
    with open(f'/students/2022-2023/master/spacey/jennefer/master_thesis/graphs/graph_thres_{"_".join(str(args.threshold).split("."))}_{"_".join(args.input_file.split(".")[0].split("_")[1:])}.pickle', "wb") as handle:
        pickle.dump(G, handle)


    # TODO: Try to get graph with gpu networkx
    # https://developer.nvidia.com/blog/accelerating-networkx-on-nvidia-gpus-for-high-performance-graph-analytics/

    # # Time spend on full data set >5.5 minutes and >40GB RAM
    # G = nx.from_pandas_edgelist(
    #     similarity_scores,
    #     "source",
    #     "target",
    #     "weight"
    # )
    # print(G)

    print("End of cos_sim2graph.py")
