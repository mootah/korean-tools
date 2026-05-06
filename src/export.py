import csv
import rich_click as click
from pathlib import Path

@click.command()
@click.argument('video_id', required=True)
@click.option('-i', '--input', 'input_file', type=click.Path(exists=True), help='Input translated TSV file.')
@click.option('-o', '--output', 'output_file', type=click.Path(), help='Output Anki TSV file.')
def main(video_id, input_file, output_file):
    """
    Create a TSV file for Anki import.
    """

    if not input_file:
        input_file = Path('data') / f"_{video_id}" / f"_{video_id}.translated.tsv"
    if not output_file:
        output_file = Path('data') / f"_{video_id}" / f"_{video_id}.anki.tsv"

    input_path = Path(input_file)
    output_path = Path(output_file)

    if not input_path.exists():
        click.secho(f"Error: Input file not found: {input_path}", fg="red")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(input_path, 'r', encoding='utf-8') as f_in, \
         open(output_path, 'w', encoding='utf-8', newline='') as f_out:
         
        reader = csv.DictReader(f_in, delimiter='\t')
        
        fieldnames = ['id', 'sentence', 'sentence_ja', 'audio', 'image', 'url']
        writer = csv.DictWriter(f_out, fieldnames=fieldnames, delimiter='\t')
        
        # Write header
        writer.writeheader()
        
        for row in reader:
            row_id = row.get('id', '')
            try:
                start_ms = int(row.get('start', 0))
                start_s = start_ms // 1000
            except ValueError:
                start_s = 0
                
            writer.writerow({
                'id': row_id,
                'sentence': row.get('sentence', ''),
                'sentence_ja': row.get('sentence_ja', ''),
                'audio': f'[sound:{row_id}.webm]',
                'image': f'<img src="{row_id}.webp">',
                'url': f'https://youtu.be/{video_id}?t={start_s}'
            })

    click.secho(f"Successfully created Anki import file '{output_path}'", fg="green")

if __name__ == '__main__':
    main()
