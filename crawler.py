import requests
from bs4 import BeautifulSoup
import math
import time
import os
import csv
import datetime
import json

def get_soup_with_html(url: str):

    #last_sleep = 1
    while True:

        try:
            response = requests.get(url, headers={'User-agent': 'bot'})
            #time.sleep(0.5)

            if response:
                return BeautifulSoup(response.content, 'html.parser')
            else:
                print("Blocked - {0}".format(response.status_code))
                if response.status_code == 404:
                    append_list_to_file([url], 'TODO_404.csv')
                    return None
                time.sleep(60)
                #if last_sleep < 60:
                #    last_sleep*=2
        except:
            time.sleep(60*5)


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

    return [artist['href'] for artist in  artists]

def extract_artists_from_credits(page: BeautifulSoup):
    artists = page.find_all('a')

    return [artist['href'] for artist in artists]


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


def save_dictionary_to_json_file(file_name: str, data):

    with open(get_local_data_path(file_name), 'w') as fp:
        json.dump(data, fp, indent=4, sort_keys=True)

def load_dictionary_from_json_file(filename: str):
    with open(get_local_data_path(filename)) as file:
        ret = json.load(file)
        return ret

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

def extract_artists_from_album_data():
    album_data = load_dictionary_from_json_file('albums.json')
    print("Starting...")

    artists = set()

    for country, albums in album_data.items():
        print(country)

        for album in albums:
            title_soup = BeautifulSoup(album['title'], 'html.parser')
            credits_soup = BeautifulSoup(album['credits'], 'html.parser')

            artists.update(extract_artists_from_title(title_soup))
            artists.update(extract_artists_from_credits(credits_soup))

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
        if i <= 4557:
            continue;
        url = "{0}/{1}".format(discogs_base_url, suffix)
        print("Processing {0}. - {1}".format(i, url))
        page = get_soup_with_html(url)
        if page == None:
            continue
        extract_html_from_artist_page(page, url, i)

    end_time = time.time()

    print("Executed in {0}s".format(end_time-start_time))

def append_row_to_file(lst: list, filename: str):
    with open(get_local_data_path(filename), mode='a', encoding='utf-8', newline='') as file:
        csv_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL, )

        csv_writer.writerow(lst)
    file.close()

def check_and_create_local_data_dir():
    if not os.path.exists(local_data_dir):
        os.makedirs(local_data_dir)

def get_local_data_path(filename: str):
    check_and_create_local_data_dir()
    return os.path.join(local_data_dir, filename)

discogs_base_url = 'https://www.discogs.com'
countries = ['Serbia', 'Yugoslavia']
year_bounds = {
    countries[0]: [1990, 2019],
    countries[1]: [1927, 2019]
}

local_data_dir = 'local_data'

if __name__ == '__main__':
    print("Starting...")
    print(datetime.datetime.now().time())

    fetch_all_artist_data_from_file('artists.json')

    print("Done")