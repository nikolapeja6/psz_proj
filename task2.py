from database_interface import *
import matplotlib

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

def c():
    albums = fetch_all_albums_from_database()
    sorted_albums = sorted(albums, key= lambda x: x['versions'], reverse=True)

    sorted_albums = [[album['title'], album['versions']] for album in sorted_albums]

    ret = list()
    i = 0
    last = -1
    while i < len(sorted_albums) and len(ret)< 20:
        if len(ret) == 0 or sorted_albums[i][1] != last:
            last = sorted_albums[i][1]
            ret.append([last, set([sorted_albums[i][0]])])
            i+=1
            continue
        ret[-1][1].add(sorted_albums[i][0])
        last = sorted_albums[i][1]
        i+=1

    return ret

def d():
    artists = fetch_all_artists_from_database()

    ret = dict()

    for metric in ['credits', 'credits_cnt', 'vocals', 'vocals_cnt', 'arranged', 'arranged_cnt',
                   'lyrics', 'lyrics_cnt', 'music', 'music_cnt']:
        res = sorted(artists, key=lambda x: x[metric], reverse=True)[0:100]
        res = [[x[metric], x['name']] for x in res]

        ret[metric] = res

    return ret

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
    #print(c())
    #print(d())
    print(f())