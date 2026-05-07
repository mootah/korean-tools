# Tools for Learning Korean

## Usage

> [!NOTE]
> Dependencies: `uv`, `ffmpeg`, `yt-dlp`, `ollama` (with `translategemma:12b` model by default)


### Download video, parse into sentences, extract segments, translate sentences

```zsh
./bin/youtube.sh <video_id> [context for translation]
```

### Copy media files to the proper directories (Anki)

```zsh
./bin/install_media_into_anki.sh <video_id>
```
