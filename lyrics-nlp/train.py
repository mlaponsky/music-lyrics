from typing import Dict
import logging
import click
import json
from lyrics_nlp.config import Word2VecConfig, PhraserConfig, FastTextConfig
from lyrics_nlp.embedding.words import WordEmbeddingTrainer


logger = logging.getLogger(__name__)


@click.command()
@click.option("--train-phrases/--no-phrases", default=True)
@click.option("-f", "--input-file", required=True, type=str)
@click.option("-o", "--output-dir", default="target", type=str)
def main(train_phrases: bool, input_file: str, output_dir: str):
    with open("config.json") as f:
        config = json.load(f)
    model_config: Dict = config["model"]
    model_params: Dict = model_config["params"]
    config_type: type = Word2VecConfig if model_config["type"] == "word2vec" else FastTextConfig
    wv_config = config_type(**model_params)
    phraser_config = PhraserConfig() if train_phrases else None
    client = WordEmbeddingTrainer.build(model_config=wv_config,
                                        target_dir=output_dir,
                                        phraser_config=phraser_config)
    client.train(input_file)


if __name__ == "__main__":
    main()
