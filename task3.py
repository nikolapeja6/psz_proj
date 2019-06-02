from database_interface import *
import task2
from matplotlib import pyplot as plt
import numpy as np
import regex


def util_plot_pie(values: list, labels: list, colors=None):
    plt.pie(values, labels=labels, autopct='%1.1f%%', colors=colors)
    plt.axis('equal')
    plt.show()


def a(top: int):
    genres = task2.a()

    values = list()
    labels = list()

    i = 0
    while i <= top:
        labels.append(genres[i][0])
        values.append(genres[i][1])
        i += 1

    total = sum(x[1] for x in genres)
    covered = sum(values)

    values.append(total - covered)
    labels.append('Other')

    util_plot_pie(values, labels)


def b():
    songs = fetch_all_songs_from_database()

    durations = [song['duration'] for song in songs]

    max_dur = max(durations)
    bins = [0, 90, 180, 240, 300, 360, max_dur]
    histogram_helper(durations, bins=bins)

    labels = ['0', '1-90', '90-180', '180-240', '240-300', '300-360', '360+']
    cnts = [0,0,0,0,0,0,0]
    for duration in durations:
        if duration == 0:
            i = 0
        elif duration < 90:
            i = 1
        elif duration < 180:
            i = 2
        elif duration < 240:
            i = 3
        elif duration < 300:
            i = 4
        elif duration < 360:
            i = 5
        else:
            i = 6

        cnts[i] += 1

    util_plot_pie(cnts, labels)

def histogram_helper(data: list, begin: int=0, end: int=0, step: int=0, bins: list= None):
    if bins is None:
        n, bns, patches = plt.hist(data, bins=range(begin, end+step, step), color='#0504aa', alpha=0.7, rwidth=0.85)
    else:
        n, bns, patches = plt.hist(data, bins=bins, color='#0504aa', alpha=0.7, rwidth=0.85)
    plt.grid(axis='y', alpha=0.75)
    plt.xlabel('Decades')
    plt.ylabel('Albums')
    plt.title('Number of albums per decade')
    maxnum = n.max()
    plt.ylim(0, maxnum * 1.1)
    plt.show()


def c():
    albums = fetch_all_albums_from_database()

    data = [album['year'] for album in albums]
    #data = [1950, 1951, 1959, 1960, 2019, 2020]

    histogram_helper(data, 1950, 2019, 1)
    histogram_helper(data, 1950, 2019, 10)

def is_cyrillic(string: str):
    return regex.search(r'\p{IsCyrillic}', string) is not None

def d():
    albums = fetch_all_albums_from_database()

    latin = 0
    cyrillic = 0

    for album in albums:
        if is_cyrillic(album['title']):
            cyrillic += 1
        else:
            latin += 1

    values = [latin, cyrillic]
    labels = ['Latin ({0})'.format(latin), 'Cyrillic ({0})'.format(cyrillic)]
    colors = ['lightblue', 'gold']

    util_plot_pie(values, labels, colors)

def e():
    albums = fetch_all_albums_from_database()

    values = [0, 0, 0, 0]
    labels = ['1', '2', '3', '4+']
    colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue']

    for album in albums:
        n = len(album['genre'].split('#'))

        if n >= len(values):
            n = -1

        values[n] += 1

    util_plot_pie(values, labels, colors)


if __name__ == '__main__':
    #a(6)
    b()
    #c()
    #d()
    #e()