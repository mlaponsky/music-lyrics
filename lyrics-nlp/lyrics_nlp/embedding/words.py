import uuid
import os
import json
import logging
from copy import copy
from datetime import datetime
from gensim.models import FastText, Word2Vec
from gensim.models.word2vec import LineSentence
from gensim.models.keyedvectors import KeyedVectors
from gensim.models.phrases import ENGLISH_CONNECTOR_WORDS
from lyrics_nlp.embedding.utils import MonitorCallback
from lyrics_nlp.config import Word2VecConfig, FastTextConfig, PhraserConfig
from lyrics_nlp.preprocess import construct_phraser, Phraser

logger = logging.getLogger(__name__)

Corpus = (LineSentence, str)


def get_model_type(config: Word2VecConfig):
    if isinstance(config, FastTextConfig):
        return FastText
    return Word2Vec


class WordEmbeddingTrainer(object):
    def __init__(self,
                 id_: str,
                 model: Word2Vec,
                 target_dir: str,
                 phraser: Phraser = None):
        self._id: str = id_
        self._target_dir: str = target_dir
        self._model: Word2Vec = model
        self._label: str = self._get_label()
        self._phraser: Phraser = phraser

    @classmethod
    def build(cls,
              model_config: Word2VecConfig,
              target_dir: str = None,
              phraser_config: PhraserConfig = None):
        id_: str = uuid.uuid4().hex[:8]
        target_dir = os.path.join(target_dir or str(),
                                  "models",
                                  str(int(datetime.now().timestamp())))
        os.makedirs(target_dir, exist_ok=True)

        model_type = get_model_type(model_config)
        model = model_type(callbacks=[MonitorCallback()], **model_config.__dict__)

        config = dict(model=model_config.__dict__,
                      phraser=phraser_config.__dict__ if phraser_config else None)
        logger.info(f"Model Config = {model_config}")
        logger.info(f"Phraser Config = {phraser_config}")
        with open(os.path.join(target_dir, "model_parameters.json"), "w") as f:
            json.dump(config, f, indent=4, sort_keys=True)

        phraser = None
        if phraser_config:
            params = copy(phraser_config.__dict__)
            del params["max_phrase_length"]
            params["connector_words"] = ENGLISH_CONNECTOR_WORDS
            phraser = Phraser(phraser=construct_phraser(params),
                              max_phrase_length=phraser_config.max_phrase_length)
        return cls(id_=id_,
                   target_dir=target_dir,
                   model=model,
                   phraser=phraser)

    def train(self, corpus: str) -> None:
        if self._phraser:
            corpus = LineSentence(corpus)
            phrases_file = os.path.join(self._target_dir,
                                        f"phrases_max={self._phraser.max_phrase_length}.corpus")
            self._phraser.build_corpus(corpus, phrases_file)
            corpus = phrases_file
        self._train_model(corpus)

    def _train_model(self, corpus: Corpus):
        key = "corpus_iterable" if isinstance(corpus, LineSentence) else "corpus_file"
        kwargs = {key: corpus}
        logger.info("Building vocab....")
        self._model.build_vocab(**kwargs)
        logger.info(f"Training {self._label} model....")
        self._model.train(epochs=self._model.epochs,
                          total_examples=self._model.corpus_count,
                          total_words=self._model.corpus_total_words,
                          **kwargs)
        self._model.save(os.path.join(self._target_dir, f"{self._label}.model"))
        self._model.wv.save(os.path.join(self._target_dir, f"{self._label}.vectors"))

    def _get_label(self) -> str:
        if isinstance(self._model, FastText):
            return "fasttext"
        return "word2vec"


class WordVectors(object):
    def __init__(self, vectors: KeyedVectors):
        self._vectors: KeyedVectors = vectors
