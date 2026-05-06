#!/bin/env bash
MEDIA_DIR=data/_$1/segments
cp $MEDIA_DIR/* $HOME/.local/share/Anki2/main/collection.media
