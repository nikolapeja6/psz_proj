from pyparsing import pyparsing_common

from database_interface import *
import datetime
from sklearn.cluster import KMeans
import numpy as np
import task2
import data_cruncher
import pandas
from matplotlib import pyplot as plt
from sklearn.decomposition import PCA
import pylab as pl
import networkx as nx
from matplotlib import colors as mcolors
import plotly.plotly as py
import plotly.graph_objs as go
import plotly
import msvcrt
from bokeh.plotting import figure, show, output_file, ColumnDataSource

genre_features = sorted([genre[0] for genre in task2.a()])
format_features = data_cruncher.formats
style_features = sorted([genre[0] for genre in task2.b()])
album_label_len = max([len(album['label']) for album in fetch_all_albums_from_database()])
album_title_len = max([len(album['title']) for album in fetch_all_albums_from_database()])

def random_color():
    #dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)
    colors = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)

    # Sort colors by hue, saturation, value and name.
    by_hsv = sorted((tuple(mcolors.rgb_to_hsv(mcolors.to_rgba(color)[:3])), name)
                    for name, color in colors.items())
    cls = [name for hsv, name in by_hsv]
    return cls[np.random.choice(range(len(cls)))]
    #rgb = list(np.random.choice(range(256), size=3))
    #R, G, B = rgb[0], rgb[1], rgb[2]
    #R + G * (256) + B * (256 ^ 2)
    #return R + G * (256) + B * (256 ^ 2)
#'%02x%02x%02x' % (rgb[0], rgb[1], rgb[2])


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


def task4(num_of_clusters: int, features: list):
    albums = fetch_all_albums_from_database()

    albums_features = albums_to_features(albums, features)

    kmeans = KMeans(n_clusters=num_of_clusters, random_state=0).fit(albums_features)

    labels = list(kmeans.labels_)

    '''
    data = pandas.DataFrame(albums_features)
    data['cluster'] = kmeans.predict(albums_features)
    pandas.plotting.parallel_coordinates(data, 'cluster')
    '''
    #label_color = [LABEL_COLOR_MAP[l] for l in labels]
    pca = PCA(n_components=2).fit(albums_features)
    pca_2d = pca.transform(albums_features)

    color_dic = dict()
    for i in range(num_of_clusters):
        color_dic[i] = col[i]

    cls = [color_dic[label] for label in labels]

    pos  =list()
    for item in pca_2d:
        pos.append(list(item))

    # networkx and matoplotlib
    '''
    print('a')
    #graph.add_nodes_from(range(len(albums)))#[album['title'] for album in albums])
    print('b')
    #nodes = nx.draw_networkx_nodes(graph, pos,node_size=1, font_size='xx-small', with_labels=False, node_color=cls)
    print('c')
    #nodes.set_facecolor('white')
    #nodes.set_alpha(0.1)
    plt.scatter(pca_2d[:,0], pca_2d[:,1], c=cls, )
    print('d')
    fig = plt.gcf()
    plt.show()
    fig.savefig('aaa.pdf', format='pdf', dpi=500)
    '''

    # Ono djubre koje se placa ako je online
    '''
    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=False,
            # colorscale options
            # 'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            # 'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            # 'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            #colorscale='YlGnBu',
            #reversescale=True,
            color=[],
            size=5,
        )
        )

    print('a')

    for i in range(len(albums)):
        print(i)

        x, y = pca_2d[i]
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['marker']['color'] += tuple([cls[i]])
        node_info = albums[i]['title']
        node_trace['text'] += tuple([node_info])

    fig = go.Figure(data=[node_trace],
                    layout=go.Layout(
                        title='<br>Network graph made with Python',
                        titlefont=dict(size=16),
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        annotations=[dict(
                            text="Python code: <a href='https://plot.ly/ipython-notebooks/network-graphs/'> https://plot.ly/ipython-notebooks/network-graphs/</a>",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002)],
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))

    plotly.offline.plot(fig, filename=get_local_data_path('task4.html'))
    '''

    TOOLTIPS = [
        ('title', '@title'),
        ('URL', '@url')
    ]

    source = ColumnDataSource(data=dict(
        x=pca_2d[:, 0],
        y=pca_2d[:, 1],
        title=[album['title'] for album in albums],
        url=[album['url'] for album in albums],
        color=cls
    ))

    for feature in features:
        TOOLTIPS.append((feature, "@{0}".format(feature)))
        source.add([album[feature] for album in albums], feature)

    p = figure(sizing_mode='stretch_both', title="K-Means clustering of albums on metrics: "+", ".join(features),
               tooltips=TOOLTIPS)

    p.circle('x', 'y', source=source,
             color='color', fill_alpha=0.1, size=5)

    output_file(get_local_data_path("task4_b.html"), title="PSZ | K-Means clustering of Albums")

    show(p)


if __name__ == '__main__':
    print("Starting...")

    #print(pca_2d)
    #'artist',
    task4(3, [
    'format',
    'genre',
    #'label',
    'style',
    #'title',
    #'versions',
    #'year',
    ])

    print("Done")
