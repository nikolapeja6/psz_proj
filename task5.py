from task4 import *
from sklearn.cluster import MeanShift
from sklearn.cluster import DBSCAN
import datetime
import fastcluster
#from scipy.cluster.hierarchy import dendrogram, linkage

def task5(num_of_clusters: int, features: list):
    albums = fetch_all_albums_from_database()

    albums_features = albums_to_features(albums, features)

    print('a')
    #clustering = MeanShift(bandwidth=500, bin_seeding=True).fit(albums_features)
    clustering = DBSCAN(eps=0.1, min_samples=500, metric='euclidean', metric_params=None, algorithm='auto', leaf_size=3000, p=None, n_jobs=-1).fit(albums_features)

    print('b')

    labels = list(clustering.labels_)
    pca = PCA(n_components=2).fit(albums_features)
    pca_2d = pca.transform(albums_features)

    visialize_ndoes(labels, pca_2d, num_of_clusters, features, albums, 'task5', 'DBSCAN')#'K-Means')


if __name__ == '__main__':
    print("Starting...")
    print(datetime.datetime.now().time())

    #'artist',
    task5(10, [
    'format',
    'genre',
    #'label',
    'style',
    #'title',
    #'versions',
    #'year',
    ])

    print("Done")
    print(datetime.datetime.now().time())

