import numpy as np
from .utils import euclidean_distance  # Import function euclidean_distance
from .kmeans import KMeans

class HierarchicalClustering:
    """
      Description:
      ------------
      HierarchicalClustering performs hierarchical clustering using either the agglomerative (bottom-up)
      or divisive (top-down) approach.

      Arguments:
      -----------
      - n_clusters (int or None): Desired number of clusters (required for divisive method).
      - linkage (str): Linkage criterion to use for merging clusters ('single', 'complete', 'average').
      - method (str): Clustering strategy ('agglomerative' or 'divisive').

      Functions:
      -----------
      - __init__(self, n_clusters=None, linkage='single', method='agglomerative'): Initializes the clustering parameters.
      - fit_predict(self, data, kmeans=None): Performs hierarchical clustering and returns cluster labels.
      - _agglomerative_clustering(self, data): Implements the agglomerative clustering algorithm.
      - _divisive_clustering(self, data, kmeans): Implements the divisive clustering algorithm.
      - _bisect_cluster(self, data, cluster, kmeans): Splits a cluster into two using KMeans.
      - _compute_distance_matrix(self, data): Computes the pairwise distance matrix.
      - _compute_linkage_distance(self, cluster1, cluster2, distances, linkage): Computes inter-cluster distance.
      
      Example:
      ---------
      hierarchical = HierarchicalClustering(n_clusters=3, linkage='complete', method='agglomerative')
      labels = hierarchical.fit_predict(data)
      hierarchical.plot_clusters(data, labels)
    """

    def __init__(self, n_clusters=None, linkage='single', method='agglomerative'):
        """
        Description:
        ------------
        Initializes the hierarchical clustering parameters.

        Arguments:
        -----------
        - n_clusters (int, optional): Desired number of clusters (required for the divisive method).
          If None, agglomerative clustering proceeds until all points are merged.
        - linkage (str, optional): Linkage criterion to use ('single', 'complete', 'average').
        - method (str, optional): Clustering method to apply ('agglomerative' or 'divisive').

        Functions:
        -----------
        - Sets the number of clusters, linkage method, and clustering method.

        Example:
        ---------
        hierarchical = HierarchicalClustering(n_clusters=3, linkage='complete', method='agglomerative')
        """
        self.n_clusters = n_clusters
        self.linkage = linkage
        self.method = method
        self.labels = None
        self.linked_matrix = None  # Adding a variable to store the linkage matrix

    def fit_predict(self, data, kmeans=None):
        """
        Description:
        ------------
        Performs hierarchical clustering on the given data.

        Arguments:
        -----------
        - data (numpy.ndarray): Data to be clustered (n_samples, n_features).
        - kmeans (KMeans, optional): KMeans instance, required for the divisive method

        Functions:
        -----------
        - Executes either agglomerative or divisive clustering based on the chosen method.
        - Returns the cluster labels assigned to each data point.

        Example:
        ---------
        labels = hierarchical.fit_predict(data)
        """
        if self.method == 'agglomerative':
            self.labels = self._agglomerative_clustering(data)
        elif self.method == 'divisive':
            if self.n_clusters is None:
                raise ValueError("n_clusters must be specified for the divisive method.")
            self.labels = self._divisive_clustering(data, kmeans)
        else:
            raise ValueError("Method not found. Choose 'agglomerative' or 'divisive'.")

        return self.labels

    def _agglomerative_clustering(self, data):
        """
        Description:
        ------------
        Implements agglomerative (bottom-up) hierarchical clustering.

        Arguments:
        -----------
        - data (numpy.ndarray): The dataset to be clustered.

        Functions:
        -----------
        - Initializes each point as a cluster.
        - Iteratively merges the closest clusters until the desired number of clusters is reached.
        - Assigns cluster labels to each data point.

        Example:
        ---------
        labels = self._agglomerative_clustering(data)
        """
        # Initialization: each point is a cluster
        clusters = [{i} for i in range(len(data))]
        distances = self._compute_distance_matrix(data)

        # Agglomerative clustering loop
        while len(clusters) > self.n_clusters if self.n_clusters else len(clusters) > 1:
            # Find the two closest clusters
            min_i, min_j = None, None
            min_distance = float('inf')
            for i in range(len(clusters)):
                for j in range(i + 1, len(clusters)):
                    distance = self._compute_linkage_distance(clusters[i], clusters[j], distances, self.linkage)
                    if distance < min_distance:
                        min_distance = distance
                        min_i, min_j = i, j

            # Merge the two closest clusters
            clusters[min_i] = clusters[min_i].union(clusters[min_j])
            del clusters[min_j]

            # Break if the desired number of clusters is reached
            if self.n_clusters and len(clusters) <= self.n_clusters:
                break

        # Assign labels
        labels = np.zeros(len(data), dtype=int)
        for i, cluster in enumerate(clusters):
            for point_index in cluster:
                labels[point_index] = i

        return labels

    def _divisive_clustering(self, data, kmeans):
        """
        Description:
        ------------
        Implements divisive (top-down) hierarchical clustering.

        Arguments:
        -----------
        - data (numpy.ndarray): The dataset to be clustered.
        - kmeans (KMeans): An instance of a KMeans algorithm used to split clusters.

        Returns:
        --------
        - numpy.ndarray: Cluster labels assigned to each data point.
        """
        # Initialization: all points are in a single cluster
        clusters = [set(range(len(data)))]

        while len(clusters) < self.n_clusters:
            # Find the largest cluster (the one with the greatest number of points)
            largest_cluster_index = np.argmax([len(cluster) for cluster in clusters])
            largest_cluster = clusters[largest_cluster_index]

            # Split the larger cluster into two sub-clusters
            cluster1, cluster2 = self._bisect_cluster(data, largest_cluster, kmeans)

            # Replace the original cluster with the two new subclusters
            del clusters[largest_cluster_index]
            clusters.append(cluster1)
            clusters.append(cluster2)

        # Assign labels
        labels = np.zeros(len(data), dtype=int)
        for i, cluster in enumerate(clusters):
            for point_index in cluster:
                labels[point_index] = i

        return labels

    def _bisect_cluster(self, data, cluster, kmeans):
        """
        Description:
        ------------
        Splits a cluster into two sub-clusters using a simple method (K-Means with k=2).

        Arguments:
        -----------
        - data (numpy.ndarray): The complete dataset.
        - cluster (set): Indices of the data points belonging to the cluster to be split.
        - kmeans (KMeans): An instance of the KMeans algorithm (can be reinitialized inside the method).

        Returns:
        --------
        - tuple: Two sets representing the indices of the resulting sub-clusters.
        """
        # Convert cluster to data
        cluster_data = data[list(cluster)]

        # Use k-means to divide the cluster into two
        kmeans = KMeans(n_clusters=2, random_state=42)  # Vous pouvez ajuster les paramètres de KMeans
        labels = kmeans.fit_predict(cluster_data)

        # Create the two subclusters
        cluster1 = set([list(cluster)[i] for i in range(len(cluster)) if labels[i] == 0])
        cluster2 = set([list(cluster)[i] for i in range(len(cluster)) if labels[i] == 1])

        return cluster1, cluster2

    def _compute_distance_matrix(self, data):
        """
        Description:
        ------------
        Computes the distance matrix between all data points.

        Arguments:
        -----------
        - data (numpy.ndarray): The dataset (n_samples, n_features).

        Returns:
        --------
        - numpy.ndarray: A symmetric matrix containing pairwise distances between data points.
        """
        n_samples = len(data)
        distances = np.zeros((n_samples, n_samples))
        for i in range(n_samples):
            for j in range(i + 1, n_samples):
                distances[i, j] = distances[j, i] = euclidean_distance(data[i], data[j])
        return distances

    def _compute_linkage_distance(self, cluster1, cluster2, distances, linkage='single'):
        """
        Description:
        ------------
        Computes the distance between two clusters using the specified linkage criterion.

        Arguments:
        -----------
        - cluster1 (set): Indices of the first cluster.
        - cluster2 (set): Indices of the second cluster.
        - distances (numpy.ndarray): Precomputed distance matrix between all data points.
        - linkage (str): Linkage criterion to use ('single', 'complete', or 'average').

        Returns:
        --------
        - float: The computed linkage distance between the two clusters.
        """
        if linkage == 'single':
            # Minimum distance between points of the two clusters
            min_distance = float('inf')
            for i in cluster1:
                for j in cluster2:
                    distance = distances[i, j]
                    if distance < min_distance:
                        min_distance = distance
            return min_distance
        elif linkage == 'complete':
            # Maximum distance between points of the two clusters
            max_distance = float('-inf')
            for i in cluster1:
                for j in cluster2:
                    distance = distances[i, j]
                    if distance > max_distance:
                        max_distance = distance
            return max_distance
        elif linkage == 'average':
            # Average distance between points of the two clusters
            total_distance = 0
            for i in cluster1:
                for j in cluster2:
                    total_distance += distances[i, j]
            return total_distance / (len(cluster1) * len(cluster2))
        else:
            raise ValueError("Critère de linkage non reconnu. Choisissez 'single', 'complete' ou 'average'.")
