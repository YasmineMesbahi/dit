Dans l'ordre d'utilisation:


summarize_corpus.py: produces a summary of a set of texts in the form of CDSs   

word2vec.py: creates file word_vectors.npy containing vector representations of each word from the vocabulary of the corpus

add_vect_cds: add vector embedding to cds(in neo4j graph) and store all vectors embedding in cdss_embeddings.npy and 2D projection in V.npy

add_kmeans_to_graph.py: add Kmeans to graph and find the cdss closest to the cluster centers

plot_clustering.py: plot clustering
