import logging
import os
import spacy
import json
from datetime import datetime

from gensim.models import Phrases
from gensim.models.word2vec import LineSentence
from spacy.tokens.doc import Doc
from tqdm import tqdm
from spacy.language import Language
from typing import IO, Iterator, Callable, Iterable, Dict, Any
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from common.model import Song
from spacy.tokens.token import Token
from lyrics_nlp.config import PreprocessingConfig


LANG_TAG = "en"
NUMBER_MASK = "numtoken"
DATE_FMT = "%Y%m%d"
EXTRA_PUNCTUATION = ("+", "+", "*", "~")

PhraseCorpus = (Iterable, LineSentence)

logger = logging.getLogger(__name__)


def _deduplicate_chorus(lyrics: Iterable[str]) -> Iterable[str]:
    lyric_set = set()
    final_lyrics = []
    for line in lyrics:
        lyric = line.strip()
        if lyric not in lyric_set:
            lyric_set.add(lyric)
            final_lyrics.append(lyric)
    del lyric_set
    return final_lyrics


def stream_songs(infile: IO,
                 text_transformer: Callable[[str], str],
                 per_line: bool = True,
                 deduplicate_chorus: bool = True) -> Iterator[str]:
    songs = (Song(**json.loads(line)) for line in infile)
    for song in songs:
        lyrics: Iterable[str] = _deduplicate_chorus(song.lyrics) if deduplicate_chorus else song.lyrics
        lyrics = [" ".join(lyrics)] if per_line else lyrics
        for lyric in lyrics:
            lyric = text_transformer(lyric)
            try:
                if detect(lyric) == LANG_TAG:
                    yield lyric
            except LangDetectException:
                continue


def preprocess_corpus(in_path: str,
                      target_dir: str,
                      config: PreprocessingConfig = None,
                      spacy_model: str = None):
    if not config:
        config = PreprocessingConfig()
    target_dir = os.path.join(target_dir,
                              "preprocessing",
                              str(int(datetime.now().timestamp())))
    os.makedirs(target_dir, exist_ok=True)
    with open(os.path.join(target_dir, "preprocess.json"), "w") as f:
        json.dump(config.__dict__, f, indent=4, sort_keys=True)
    if not spacy_model:
        nlp = spacy.blank("en")
    else:
        nlp = spacy.load(spacy_model)
    processor = processor_factory(nlp=nlp, target_dir=target_dir, config=config)
    processor(in_path)


def processor_factory(nlp: Language, target_dir: str, config: PreprocessingConfig, n_process: int = 2):

    def replace_numbers(tokens: Iterable[Token]) -> Iterable[Token]:
        words = []
        spaces = []
        for token in tokens:
            if token.is_digit:
                words.append(NUMBER_MASK)
            else:
                words.append(token.text)
            spaces.append(True if token.whitespace_ else False)
        doc = Doc(vocab=nlp.vocab, words=words, spaces=spaces)
        return list(doc)

    def processor_method():
        if config.lemmatize:
            return lambda texts: nlp.pipe(texts, n_process=n_process)
        return nlp.tokenizer.pipe

    def transform_text(text: str):
        text = text.replace("\n", " ")
        if config.remove_punctuation:
            for char in EXTRA_PUNCTUATION:
                text = text.replace(char, "")
        if config.lowercase:
            return text.lower()
        return text

    def process(in_path: str):
        out_path: str = os.path.join(target_dir, "raw.corpus")
        with open(in_path) as infile, open(out_path, "w") as outfile:
            lyrics = stream_songs(infile, transform_text)
            processor = processor_method()
            for doc in tqdm(processor(lyrics)):
                tokens = [token for token in doc]
                if config.ascii_only:
                    tokens = [t for t in tokens if t.is_ascii]
                if config.remove_stop:
                    tokens = [t for t in tokens if not t.is_stop]
                if config.remove_punctuation:
                    tokens = [t for t in tokens if not t.is_punct]
                if config.replace_numbers:
                    tokens = replace_numbers(tokens)
                outfile.write(" ".join(t.text for t in tokens))
                outfile.write("\n")

    return process


def construct_phraser(params: Dict[str, Any]) -> Callable:

    def build_phraser(sentences: PhraseCorpus) -> Phrases:
        return Phrases(sentences=sentences, **params)

    return build_phraser


class Phraser(object):
    def __init__(self,
                 phraser: Callable,
                 max_phrase_length: int):
        self._phraser: Callable[[Dict[str, Any]], PhraseCorpus] = phraser
        self._max_phrase_length: int = max_phrase_length
        self._current_length: int = 1

    @property
    def max_phrase_length(self):
        return self._max_phrase_length

    def build_corpus(self, corpus: PhraseCorpus, outfile: str) -> None:
        self._current_length += 1
        phrases: Phrases = self._phraser(corpus)
        logger.info(f"Building phrases of length {self._current_length} "
                    f"(maximum length = {self._max_phrase_length})...")
        with open(outfile, "w", encoding="utf-8") as f:
            for sentence in corpus:
                phrase_sentence = u" ".join(phrases[sentence])
                f.write(f"{phrase_sentence}\n")
        if self._current_length == self._max_phrase_length:
            return
        return self.build_corpus(LineSentence(outfile), outfile)