import datetime
import sqlite3
import os
from util import *

sql_create_album_table_string = 'CREATE TABLE albums (' \
                            'url text, ' \
                            'format text, ' \
                            'genre text, ' \
                            'label text, ' \
                            'style text, ' \
                            'title text, ' \
                            'artist text, ' \
                            'versions integer, ' \
                            'y integer' \
                            ')'

sql_create_artist_table_string = 'CREATE TABLE artists (' \
                                 'url text, ' \
                                 'arranged integer, ' \
                                 'arranged_cnt integer, ' \
                                 'credits integer, ' \
                                 'credits_cnt integer, ' \
                                 'lyrics integer, ' \
                                 'lyrics_cnt integer, ' \
                                 'music integer, ' \
                                 'music_cnt integer, ' \
                                 'name text, ' \
                                 'sites text, ' \
                                 'vocals integer,' \
                                 'vocals_cnt integer ' \
                                 ')'

sql_insert_album_string = "INSERT INTO albums VALUES (?,?,?,?,?,?,?,?,?)"


sql_insert_artist_string = "INSERT INTO artists VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)"



def create_tables_in_database():
    con = connect_to_database()
    c = con.cursor()

    c.execute(sql_create_album_table_string)
    c.execute(sql_create_artist_table_string)

    con.commit()
    con.close()

def insert_album_into_database(c, album:dict):
    c.execute(sql_insert_album_string,[
            album.get('url', ""),
            album.get('format', ""),
            album.get('genre', ""),
            album.get('label', ""),
            album.get('style', ""),
            album.get('title', ""),
            album.get('artist', ""),
            album.get('versions', 0),
            album.get('year', 0)
             ])

def row_to_album(row: tuple):
    album = {
        'url': row[0],
        'format': row[1],
        'genre': row[2],
        'label': row[3],
        'style': row[4],
        'title': row[5],
        'artist': row[6],
        'versions': row[7],
        'year': row[8],
    }

    return album


def row_to_artist(row: tuple):
    artist = {
        'url': row[0],
        'arranged': row[1],
        'arranged_cnt': row[2],
        'credits': row[3],
        'credits_cnt': row[4],
        'lyrics': row[5],
        'lyrics_cnt': row[6],
        'music': row[7],
        'music_cnt': row[8],
        'name': row[9],
        'sites': row[10],
        'vocals': row[11],
        'vocals_cnt': row[12],
    }

    return artist

def fetch_all_albums_from_database():
    con = connect_to_database()
    c = con.cursor()

    albums = list()

    for row in c.execute('SELECT * FROM albums'):
        albums.append(row_to_album(row))

    con.close()
    return albums


def fetch_all_artists_from_database():
    con = connect_to_database()
    c = con.cursor()

    artists = list()

    for row in c.execute('SELECT * FROM artists'):
        artists.append(row_to_artist(row))

    con.close()

    return artists


def insert_artist_into_database(c, url: str, artist:dict):
    c.execute(sql_insert_artist_string,[
              url,
              artist['arranged'],
              artist['arranged_cnt'],
              artist['credits'],
              artist['credits_cnt'],
              artist['lyrics'],
              artist['lyrics_cnt'],
              artist['music'],
              artist['music_cnt'],
              artist['name'],
              artist['sites'],
              artist['vocals'],
              artist['vocals_cnt']
              ])


def insert_all_artists_into_database(filename: str):
    artists = load_dictionary_from_json_file(filename)
    con = connect_to_database()
    c = con.cursor()

    for url, artist in artists.items():
        insert_artist_into_database(c, url, artist)

    con.commit()
    con.close()


def insert_all_albums_into_database(filename: str):
    albums = load_dictionary_from_json_file(filename)
    con = connect_to_database()
    c = con.cursor()

    for album in albums:
        insert_album_into_database(c, album)

    con.commit()
    con.close()


def connect_to_database():
    return sqlite3.connect(os.path.join('data', 'psz_database.db'))

if __name__ == '__main__':
    print('Starting...')
    print(datetime.datetime.now().time())

    #create_tables_in_database()
    #insert_all_albums_into_database('album_secondary_data.json')
    #insert_all_artists_into_database('updated_artist_secondary_data.json')

    #print(fetch_all_albums_from_database())
    #print(fetch_all_artists_from_database())

    print('Done')
