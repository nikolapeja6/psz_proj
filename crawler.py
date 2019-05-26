import requests
from bs4 import BeautifulSoup
import math
import time
import os

def get_soup_with_html(url: str):

    #last_sleep = 1
    while True:
        response = requests.get(url)

        if response:
            return BeautifulSoup(response.content, 'html.parser')
        else:
            print("Blocked")
            time.sleep(60)
            #if last_sleep < 60:
            #    last_sleep*=2


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


def append_list_to_file(lst: list, filename: str):
    with open(get_local_data_path(filename), 'a') as f:
        for item in lst:
            f.write("%s\n" % item)
    f.close()


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

    for country in countries:
        get_all_albums_from_country(country)

    print("Done")