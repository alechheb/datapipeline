# Part 1

J'ai décidé d'utiliser `Pandas` pour la manipulation des données parce que j'estime qu'elle répond au besoin (que j'ai compris).

## Implémentation sous Airflow:
Un exemple du fichier dag a été créé sous `datapipeline/airflow`

Il y a plusieurs implémentations possibles de la pipeline dans Airflow. Voici 2 versions :

### En utilisant la base de données à chaque étape :
Vous trouvez un exemple simplissime de la création du dag. Si vous avez besoin de plus d'information n'hésitez pas à me contacter.

* Prérequis :
  1. Ajouter une connexion airflow pour accéder à la base de données.
  2. Ajouter une variable airflow contenant la configuration du dag (nom de la queue à utiliser...)

Il y aura 4 operators:
- DrugsOperator: Parse le fichier `drugs.csv` et alimente la table `drugs`.
- TrialsOperator: Parse le fichier `clinical_trials.csv` et alimente la table `clinical_trials` et `journal` ainsi que la table d'association avec la `date_mention`
- PubmedOperator: Parse le fichier `pub_med.csv` et alimente la table `clinical_trials` et `journal` ainsi que la table d'association avec la `date_mention`
- GraphOperator: Récupère les données précédemment insérées en SQL et génère le graphe de liaison.


### En utilisant les XCOM pour passer les données entre les différentes tâches airflow:

* Prérequis :
  2. Ajouter une variable airflow contenant la configuration du dag (nom de la queue à utiliser...), et l'algorithme de compression des dataframes échangés par exemple.

Il y aura 3 operators:
- DrugsOperator: Parse le fichier `drugs.csv` et passe le dataframe compressé via le XCOM (xcom_push) aux 2 tâches suivantes.
- TrialsOperator: Parse le fichier `clinical_trials.csv` et passe le dataframe compressé via le XCOM (xcom_push) à la dernière tâche GraphOperator
- PubmedOperator: Parse le fichier `pub_med.csv` et passe le dataframe compressé via le XCOM (xcom_push) à la dernière tâche GraphOperator
- GraphOperator: Récupère les dataframes précédemment pushées (xcom_push from upstream tasks) et génère le graphe de liaison.

* Note:
- Cette solution représente pour moi le dernier recours par ce qu'elle a des limites dans le cas de grandes volumétries; Parce que tout ce qu'on envoie via les XCOM est stocké en base de données airflow et par conséquent la taille du dataframe pushé est limitée (1 Go sur postgresql)

### Ad-hoc
A noter qu'il y a quelques problèmes d'encodage qui font que certains journaux sont considérés comme différents alors qu'il ne le sont pas :

````bash
python -m datapipeline.adhoc
>> The most common paper that mentions the most different drugs is: Psychopharmacology
````

### Pour aller plus loin
Pour pouvoir gérer de grosse volumétrie de données nous pouvons :

* Utiliser les générateurs pour lire le gros fichier par chunk. L'idée est de ne pas charger tout le fichier en mémoire.
  * Changement du code : Cela revient à ajouter l'argument `chunk_size` à la méthode read de `CSVReader` ou créer une fonction spécifique qui chunk le fichier sans tout charger en mémoire.(une fonction qui prend la taille du chunk et `yield` le retour)
* Optimiser le stockage mémoire en changeant le type des colonnes (Utilisation des categories pandas, passage à int4 au lieu de int16...) le gain ne sera pas énorme mais c'est bonne pratique à faire quel que soit le cas. 
  * Changement du code :Dans mon code ça revient à soit utiliser l'argument `low_memory` ou forcer le type des colonnes en les passant à `read_csv` ou bien créer une fonction qui parcours les dataframes et infer le type le plus adapté (Facile à faire)
* Utiliser une librairie ou framework pour le traitement distribué : `Dask` par exemple dont l'API reprend pas mal de fonctionnalité de l'API pandas ce qui rend le passage dask >> Pandas >> Dask simple et rapide.
* Si on des millions de petits fichiers à traiter, on peut imaginer un job qui récupère les fichiers les envoient vers un broker de message (RabbitMq, Azure service Bus...) et des microservices (deployment k8s) contrôlés par auto scaler Kubernetes (Keda) qui up scale les déploiements à la réception de ces messages et à la fin du traitement down scale.

Et pour maintenir un équilibre Consommation mémoire / Rapidité, il faut utiliser le multiprocessing pour pouvoir faire travailler tous les CPUs et ainsi avoir les résultats le plus rapidement possible. Cela revient à l'une des options suivantes:
 1. soit lire un petit fichier par process (Comme ce que fait le `scheduler` airflow lorsqu'il parse le dag_file)
 2. Lorsqu'il s'agit d'un grand dataframe, il faut paralléliser les opérations dites `flats`. Même concept que le calcul distribué mais sur la machine même (interne/local)




# Part 2: [Requêtes SQL](ventes.sql)