from task4 import *
from sklearn.cluster import MeanShift
from sklearn.cluster import DBSCAN
import datetime
import fastcluster
#from scipy.cluster.hierarchy import dendrogram, linkage

def task5(num_of_clusters: int, original_dimensions: bool, features: list):
    albums = fetch_all_albums_from_database()

    albums_features = albums_to_features(albums, features)

    pca = PCA(n_components=2).fit(albums_features)
    pca_2d = pca.transform(albums_features)

    clustering = DBSCAN(eps=0.1, min_samples=300, metric='euclidean', metric_params=None, algorithm='auto',
                        leaf_size=60000//num_of_clusters, p=None, n_jobs=-1).fit(pca_2d)
    labels = list(clustering.labels_)
    visialize_ndoes(labels, pca_2d, num_of_clusters, features, albums, 'task5', 'DBSCAN')

    if original_dimensions:
        clustering = DBSCAN(eps=0.1, min_samples=500, metric='euclidean', metric_params=None, algorithm='auto', leaf_size=3000, p=None, n_jobs=-1).fit(albums_features)
        labels = list(clustering.labels_)
        visialize_ndoes(labels, pca_2d, num_of_clusters, features, albums, 'task5_b', 'DBSCAN')


if __name__ == '__main__':
    print("Starting...")
    print(datetime.datetime.now().time())

    #'artist',
    task5(10, False, [
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

