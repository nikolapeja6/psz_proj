import datetime
import time
from bs4 import BeautifulSoup
from util import *
import re
import crawler
from fuzzywuzzy import process
from fuzzywuzzy import fuzz

def html_to_bs4(html: str):
    return BeautifulSoup(html, 'html.parser')

def extract_data_from_artist_html(metrics_html: str, title_html):
    page = html_to_bs4(metrics_html)

    ul = page.find('ul', attrs={'class': 'facets_nav'})

    links = ul.find_all('a')

    ret = dict()

    for link in links:
        text = link.text.strip()
        words = text.split()

        value = words[0]
        label = " ".join(words[1:])
        label = label.lower()

        #print("{0}={1}".format(label, value))

        ret[label] = value

    page = html_to_bs4(title_html)

    divs = page.find_all('div')

    i = 0
    while i< len(divs):
        div = divs[i]
        i+=1
        if div.text.strip() == "Sites:":
            break

    if i != len(divs):
        sites = divs[i].find_all('a')
        sites = [str(a['href']) for a in sites]
        sites = json.dumps(sites)
        ret['sites'] = sites

    name = page.find('h1').text.strip()

    ret['name'] = name

    return ret

def extract_data_from_artists(filename: str):
    artists = load_dictionary_from_json_file(filename)

    artists_secondary = dict()

    for i, artist in enumerate(artists):
        url = artist['url']
        numbers = artist['numbers']
        title = artist['title']

        #print(url)
        print(i)

        data = extract_data_from_artist_html(numbers, title)

        vocals = int(data.get('vocals', 0))
        credits = int(data.get('credits', 0))
        arranged_by = int(data.get('writing & arrangement', 0))
        lyrics_by = int(data.get('writing & arrangement', 0))
        music_by = int(data.get('instruments & performance', 0))
        sites = data.get('sites', None)
        name = data.get('name', "")

        secondary_data = {
            'vocals': vocals,
            'credits': credits,
            'arranged': arranged_by,
            'lyrics': lyrics_by,
            'music': music_by,
            'vocals_cnt': 0,
            'credits_cnt': 0,
            'arranged_cnt': 0,
            'lyrics_cnt': 0,
            'music_cnt': 0,
            'sites': sites,
            'name': name
        }

        artists_secondary[url] = secondary_data

    save_dictionary_to_json_file('artist_secondary_data.json', artists_secondary)

    return artists_secondary

def transform_duration_string(duration_str: str):
    if duration_str == None or duration_str == "":
        return 0

    numbers = duration_str.split(":")

    if len(numbers) == 0:
        return 0

    if len(numbers) == 1:
        return numbers[0]

    return int(numbers[0])*60 + int(numbers[1])

def get_name_and_url_from_tr_soup(tr: BeautifulSoup):
    tds = tr.find_all('td', attrs={'class': 'tracklist_track_title'})

    for td in tds:
        a = td.find('a')
        if a != None and a['href'].startswith('/track/'):
            if a.text == None or a.text == "":
                return a['href'], td.text.strip()
            else:
                return a['href'], a.text.strip()

    return None, tr.text


def extract_songs_data_from_tracklist_html(tracklist_html: str):

    if tracklist_html == None or tracklist_html.strip() == "":
        return None

    page = html_to_bs4(tracklist_html)

    table = page.find('tbody')

    trs = page.find_all('tr', attrs={'class': 'track'})

    if trs == None:
        return None

    songs = list()

    for tr in trs:
        url, name = get_name_and_url_from_tr_soup(tr)
        duration = tr.find('td', attrs={'class': 'tracklist_track_duration'}).text.strip()
        duration = transform_duration_string(duration)

        song = {
            'url': url,
            'name': name,
            'duration': duration,
        }

        songs.append(song)

    return songs

formats = [
    'Vinyl',
    'Disc',
    'Cassette',
    'Cyl',
    'CD',
    'DVD',
    'Blu-ray',
    'VHS',
    'VHD',
    'Floppy',
    'M/Stick',
    'MP3',
    'WAV',
    'FLAC',
    'WMV',
    'AAC',
    'File',
    'MPEG',
    'DAT',
    'All Media',
    'Box Set',
    'Flexi-disc',
    'Shellac',
    'Hybrid',
    'Lathe Cut',
    '8-Track Cartridge',
    'PlayTape',
    'Reel-To-Reel'
]

def remove_multiple_consecutive_blank_lines(string: str):
    string = re.sub('\n', ' ', string)
    string = re.sub('\t', ' ', string)
    return re.sub(' +', ' ', string)


def reformat_genres_and_styles(data: str):
    data = data.replace('&', ',')
    data = data.split(',')
    data = [d.strip() for d in data]
    data = list(filter(None, data))
    return '#'.join(data)

def extract_formats_from_format(format: str):
    ret = list()

    for form in formats:
        if form in format:
            ret.append(form)

    ret = '#'.join(ret)

    return ret


def extract_data_from_album_title_html(title_html: str):
    page = html_to_bs4(title_html)

    title = page.find('h1').text.split(u"\u2013")[1].strip()
    artist = page.find('h1').find('a')['href']

    data = {
        'title': title,
        'artist': artist
    }

    divs = page.find('div', attrs={'class': 'profile'}).find_all('div')

    if divs == None or len(divs) == 0:
        return data

    i = 0
    while i < len(divs):
        div = divs[i]
        i+=1

        if div.text == "Label:":
            data['label'] = remove_multiple_consecutive_blank_lines(divs[i].text.strip())

        if div.text == 'Format:':
            data['format'] = extract_formats_from_format(remove_multiple_consecutive_blank_lines(divs[i].text.strip()))

        if div.text == 'Released:':
            data['year'] = int(divs[i].text.strip().split()[-1])

        if div.text == 'Year:':
            data['year'] = int(divs[i].text.strip())

        if div.text == 'Genre:':
            data['genre'] = reformat_genres_and_styles(remove_multiple_consecutive_blank_lines(divs[i].text.strip()))

        if div.text == 'Style:':
            data['style'] = reformat_genres_and_styles(remove_multiple_consecutive_blank_lines(divs[i].text.strip()))

        i += 1

    return data

def extract_number_of_album_versions(versions_html: str):

    if versions_html == None or versions_html == "" or versions_html == "None":
        return 1

    page = html_to_bs4(versions_html)
    versions_h3 = page.find('h3').text

    m = re.search('.*ersion[^(]+\(([^()]+)\)', versions_h3)

    if m:
        number_of_versions_str = m.group(1)
        number_of_versions = int(number_of_versions_str.split()[-1])

        return number_of_versions
    else:
        return 1


# TODO - artists with no URL
def extract_credits_from_tracklist_html(tracklist_html: str):
    ret = {
        'lyrics': [],
        'music': [],
        'arranged': [],
        'vocals': [],
        'credits': []
    }

    if tracklist_html == None or tracklist_html == "" or tracklist_html == "None":
        return ret

    page = html_to_bs4(tracklist_html)

    artists = page.find_all('li', attrs={'class': 'tracklist_extra_artist_span'})

    if artists == None or len(artists) == 0:
        return ret

    for artist in artists:
        text = artist.text.lower()

        urls = artist.find_all('a')

        if urls == None or len(urls) == 0:
            continue

        urls = [url['href'] for url in urls]
        ret['credits'].extend(urls)

        if 'lyrics' in text or 'written' in text:
            ret['lyrics'].extend(urls)

        if 'music' in text:
            ret['music'].extend(urls)

        if 'arranged' in text:
            ret['arranged'].extend(urls)

        if 'vocal' in text:
            ret['vocals'].extend(urls)

    ret['lyrics'] = list(set(ret['lyrics']))
    ret['music'] = list(set(ret['music']))
    ret['arranged'] = list(set(ret['arranged']))
    ret['vocals'] = list(set(ret['vocals']))
    ret['credits'] = list(set(ret['credits']))

    return ret



# TODO - artists with no URL
def extract_credits_from_credits_html(credits_html: str):
    ret = {
        'lyrics': [],
        'music': [],
        'arranged': [],
        'vocals': [],
        'credits': []
    }

    if credits_html == None or credits_html == "" or credits_html == "None":
        return ret

    page = html_to_bs4(credits_html)

    artists = page.find_all('li')

    if artists == None or len(artists) == 0:
        return ret

    for artist in artists:
        text = artist.text.lower()

        urls = artist.find_all('a')

        if urls == None or len(urls) == 0:
            continue

        urls = [url['href'] for url in urls]
        ret['credits'].extend(urls)

        if 'lyrics' in text or 'written' in text:
            ret['lyrics'].extend(urls)

        if 'music' in text:
            ret['music'].extend(urls)

        if 'arranged' in text:
            ret['arranged'].extend(urls)

        if 'vocal' in text:
            ret['vocals'].extend(urls)

    ret['lyrics'] = list(set(ret['lyrics']))
    ret['music'] = list(set(ret['music']))
    ret['arranged'] = list(set(ret['arranged']))
    ret['vocals'] = list(set(ret['vocals']))
    ret['credits'] = list(set(ret['credits']))

    return ret

def merge_two_credits(credits1: dict, credits2: dict):
    ret = {
        'lyrics': set(),
        'music': set(),
        'arranged': set(),
        'vocals': set(),
        'credits': set(),
    }

    for credits in [credits1, credits2]:
        ret['lyrics'].update(credits['lyrics'])
        ret['music'].update(credits['music'])
        ret['arranged'].update(credits['arranged'])
        ret['vocals'].update(credits['vocals'])
        ret['credits'].update(credits['credits'])

    ret['lyrics'] = list(ret['lyrics'])
    ret['music'] = list(ret['music'])
    ret['arranged'] = list(ret['arranged'])
    ret['vocals'] = list(ret['vocals'])
    ret['credits'] = list(ret['credits'])

    return ret


def extract_credits_from_album_html(album: dict):
    credits_html = album['credits']
    tracklist_html = album['tracklist']

    tracklist_credits = extract_credits_from_tracklist_html(tracklist_html)
    credits_credits = extract_credits_from_credits_html(credits_html)

    return merge_two_credits(tracklist_credits, credits_credits)

def extract_data_from_single_album_html(album: dict):
    tracklist_html = album['tracklist']
    title_html = album['title']
    url = album['url']
    versions_html = album['versions']

    songs = extract_songs_data_from_tracklist_html(tracklist_html)
    title = extract_data_from_album_title_html(title_html)
    versions = extract_number_of_album_versions(versions_html)

    title['versions'] = versions
    title['url'] = url

    for song in songs:
        song['format'] = title.get('format', "")
        song['year'] = title.get('year', "")
        song['genre'] = title.get('genre', "")
        song['style'] = title.get('style', "")
        song['album'] = url

    return [title, songs]


def count_credits_from_artists():
    artists_list = load_dictionary_from_json_file('artists.json')

    artists = dict()
    for artist in artists_list:
        artists[artist] = {'lyrics': 0, 'music': 0, 'arranged': 0, 'vocals': 0, 'credits': 0}

    album_data = load_dictionary_from_json_file('albums.json')

    for country, albums in album_data.items():
        print(country)

        for i, album in enumerate(albums):
            print(i)
            credits = extract_credits_from_album_html(album)
            for key, values in credits.items():
                for artist in values:
                    artists[artist][key] += 1

    artists_secondary = load_dictionary_from_json_file('artist_secondary_data.json')

    for key, value in artists.items():
        key = "{0}/{1}".format(crawler.discogs_base_url, key)
        if not key in artists_secondary:
            continue
        for metric, cnt in value.items():
            artists_secondary[key]["{0}_cnt".format(metric)] = cnt

    save_dictionary_to_json_file('updated_artist_secondary_data.json', artists_secondary)


def update_and_merge_songs(song_dst: dict, song: dict):
    song_dst['album'] = song_dst['album']+1

    for field in ['country', 'format', 'year', 'genre', 'style']:
        song_dst[field] = "{0}|{1}".format(song_dst[field], song[field])


def merge_songs(limit: int):
    songs_secondary = load_dictionary_from_json_file('songs_secondary_data.json')

    updated_songs_secondary = list()

    for ind, song in enumerate(songs_secondary):
        print(ind)
        name = song['name'].lower()
        best_match = 0
        best_i = 0
        i = 0
        while i < len(updated_songs_secondary):
            match = fuzz.ratio(updated_songs_secondary[i]['name'].lower(), name)
            if match > best_match:
                best_match = match
                best_i = i

            i += 1

        if len(updated_songs_secondary) != 0 and best_match >= limit:
            if best_match != 100:
                append_row_to_file([name, updated_songs_secondary[best_i]['name'], best_match], 'similar_songs.csv')

            update_and_merge_songs(updated_songs_secondary[best_i], song)
        else:
            song['album'] = 1
            updated_songs_secondary.append(song)

    save_dictionary_to_json_file('updated_songs_secondary.json', updated_songs_secondary)


def extract_data_from_albums(filename: str):
    album_data = load_dictionary_from_json_file(filename)

    album_secondary_data = list()
    songs_secondaty_data = list()

    for country, albums in album_data.items():
        print(country)

        for i, album in enumerate(albums):
            print(i)
            title, songs = extract_data_from_single_album_html(album)
            for song in songs:
                song['country'] = country
            album_secondary_data.append(title)
            songs_secondaty_data.extend(songs)

    print('Saving albums to file...')
    save_dictionary_to_json_file('album_secondary_data.json', album_secondary_data)
    print('Saving songs to file...')
    save_dictionary_to_json_file('songs_secondary_data.json', songs_secondaty_data)


if __name__ == '__main__':
    print("Starting...")
    print(datetime.datetime.now().time())

    #extract_data_from_artists('artist_data.json')
    #extract_data_from_albums('albums.json')

    #extract_data_from_albums('albums.json')

    count_credits_from_artists()

    #merge_songs(91)

    print("Done")