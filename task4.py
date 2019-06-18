from pyparsing import pyparsing_common

from database_interface import *
from sklearn.cluster import KMeans
import numpy as np
import task2
import data_cruncher
from sklearn.decomposition import PCA
from matplotlib import colors as mcolors
from bokeh.plotting import figure, show, output_file, ColumnDataSource

genre_features = sorted([genre[0] for genre in task2.a()])
format_features = data_cruncher.formats
style_features = sorted([genre[0] for genre in task2.b()])
album_label_len = max([len(album['label']) for album in fetch_all_albums_from_database()])
album_title_len = max([len(album['title']) for album in fetch_all_albums_from_database()])

def random_color():
    colors = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)

    # Sort colors by hue, saturation, value and name.
    by_hsv = sorted((tuple(mcolors.rgb_to_hsv(mcolors.to_rgba(color)[:3])), name)
                    for name, color in colors.items())
    cls = [name for hsv, name in by_hsv]
    return cls[np.random.choice(range(len(cls)))]


def list_to_feature_vector(lst: list, all_features: list):
    ret = list()

    for feature in all_features:
        if feature in lst:
            ret.append(1)
        else:
            ret.append(0)


    return ret

def string_to_number_array(string: str, max_len: int):
    ret = [0]*max_len

    for i, char in enumerate(string):
        ret[i] = ord(char)

    return ret


def format_tofeature_vector(format: str):
    formats = format.split('#')

    ret = list_to_feature_vector(formats, format_features)

    return ret

def genre_to_feature_vector(genre: str):
    genres = genre.split('#')

    ret = list_to_feature_vector(genres, genre_features)

    return ret

def label_to_feature_vector(label: str):
    return string_to_number_array(label, album_label_len)

def style_to_feature_vector(style: str):
    return list_to_feature_vector(style, style_features)

def title_to_feature_vector(title: str):
    return string_to_number_array(title, album_title_len)

def versions_to_feeature_vector(vecrions: int):
    return vecrions

def year_to_feature_vector(year: int):
    return year

def album_to_feature_vector(album: dict, features: list):
    ret = list()

    for feature in features:
        if 'format' == feature:
            ret.extend(format_tofeature_vector(album[feature]))
        if 'genre' == feature:
            ret.extend(genre_to_feature_vector(album[feature]))
        if 'label' == feature:
            ret.extend(label_to_feature_vector(album[feature]))
        if 'style' == feature:
            ret.extend(style_to_feature_vector(album[feature]))
        if 'title' == feature:
            ret.extend(title_to_feature_vector(album[feature]))
        if 'versions' == feature:
            ret.append(album[feature])
        if 'year' == feature:
            ret.append(album[feature])

    return ret

def albums_to_features(albums: list, features: list):
    ret = [album_to_feature_vector(album, features) for album in albums]

    return np.array(ret)

col = ['blue', 'green', 'red',  'pink', 'black']


def visialize_ndoes(labels: list, pca_2d: list, num_of_clusters: int, features: list, albums: list, task_name: str,
                    method: str):
    color_dic = dict()
    for i in range(-1, num_of_clusters+1):
        color_dic[i] = random_color()

    cls = [color_dic[label] for label in labels]

    TOOLTIPS = [
        ('title', '@title'),
        ('URL', '@url'),
        ('Cluster', '@cluster')
    ]

    source = ColumnDataSource(data=dict(
        x=pca_2d[:, 0],
        y=pca_2d[:, 1],
        title=[album['title'] for album in albums],
        url=[album['url'] for album in albums],
        color=cls,
        cluster=labels
    ))

    for feature in features:
        TOOLTIPS.append((feature, "@{0}".format(feature)))
        source.add([album[feature] for album in albums], feature)

    p = figure(sizing_mode='stretch_both', title=method+" clustering of albums on metrics: "+", ".join(features),
               tooltips=TOOLTIPS, output_backend='webgl')

    p.circle('x', 'y', source=source, color='color', fill_alpha=0.2, size=5)
    output_file(get_local_data_path(task_name+".html"), title="PSZ | {0} clustering of Albums".format(method))
    show(p)

def task4(num_of_clusters: int, features: list):
    albums = fetch_all_albums_from_database()

    albums_features = albums_to_features(albums, features)

    kmeans = KMeans(n_clusters=num_of_clusters, random_state=0).fit(albums_features)

    labels = list(kmeans.labels_)
    pca = PCA(n_components=2).fit(albums_features)
    pca_2d = pca.transform(albums_features)

    visialize_ndoes(labels, pca_2d, num_of_clusters, features, albums, 'task4', 'K-Means')



if __name__ == '__main__':
    print("Starting...")

    #'artist',
    task4(10, [
    'format',
    'genre',
    #'label',
    'style',
    #'title',
    #'versions',
    #'year',
    ])

    print("Done")
