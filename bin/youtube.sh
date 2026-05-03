#!/bin/bash

VIDEO_ID=$1

echo "===== DOWNLOAD ====="
uv run src/download.py "$VIDEO_ID"

echo "===== PARSE ====="
uv run src/parse.py "$VIDEO_ID"

echo "===== EXTRACT ====="
uv run src/extract.py "$VIDEO_ID"

echo "===== TRANSLATE ====="
echo "Any context? (Press [Enter] to continue)"
read context

if [[ -n "$context" ]]; then
    uv run src/translate.py "data/_${VIDEO_ID}/_${VIDEO_ID}.tsv" --context "$context"
else
    echo "translate without context"
    uv run src/translate.py "data/_${VIDEO_ID}/_${VIDEO_ID}.tsv"
fi

