from typing import Iterable, List

import logging
from pathlib import Path

from scrapy import Selector
from scrapy.http import Response
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor

logger = logging.getLogger()

BASE_URL: str = r"http://ohhla.com/"
STARTING_PAGES: Iterable[str] = (r"all.html",
                                 r"all_two.html",
                                 r"all_three.html",
                                 r"all_four.html,"
                                 r"all_five.html")
# INTERMEDIATES: Iterable[str] = (r".*/anonymous/", r".*/#.*")
# TO_DENY = [f"{BASE_URL}/{i}" for i in INTERMEDIATES]
TO_DENY = []

ARTIST_RULE: Rule = Rule(
    LinkExtractor(allow=("http://ohhla.com/anonymous/.+",
                         "http://ohhla.com/YFA_.+html"),
                  deny=TO_DENY,
                  deny_extensions=("txt",)),
    follow=True
)

SONG_RULE: Rule = Rule(
    LinkExtractor(allow=("http://ohhla.com/anonymous/.*txt",)),
    callback="download_lyrics",
)

ALBUM_RULE: Rule = Rule(
    LinkExtractor(restrict_xpaths='/html/body/table/tr/td//a',
                  deny=TO_DENY),
)

ALBUM_TABLE_RULE: Rule = Rule(
    LinkExtractor(restrict_xpaths='//*[@id="leftmain"]//a',
                  deny=TO_DENY),
)

ENABLED_RULES = (ARTIST_RULE, SONG_RULE)


class OhhlaException(Exception):
    def __init__(self, message: str):
        self.message: str = message
        super().__init__(message)


class OhhlaSpider(CrawlSpider):
    name = "ohhla"
    allowed_domains = ["ohhla.com", "OHHLA.com", "www.ohhla.com", "www.OHHLA.com"]
    start_urls: Iterable[str] = [f"{BASE_URL}{p}" for p in STARTING_PAGES]
    rules = ENABLED_RULES

    def __init__(self, output_dir: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._output_dir: str = output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Output dir = {output_dir}.")

    def download_lyrics(self, response: Response):
        # self.logger.info(f"Downloading {response.url}")
        download_location: str = response.url.split("anonymous")[-1].strip("/")
        fpath = Path(self._output_dir, download_location)
        if fpath.exists():
            return
        fpath.parent.mkdir(parents=True, exist_ok=True)
        try:
            lyrics: str = self._get_lyrics_text(response)
            with fpath.open("w") as f:
                f.write(lyrics)
            self.logger.info(f"Saved {fpath}.")
        except OhhlaException as e:
            self.logger.warn(e.message)
        return

    @staticmethod
    def _get_lyrics_text(response: Response) -> str:
        selectors: List[Selector] = response.xpath("//pre")
        if not selectors:
            try:
                return response.body.decode("latin1")
            except Exception:
                raise OhhlaException(f"Skipping {response.url}; could not decode into 'latin1' encoding.")
        elif len(selectors) > 1:
            raise OhhlaException(f"Skipping {response.url}; non-conformant for a song page.")
        else:
            return response.xpath("//pre")[0].root.text
