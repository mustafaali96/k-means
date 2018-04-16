from random import sample
from typing import List

from scipy.spatial.distance import cityblock
from scipy.spatial.distance import euclidean


class KMeans:

    def __init__(self, num_clusters=8, distance_function='euclidean'):
        self._num_clusters = num_clusters
        self._distance_function = distance_function
        self.centroids_ = None
        self.labels_ = None
        self.inertia_ = None

    def fit(self, data: List[List]) -> 'KMeans':
        """Cluster the data into k sets.

        Stopping Criterion: Repeat until only 1% of points change clusters.

        Args:
            data: Data to cluster into k sets.

        Returns:
            self
        """
        self.centroids_ = self._select_initial_centroids(data)
        self._form_clusters_and_update_centroids(data)
        percentage_of_points_changed = 100.0
        while percentage_of_points_changed >= 1.0:
            previous_labels = self.labels_[:]
            for i, point in enumerate(data):
                self.labels_[i] = get_cluster_label(point, self.centroids_)
                self.centroids_ = partition_and_get_centroids(data, self.labels_)
            self.inertia_ = self._get_inertia(data)
            percentage_of_points_changed = get_percentage_of_points_changed(previous_labels, self.labels_)
        return self

    def _get_inertia(self, data: List[List]) -> float:
        closest_centroids = get_closest_centroids_from_labels(data, self.centroids_, self.labels_)
        return get_inertia(data, closest_centroids)

    def predict(self, data: List[List]) -> List:
        """Predict the closest cluster each sample belongs to.

        Args:
            data: Data to predict the clusters for.

        Returns:
            Predicted cluster each sample belongs to.
        """
        return get_cluster_labels(data, self.centroids_)

    def _form_clusters_and_update_centroids(self, data: List[List]) -> None:
        """Form K clusters by assigning each point to its closest centroid,
        and recompute centroid of each cluster.

        Args:
            data: The data to cluster.

        Returns:
            None
        """
        self.labels_ = get_cluster_labels(data, self.centroids_)
        self.centroids_ = partition_and_get_centroids(data, self.labels_)
        self.inertia_ = self._get_inertia(data)

    def _select_initial_centroids(self, data: List[List]) -> List:
        """Select K points as initial centroids.

        Uses random initialization.

        Args:
            data: The dataset.

        Returns:
            K initial centroids.
        """
        return sample(data, self._num_clusters)


def partition_and_get_centroids(data: List[List], labels: List[int]) -> List[List]:
    """Partition by cluster anc compute the centroids for each cluster in the data.

    Args:
        data: The dataset to compute the centroids for.
        labels: The labels containing which cluster each point belongs to.

    Returns:
        The centroids of each cluster.
    """
    partition = partition_by_cluster(data, labels)
    return get_centroids(partition)


def get_centroids(clusters: List[List]) -> List[List]:
    """Compute the centroids for a list of clusters.

    Args:
        clusters: A list of clusters.

    Returns:
        The center point of each cluster.
    """
    centroids = []
    for cluster in range(len(clusters)):
        points_in_cluster = clusters[cluster]
        centroid = get_centroid(points_in_cluster)
        centroids.append(centroid)
    return centroids


def partition_by_cluster(data: List[List], labels: List[int]) -> List:
    """Partition a dataset by which cluster each point belongs to.

    Args:
        data: The dataset to partition.
        labels: The label of which cluster each point belongs to.

    Returns:
        Partitioned dataset by which cluster each point belongs to.
    """
    clusters = list(set(labels))
    partition = [[] for _ in range(len(clusters))]
    for point, label in zip(data, labels):
        partition[label].append(point)
    return partition


def get_centroid(cluster: List[List]) -> List:
    """Calculate the center for a cluster of points.
    
    Args:
        cluster: A cluster of points.

    Returns:
        The center of the cluster.
    """
    total = len(cluster)
    return [sum(points) / total for points in zip(*cluster)]


def get_percentage_of_points_changed(previous_labels: List, labels: List) -> float:
    """Get the percentage of points that changed clusters.

    Args:
        previous_labels: The labels of the points before the update.
        labels: The labels of the points after the update.

    Returns:
        The percentage of points that changed clusters.
    """
    num_points = len(labels)
    num_changed = 0
    for i in range(num_points):
        if previous_labels[i] != labels[i]:
            num_changed += 1
    return num_changed / num_points * 100.0


def get_cluster_labels(data: List[List], centroids: List[List], distance_function: str = None) -> List[int]:
    """Gets the cluster label for a set of points.

    Args:
        data: A set of points. The dataset.
        centroids: The center of each cluster.
        distance_function: Whether to use euclidean or manhattan distance.
                           Defaults to euclidean distance.

    Returns:
        A list of cluster labels. Corresponds to the index of the closest centroid.
    """
    cluster_labels = []
    for point in data:
        cluster_label = get_cluster_label(point, centroids, distance_function)
        cluster_labels.append(cluster_label)
    return cluster_labels


def get_cluster_label(point: List, centroids: List[List], distance_function: str = None) -> int:
    """Gets the cluster label of a point.

    Args:
        point: The point to calculate which cluster it belongs to.
        centroids: The center of each cluster.
        distance_function: Whether to use euclidean or manhattan distance.
                           Defaults to euclidean distance.

    Returns:
        The cluster label. This corresponds to the index of the closest centroid.
    """
    distances_from_centroids = [distance(point, centroid, func=distance_function) for centroid in centroids]
    min_distance = min(distances_from_centroids)
    return distances_from_centroids.index(min_distance)


def distance(a: List[float], b: List[float], func='euclidean') -> float:
    if func == 'euclidean' or func is None:
        return euclidean(a, b) ** 2
    elif func == 'manhattan':
        return cityblock(a, b)
    else:
        raise ValueError('Invalid distance function {}.'.format(func))


def get_inertia(data: List[List], closest_centroids: List[List], distance_function: str = None) -> float:
    """Get the sum of distances of each sample to their closest centroid.

    Args:
        data: Dataset.
        closest_centroids: The closest centroid for each point.
        distance_function: Whether to use euclidean or manhattan distance.
                           Defaults to euclidean distance.

    Returns:
        Sum of squared distances of each sample to their closest centroid.
    """
    errors = []
    for point, closest_centroid in zip(data, closest_centroids):
        error = distance(point, closest_centroid, func=distance_function)
        errors.append(error)
    return sum(errors)


def get_closest_centroids(data: List[List], centroids: List[List]) -> List[List]:
    """Get the closest centroid for each point in the dataset.

    Args:
        data: The dataset.
        centroids: The center point of each cluster.

    Returns:
        The closest centroid for each point in the dataset.
    """
    closest_centroids = []
    cluster_labels = get_cluster_labels(data, centroids)
    for point, cluster_label in zip(data, cluster_labels):
        closest_centroid = centroids[cluster_label]
        closest_centroids.append(closest_centroid)
    return closest_centroids


def get_closest_centroids_from_labels(data: List[List], centroids: List[List], labels: List[int]) -> List[List]:
    """Get the closest centroid for each point in the dataset using the cluster labels.

    Less computationally expensive than get_closest_centroids.

    Args:
        data: The dataset.
        centroids: The center point of each cluster.
        labels: The cluster each point in the dataset belongs to.

    Returns:
        The closest centroid for each point in the dataset.
    """
    closest_centroids = []
    for point, label in zip(data, labels):
        closest_centroid = centroids[label]
        closest_centroids.append(closest_centroid)
    return closest_centroids


def get_inertia_per_cluster(data: List[List], centroids: List[List], labels: List[int]) -> List[float]:
    """Get the sum of squared error for each cluster.

    Args:
        data: The dataset.
        centroids: The center point for each cluster.
        labels: The cluster each point belongs to.

    Returns:
        The sum of squared error for each cluster.
    """
    inertia_per_cluster = []
    partitioned_data = partition_by_cluster(data, labels)
    closest_centroids = get_closest_centroids_from_labels(data, centroids, labels)
    partitioned_closest_centroids = partition_by_cluster(closest_centroids, labels)
    for data_per_cluster, closest_centroids_per_cluster in zip(partitioned_data, partitioned_closest_centroids):
        cluster_inertia = get_inertia(data_per_cluster, closest_centroids_per_cluster)
        inertia_per_cluster.append(cluster_inertia)
    return inertia_per_cluster
