import hdbscan

from sklearn.neighbors import DistanceMetric
V = np.cov(pts_deg)
metric = DistanceMetric.get_metric('mahalanobis', V=V)

#clusterer = hdbscan.HDBSCAN(min_cluster_size=5, metric='haversine', prediction_data=False, cluster_selection_epsilon=0.7)
#clusterer = hdbscan.HDBSCAN(min_cluster_size=5, metric='mahalanobis', prediction_data=False, cluster_selection_epsilon=0.7)
clusterer = hdbscan.HDBSCAN(min_cluster_size=5, metric='haversine', prediction_data=False, cluster_selection_epsilon=0.01)
help(clusterer)
help(clusterer.fit_predict)
labels = clusterer.fit_predict(pos_matrix)
