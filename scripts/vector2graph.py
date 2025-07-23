# import
import pickle
import numpy as np
import pandas as pd
import networkx as nx
from pathlib import Path

from graspologic.partition import leiden
from graspologic.embed import LaplacianSpectralEmbed
from graspologic.utils import pass_to_ranks
from graspologic.layouts.colors import _get_colors
from umap import UMAP
from scipy.sparse import csr_array
from graspologic.plot import networkplot

import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib_venn import venn3

from sentence_transformers import SentenceTransformer, util
from sentence_transformers.cross_encoder import CrossEncoder
from sklearn.decomposition import NMF
from sklearn.cluster import AgglomerativeClustering

# Load a pretrained Sentence Transformer model
model_st = SentenceTransformer('NeuML/pubmedbert-base-embeddings')

# Multiple vector files
filename1 = 'no_lemma_applied_df_xml2corpus_by_sentence_pmid_free_3600_250606.pickle'
filename2 = 'nltk_df_xml2corpus_by_sentence_pmid_free_3600_250606.pickle'
filename3 = 'spacy_df_xml2corpus_by_sentence_pmid_free_3600_250606.pickle'
# filename.split('.')[0]
files = [filename1, filename2, filename3]

# Load vectors
vectors = {}
for file in files:
    with open(f"./data/vectors/{file}", 'rb') as handle:
        embeddings = pickle.load(handle)
        vectors[file.split("_")[0]] = embeddings

# Selected vector
embeddings = vectors['no']

# Get similarity scores (on cosine distance)
model_st.similarity_fn_name = "cosine"
similarities = model_st.similarity(embeddings, embeddings)

# Get graph
print('generate graph')


# ~~~~~~~~
# select small sample size
# subset = 1000
# similarities = similarities[:subset, :subset] # TODO: remove small sample and activate this line.
G = nx.to_networkx_graph(similarities.numpy()) 
# ~~~~~~~~

# Create `graphs` directory, if it does not yet exists.
Path("data/graphs/").mkdir(exist_ok = True)

# File name for saving
save_filename = f"{G.number_of_nodes()}_{filename1.split('.')[0]}"

# Save TODO: while building code
print(f'Start saving graph as "data/graphs/{save_filename}.pickle"')
with open(f"data/graphs/{save_filename}.pickle", "wb") as handle:
    pickle.dump(G, handle)

# Plot several plots

def tidy_node_df(node_comm_dict: dict) -> pd.DataFrame:
    df = pd.Series(node_comm_dict)
    df.index.name = "node_id"
    df.name = "community"
    df = df.to_frame().sort_index()
    return df

def plot_n_nodes_per_comm(df: pd.DataFrame, filename):
    df["community"].value_counts().plot(kind='bar')
    plt.xlabel('cluster_id')
    plt.ylabel('number of nodes')
    plt.title('number of nodes per cluster')
    plt.savefig(filename)
    plt.close()



# Plot several plots
thresholds = [0.75, 0.85, 0.90, 0.95]
plot_filepath = f"data/graphs/img_{save_filename}/"

print(f'Start plotting graphs with following thresholds: {thresholds}\nSaving to "{plot_filepath}"')

# Create `plot_filepath` directory, if it does not yet exists.
Path(plot_filepath).mkdir(exist_ok = True)

# ----
for thres in thresholds:

    clustered_graph = nx.to_networkx_graph([e for e in G.edges(data=True) if (e[2]['weight'] > thres) & (e[0] != e[1])])
    out_graph = leiden(clustered_graph)
    node_df = tidy_node_df(out_graph)
    plot_n_nodes_per_comm(node_df, f'{plot_filepath}n_nodes_per_comm_{str(thres).split(".")[1]}.png')

    # Size of each node in the layout relate to the number or strength of connections
    nodelist = node_df.index
    adj = nx.to_scipy_sparse_array(clustered_graph, nodelist=nodelist)

    node_df["strength"] = adj.sum(axis=1) + adj.sum(axis=0)
    node_df['rank_strength'] = node_df['strength'].rank(method='dense')

    # Graph embedding 
    # First LSE then UMAP
    n_components = 32 #adj.shape[0]
    
    try:
        lse = LaplacianSpectralEmbed(n_components=n_components, concat=True) # used in tutorial
        lse_embedding = lse.fit_transform(adj)
    except ValueError:
        print(f'An error occurred while thres = {thres}.\n`n_components` is now adjusted to `adj.shape[0] -1` == {adj.shape[0]}')
        n_components = adj.shape[0] - int(adj.shape[0] / 2)
        lse = LaplacianSpectralEmbed(n_components=n_components, concat=True) # used in tutorial
        lse_embedding = lse.fit_transform(adj)

    umap = UMAP(
        n_components= 2,
        n_neighbors= n_components,
        min_dist= 0.8,
        metric= "cosine",
    )
    umap_embedding = umap.fit_transform(lse_embedding)

    node_df["x"] = umap_embedding[:, 0]
    node_df["y"] = umap_embedding[:, 1]

    # Create a dictionary where each cluster_id gets an unique colour.
    colours = sns.color_palette("nipy_spectral", node_df["community"].nunique())
    palette = dict(zip(node_df["community"].unique(), colours))

    # Plot graph
    ax = networkplot(
        adj,
        node_data=node_df,
        x="x",
        y="y",
        node_size="rank_strength",
        node_sizes=(10, 80),
        node_hue="community",

        edge_linewidth=0.3,
        figsize=(20, 20),
        palette=palette,
        title = f"Cosine similarity with threshold of {thres}",
    )
    ax.axis("off")

    plt.savefig(f'{plot_filepath}graph_{str(thres).split(".")[1]}.png')
    plt.close()



print("End")
