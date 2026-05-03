from pathlib import Path
import rich_click as click
from yt_dlp import YoutubeDL

@click.command()
@click.argument("video_id")
@click.option("--lang", "-l", default="ko", help="Subtitle language")
@click.option("--write-auto-subs", is_flag=True, help="Download auto-generated subtitles")
@click.option("--subs-only", is_flag=True, help="Download only subtitles")
@click.option("--force", "-f", is_flag=True, help="Force download even if file already exists")
def download(video_id: str, lang: str, write_auto_subs: bool, subs_only: bool, force: bool):
    """Download video and subtitles from YouTube."""
    ydl_opts = {
        'format': '18',
        'outtmpl': f'data/_{video_id}/_{video_id}.%(ext)s',
        'writesubtitles': True,
        'writeautomaticsub': write_auto_subs,
        'subtitleslangs': [lang],
        'subtitlesformat': 'srv2',
        'skip_download': subs_only,
        'overwrites': force,
    }
    
    url = f'https://www.youtube.com/watch?v={video_id}'
    
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    base_dir = Path("data") / f"_{video_id}"
    subtitle_file = base_dir / f"_{video_id}.{lang}.srv2"
    target_file = base_dir / f"_{video_id}.srv2"
    
    if subtitle_file.exists():
        if target_file.exists():
            target_file.unlink()
        subtitle_file.rename(target_file)

if __name__ == '__main__':
    download()