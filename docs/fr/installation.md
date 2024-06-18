# Installation

Ce tutoriel d'installation couvre les installations avec Docker comme en local, et est découpé en 3 parties :
1. [Déployer un modèle Albert](#déployer-un-modèle-albert)
2. [Déployer les bases de données](#déployer-les-bases-de-données)
3. [Déployer l'API](#déployer-lapi)
4. [Mettre en place la RAG](#mettre-en-place-la-rag)




## Déployer un modèle Albert

Les modèles Albert sont déployables avec [VLLM](https://docs.vllm.ai/en/latest/). Nous mettons à disposition une "API LLM" (située dans `llm/`) permettant d'embarquer un LLM Albert ainsi qu'une modèle d'embeddings pour le [Retrieval Augmented Generation, RAG](https://en.wikipedia.org/wiki/Prompt_engineering#Retrieval-augmented_generation).
Pour plus d'informations sur les modèles, référez-vous à la documentation sur les [modèles supportés](./models.md).



### Avec Docker

#### *Build*

* Avec [VLLM](https://docs.vllm.ai/en/latest/) :

  ```sh
  docker build --tag albert/llm:latest --build-context pyalbert=./pyalbert --file ./llm/Dockerfile ./llm --no-cache
  ```

* Avec [GPT4All](https://gpt4all.io/), dans le cas sans GPU pour un système d'exploitation non MacOS :

  Si vous ne disposez pas de GPU, vous trouverez dans un [fichier Dockerfile](../../contrib/gpt4all/Dockerfile) pour *build* l'image de l'API avec GPT4All (à la place de VLLM). Cette API est sur le format de l'API VLLM précédement décrite mais ne nécessite pas l'utilisation de GPU. Toutefois, celle-ci est maintenue en *best effort* par les équipes.

  La commande pour build l'image est donc la suivante :
  ```sh
  docker build --tag albert/llm_ggml:latest --build-context pyalbert=./pyalbert --file ./contrib/gpt4all/Dockerfile_GGML ./contrib/gpt4all --no-cache
  docker build --tag albert/llm_gguf:latest --build-context pyalbert=./pyalbert --file ./contrib/gpt4all/Dockerfile_GGUF ./contrib/gpt4all --no-cache
  ```
  Les modèles disponibles sans GPU sont listés dans la [documentation sur les modèles](./models.md).


#### *Run*

* Avec [VLLM](https://docs.vllm.ai/en/latest/) :
  ```sh
  docker compose --env-file ./llm/.env.example --file ./llm/docker-compose.yml up --detach
  ```

* Avec [GPT4All](https://gpt4all.io/), dans le cas sans GPU pour un système d'exploitation non MacOS :
  ```sh
  docker compose --env-file ./contrib/gpt4all/.env_GGML --file ./contrib/gpt4all/docker-compose_GGML.yml up --detach
  docker compose --env-file ./contrib/gpt4all/.env_GGUF --file ./contrib/gpt4all/docker-compose_GGUF.yml up --detach
  ```



### En local, sans Docker

#### *Install*
* Mettre à jour les variables suivantes dans le fichier `pyalbert/.env`, afin d'initialiser l'administrateur de l'application avec ces données :
  - `FIRST_ADMIN_USERNAME`,
  - `FIRST_ADMIN_EMAIL`,
  - `FIRST_ADMIN_PASSWORD`.
* Avec [VLLM](https://docs.vllm.ai/en/latest/) :
  ```bash
  pip install llm/.
  ln -s $(pwd)/pyalbert llm/pyalbert
  ```
* Avec [GPT4All](https://gpt4all.io/), dans le cas sans GPU :
  ```bash
  pip install contrib/gpt4all/
  # ne fonctionne pas dans un Terminal MacOS sous bash
  ln -s $(pwd)/pyalbert contrib/gpt4all/pyalbert
  # fonctionne dans un Terminal MacOS sous bash
  cp -R $(pwd)/pyalbert contrib/gpt4all/pyalbert
  ```


#### *Run*
* Avec [VLLM](https://docs.vllm.ai/en/latest/) :

  Exemple pour mettre en service un modèle d'Albert sur des paramètrages donnés
  ```sh
  python3 llm/app.py --llm-hf-repo-id AgentPublic/albertlight-8b --tensor-parallel-size 1 --gpu-memory-utilization 0.4 --models-dir ~/_models --host 0.0.0.0 --port 8000
  ```

* Avec [GPT4All](https://gpt4all.io/), dans le cas sans GPU :

  ```sh
  export EMBEDDINGS_HF_REPO_ID=intfloat/multilingual-e5-large
  export LLM_HF_REPO_ID=RichardErkhov/AgentPublic_-_albertlight-7b-gguf
  export LLM_MODEL_FILE=albertlight-7b.Q4_K_M.gguf
  export DEBUG=--debug
  export FORCE_DOWNLOAD=
  python3 contrib/gpt4all/app.py --embeddings-hf-repo-id $EMBEDDINGS_HF_REPO_ID --host 0.0.0.0 --llm-hf-repo-id $LLM_HF_REPO_ID --llm-model-file $LLM_MODEL_FILE $FORCE_DOWNLOAD $DEBUG --models-dir ~/_models --port 8000
  ```



### Accès à l'API du modèle

> ⚠️ Si vous ne spécifiez pas de modèle d'*embeddings*, l'*endpoint* de l'API `/embeddings` retournera une réponse 404 et sera masqué dans la documentation automatique (Swagger).

Vous pouvez accéder à ladite documentation automatique de l'API du modèle depuis : [http://localhost:8000/docs](http://localhost:8000/docs).




## Déployer les bases de données 

Le framework Albert nécessite trois bases de données : une base PostgreSQL, une base Elasticsearch et une base Qdrant. Pour plus d'information sur leur utilité, référez-vous à la documentation [databases.md](./databases.md).

Pour ces bases de données aucun build n'est nécessaire puisque les images Docker sont disponibles sur le registry Docker officiel.



### PostgreSQL

Nous vous recommandons de configurer la variable d'environnement `POSTGRES_STORAGE_DIR` vers un repertoire local pour assurer une meilleure persistance des données.

* *Run*
  ```sh
  export PROJECT_NAME=postgres
  # configurer un dossier local
  export POSTGRES_STORAGE_DIR=./data/postgres
  # définir un mot de passe d'accès à la base
  export POSTGRES_PASSWORD=posgtresPassword
  docker compose --file ./databases/postgres/docker-compose.yml up --detach
  ```
* Vérifications
  ```sh
  # exporte les journaux du conteneur PostgreSQL dans un fichier texte
  docker container logs albert_db_postgresql >& LLM_Albert_database_PostgreSQL_logs.txt
  # se connecte au shell bash du conteneur PostgreSQL
  docker exec -it albert_db_postgresql bash
  # se connecte à l'utilisateur postgres de PostgreSQL
  psql -U postgres
  # liste les bases de données de l'utilisateur posgres
  \list
  # quitte l'utilitaire pgSQL
  \q
  # quitte le conteneur PostgreSQL
  exit
  ```



### Vector stores (Elasticsearch et Qdrant)

Nous vous recommandons de configurer les variables d'environnement `QDRANT_STORAGE_DIR` et `ELASTIC_STORAGE_DIR` vers un repertoire local pour assurer une meilleure persistance des données.

> ⚠️ **Attention le dossier mentionné dans la variable ELASTIC_STORAGE_DIR doit avoir comme droits 1000:1000.** 

* *Run*
  ```sh
  export PROJECT_NAME=vector-store
  # configurer des dossiers locaux
  export ELASTIC_STORAGE_DIR=./data/elastic
  export QDRANT_STORAGE_DIR=./data/qdrant
  # définir un mot de passe d'accès à la base
  export ELASTIC_PASSWORD=elasticPassword
  docker compose --file ./databases/vector_store/docker-compose.yml up --detach
  ```
* Vérifications
  ```sh
  # vérifie la bonne santé du conteneur ElasticSearch
  curl localhost:9200/_cat/health
  curl localhost:9200/_cluster/health?pretty
  # exporte les journaux du conteneur ElasticSearch dans un fichier texte
  docker container logs albert_db_vector_elasticsearch >& LLM_Albert_database_vector_ElasticSearch_logs.txt
  # exporte les journaux du conteneur Qdrant dans un fichier texte
  docker container logs albert_db_vector_qdrant >& LLM_Albert_database_vector_Qdrant_logs.txt
  ```




## Déployer l'API de l'application

### Avec Docker

Assurez-vous que votre variable d'environnement `ENV` dans [pyalbert/.env](../pyalbert/.env) est égale à `dev` telle que `ENV="dev"`, puis lancez le conteneur de l'API :

```bash
docker compose --env-file ./pyalbert/.env.example --file ./api/docker-compose.yml up --detach
```



### En local, sans Docker

1. Installez les dépendances
   ```bash
   cd api/
   # ne fonctionne pas dans un Terminal MacOS sous bash
   ln -s $(pwd)/../pyalbert pyalbert
   # fonctionne dans un Terminal MacOS sous bash
   cp -R ../pyalbert .
   pip install . pyalbert
   ```

2. Assurez-vous que votre variable d'environnement `ENV` dans [pyalbert/.env](../pyalbert/.env) est égale à `dev` telle que `ENV="dev"`

3. Créez le schéma de la base de données (sqlite en mode dev) en utilisant Alembic :
   ```sh
   # effectue les migrations
   PYTHONPATH=. alembic upgrade head
   # vérifie l'historique de celles-ci
   PYTHONPATH=. alembic history --verbose
   ```

4. Lancez l'API
   ```sh
   # définit le répertoire de stockage des courriels de création des utilisateurs, de confirmation de création des utilisateurs et de réinitialisation du mot de passe des utilisateurs
   export MJ_FOLDER=./data/emails
   # définit les modèles utilisés et l'URL correspondante de leur API
   export LLM_TABLE="[('RichardErkhov/AgentPublic_-_albertlight-7b-gguf','http://localhost:8000')]"
   # définit le port d'écoute des embeddings à la valeur du port de l'API du LLM
   export EMBEDDINGS_PORT=8000
   uvicorn app.main:app --reload --host 0.0.0.0
   # pour la lancer avec un port spécifique
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8100
   ```

5. Pour tester, vous pouvez accéder à la documentation automatique (Swagger) de l'API de l'application depuis : [http://localhost:8100/docs](http://localhost:8100/docs).

6. Exécutez les tests unitaires :
   ```sh
   pytest app/tests
   ```

   Ou, pour le support des rapports :

   ```sh
   pytest --cov=app --cov-report=html --cov-report=term-missing app/tests
   ```



### Vérifications

#### Données de l'utilisateur administrateur depuis la base de données
```sh
# se connecte au shell bash du conteneur PostgreSQL
docker exec -it albert_db_postgresql bash
# se connecte à l'utilisateur postgres de PostgreSQL
psql -U postgres
# liste les tables de l'utilisateur posgres
\dt
# liste les utilisateurs enregistrés :
# - les valeurs correspondant aux variables FIRST_ADMIN_USERNAME et FIRST_ADMIN_EMAIL doivent apparaître respectivement dans les colonnes username et email,
# - les booléens is_confirmed et is_admin doivent être initialisés à true (t)
SELECT * FROM users;
# quitte l'utilitaire pgSQL
\q
# quitte le conteneur PostgreSQL
exit
```


#### Confirmation de l'utilisateur administrateur depuis l'API

- Installer [Postman](https://www.postman.com/downloads/)
- Configurer Postman avec les valeurs suivantes dans les onglets :
  * *Authorization*
    + `Auth type` = `JWT Bearer`
    + `Algorithm` = `HS256`
    + `Secret` = la valeur de la variable `SECRET_KEY` définie dans le fichier [pyalbert/.env](../pyalbert/.env)
    + `Payload` =
      ```json
      {
          "exp": {{exp}},
          "iat": {{$timestamp}},
          "sub": "1"
      }
      ```
      Les commentaires suivants ne peuvent être écrits dans le Payload sous peine de faire échouer la bonne reconnaissance de l'en-tête :
      - la valeur de "exp" est celle de la variable éponyme, définie dans le script de pré-requête,
      - la valeur de "iat" est celle de la variable globale $timestamp représentant la date courante en millisecondes,
      - la valeur de "sub" est celle de l'id de l'utilisateur administrateur connecté en premier à Albert (constantes $FIRST_ADMIN_*) et donc enregsitré le premier en base de données.
  * *Scripts*
    + `Pre-req` =
      ```javascript
      // définit la variable d''environnement "exp" en utilisant la variable globale $timestamp,
      // représentant la date courante en millisecondes à laquelle sont ajoutées 24 heures
      pm.environment.set("exp", pm.variables.replaceIn('{{$timestamp}}') + 3600 * 24);
      ```
- Choisir la bonne méthode HTTP et configurer le corps de la requête :
  * Lecture des informations du compte courant :
    + Méthode = `GET`
    + URL / endpoint = `http://localhost:8100/user/me`
    + Corps = `none`
    + Réponse =
      ```json
      {
          "username": "la valeur de la variable $FIRST_ADMIN_USERNAME",
          "email": "la valeur de la variable $FIRST_ADMIN_EMAIL",
          "id": 1,
          "is_confirmed": true,
          "is_admin": true
      }
      ```
  * Confirmation d'un compte :
    + Méthode = `POST`
    + URL / endpoint = `http://localhost:8100/user/confirm`
    + Corps = `raw / JSON`
      ```json
      {
          "email": "la valeur de la variable $FIRST_ADMIN_EMAIL",
          "is_confirmed": true
      }
      ```
    + Réponse =
      ```json
      {
          "detail": "Account creation already accepted or declined"
      }
      ```




## Mettre en place la RAG

### En local, sans Docker
```sh
# met à jour le lien vers les certificats pour Python 3.x (>= 3.6) afin d'éviter les erreurs au lancement de PyAlbert
/Applications/Python\ 3.x/Install\ Certificates.command
python pyalbert/albert.py download_rag_sources --storage-dir ./data/RAG
python pyalbert/albert.py create_whitelist --storage-dir ./data/RAG
python pyalbert/albert.py make_chunks --structured --storage-dir ./data/RAG
python pyalbert/albert.py index experiences --index-type bm25 --storage-dir ./data/RAG
python pyalbert/albert.py index sheets --index-type bm25 --storage-dir ./data/RAG
python pyalbert/albert.py index chunks --index-type bm25 --storage-dir ./data/RAG
# définit le port d'écoute des embeddings à la valeur du port de l'API du LLM
export EMBEDDINGS_PORT=8000
# dure 7h sur Apple M3
python pyalbert/albert.py index experiences --index-type e5 --storage-dir ./data/RAG
# dure 2h30 sur Apple M3
python pyalbert/albert.py index chunks --index-type e5 --storage-dir ./data/RAG
```

