import numpy as np
from .utils import euclidean_distance  # Import function euclidean_distance

class DBSCAN:
    """
    Description:
    ------------
    DBSCAN (Density-Based Spatial Clustering of Applications with Noise) is a clustering algorithm that identifies clusters based on the density of points. It groups nearby points (defined by epsilon and min_samples) and labels outliers as noise.

    Arguments:
    -----------
    - eps (float): The maximum radius to consider two points as neighbors.
    - min_samples (int): The minimum number of points to form a cluster.

    Functions:
    -----------
    - __init__(self, eps=0.5, min_samples=5): Initializes DBSCAN with epsilon and min_samples.
    - fit_predict(self, data): Performs DBSCAN clustering on the data.
    - _region_query(self, data, point_index): Finds neighbors within a given radius.
    - _expand_cluster(self, data, point_index, cluster_id, neighbors): Extends a cluster from a center point.
    - plot_clusters(self, data): Plots the resulting clusters (for 2D data).

    Example:
    ---------
    dbscan = DBSCAN(eps=0.5, min_samples=5)
    labels = dbscan.fit_predict(data)
    dbscan.plot_clusters(data)
    """

    def __init__(self, eps=0.5, min_samples=5):
        """
        Description:
        ------------
        Initializes the DBSCAN parameters.

        Arguments:
        -----------
        - eps (float): The maximum radius to consider two points as neighbors.
        - min_samples (int): The minimum number of points to form a cluster.

        Functions:
        -----------
        - Sets the epsilon (eps) and minimum samples (min_samples) parameters.
        - Initializes cluster labels to None.

        Example:
        ---------
        dbscan = DBSCAN(eps=0.5, min_samples=5)
        """
        self.eps = eps
        self.min_samples = min_samples
        self.labels = None  # Cluster labels

    def fit_predict(self, data):
        """
        Description:
        ------------
        Performs DBSCAN clustering on the provided data.

        Arguments:
        -----------
        - data (numpy.ndarray): The data to cluster (n_samples, n_features).

        Functions:
        -----------
        - Initializes all points as noise (label -1).
        - Iterates through each point to find core points and expand clusters.
        - Returns the cluster labels for each point.

        Example:
        ---------
        labels = dbscan.fit_predict(data)
        """
        self.labels = np.full(len(data), -1)  # Initialize all points as noise
        cluster_id = 0

        for i in range(len(data)):
            if self.labels[i] != -1:
                continue  # Point already visited

            # Find the neighbors of the current point
            neighbors = self._region_query(data, i)

            if len(neighbors) < self.min_samples:
                # Not a central point, remains noise
                continue

            # New cluster
            self._expand_cluster(data, i, cluster_id, neighbors)
            cluster_id += 1

        return self.labels

    def _region_query(self, data, point_index):
        """
        Description:
        ------------
        Finds the neighbors of a point within a given radius.

        Arguments:
        -----------
        - data (numpy.ndarray): The data.
        - point_index (int): The point index.

        Functions:
        -----------
        - Calculates the Euclidean distance between the point and all other points.
        - Returns a list of indices of neighboring points within the epsilon radius.

        Example:
        ---------
        neighbors = self._region_query(data, 5)
        """
        neighbors = []
        for i in range(len(data)):
            if euclidean_distance(data[point_index], data[i]) <= self.eps:
                neighbors.append(i)
        return neighbors
        
    def _expand_cluster(self, data, point_index, cluster_id, neighbors):
        """
        Description:
        ------------
        Extends a cluster from a core point.

        Arguments:
        -----------
        - data (numpy.ndarray): The data.
        - point_index (int): The index of the core point.
        - cluster_id (int): The ID of the current cluster.
        - neighbors (list): The indices of the core point's neighbors.

        Functions:
        -----------
        - Assigns the cluster ID to the core point.
        - Iteratively expands the cluster by finding neighbors of neighbors.
        - Assigns the cluster ID to all reachable points.

        Example:
        ---------
        self._expand_cluster(data, 10, 0, neighbors)
        """
        self.labels[point_index] = cluster_id
        i = 0
        while i < len(neighbors):
            neighbor_index = neighbors[i]
            if self.labels[neighbor_index] == -1:
                # Go to neighor
                self.labels[neighbor_index] = cluster_id

                # Find neighors to neighor
                new_neighbors = self._region_query(data, neighbor_index)
                if len(new_neighbors) >= self.min_samples:
                    # Adds new neighbors to the list of neighbors to visit
                    neighbors += set(new_neighbors)
            i += 1
