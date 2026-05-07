#!/bin/bash

VIDEO_ID=$1
CONTEXT=$2

echo "===== DOWNLOAD ====="
uv run src/download.py "$VIDEO_ID"

echo "===== PARSE ====="
uv run src/parse.py "$VIDEO_ID"

echo "===== EXTRACT ====="
uv run src/extract.py "$VIDEO_ID"

echo "===== TRANSLATE ====="

if [[ -n "$CONTEXT" ]]; then
    echo "Context: $CONTEXT"
    uv run src/translate.py "data/_${VIDEO_ID}/_${VIDEO_ID}.tsv" --context "$CONTEXT"
else
    echo "No context provided"
    uv run src/translate.py "data/_${VIDEO_ID}/_${VIDEO_ID}.tsv"
fi

echo "===== EXPORT ====="
uv run src/export.py "$VIDEO_ID"
