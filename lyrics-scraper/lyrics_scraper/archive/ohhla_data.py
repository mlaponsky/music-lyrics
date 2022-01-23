import pymysql as mysql
import json
import datetime
import re
import sys
import time
import os
import re

from bs4 import BeautifulSoup
from urllib.parse import quote
from urllib.request import urlopen
from urllib.error import HTTPError, URLError


conn = mysql.connect(host='localhost',
                     port=3306,
                     username="root",
                     pwd=os.environ.get('MYSQL_PWD'))
cur = conn.cursor()

BASE_URL = "http://www.ohhla.com/"
SECTION_LINKS = ['all' 'all_two', 'all_three',
                 'all_four', 'all_five', 'soundtracks']
BASE_DIV = "leftmain"

def get_artist_links(section):
    url = BASE_URL + section + ".html"
    html = urlopen(url).read()
    soup = BeautifulSoup(html)
    links = soup.find("div", {"id": BASE_DIV})
                .find("pre")
                .findAll("a")[1:]
    return links

def fetch_artists(links):
    for link in links:
        cur.execute("""INSERT INTO rap_artists (artist_name)
                       VALUES (%s)""",(link.getText()))
        conn.commit()
        artist_id = cur.execute("""SELECT id FROM rap_artists
                                    WHERE artist_name = (%s)""",
                                    (link.getText()))
        cur.execute("""INSERT INTO alt_names (id, name) VALUES (%s, %s)""",
                                                (artist_id, link.getText()))
        return

def parse_title_row(title_string):
    title = title_string.strip()
    title = title.strip("BUY NOW!")
    title_array = title.split(" - ")
    artist, album = title[0], title[1]
    return artist, album

def fetch_from_plain(soup):

    return

def fetch_from_soundtrack(link):
    html = urlopen(BASE_URL + link).read()
    soup = BeautifulSoup(html, "html5lib")
    container = soup.find("div",{"id": BASE_DIV})
    albums = container.findAll("p")
    for album in albums:
        tracks = album.findAll("tr")
def fetch_from_tabled(link):
    """ Function to retreive song links and metadata
        for the table-formatted artist pages.

        FOR rap_artists:
          -- artist_name

        FOR rap_collabs:
          -- primary artist if in "misc" category

        FOR rap_songs:
          -- song_name
          -- primary artist (id from rap_artists after registered)
          -- date
          -- album
          -- lyrics
    """

    html = urlopen(BASE_URL + link).read()
    soup = BeautifulSoup(html, "html5lib")
    container = soup.find("div",{"id": BASE_DIV})
    albums = container.findAll("p")
    tp = re.compile("\d{4}\).*")
    ap = re.compile("\nArtist.*\n", re.M)
    for album in albums:
        tracks = album.findAll("tr")
        if album.find("a").getText() == "remix":
            for t in tracks[2:]:
                t_meta = t.findAll("td")
                lyrics = fetch_lyrics(t.find("a").get("href"))
        elif album.find("a").getText() == "misc"
            for t in tracks[2:]:
                t_meta = t.findAll("td")
                lyrics = fetch_lyrics(t.find("a").get("href"))
        else:
            # title_string = parse_title_row(rows[0].getText()
            #                                       .strip(p.findall(title_string)[0][6:])
            #                                       .strip()
            # title_array = title_string.split(' - ')
            # album_plus_date = title_array[1]
            # album_array = album_plus_date.split("(")
            #
            # album_title = album_array[0].strip()
            # date = album_array[1].strip(")")
            for t in tracks[2:]:
                t_meta = t.findAll("td")
                song_name = t_meta[1].getText()
                lyrics = fetch_lyrics(t.find("a").get("href"))
    return

def fetch_lyrics(link):
    html = urlopen(BASE_URL+link).read()
    soup = BeautifulSoup(html)
    return soup.find("pre").getText()

def parse_lyrics(text):
    artist_raw = re.findall("\nArtist.*\n", text, re.M)[0].strip()
    artist_plus = re.sub('Artist: ', '', artist_raw)
    artist_array = artist_plus.split('f/')
    artist = artist_array[0]
    collabs = []
    if len(artist_array) > 1:
        collabs = artist[1].split(',')

    album_raw = re.findall("\nAlbum.*\n", text, re.M)[0].strip()
    album = re.sub('Album: ', '', album_raw)

    song_raw = re.findall("\nSong.*\n", text, re.M)[0].strip()
    song = re.sub("Song: ", '', song_raw)
    return song, album, artist, collabs
