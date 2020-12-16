from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=False)
class Song(object):
    path: str
    artist: str = None
    album: str = None
    title: str = None
    lyrics: List[str] = field(default_factory=list)
