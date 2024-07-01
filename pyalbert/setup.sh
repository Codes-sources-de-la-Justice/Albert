#!/bin/bash

#|##################################################
#|Setup Albert from scratch
#|##################################################

# Fetch and parse corpuses
pyalbert create_whitelist --storage-dir=./data/sources
pyalbert download_rag_sources --storage-dir=./data/sources
pyalbert make_chunks --structured --storage-dir=./data/sources
# Feed the search engines
pyalbert index experiences --index-type bm25 --storage-dir=./data/sources
pyalbert index sheets      --index-type bm25 --storage-dir=./data/sources
pyalbert index chunks      --index-type bm25 --storage-dir=./data/sources
pyalbert index experiences --index-type e5 --storage-dir=./data/sources
pyalbert index chunks      --index-type e5 --storage-dir=./data/sources

# Launch albert api on localhost (test)
pyalbert serve
