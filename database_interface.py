import datetime
import sqlite3
from util import *
import json
import data_cruncher
from crawler import discogs_base_url

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

sql_create_song_table_string = 'CREATE TABLE songs (' \
                               'album text, ' \
                               'country text, ' \
                               'duration integer, ' \
                               'format text, ' \
                               'genre text, ' \
                               'name text, ' \
                               'style text, ' \
                               'url text, ' \
                               'y integer ' \
                               ')'

sql_insert_album_string = "INSERT INTO albums VALUES (?,?,?,?,?,?,?,?,?)"


sql_insert_artist_string = "INSERT INTO artists VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)"

sql_insert_song_string = "INSERT INTO songs VALUES (?,?,?,?,?,?,?,?,?)"


def create_tables_in_database():
    con = connect_to_database()
    c = con.cursor()

    c.execute(sql_create_album_table_string)
    c.execute(sql_create_artist_table_string)
    c.execute(sql_create_song_table_string)

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


def insert_song_into_database(c, song: dict):
    c.execute(sql_insert_song_string, [
        song['album'],
        song['country'],
        song['duration'],
        song['format'],
        song['genre'],
        song['name'],
        song['style'],
        song['url'],
        song['year']
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
        'credits_songs': row[13],
        'vocal_songs': row[14],
        'arranged_songs': row[15],
        'lyrics_songs': row[16],
        'music_songs': row[17],
    }

    if artist['sites'] is not None:
        artist['sites'] = json.loads(row[10])

    for key in artist.keys():
        if artist[key] is None and key not in ['name', 'sites']:
            artist[key] = 0

    return artist


def row_to_song(row: tuple):
    song = {
        'album': row[0],
        'country': row[1],
        'duration': row[2],
        'format': row[3],
        'genre': row[4],
        'name': row[5],
        'style': row[6],
        'url': row[7],
        'year': row[8],
    }

    return song


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


def fetch_all_songs_from_database():
    con = connect_to_database()
    c = con.cursor()

    songs = list()

    for row in c.execute('SELECT * FROM songs'):
        songs.append(row_to_song(row))

    con.close()
    return songs


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


def insert_all_songs_into_database(filename: str):
    songs = load_dictionary_from_json_file(filename)
    con = connect_to_database()
    c = con.cursor()

    for  song in songs:
        insert_song_into_database(c, song)

    con.commit()
    con.close()


def update_database_with_new_metrics(create_new_columns: bool = False):

    if create_new_columns:
        con = connect_to_database()
        c = con.cursor()

        m = ['credits_songs']
        for metric in data_cruncher.metrics:
            m.append("{0}_songs".format(metric))

        for column_name in m:
            c.execute('ALTER TABLE artists ADD COLUMN {0} INTEGER;'.format(column_name))

        con.commit()
        con.close()

    data = load_dictionary_from_json_file('updated_artist_metrics---songs---.json')

    con = connect_to_database()
    c = con.cursor()
    for metric, data_list in data.items():
        col_name = "{0}_songs".format(metric)
        for url, cnt in data_list:
            url = "{0}/{1}".format(discogs_base_url, url)
            in_database = list(c.execute("SELECT COUNT(*) FROM artists WHERE url='{0}'".format(url)))[0][0]
            if in_database == 0:
                c.execute("INSERT INTO artists (url, {0}) VALUES ('{1}', {2})".format(col_name, url, cnt))
            else:
                c.execute("UPDATE artists SET {0}={1} WHERE url='{2}'".format(col_name, cnt, url))
    con.commit()
    con.close()


def connect_to_database():
    return sqlite3.connect(os.path.join('data', 'psz_database.db'))


if __name__ == '__main__':
    print('Starting...')
    print(datetime.datetime.now().time())

    update_database_with_new_metrics()

    #create_tables_in_database()
    #insert_all_albums_into_database('album_secondary_data.json')
    #insert_all_artists_into_database('updated_artist_secondary_data.json')
    #insert_all_songs_into_database('songs_secondary_data.json')

    #print(fetch_all_albums_from_database())
    #print(fetch_all_artists_from_database())
    #print(fetch_all_songs_from_database())

    print('Done')
