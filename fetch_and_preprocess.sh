#!/bin/bash
set -e
sh build_java.sh

# python scripts/download.py



export PYTHONPATH="$PYTHONPATH:."
# python scripts/preprocess_hs.py
# python scripts/preprocess_django.py
