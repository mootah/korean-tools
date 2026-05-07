import os
import csv
import subprocess
import rich_click as click
from pathlib import Path
import concurrent.futures

def process_segment(idx, start_ms, end_ms, mp4_file, output_dir):
    start_sec = start_ms / 1000.0
    duration_sec = (end_ms - start_ms) / 1000.0
    mid_sec = start_sec + (duration_sec / 2.0)
    
    out_webp = output_dir / f"{idx}.webp"
    out_webm = output_dir / f"{idx}.webm"
    
    # Extract Image (WebP) at the middle of the segment
    # Fast seek using -ss before -i. 
    # Scale width to 480px, maintaining aspect ratio. Quality 50.
    cmd_image = [
        "ffmpeg", "-y", "-v", "error",
        "-ss", str(mid_sec),
        "-i", str(mp4_file),
        "-vframes", "1",
        "-c:v", "libwebp",
        "-q:v", "50",
        "-vf", "scale=480:-1",
        str(out_webp)
    ]
    
    # Extract Audio (WebM/Opus) for the segment
    # -vn to remove video. Bitrate 48k is good for speech.
    cmd_audio = [
        "ffmpeg", "-y", "-v", "error",
        "-ss", str(start_sec),
        "-i", str(mp4_file),
        "-t", str(duration_sec),
        "-vn",
        "-c:a", "libopus",
        "-b:a", "48k",
        str(out_webm)
    ]

    subprocess.run(cmd_image, check=True)
    subprocess.run(cmd_audio, check=True)

@click.command()
@click.argument('video_id')
@click.option('--mp4', type=click.Path(exists=True))
@click.option('--tsv', type=click.Path(exists=True))
@click.option('--out', type=click.Path())
@click.option('--workers', default=os.cpu_count() or 4, help="Number of concurrent ffmpeg processes.")
def main(video_id, mp4, tsv, out, workers):
    """
    Extract screenshots and audio segments from a video based on a TSV file.
    Output is saved in data/_{video_id}/segments/
    """
    
    if mp4 is None:
        mp4 = f"data/_{video_id}/_{video_id}.mp4"
    if tsv is None:
        tsv = f"data/_{video_id}/_{video_id}.tsv"
    if out is None:
        out = f"data/_{video_id}/segments"

    mp4_file = Path(mp4)
    tsv_file = Path(tsv)
    output_dir = Path(out)
    
    if not mp4_file.exists():
        click.secho(f"Error: Video file not found: {mp4_file}", fg="red")
        return
    if not tsv_file.exists():
        click.secho(f"Error: TSV file not found: {tsv_file}", fg="red")
        return
        
    output_dir.mkdir(parents=True, exist_ok=True)
    
    segments = []
    with open(tsv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            try:
                start = int(row['start'])
                end = int(row['end'])
                segments.append((row['id'], start, end))
            except (ValueError, KeyError):
                continue
                
    click.echo(f"Found {len(segments)} segments. Extracting...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = []
        for idx, start, end in segments:
            futures.append(
                executor.submit(process_segment, idx, start, end, mp4_file, output_dir)
            )
            
        with click.progressbar(concurrent.futures.as_completed(futures), length=len(futures), label="Extracting") as bar:
            for future in bar:
                try:
                    future.result()
                except Exception as e:
                    click.secho(f"\nError processing segment: {e}", fg="red")
                    
    click.secho(f"Finished extracting to {output_dir}", fg="green")

if __name__ == '__main__':
    main()
