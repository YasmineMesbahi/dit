mrtoneo4j
� Machine Reading to Neo4j � permet de transformer les sorties JSON de la Machine Reading de Synapse D�veloppement en graphe Neo4j.

baseline,Kmeans  et Sumbasic sont les trois methodes implement� pour g�n�rer des r�sum� 


Baseline:

1)On fait appel � la machine reading sur le corpus(cluster de doc) pour
avoir la liste des CDS(propositions) de ce corpus.

2) On stock tous les cds dans le base de donn� sous forme de graphe
Neo4j.

3) On cherche tous les cds qui ont le meme sujet, verb, objet et on cr�e
une relation entre eux. Ces cds constituent un ensemble des informations
rendundants.

Kmeans: 

Projection dans l�espace vectoriel les cds et appliquer l�algorithme de kmeans sur l�ensemble des vecteurs qui rappresent les cds.

Sumbasic: SumBasic est un syst�me d�velopp� pour op�rationnaliser l�id�e d�utiliser la fr�quence pour la s�lection des phrases. Il ne repose que sur la probabilit� des mots pour calculer l�importance. C�est un systeme de r�sum� qui utilise un composant de s�lection de phrases bas�e sur la fr�quence, avec un composant pour re-pond�rer les probabilit�s du mot afin de minimiser la redondance.

Comression rate: calcul le ratio de compression (combien plus court est le r�sum� par rapport � le text original) 