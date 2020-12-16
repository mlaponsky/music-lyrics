from dataclasses import dataclass
import re

ARTIST_PATTERN: str = r"^(artist:)"
ALBUM_PATTERN: str = r"^(album:)"
SONG_PATTERN: str = r"^(song:)"


@dataclass
class OhhlaRegex(object):
    artist: re.Pattern
    album: re.Pattern
    song: re.Pattern

    @classmethod
    def build(cls):
        return cls(artist=re.compile(ARTIST_PATTERN, re.IGNORECASE),
                   album=re.compile(ALBUM_PATTERN, re.IGNORECASE),
                   song=re.compile(SONG_PATTERN, re.IGNORECASE))
