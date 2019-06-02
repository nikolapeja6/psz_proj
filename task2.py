from database_interface import *
import matplotlib
from collections import Counter
import cyrtranslit
import task3

def a():
    albums = fetch_all_albums_from_database()

    genres = {}

    for album in albums:
        genres_list = album['genre'].split("#")

        for genre in genres_list:
            genres[genre] = genres.get(genre, 0) + 1

    return sorted(genres.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)

def b():
    albums = fetch_all_albums_from_database()

    styles = {}

    for album in albums:
        styles_list = album['style'].split("#")

        for style in styles_list:
            styles[style] = styles.get(style, 0) + 1

    return sorted(styles.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)


def c(top: int):
    albums = fetch_all_albums_from_database()
    sorted_albums = sorted(albums, key= lambda x: x['versions'], reverse=True)

    sorted_albums = [[album['title'], album['versions']] for album in sorted_albums]

    ret1 = list()
    i = 0
    last = -1
    while i < len(sorted_albums) and len(ret1)< top:
        if len(ret1) == 0 or sorted_albums[i][1] != last:
            last = sorted_albums[i][1]
            ret1.append([last, set([sorted_albums[i][0]])])
            i+=1
            continue
        ret1[-1][1].add(sorted_albums[i][0])
        last = sorted_albums[i][1]
        i+=1

    c = Counter([album['title'] for album in albums])
    ret2 = c.most_common(top)

    c = Counter(["{0}#{1}".format(album['title'], album['artist']) for album in albums])
    ret3 = c.most_common(top)
    ret3 = [[string.split('#')[0], num] for string, num in ret3]


    return [ret1, ret2, ret3]

def d():
    artists = fetch_all_artists_from_database()

    ret = dict()

    for metric in ['credits', 'credits_cnt', 'vocals', 'vocals_cnt', 'arranged', 'arranged_cnt',
                   'lyrics', 'lyrics_cnt', 'music', 'music_cnt']:
        res = sorted(artists, key=lambda x: x[metric], reverse=True)[0:100]
        res = [[x[metric], x['name']] for x in res]

        ret[metric] = res

    return ret


def to_latin(string: str):
    if task3.is_cyrillic(string):
        return cyrtranslit.to_latin(string)
    return string


def e(top: int, generate_report=False):
    songs = fetch_all_songs_from_database()

    song_names = list()
    for song in songs:
        name = to_latin(song['name'])
        song_names.append(name)

    c = Counter(song_names)

    counted_songs = c.most_common(top)

    if generate_report:

        res = list()
        for counted_song in counted_songs:
            cnt = counted_song[1]
            name = counted_song[0]

            lst = list()

            for song in songs:
                if to_latin(song['name']) == name:
                    sng = {
                        'format': song['format'],
                        'country': song['country'],
                        'year': song['year'],
                        'genre': song['genre'],
                        'style': song['style'],
                        'url': song['url']
                    }
                    lst.append(sng)

            res.append((cnt, name, lst))

        save_dictionary_to_json_file('tast2_e.json', res)

    return counted_songs


def f():
    artists = fetch_all_artists_from_database()

    ret = list()

    for artist in artists:
        if artist['sites'] != None:
            ret.append([artist['name'], ", ".join(artist['sites'])])

    return ret

if __name__ == '__main__':
    #print(a())
    #print(b())

    print('C')
    for item in c(20):
        print(item)
    #print(d())
    # TODO check
    #print(e(100, True))
    #print(f())