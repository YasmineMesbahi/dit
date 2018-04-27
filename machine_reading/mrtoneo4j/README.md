# mrtoneo4j #

« Machine Reading to Neo4j » permet de transformer les sorties JSON de la Machine Reading de Synapse Développement en graphe Neo4j. 

### Prérequis ###

* [API Machine Reading](http://api-synapse-dev.azurewebsites.net/apidoc/?service=machinereading)
* Python 3 avec les moodules : requests, path 
* Neo4j Python Driver :  pip install neo4j-driver
* [Neo4j Community Edition](https://neo4j.com/download/community-edition/)
* Windows

### Exécution du fichier « mrtoneo4j.py » ###

* cd ‘‘C:/Python36-32’’   # repository of python supposed in C:/
* python mrtoneo4j/mrtoneo4j.py # mrtoneo4j.py supposed in python repository


### Passage des paramètres par console ###

*	python mrtoneo4j/mrtoneo4j.py 
*	--help “show help message with default values”
*	--localhost     ‘’Localhost Neo4j’’
*	--login     ‘’Login Neo4j”
*	--password     “Password Neo4j”
*	--url      ‘‘Machine Reading endpoint URL’’ 
*	--key     ‘’API key allowing to consume Machine Reading WS.’ 
*	--lang    ‘Language of the texts to be analysed. Possible values: fr for French, en for English.’’ 
*	--folder  ‘‘Path to folder containing texts to be analysed, please write the complete path or : mrtoneo4j/input_texts ’’


### Exemple ###

* input_texts/File_1 : je mange maintenant. Je marche demain. 
* input_texts/File_2 : je grandis aujourd'hui. Je vieillirai dans 10 ans.
* input_texts/File_3 : L'enfant joue dans l'école.
* input_texts/File_4 : Est-ce qu’il pleuvra demain ?
* input_texts/File_5 : je suis très contente pour toi. Après, à toi de voir

![Example of output in Neo4j format](neo4j_output_example.png)

Code source mis à jour le 14/04/2017