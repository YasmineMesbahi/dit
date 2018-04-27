mrtoneo4j
« Machine Reading to Neo4j » permet de transformer les sorties JSON de la Machine Reading de Synapse Développement en graphe Neo4j.

baseline,Kmeans  et Sumbasic sont les trois methodes implementé pour générer des résumé 


Baseline:

1)On fait appel à la machine reading sur le corpus(cluster de doc) pour
avoir la liste des CDS(propositions) de ce corpus.

2) On stock tous les cds dans le base de donné sous forme de graphe
Neo4j.

3) On cherche tous les cds qui ont le meme sujet, verb, objet et on crée
une relation entre eux. Ces cds constituent un ensemble des informations
rendundants.

Kmeans: 

Projection dans l’espace vectoriel les cds et appliquer l’algorithme de kmeans sur l’ensemble des vecteurs qui rappresent les cds.

Sumbasic: SumBasic est un système développé pour opérationnaliser l’idée d’utiliser la fréquence pour la sélection des phrases. Il ne repose que sur la probabilité des mots pour calculer l’importance. C’est un systeme de résumé qui utilise un composant de sélection de phrases basée sur la fréquence, avec un composant pour re-pondérer les probabilités du mot afin de minimiser la redondance.

Comression rate: calcul le ratio de compression (combien plus court est le résumé par rapport à le text original) 