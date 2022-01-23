import json
from typing import Iterator, IO, Iterable, Optional, List
import logging
from common.model import Song
from lyrics.ohhla import OhhlaRegex
from lyrics.utils import strip_match
import uuid

logger = logging.getLogger()


class OhhlaParser(object):
    def __init__(self,
                 patterns_map: OhhlaRegex,
                 results_path: str,
                 exceptions_path: str):
        self._patterns_map: OhhlaRegex = patterns_map
        self._results_path: str = results_path
        self._exceptions_path: str = exceptions_path
        self._success: int = 0
        self._failure: int = 0

    @classmethod
    def build(cls, results_path: str, exceptions_path: str):
        return cls(patterns_map=OhhlaRegex.build(),
                   results_path=results_path,
                   exceptions_path=exceptions_path)

    def __repr__(self) -> str:
        return ("Parser Results:\n"
                f"\t -> Results path: {self._results_path}\n"
                f"\t -> Exceptions path: {self._exceptions_path}\n"
                f"\t -> {self._success} songs successfully parsed, "
                f"{self._failure} edge cases.")

    def extract(self, files: Iterable[str]):
        with open(self._results_path, "w") as results_file, \
                open(self._exceptions_path, "w") as exceptions_file:
            for filepath in files:
                self._save(infile=filepath,
                           results_file=results_file,
                           exceptions_file=exceptions_file)

    def _save(self,
              infile: str,
              results_file: IO,
              exceptions_file: IO) -> None:
        song: Song = self._parse_page(infile)
        if not all(song.__dict__.values()):
            filepath: str = f"{song.album_label}/{song.album_label}/{song.title_label}"
            logger.warning(f"Failed for {filepath}.")
            exceptions_file.write(f"{filepath}\n")
            self._failure += 1
        else:
            results_file.write(f"{json.dumps(song.__dict__)}\n")
            self._success += 1
        return

    def _parse_page(self, filepath: str) -> Song:
        artist_label, album_label, title_label = filepath.split("/")[-3:]
        title: Optional[str] = None
        album: Optional[str] = None
        artist: Optional[str] = None
        lyrics: List[str] = []
        try:
            lines: Iterator[str] = _open_page(filepath)
            for _ in range(4):
                line = next(lines)
                title = self._fill_title(line, title)
                album = self._fill_album(line, album)
                artist = self._fill_artist(line, artist)
            lyrics = list(lines)
        except StopIteration:
            pass
        return Song(artist_label=artist_label,
                    album_label=album_label,
                    title_label=title_label,
                    artist=artist,
                    album=album,
                    title=title,
                    lyrics=lyrics)

    def _fill_title(self, line: str, title: Optional[str]) -> Optional[str]:
        if not title:
            title = strip_match(line, self._patterns_map.song)
        return title

    def _fill_artist(self, line: str, artist: Optional[str]) -> Optional[str]:
        if not artist:
            artist = strip_match(line, self._patterns_map.artist)
        return artist

    def _fill_album(self, line: str, album: Optional[str]) -> Optional[str]:
        if not album:
            album = strip_match(line, self._patterns_map.album)
        return album


def _open_page(filepath: str) -> Iterator[str]:
    with open(filepath, "r") as f:
        for line in f:
            cleaned_line = line.strip()
            if cleaned_line:
                yield cleaned_line
