import csv
import rich_click as click
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import warnings
import html
from pathlib import Path

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)


@click.command()
@click.argument('video_id')
def main(video_id):
    """
    Parse an srv2 subtitle file and output a TSV file with start, end, and text columns.
    Assumes files are in data/_{video_id}/ directory.
    """
    base_dir = Path("data") / f"_{video_id}"
    input_file = base_dir / f"_{video_id}.srv2"
    output = base_dir / f"_{video_id}.tsv"
    
    if not input_file.exists():
        click.secho(f"Error: Input file not found: {input_file}", fg="red")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    texts = soup.find_all('text')

    with open(output, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['id', 'start', 'end', 'sentence'])

        for i, text_tag in enumerate(texts):
            idx = f"yt_{video_id}_{i:05d}"
            t_str = text_tag.get('t')
            d_str = text_tag.get('d')
            
            if t_str is None or d_str is None:
                continue
            
            try:
                start = int(t_str)
                duration = int(d_str)
                end = start + duration
            except ValueError:
                continue

            text_content = text_tag.get_text(strip=True)
            text_content = html.unescape(text_content)

            if not text_content:
                continue

            writer.writerow([idx, start, end, text_content])
            
    click.secho(f"Successfully parsed '{input_file}' and saved to '{output}'", fg="green")

if __name__ == '__main__':
    main()
