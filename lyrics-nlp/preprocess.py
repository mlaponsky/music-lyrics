import click
import logging
from lyrics_nlp.config import PreprocessingConfig
from lyrics_nlp.preprocess import preprocess_corpus


logger = logging.getLogger(__name__)


@click.command()
@click.option("-f", "--input-file", type=str, required=True)
@click.option("-o", "--output-dir", type=str, default="target")
@click.option("-m", "--spacy-model", type=str, default="en_core_web_lg")
@click.option("--lemmatize/--unlemmatized", default=True)
@click.option("--uncased/--cased", default=True)
@click.option("--remove-stop/--keep-stop", default=True)
@click.option("--replace-numbers/--keep-numbers", default=True)
@click.option("--remove_punctuation/--keep-punctuation", default=True)
@click.option("--ascii-only/--non-ascii", default=True)
@click.option("--per-line/--single-line", default=True)
@click.option("--deduplicate/--keep-chorus", default=True)
def main(input_file: str,
         output_dir: str,
         spacy_model: str,
         lemmatize: bool,
         uncased: bool,
         remove_stop: bool,
         replace_numbers: bool,
         remove_punctuation: bool,
         ascii_only: bool,
         per_line: bool,
         deduplicate: bool):
    config = PreprocessingConfig(lowercase=uncased,
                                 lemmatize=lemmatize,
                                 remove_stop=remove_stop,
                                 replace_numbers=replace_numbers,
                                 remove_punctuation=remove_punctuation,
                                 ascii_only=ascii_only,
                                 per_line=per_line,
                                 deduplicate_chorus=deduplicate)
    logger.info(f"Preprocessing config = {config}")
    preprocess_corpus(in_path=input_file, target_dir=output_dir, config=config, spacy_model=spacy_model)


if __name__ == "__main__":
    main()
