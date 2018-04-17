from math import cos
from math import pi
from math import sin
from random import Random
from typing import List, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot_clusters(clusters: List[List], labels: List[int]) -> None:
    """Plot cluster data.

    Args:
        clusters: Cluster data to plot.
        labels: Labels of each point.

    Returns:
        None
    """
    columns = ['x', 'y']
    data = pd.DataFrame(clusters, columns=columns)
    data['labels'] = pd.Series(labels, index=data.index)  # Add labels as a column for coloring
    sns.lmplot(*columns, data=data, fit_reg=False, legend=False, hue='labels')
    plt.show()


def generate_clusters(num_clusters: int,
                      num_points: int,
                      spread: float,
                      bound_for_x: Tuple[float, float],
                      bound_for_y: Tuple[float, float],
                      seed=None) -> List[List]:
    """Generate random data for clustering.

    Source:
    https://stackoverflow.com/questions/44356063/how-to-generate-a-set-of-random-points-within-a-given-x-y-coordinates-in-an-x

    Args:
        num_clusters: The number of clusters to generate.
        num_points: The number of points to generate.
        spread: The spread of each cluster. Decrease for tighter clusters.
        bound_for_x: The bounds for possible values of X.
        bound_for_y: The bounds for possible values of Y.
        seed: Seed for the random number generator.

    Returns:
        K clusters consisting of N points.
    """
    random = Random(seed)
    x_min, x_max = bound_for_x
    y_min, y_max = bound_for_y
    num_points_per_cluster = int(num_points / num_clusters)
    clusters = []
    for _ in range(num_clusters):
        x = x_min + (x_max - x_min) * random.random()
        y = y_min + (y_max - y_min) * random.random()
        clusters.extend(generate_cluster(num_points_per_cluster, (x, y), spread, seed))
    return clusters


def generate_cluster(num_points: int, center: Tuple[float, float], spread: float, seed=None) -> List[List]:
    """Generates a cluster of random points.

    Source:
    https://stackoverflow.com/questions/44356063/how-to-generate-a-set-of-random-points-within-a-given-x-y-coordinates-in-an-x

    Args:
        num_points: The number of points for the cluster.
        center: The center of the cluster.
        spread: How tightly to cluster the data.
        seed: Seed for the random number generator.

    Returns:
        A random cluster of consisting of N points.
    """
    x, y = center
    seed = (seed + y) * x  # Generate different looking clusters if called from generate_clusters
    random = Random(seed)
    points = []
    for i in range(num_points):
        theta = 2 * pi * random.random()
        s = spread * random.random()
        point = [x + s * cos(theta), y + s * sin(theta)]
        points.append(point)
    return points
