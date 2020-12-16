import pymysql as mysql
import json
import datetime
import re
import sys
import time
import os

conn = mysql.connect(host='localhost',
                     port=3306,
                     username="root",
                     pwd=os.environ.get('MYSQL_PWD'))
cur = conn.cursor()

def init_wiki():
    return wiki.Site('en', 'wikipedia')

def fetch_page(enwp, query):
    # Gets the page object for a query.
    return wiki.Page(enwp, query)

def fetch_links(page):
    '''
       Gets list of all pages linked to by the parameter page.
       Ignores other list pages.
       Returns a list of page objects.
    '''
    return [p for p in page.linkedPages(namespaces=0) if
                                 "List of" not in p.title()]
