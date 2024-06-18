# Installation

Ce tutoriel d'installation couvre les installations avec Docker comme en local, et est découpé en 4 parties :
1. [Déployer un modèle Albert](#déployer-un-modèle-albert)
2. [Déployer les bases de données](#déployer-les-bases-de-données)
3. [Déployer l'API de l'application](#déployer-lapi-de-lapplication)
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

  Si vous ne disposez pas de GPU, vous trouverez un [fichier `Dockerfile`](../../contrib/gpt4all/Dockerfile) pour *build* l'image de l'API avec GPT4All (à la place de VLLM). Cette API est sur le format de l'API VLLM précédement décrite mais ne nécessite pas l'utilisation de GPU. Toutefois, celle-ci est maintenue en *best effort* par les équipes.

  La commande pour build l'image est donc la suivante :
  ```sh
  docker build --tag albert/llm:latest --build-context pyalbert=./pyalbert --file ./contrib/gpt4all/Dockerfile ./contrib/gpt4all --no-cache
  ```
  Les modèles disponibles sans GPU sont listés dans la [documentation sur les modèles](./models.md).


#### *Run*

* Avec [VLLM](https://docs.vllm.ai/en/latest/) :
  ```sh
  docker compose --env-file ./llm/.env.example --file ./llm/docker-compose.yml up --detach
  ```

* Avec [GPT4All](https://gpt4all.io/), dans le cas sans GPU pour un système d'exploitation non MacOS :
  ```sh
  docker compose --env-file ./contrib/gpt4all/.env.example --file ./contrib/gpt4all/docker-compose.yml up --detach
  ```



### En local, sans Docker

#### *Install*

* Dans le fichier [`pyalbert/.env`](../../pyalbert/.env), vérifier et/ou mettre à jour les variables suivantes :
  - afin que l'environnement déployé soit bien celui de développement :
    ```sh
    ENV=dev
    ```
  - afin d'initialiser l'administrateur de l'application avec ces données :
    ```sh
    FIRST_ADMIN_USERNAME=loginOfAdministrator
    FIRST_ADMIN_EMAIL=emailAddressOfAdministrator
    FIRST_ADMIN_PASSWORD=plainTextPasswordOfAdministrator
    ```
  - afin que les requêtes provenant des 3 API utilisées (LLM, application et *front-end*) ne soient pas bloquées :
    ```sh
    BACKEND_CORS_ORIGINS="http://localhost:8000,http://localhost:8100,http://localhost:4173"
    ```
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
* S'assurer que les 3 fichiers suivants de configuration du *prompt* du modèle sont bien présents dans le sous-répertoire propre au modèle, lui-même situé dans le répertoire des modèles `~/_models` :
  - `prompt_config.yml` (exemple de contenu provenant du fichier [`pyalbert/prompt/examples/prompt_config.yml`](../../pyalbert/prompt/examples/prompt_config.yml)) :
    ```yaml
    prompt_format: llama-chat
    max_tokens: 2048
    prompts:
      - mode: simple
        template: simple_prompt_template.jinja
      - mode: rag
        template: rag_prompt_template.jinja
        default:
          limit: 4
    ```
  - `rag_prompt_template.jinja` (exemple de contenu provenant du fichier [`pyalbert/prompt/examples/rag_prompt_template.jinja`](../../pyalbert/prompt/examples/rag_prompt_template.jinja)) :
    ```jinja
    Utilisez les éléments de contexte à votre disposition ci-dessous pour répondre à la question finale. Si vous ne connaissez pas la réponse, dites simplement que vous ne savez pas, n'essayez pas d'inventer une réponse.
    {% for chunk in sheet_chunks %}
    {{chunk.url}} : {{chunk.title}} {% if chunk.context %}({{chunk.context}}){% endif %}
    {{chunk.text}} {% if not loop.last %}{{"\n"}}{% endif %}
    {% endfor %}
    Question: {{query}}
    ```
  - `simple_prompt_template.jinja` (exemple de contenu  provenant du fichier [`pyalbert/prompt/examples/simple_prompt_template.jinja`](../../pyalbert/prompt/examples/simple_prompt_template.jinja)) :
    ```jinja
    {{query}}
    ```
* Si ce n'est pas le cas :
  - les créer à partir du modèle ci-dessus ou en copiant les fichiers exemples situés dans le répertoire [`pyalbert/prompt/examples/`](../../pyalbert/prompt/examples/), en prenant soin d'adapter la valeur de l'entrée `prompt-format` du fichier `prompt_config.yml`,
  - passer à `False` la valeur du paramètre `allow_download` de la fonction `get_prompt_config` du fichier `app.py` situé dans le répertoire [`llm`](../../llm/app.py) (si au moins un GPU compatible CUDA est présent) ou [`contrib/gpt4all`](../../contrib/gpt4all/app.py) (sinon) :
    ```python
    @app.get("/get_prompt_config")
    async def get_prompt_config(
        request: Request, config_file: Optional[str] = None, allow_download: bool = True
    ) -> Response:
    ```
    doit devenir :
    ```python
    @app.get("/get_prompt_config")
    async def get_prompt_config(
        request: Request, config_file: Optional[str] = None, allow_download: bool = False
    ) -> Response:
    ```


#### *Run*

Exemple pour mettre en service un modèle d'Albert sur des paramètrages donnés :

* Avec [VLLM](https://docs.vllm.ai/en/latest/) :
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

> ⚠️ Si vous ne spécifiez pas de modèle d'*embeddings*, l'*endpoint* de l'API `/embeddings` retournera une réponse 404 et sera masqué dans la documentation automatique (*Swagger*).

Vous pouvez accéder à ladite documentation automatique de l'API du modèle depuis : [http://localhost:8000/docs](http://localhost:8000/docs).




## Déployer les bases de données 

Le *framework* Albert nécessite trois bases de données : une base PostgreSQL, une base Elasticsearch et une base Qdrant. Pour plus d'information sur leur utilité, référez-vous à la documentation [`databases.md`](./databases.md).

Pour ces bases de données, aucun *build* n'est nécessaire puisque les images Docker sont disponibles sur le *registry* Docker officiel.



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



### *Vector stores* (Elasticsearch et Qdrant)

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

Assurez-vous que les variables d'environnement évoquées dans la partie [Déployer un modèle Albert / En local, sans Docker / *Install*](#install) sont bien définies dans [`pyalbert/.env`](../../pyalbert/.env).



### Avec Docker

Lancez le conteneur de l'API :
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

2. Créez le schéma de la base de données (sqlite en mode dev) en utilisant Alembic :
   ```sh
   # effectue les migrations
   PYTHONPATH=. alembic upgrade head
   # vérifie l'historique de celles-ci
   PYTHONPATH=. alembic history --verbose
   ```

3. Lancez l'API
   ```sh
   # définit le répertoire de stockage des courriels de création des utilisateurs, de confirmation de création des utilisateurs et de réinitialisation du mot de passe des utilisateurs
   export MJ_FOLDER=./data/emails
   # définit les modèles utilisés et l'URL correspondante de leur API
   # - dans le cas avec GPU
   export LLM_TABLE="[('AgentPublic/albertlight-8b','http://localhost:8000')]"
   # - dans le cas sans GPU
   export LLM_TABLE="[('RichardErkhov/AgentPublic_-_albertlight-7b-gguf','http://localhost:8000')]"
   # définit le port d'écoute des embeddings à la valeur du port de l'API du LLM
   export EMBEDDINGS_PORT=8000
   # définit la version de l'API de l'application (par défaut : /api/v2)
   export API_ROUTE_VER=/
   # définit l'URL de l'application permettant de générer les réponses aux questions dans l'interface
   export API_URL=http://localhost:8100
   uvicorn app.main:app --reload --host 0.0.0.0
   # pour la lancer avec un port spécifique
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8100
   ```

4. Pour tester, vous pouvez accéder à la documentation automatique (*Swagger*) de l'API de l'application depuis : [http://localhost:8100/docs](http://localhost:8100/docs).

5. Exécutez les tests unitaires :
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
```
```sql
/*
 * liste les utilisateurs enregistrés :
 * - les valeurs correspondant aux variables FIRST_ADMIN_USERNAME et FIRST_ADMIN_EMAIL doivent apparaître respectivement dans les colonnes username et email,
 * - les booléens is_confirmed et is_admin doivent être initialisés à true (t)
 */
SELECT * FROM users;
```
```sh
# quitte l'utilitaire pgSQL
\q
# quitte le conteneur PostgreSQL
exit
```


#### Confirmation de l'utilisateur administrateur depuis l'API

Voir également la [documentation d'obtention d'un jeton d'accès à l'API Albert](./api-token.md)

- Installer [Postman](https://www.postman.com/downloads/)
- Configurer Postman avec les valeurs suivantes dans les onglets :
  * *Authorization*
    + `Auth type` = `JWT Bearer`
    + `Algorithm` = `HS256`
    + `Secret` = la valeur de la variable `SECRET_KEY` définie dans le fichier [`pyalbert/.env`](../../pyalbert/.env)
    + `Payload` =
      ```json
      {
          "exp": {{exp}},
          "iat": {{$timestamp}},
          "sub": "1"
      }
      ```
      Les commentaires suivants ne peuvent être écrits dans le *Payload* sous peine de faire échouer la bonne reconnaissance de l'en-tête :
      - la valeur de `"exp"` est celle de la variable éponyme, définie dans le script de pré-requête,
      - la valeur de `"iat"` est celle de la variable globale `$timestamp` représentant la date courante en millisecondes,
      - la valeur de `"sub"` est celle de l'identifiant de l'utilisateur administrateur connecté en premier à Albert (constantes `$FIRST_ADMIN_*`) et donc enregsitré le premier en base de données.
  * *Scripts*
    + `Pre-req` =
      ```javascript
      // définit la variable d''environnement "exp" en utilisant la variable globale $timestamp,
      // représentant la date courante en millisecondes à laquelle sont ajoutées 24 heures
      pm.environment.set("exp", pm.variables.replaceIn('{{$timestamp}}') + 3600 * 24);
      ```
- Choisir la bonne méthode HTTP (indiquée dans la [documentation automatique / *Swagger* de l'API de l'application](http://localhost:8100/docs)) et configurer le corps de la requête :
  * Lecture des informations du compte courant :
    + Méthode = `GET`
    + URL / *endpoint* = `http://localhost:8100/user/me`
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
    + URL / *endpoint* = `http://localhost:8100/user/confirm`
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

* Sur Apple, mettre à jour le lien vers les certificats pour Python 3.x (>= 3.6) afin d'éviter les erreurs au lancement de PyAlbert
  ```sh
  /Applications/Python\ 3.x/Install\ Certificates.command
  ```
* Définir le port d'écoute des embeddings à la valeur du port de l'API du LLM
  ```sh
  export EMBEDDINGS_PORT=8000
  ```
* Définir un alias `pyalbert` à `python pyalbert/albert.py`
  ```sh
  alias pyalbert=python pyalbert/albert.py
  ```
* Appliquer les instructions de la [documentation de PyAlbert](./pyalbert.md)
