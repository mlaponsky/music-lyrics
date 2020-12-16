import json
import os
from typing import Iterator, IO, Iterable
import logging
import sys
sys.path.append("/Users/maxlaponsky/Projects/music-lyrics/lyrics-etl")
from lyrics.ohhla import OhhlaRegex
from lyrics.ohhla.model import Song
from lyrics.utils import strip_match, get_files


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
            logger.warning(f"Failed for {song.path}.")
            exceptions_file.write(f"{song.path}\n")
            self._failure += 1
        else:
            results_file.write(f"{json.dumps(song.__dict__)}\n")
            self._success += 1
        return

    def _parse_page(self, filepath: str) -> Song:
        path: str = "/".join(filepath.split("/")[-3:])
        song: Song = Song(path=path)
        try:
            lines: Iterator[str] = _open_page(filepath)
            for _ in range(4):
                line = next(lines)
                self._fill_title(line, song)
                self._fill_album(line, song)
                self._fill_artist(line, song)
            song.lyrics = list(lines)
            return song
        except StopIteration:
            return song

    def _fill_title(self, line: str, song: Song) -> None:
        if not song.title:
            song.title = strip_match(line, self._patterns_map.song)
        return

    def _fill_artist(self, line: str, song: Song) -> None:
        if not song.artist:
            song.artist = strip_match(line, self._patterns_map.artist)
        return

    def _fill_album(self, line: str, song: Song) -> None:
        if not song.album:
            song.album = strip_match(line, self._patterns_map.album)
        return


def _open_page(filepath: str) -> Iterator[str]:
    with open(filepath, "r") as f:
        for line in f:
            cleaned_line = line.strip()
            if cleaned_line:
                yield cleaned_line


if __name__ == "__main__":
    base_dir = "/Users/maxlaponsky/Projects/music-lyrics/"
    ROOT_DIR = os.path.join(base_dir, "lyrics-scraper/lyrics/data")
    outfile_path: str = os.path.join(base_dir, "lyrics-etl/target/songs.jsonl")
    exceptions_path: str = os.path.join(base_dir, "lyrics-etl/target/exceptions.jsonl")
    input_files: Iterable[str] = get_files(ROOT_DIR)
    parser = OhhlaParser.build(outfile_path, exceptions_path)
    parser.extract(input_files)
    print("===== LYRICS EXTRACTION COMPLETE =====")
    print(str(parser))
