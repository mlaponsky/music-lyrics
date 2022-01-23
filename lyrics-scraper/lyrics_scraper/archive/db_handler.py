import pymysql as mysql
import os


def start_connection():
    # Connects to set database with my local pwd; returns both conn and cursor.
    conn = mysql.connect(host='localhost',
                         port=3306,
                         username="root",
                         pwd=os.environ.get('MYSQL_PWD'))
    cur = conn.cursor()
    return conn, cur
