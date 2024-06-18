# PyAlbert

PyAlbert est un module Python pour faciliter l'utilisation des modèles Albert.
Il permet de :

### Télécharger les archives des sources de données de la RAG
```sh
pyalbert download_rag_sources --storage-dir /data/sources
```
Exemple de sortie obtenue :
```text
Dowloading 'experiences'...
-1 / unknown
Dowloading 'vdd'...
100% [........................................................................] 19957425 / 19957425
Dowloading 'travail'...
100% [........................................................................] 10457926 / 10457926
Corpus files successfuly downloaded
```

### Créer le fichier de liste blanche au format JSON, utilisée en *post-processing* et contenant les numéros de téléphone, les adresses mail et les URL de domaine extraits des annuaires locaux et nationaux
```sh
pyalbert create_whitelist --storage-dir /data/sources
```
Exemple de sortie obtenue :
```text
Configuration file for white list = ./pyalbert/config/whitelist_config.json
2024-06-26 08:07:42,791:INFO: downloading local_directory archive...
100% [......................................................................] 166054712 / 166054712
2024-06-26 08:08:06,435:INFO: unpacking local_directory archive...
2024-06-26 08:08:16,023:INFO: deleting local_directory archive...
2024-06-26 08:08:16,028:INFO: Whitelist directories successfully downloaded
2024-06-26 08:08:16,028:INFO: downloading national_directory archive...
100% [..........................................................................] 2960778 / 2960778
2024-06-26 08:08:16,958:INFO: unpacking national_directory archive...
2024-06-26 08:08:16,997:INFO: deleting national_directory archive...
2024-06-26 08:08:16,997:INFO: Whitelist directories successfully downloaded
2024-06-26 08:08:16,997:INFO: creating whitelist file ...
2024-06-26 08:08:40,568:INFO: Whitelist file successfuly created
```

### Créer les *chunks* (élément au format JSON d'environ 1 000 caractères conservant des phrases entières) de documents pour la RAG à partir des fichiers XML de données publiques
```sh
pyalbert make_chunks --structured --storage-dir /data/sources
```
Exemple de sortie obtenue :
```text
Chunks created in /data/sources/sheets_as_chunks.json
Chunks info created in /data/sources/chunks.info
```

### Créer les index de la base de données Elasticsearch qui contient les sources de données pour la RAG :
* ```sh
  pyalbert index experiences --index-type bm25 --storage-dir /data/sources
  ```
  Exemple de sortie obtenue :
  ```text
  Creating Elasticsearch index for 'experiences'...
  ListApiResponse([{'epoch': '1719382233', 'timestamp': '06:10:33', 'count': '60784'}])
  ```
* ```sh
  pyalbert index sheets      --index-type bm25 --storage-dir /data/sources
  ```
  Exemple de sortie obtenue :
  ```text
  Creating Elasticsearch index for 'sheets'...
  Warning on situation Fonction publique d''État : Texte == None ==> not stored
  Warning on situation Territoriale : Texte == None ==> not stored
  ListApiResponse([{'epoch': '1719382300', 'timestamp': '06:11:40', 'count': '0'}])
  ```
* ```sh
  pyalbert index chunks      --index-type bm25 --storage-dir /data/sources
  ```
  Exemple de sortie obtenue :
  ```text
  Creating Elasticsearch index for 'chunks'...
  ListApiResponse([{'epoch': '1719382543', 'timestamp': '06:15:43', 'count': '31405'}])
  ```

### Définir le port d'écoute des embeddings à la valeur du port de l'API du LLM
```sh
export EMBEDDINGS_PORT=8000
```

### Créer les index de la base de données Qdrant qui contient les vecteurs d'embeddings
* ```sh
  # dure 7h sur Apple M3
  pyalbert index experiences --index-type e5 --storage-dir /data/sources
  ```
  Sortie obtenue :
  ```text
  Creating Qdrant index for 'experiences'...
  ```
* ```sh
  # dure 2h30 sur Apple M3
  pyalbert index chunks      --index-type e5 --storage-dir /data/sources
  ```
  Sortie obtenue :
  ```text
  Creating Qdrant index for 'chunks'...
  ```
