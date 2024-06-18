# Pyalbert

PyAlbert est un module Python pour faciliter l'utilisation des modèles Albert.
Il permet de :

### Télécharger les sources de données du RAG
```sh
pyalbert download_rag_sources --storage-dir /data/sources
```

### Créer le fichier de liste blanche `.json` contenant les numéros de téléphone, les adresses mail et les URL de domaine extraits des annuaires locaux et nationaux :
```sh
pyalbert create_whitelist --storage-dir /data/sources
```

### Créer les chunks de documents pour le RAG
```sh
pyalbert make_chunks --structured --storage-dir /data/sources
```

### Créer les index de la base de données Elasticsearch qui contient les sources de données pour le RAG :
```sh
pyalbert index experiences --index-type bm25 --storage-dir /data/sources
pyalbert index sheets      --index-type bm25 --storage-dir /data/sources
pyalbert index chunks      --index-type bm25 --storage-dir /data/sources
```

### Créer les index de la base de données Qdrant qui contient les vecteurs d'embeddings :
```sh
pyalbert index experiences --index-type e5 --storage-dir /data/sources
pyalbert index chunks      --index-type e5 --storage-dir /data/sources
```

### Lancer l'API Albert en local (dev mode)
```sh
pyalbert serve
```
