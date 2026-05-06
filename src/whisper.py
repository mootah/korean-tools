from numpy.__config__ import show
import rich_click as click
import webvtt
from pathlib import Path
from faster_whisper import WhisperModel

def fmt_time(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    ms = int((t - int(t)) * 1000)
    return f"{h:02}:{m:02}:{s:02}.{ms:03}"

@click.command()
@click.option('--input_file', '-i', type=click.Path(exists=True), required=True, help="Path to the input mp4 file.")
@click.option('--lang','-l', default="ko", help="Language of the video.", show_default=True)
@click.option('--output_file', '-o', type=click.Path(), help="Path to the output vtt file. Defaults to input file with .vtt extension.")
@click.option('--model_name', '-m', default="ghost613/faster-whisper-large-v3-turbo-korean", help="Name of the model to use.", show_default=True)
def main(input_file, output_file, lang, model_name):
    """Transcribe an MP4 file to a VTT file."""
    input_file = Path(input_file)
    if output_file:
        out_file = Path(output_file)
    else:
        out_file = input_file.with_suffix(".vtt")

    model = WhisperModel(
        model_name,
        device="cpu",
        compute_type="int8"
    )

    click.echo(f"Transcribing {input_file}...")
    segments, info = model.transcribe(
        str(input_file),
        language=lang,
        vad_filter=False,
        beam_size=10,
        condition_on_previous_text=False,
        # length_penalty=0.8,
        word_timestamps=True,
        log_progress=True
    )

    vtt = webvtt.WebVTT()

    for segment in segments:
        for word in segment.words:
            start_str = fmt_time(word.start)
            end_str = fmt_time(word.end)
            text = word.word.strip()
            
            if text:
                caption = webvtt.Caption(
                    start_str,
                    end_str,
                    text
                )
                vtt.captions.append(caption)

        # start_str = fmt_time(segment.start)
        # end_str = fmt_time(segment.end)
        # text = segment.text.strip()
        # caption = webvtt.Caption(
        #     start_str,
        #     end_str,
        #     text
        # )
        # vtt.captions.append(caption)

    vtt.save(str(out_file))
    click.secho(f"Finished writing subtitles to {out_file}", fg="green")

if __name__ == "__main__":
    main()
