from dataclasses import dataclass


@dataclass
class PreprocessingConfig(object):
    lowercase: bool = True
    lemmatize: bool = True
    remove_stop: bool = True
    remove_punctuation: bool = True
    replace_numbers: bool = True
    ascii_only: bool = True
    per_line: bool = True
    deduplicate_chorus: bool = True


@dataclass
class Word2VecConfig(object):
    vector_size: int = 100
    alpha: float = 0.025
    window: int = 5
    min_count: int = 5
    max_vocab_size: int = None
    sample: int = int(1e-3)
    seed: int = 1
    workers: int = 3
    min_alpha: float = 1e-4
    sg: int = 0
    hs: int = 0
    negative: int = 5
    ns_exponent: float = 0.75
    cbow_mean: int = 1
    epochs: int = 5
    null_word: int = 0
    sorted_vocab: int = 1


@dataclass
class FastTextConfig(Word2VecConfig):
    min_n: int = 5
    max_n: int = 8
    bucket: int = int(2e6)


@dataclass
class PhraserConfig(object):
    min_count: int = 5
    threshold: float = 10.0
    max_vocab_size: int = int(4e7)
    scoring: str = "default"
    max_phrase_length: int = 2


@dataclass
class Doc2VecConfig(object):
    vector_size: int = 100
    alpha: float = 0.025
    window: int = 5
    min_count: int = 5
    max_vocab_size: int = None
    sample: int = int(1e-3)
    seed: int = 1
    workers: int = 3
    min_alpha: float = 1e-4
    epochs: int = 10
    hs: int = 0
    negative: int = 5
    ns_exponent: float = 0.75
    dm: bool = True
    dm_mean: bool = None
    dm_concat: bool = False
    dbow_words: bool = False
    dm_tag_count: int = 1
    shrink_window: bool = True
