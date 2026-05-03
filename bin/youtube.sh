#!/bin/bash

VIDEO_ID=$1

echo "===== DOWNLOAD ====="
uv run src/download.py "$VIDEO_ID"

echo "===== PARSE ====="
uv run src/parse.py "$VIDEO_ID"

echo "===== EXTRACT ====="
uv run src/extract.py "$VIDEO_ID"

echo "===== TRANSLATE ====="
read -p "Any context? (Press [Enter] to continue)" context

if [[ -n "$context" ]]; then
    uv run src/translate.py "$VIDEO_ID" --context "$context"
else
    uv run src/translate.py "$VIDEO_ID"
fi

