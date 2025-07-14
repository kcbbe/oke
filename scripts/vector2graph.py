# import
import pickle
import numpy as np
import pandas as pd
import networkx as nx
from pathlib import Path

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

# select small sample size
print('generate graph')
# subset = 10000 # TODO: remove cap
# small = similarities[:subset, :subset].numpy()
# G = nx.to_networkx_graph(small)
G = nx.to_networkx_graph(similarities.numpy())

# Create `vectors` directory, if it does not yet exists.
Path("data/graphs/").mkdir(exist_ok = True)

print('start save')
# Save TODO: while building code
with open(f"data/graphs/{filename1.split('.')[0]}.pickle", "wb") as handle:
    pickle.dump(G, handle)

print("End")