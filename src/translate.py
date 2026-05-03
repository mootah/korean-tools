import csv
from pathlib import Path

import rich_click as click
from openai import OpenAI


@click.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option("--base-url", default="http://localhost:11434/v1", help="Base URL for local Ollama API")
@click.option("--model", default="translategemma:12b", help="Model to use for translation")
@click.option("--context", default="", help="Context for translation")
def translate(input_file: Path, base_url: str, model: str, context: str):
    """
    Translate the 'text' field of a TSV file to Japanese using a local Ollama model.
    The translated text is added to a new 'text_ja' field, and the output is written row by row.
    """
    # Initialize OpenAI client pointing to local Ollama
    client = OpenAI(
        base_url=base_url,
        api_key="ollama",  # API key is required by the SDK but not used by local Ollama
    )

    output_file = input_file.parent / f"{input_file.stem}.translated.tsv"

    with open(input_file, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile, delimiter="\t")
        
        if reader.fieldnames is None:
            click.secho("Error: Input file is empty or missing headers.", fg="red")
            return

        if "sentence" not in reader.fieldnames:
            click.secho("Error: 'sentence' field not found in the input TSV.", fg="red")
            return

        # Prepare output fieldnames
        output_fieldnames = list(reader.fieldnames)
        if "sentence_ja" not in output_fieldnames:
            # Insert 'text_ja' right after 'text'
            text_idx = output_fieldnames.index("sentence")
            output_fieldnames.insert(text_idx + 1, "sentence_ja")

        click.echo(f"Translating {input_file} -> {output_file} using {model}")

        # Open output file in write mode and write line by line
        with open(output_file, mode="w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fieldnames, delimiter="\t")
            writer.writeheader()
            outfile.flush()

            for row in reader:
                original_text = row.get("sentence", "").strip()
                
                if not original_text:
                    row["sentence_ja"] = ""
                    writer.writerow(row)
                    outfile.flush()
                    continue

                instruction = """
                    You are a professional translator.
                    Translate the given text into natural Japanese.
                    Output ONLY the translation without any extra comments or quotes.
                """
                
                if context:
                   instruction += f"\nContext: {context}"

                try:
                    response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {
                                "role": "system",
                                "content": instruction
                            },
                            {
                                "role": "user",
                                "content": original_text
                            }
                        ],
                        temperature=0.0,
                    )
                    translated_text = response.choices[0].message.content.strip()
                    row["sentence_ja"] = translated_text
                    
                    click.echo(f"Original : {original_text}")
                    click.echo(f"Translated: {translated_text}")
                    click.echo("-" * 40)
                    
                except Exception as e:
                    click.secho(f"Error during translation: {e}", fg="red")
                    row["text_ja"] = ""  # Leave blank on error or keep original
                
                # Write row and flush immediately to save progress
                writer.writerow(row)
                outfile.flush()

    click.secho("Translation completed successfully.", fg="green")


if __name__ == "__main__":
    translate()
