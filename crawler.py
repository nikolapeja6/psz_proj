import requests
from bs4 import BeautifulSoup
import math
import time
import os
import csv
import datetime
import json
from util import *
import urllib
from database_interface import *
from ProxyRequests import ProxyRequests
import threading
import sqlite3
from data_cruncher import *



def get_soup_with_html(url: str):

    html_response = get_html_from_url(url)

    if html_response:
        return BeautifulSoup(html_response, 'html.parser')

    return None


def get_html_from_url(url: str):

    while True:

        try:
            #response1 = requests.get(url, headers={'User-agent': 'bot'})
            #print(response1.text.strip())
            r = ProxyRequests(url)
            r.set_headers({"User-Agent": "bot"})
            r.get()
            response = str(r)
            status_code = r.status_code
            #print(r.get_proxy_used())

            # time.sleep(0.5)

            if response:
                print('*', end='')
                return response
            else:
                print("Blocked - {0}".format(status_code))
                if status_code == 404:
                    append_list_to_file([url], 'TODO_404.csv')
                    return None
                time.sleep(60)
        except Exception as e:
            print(e)
            time.sleep(60 * 5)


def get_number_of_pages(url: str):
    print('Getting number of pages...')

    soup = get_soup_with_html(url)
    total_element = soup.find('strong', attrs={'class': 'pagination_total'})
    if total_element != None:
        number_of_results_str = total_element.text.split()[-1]
        number_of_pages = math.ceil(int(number_of_results_str.replace(',', ''))/250)
    else:
        number_of_pages = 0

    print('Found {0} pages'.format(number_of_pages))

    return number_of_pages

def get_albums_from_page(url: str):
    print('Getting albums from page "{0}" ...'.format(url))

    soup = get_soup_with_html(url)
    soup_albums = soup.find_all('div', attrs={'class': 'card'})

    ret = [album.a['href']for album in soup_albums]

    return ret


# Example: https://www.discogs.com/search/?limit=250&country_exact=Serbia
def url_search_country(country: str):
    return '{0}/search?limit=250&country_exact={1}'.format(discogs_base_url, country)

def url_search_year(base_url: str, year: int):
    return '{0}&year={1}'.format(base_url, year)

# Example: https://www.discogs.com/search/?limit=250&country_exact=Serbia&page=10
def url_search_page(base_url: str, page_num: int):
    return '{0}&page={1}'.format(base_url, page_num)

def get_all_albums_from_country(country: str):

    print("Fetching albums from {0}".format(country))

    filename = '{0}.csv'.format(country)
    year_begin, year_end = year_bounds[country][0], year_bounds[country][1]
    start_time = time.time()
    ret = list()

    url_search = url_search_country(country)
    for year in range(year_begin, year_end+1):
        print('Processing albums from {0} in the year {1}'.format(country, year))
        url_year = url_search_year(url_search, year)
        num_of_pages = get_number_of_pages(url_year)
        if num_of_pages == 0:
            continue

        for i in range(1, num_of_pages+1):
            url_results = url_search_page(url_year, i)
            res = get_albums_from_page(url_results)
            append_list_to_file(res, filename)
            print(res)
            ret.extend(res)

    end_time = time.time()

    print("Executed in {0}s".format(end_time-start_time))

    return ret

def get_albums_per_country():
    for country in countries:
        get_all_albums_from_country(country)



def extract_title(page: BeautifulSoup):
    ret = page.find('div', attrs={'class': 'profile'})

    return str(ret)

def extract_tracklist(page: BeautifulSoup):
    ret = page.find('div', id='tracklist')

    return str(ret)

def extract_credits(page: BeautifulSoup):
    ret = page.find('div', id='credits')

    return str(ret)


def extract_versions(page: BeautifulSoup):
    ret = page.find('div', id='m_versions')

    return str(ret)


def extract_artists_from_title(page: BeautifulSoup):
    title = page.find('h1', id='profile_title')
    artists = title.find_all('a')

    return [artist['href'] for artist in artists]

def extract_artists_from_credits(page: BeautifulSoup):
    artists = page.find_all('a')

    return [artist['href'] for artist in artists]

def extract_artists_from_tracklist(page: BeautifulSoup):
    all_a = page.find_all('a')

    ret = set()
    for a in all_a:
        if 'artist/' in a['href']:
            ret.add(a['href'])

    return list(ret)


def extract_relevant_html_from_album_page(page: BeautifulSoup, url: str, i: int):
    title = extract_title(page)
    tracklist = extract_tracklist(page)
    credits = extract_credits(page)
    versions = extract_versions(page)

    data = {
        'url': url,
        'title': title,
        'tracklist': tracklist,
        'credits': credits,
        'versions': versions
    }

    filename = os.path.join('Yugoslavia', "{0}.json".format(i))
    print(filename)

    save_dictionary_to_json_file(filename, data)

    return [title, tracklist, credits, versions]


def append_list_to_file(lst: list, filename: str):
    with open(get_local_data_path(filename), 'a', encoding='utf-8') as f:
        for item in lst:
            f.write("%s\n" % item)
    f.close()

def read_all_lines_from_file(filename: str):
    with open(get_local_data_path(filename)) as f:
        content = f.readlines()

    f.close()

    return content


def fetch_all_album_data_from_file(filename: str):
    url_sufix_list = read_all_lines_from_file(filename)

    output_filename = "album_data_{0}".format(filename)

    start_time = time.time()

    for i, suffix in enumerate(url_sufix_list):
        url = "{0}/{1}".format(discogs_base_url, suffix)
        print("Processing {0}. - {1}".format(i, url))
        page = get_soup_with_html(url)
        if page == None:
            continue
        data = extract_relevant_html_from_album_page(page, url, i)
        #append_row_to_file(data, output_filename)

    end_time = time.time()

    print("Executed in {0}s".format(end_time-start_time))


def merge_album_data(countries: list):

    all_data = dict()

    for country in countries:
        print(country)
        folder_path = get_local_data_path(country)
        if not os.path.exists(folder_path):
            continue
        data = list()
        for file in os.listdir(folder_path):
            print(file)
            data_item = load_dictionary_from_json_file(os.path.join(country, file))
            data.append(data_item)

        all_data[country] = data

    print('Saving...')

    save_dictionary_to_json_file('albums.json', all_data)

def merge_artist_data():
    all_data = list()

    folder_name = 'Artists'
    folder_path = get_local_data_path(folder_name)

    for file in os.listdir(folder_path):
        print(file)
        data_item = load_dictionary_from_json_file(os.path.join(folder_name, file))
        all_data.append(data_item)

    print('Saving...')

    save_dictionary_to_json_file('artist_data.json', all_data)

def extract_artists_from_album_data():
    album_data = load_dictionary_from_json_file('albums.json')
    print("Starting...")

    artists = set()

    for country, albums in album_data.items():
        print(country)

        for album in albums:
            title_soup = BeautifulSoup(album['title'], 'html.parser')
            credits_soup = BeautifulSoup(album['credits'], 'html.parser')
            tracklist_soup = BeautifulSoup(album['tracklist'], 'html.parser')

            artists.update(extract_artists_from_title(title_soup))
            artists.update(extract_artists_from_credits(credits_soup))
            artists.update(extract_artists_from_tracklist(tracklist_soup))

    save_dictionary_to_json_file('artists.json', list(artists))


def extract_artist_data_from_page(page: BeautifulSoup):
    ret = page.find('div', attrs={'class': 'discography_nav'})

    return str(ret)

def extract_html_from_artist_page(page: BeautifulSoup, url: str, i: int):
    title = extract_title(page)
    numbers = extract_artist_data_from_page(page)

    data = {
        'url': url,
        'title': title,
        'numbers': numbers,
    }

    filename = os.path.join('Artists', "{0}.json".format(i))

    save_dictionary_to_json_file(filename, data)


def fetch_all_artist_data_from_file(filename: str):
    url_sufix_list = load_dictionary_from_json_file(filename)

    start_time = time.time()

    for i, suffix in enumerate(url_sufix_list):
        url = "{0}/{1}".format(discogs_base_url, suffix)
        print("Processing {0}. - {1}".format(i, url))
        page = get_soup_with_html(url)
        if page == None:
            continue
        extract_html_from_artist_page(page, url, i)

    end_time = time.time()

    print("Executed in {0}s".format(end_time-start_time))

def extract_songs_from_tracklist(page: BeautifulSoup):
    table = page.find('table')

    if table == None:
        return []

    links_to_songs_wrappers = table.find_all('td', attrs={'class': 'track tracklist_track_title'})

    if links_to_songs_wrappers == None:
        return []

    links_to_songs = list()
    for song in links_to_songs_wrappers:
        if song.find('a') != None:
            links_to_songs.append(song.a['href'])

    return links_to_songs


def extract_songs_from_albums():
    albums = load_dictionary_from_json_file('albums.json')

    ret = list()

    for counry, albums in albums.items():
        print(counry)
        for album in albums:
            tracklist_html = album['tracklist']

            if tracklist_html == None:
                continue

            tracklist_page = BeautifulSoup(tracklist_html, 'html.parser')

            song_links = extract_songs_from_tracklist(tracklist_page)

            ret.extend(song_links)

    save_dictionary_to_json_file('songs.json', ret)


def download_html_pages_from_list(urls: list, folder: str, filename_sufix: str=""):
    for i, url in enumerate(urls):
        print(i)
        print(url)
        html = get_html_from_url(url)
        if html is None:
            continue
        html += '\n<!-- {0} -->'.format(url)

        filename = url[8:].replace('/', '#')
        filename = filename.replace('?', '@')
        filename = '{0}.html'.format(filename)

        if filename_sufix != '':
            filename = "{0}-{1}".format(filename_sufix, filename)

        filename = os.path.join(folder, filename)
        print(filename)

        with open(filename, 'w', encoding='utf-8') as file:
            file.write(html)

def extract_list_of_artists_from_discog_dataset():
    folder = get_discogs_dataset_path('albums')

    artists = set()

    for i, file in enumerate(os.listdir(folder)):
        print(i)

        with open(os.path.join(folder, file), 'r', encoding='utf-8') as f:
            text = f.readlines()
        text = "".join(text)
        soup = BeautifulSoup(text, 'html.parser')

        all_a = soup.find_all('a')

        for a in all_a:
            href = a.get('href', "")
            if href.startswith('/artist/'):
                artists.add(href)

    append_list_to_file(list(artists), 'discogs_dataset_artists.csv')


def get_discogs_dataset_path(filename: str):
    path = os.path.join('discogs_dataset', filename)
    return get_local_data_path(path)

discogs_base_url = 'https://www.discogs.com'
countries = ['Serbia', 'Yugoslavia']
year_bounds = {
    countries[0]: [1990, 2019],
    countries[1]: [1927, 2019]
}

song_urls = [song['url'] for song in fetch_all_songs_from_database()]
song_len = len(song_urls)


def connect_to_songs():
    return sqlite3.connect('E:\songs_database.db')


def clrean_artist_url(url:str):
    if url.endswith('/tracks'):
        url = url[0:-7]

    return url

def extract_artists_from_song(song_html: str):
    page = html_to_bs4(song_html)

    arranged = list()
    all_credits = set()
    vocals = list()
    music = list()
    lyrics = list()

    credits = page.find('div', attrs={'class':  'TrackCredits'})

    all_a = credits.find_all('a')
    for a in all_a:
        url = a['href']
        if url is not None and url != "" and 'artist/' in url:
            url = clrean_artist_url(url)
            all_credits.add(url)

    facts = credits.find_all('div', attrs={'class':  'TrackFact'})

    for fact in facts:
        text = fact.text.lower()

        if 'arranged' in text:
            all_a = fact.find_all('a')
            for a in all_a:
                url = a['href']
                if url is not None and url != "" and 'artist/' in url:
                    url = clrean_artist_url(url)
                    arranged.append(url)

        if 'lyrics' in text:
            all_a = fact.find_all('a')
            for a in all_a:
                url = a['href']
                if url is not None and url != "" and 'artist/' in url:
                    url = clrean_artist_url(url)
                    lyrics.append(url)

        if 'vocal' in text:
            all_a = fact.find_all('a')
            for a in all_a:
                url = a['href']
                if url is not None and url != "" and 'artist/' in url:
                    url = clrean_artist_url(url)
                    vocals.append(url)

        if 'music' in text:
            all_a = fact.find_all('a')
            for a in all_a:
                url = a['href']
                if url is not None and url != "" and 'artist/' in url:
                    url = clrean_artist_url(url)
                    music.append(url)


    return {
        'credits': list(all_credits),
        'arranged': arranged,
        'lyrics': lyrics,
        'music': music,
        'vocals': vocals,
    }


def worker(k: int, n: int):
    print('worker {0}'.format(k))

    i = k
    while i < song_urls:

        i += n



def execute_sql_on_song_db(sql_str: str):
    con = connect_to_database()
    c = con.cursor()

    c.execute(sql_str)

    con.commit()
    con.close()


if __name__ == '__main__':
    print("Starting...")
    print(datetime.datetime.now().time())

    #merge_artist_data()

    '''
    with open(get_discogs_dataset_path('artists.csv'), encoding='utf-8') as file:
        urls = file.readlines()
    urls = [discogs_base_url + url.strip() for url in urls]
    urls = [urllib.parse.unquote(url) for url in urls]

    download_html_pages_from_list(urls, get_discogs_dataset_path('artists'), '')
    '''

    print('a')

    #print(clrean_artist_url('https://www.discogs.com/artist/2218878-Achilleas-Oikonomou/tracks'))
    print(extract_artists_from_song(get_html_from_url('https://www.discogs.com/composition/45ab210a-1caf-4a80-8c76-e0f0123ddc5d-Poku%C5%A1aj')))

    exit(0)

    for i, artist in enumerate(artists):
        #print(i)
        if i % 100 == 0:
            print(i)
        url = artist['url']
        #get_html_from_url(url)
        thread1 = threading.Thread(target=get_html_from_url, args=([url]))
        thread1.start()

    #extract_list_of_artists_from_discog_dataset()

    print("Done")