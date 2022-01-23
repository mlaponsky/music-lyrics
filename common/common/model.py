from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict


@dataclass(frozen=True)
class NodeModel(object):
    pass


@dataclass(frozen=True)
class Song(NodeModel):
    title_label: str
    artist_label: str
    album_label: str
    artist: Optional[str] = None
    album: Optional[str] = None
    title: Optional[str] = None
    lyrics: List[str] = field(default_factory=list)
