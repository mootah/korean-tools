import re
import csv
import rich_click as click
import webvtt
import html
from pathlib import Path


@click.command()
@click.argument('video_id')
def main(video_id):
    """
    Parse a vtt subtitle file and output a TSV file with start, end, and text columns.
    Assumes files are in data/_{video_id}/ directory.
    """
    base_dir = Path("data") / f"_{video_id}"
    input_file = base_dir / f"_{video_id}.vtt"
    output = base_dir / f"_{video_id}.tsv"
    
    if not input_file.exists():
        click.secho(f"Error: Input file not found: {input_file}", fg="red")
        return

    with open(output, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['id', 'start', 'end', 'sentence'])

        try:
            vtt = webvtt.read(input_file)
        except Exception as e:
            click.secho(f"Error parsing VTT: {e}", fg="red")
            return

        for i, caption in enumerate(vtt):
            idx = f"yt_{video_id}_{i:05d}"
            
            start = int(caption.start_in_seconds * 1000)
            end = int(caption.end_in_seconds * 1000)

            text_content = caption.text.replace('\n', ' ').strip()
            text_content = html.unescape(text_content)
            text_content = re.sub(r'[\[\]]', '"', text_content)

            if not text_content:
                continue

            writer.writerow([idx, start, end, text_content])
            
    click.secho(f"Successfully parsed '{input_file}' and saved to '{output}'", fg="green")

if __name__ == '__main__':
    main()
