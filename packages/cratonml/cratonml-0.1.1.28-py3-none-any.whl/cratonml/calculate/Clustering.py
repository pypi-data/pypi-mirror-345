import numpy as np
from scipy import stats
from sklearn.cluster import HDBSCAN, KMeans
from sklearn.mixture import GaussianMixture
from typing_extensions import Optional

RANDOM_STATE = 42
ALPHA_K = 0.02


class KMeansClassifier:
    """Класс для KMeans кластеризации."""

    @staticmethod
    def __get_scaled_inertia(data: np.ndarray, cluster: KMeans) -> np.ndarray:
        """Считает взвешенную инерцию."""

        inertia_o = np.square((data - data.mean(axis=0))).sum()
        scaled_inertia = cluster.inertia_ / inertia_o + ALPHA_K * cluster.n_clusters
        return scaled_inertia

    @staticmethod
    def get_cluster(data: np.ndarray, n_clusters: int) -> KMeans:
        cluster = KMeans(
            n_clusters=n_clusters, random_state=RANDOM_STATE, algorithm="elkan"
        )
        cluster.fit(data)
        return cluster

    @staticmethod
    def __get_cluster_centers(kmeans: KMeans) -> np.ndarray:
        kmeans_centers = np.unique(np.sum(kmeans.cluster_centers_, axis=1))
        return kmeans_centers

    @staticmethod
    def __get_labels(kmeans: KMeans) -> np.ndarray:
        """Возвращает список меток."""

        kmeans_labels_before_sorting = kmeans.labels_
        kmeans_centers = KMeansClassifier.__get_cluster_centers(kmeans)
        kmeans_uniq_labels = np.unique(kmeans_labels_before_sorting)
        sorted_kmeans_uniq_labels = kmeans_uniq_labels[np.argsort(kmeans_centers)]

        kmeans_labels = np.zeros_like(kmeans_labels_before_sorting)
        for i, label in enumerate(sorted_kmeans_uniq_labels):
            kmeans_labels[kmeans_labels_before_sorting == label] = i

        return kmeans_labels

    @staticmethod
    def find_the_best_number_of_clusters(
        data: np.ndarray,
    ) -> tuple[range, np.ndarray, int]:
        """
        Подбирает оптимальное количество кластеров на основании взвешенной инерции.

        Parameters
        ----------
        data: np.ndarray
            2D массив значений.

        Returns
        -------
        tuple[range, np.ndarray, int]
            Список количества кластеров для которых производился подсчет.
            Список взвешенных инерций для каждого количества кластеров.
            Оптимальное количество кластеров.
        """

        assert data.ndim == 2, "data: Ожидался 2D массив"

        scaled_inertia_list = []
        number_of_clusters_list = range(2, min(15, data.shape[0]))
        for number_of_clusters in number_of_clusters_list:
            cluster = KMeansClassifier.get_cluster(data, number_of_clusters)
            scaled_inertia = KMeansClassifier.__get_scaled_inertia(data, cluster)
            scaled_inertia_list.append(scaled_inertia)
        scaled_inertia_array = np.asarray(scaled_inertia_list)
        best_number_of_clusters = number_of_clusters_list[
            np.argmin(scaled_inertia_array)
        ]
        return number_of_clusters_list, scaled_inertia_array, best_number_of_clusters

    @staticmethod
    def calculate(data: np.ndarray, n_clusters: int) -> tuple[KMeans, np.ndarray]:
        """
        Распределяет объекты по n_clusters кластерам по сходству. Для вычисления этого сходства используется евклидово расстояние в качестве меры.

        Parameters
        ----------
        data: np.ndarray
            Массив значений (N, M). Где N-количество точек, M - количество атрибутов.
        n_clusters: int
            Количество кластеров.

        Returns
        -------
        tuple[KMeans, np.ndarray]
            Объект класса KMeans.
            Массив меток размера N.
        """

        assert data.ndim == 2, "data: Ожидался 2D массив"
        assert (
            n_clusters > 0
        ), "Параметр n_clusters должен принимать положительное значение"
        cluster = KMeansClassifier.get_cluster(data, n_clusters)
        labels = KMeansClassifier.__get_labels(cluster)
        return cluster, labels


class GaussianMixtureClassifier:
    """Класс для Gaussian Mixture кластеризации."""

    @staticmethod
    def get_cluster(data: np.ndarray, n_clusters: int) -> GaussianMixture:
        cluster = GaussianMixture(n_components=n_clusters, random_state=RANDOM_STATE)
        cluster.fit(data)
        return cluster

    @staticmethod
    def __get_cluster_centers(gm: GaussianMixture, data: np.ndarray) -> np.ndarray:
        centers = np.empty(shape=(gm.n_components, data.shape[1]))
        for i in range(gm.n_components):
            density = stats.multivariate_normal(
                cov=gm.covariances_[i], mean=gm.means_[i]
            ).logpdf(data)
            centers[i, :] = data[np.argmax(density)]
        centers = np.sum(centers, axis=1)
        return centers

    @staticmethod
    def __get_labels(gm: GaussianMixture, data: np.ndarray) -> np.ndarray:
        """Возвращает массив меток."""

        gm_labels_before_sorting = gm.predict(data)
        gm_centers = GaussianMixtureClassifier.__get_cluster_centers(gm, data)
        gm_uniq_labels = np.unique(gm_labels_before_sorting)
        sorted_gm_uniq_labels = gm_uniq_labels[np.argsort(gm_centers)]

        gm_labels = np.zeros_like(gm_labels_before_sorting)
        for i, label in enumerate(sorted_gm_uniq_labels):
            gm_labels[gm_labels_before_sorting == label] = i

        return gm_labels

    @staticmethod
    def find_the_best_number_of_clusters(
        data: np.ndarray,
    ) -> tuple[range, np.ndarray, int]:
        """
        Подбирает оптимальное количество кластеров на основе Байесовского критерия.

        Parameters
        ----------
        data: np.ndarray
            2D массив значений.

        Returns
        -------
        tuple[range, np.ndarray, int]
            Список количества кластеров для которых производился подсчет.
            Список Байесовских критериев для каждого количества кластеров.
            Оптимальное количество кластеров.
        """

        assert data.ndim == 2, "data: Ожидался 2D массив"

        bic_list = []
        number_of_clusters_list = range(2, min(15, data.shape[0]))
        for number_of_clusters in number_of_clusters_list:
            gm = GaussianMixtureClassifier.get_cluster(data, number_of_clusters)
            bic = -gm.bic(data)
            if bic < 0:
                bic = np.nan
            bic_list.append(bic)
        bic_array = np.asarray(bic_list)
        # bic_list_log = np.log(bic_list)
        # best_number_of_clusters = number_of_clusters_list[np.nanargmin(bic_list_log)]
        best_number_of_clusters = number_of_clusters_list[np.nanargmin(bic_array)]
        return number_of_clusters_list, bic_array, best_number_of_clusters

    @staticmethod
    def calculate(
        data: np.ndarray, n_clusters: int
    ) -> tuple[GaussianMixture, np.ndarray]:
        """
        Распределяет объекты по n_clusters кластерам, предполагая, что данные состоят из смеси гауссовых распределений.

        Parameters
        ----------
        data: np.ndarray
            Массив значений (N, M). Где N - количество точек, M - количество атрибутов.
        n_clusters: int
            Количество кластеров.

        Returns
        -------
        tuple[GaussianMixture, np.ndarray]
            Объект класса GaussianMixture.
            Массив меток размера N.
        """

        assert data.ndim == 2, "data: Ожидался 2D массив"
        assert (
            n_clusters > 0
        ), "Параметр n_clusters должен принимать положительное значение"
        cluster = GaussianMixtureClassifier.get_cluster(
            data=data, n_clusters=n_clusters
        )
        labels = GaussianMixtureClassifier.__get_labels(gm=cluster, data=data)
        return cluster, labels


class HDBSCANClassifier:
    """Класс для HDBSCAN кластеризации."""

    @staticmethod
    def get_cluster(
        data: np.ndarray,
        min_cluster_size: Optional[int],
        min_samples: Optional[int],
        cluster_selection_epsilon: float,
    ) -> HDBSCAN:
        cluster = HDBSCAN(
            min_cluster_size=min_cluster_size,
            min_samples=min_samples,
            cluster_selection_epsilon=cluster_selection_epsilon,
        )
        cluster.fit(data)
        return cluster

    @staticmethod
    def __get_labels(hdbscan: HDBSCAN) -> np.ndarray:
        """Возвращает список меток."""

        hdbscan_labels = hdbscan.labels_
        return hdbscan_labels

    @staticmethod
    def get_number_of_clusters(labels: np.ndarray) -> int:
        """
        Возвращает количество кластеров.

        Parameters
        ----------
        labels: np.ndarray
            1D массив меток.

        Returns
        -------
        int
            Количество кластеров.
        """

        assert labels.ndim == 1, "labels: Ожидался 1D массив"

        return np.unique(labels).shape[0]

    @staticmethod
    def calculate(
        data: np.ndarray,
        min_cluster_size: int = 5,
        min_samples: Optional[int] = None,
        cluster_selection_epsilon: float = 0.0,
    ) -> tuple[HDBSCAN, np.ndarray]:
        """
        Выявляет кластеры в наборе данных на основе распределения плотности точек данных.

        Parameters
        ----------
        data: np.ndarray
            Массив значений (N, M). Где N-количество точек, M - количество атрибутов.
        min_cluster_size: int, default=5
            Минимальное количество выборок, чтобы эта группа считалась кластером(параметр HDBSCAN).
        min_samples: int, default=None
            Минимальное количество выборок в окрестности, чтобы точка считалась центральной(параметр HDBSCAN).
        cluster_selection_epsilon: float, default=0.0
            Максимальное расстояние, допустимое между точками, чтобы они считались связанными в процессе кластеризации на основе плотности(параметр HDBSCAN).

        Returns
        -------
        tuple[HDBSCAN, np.ndarray]
            Объект класса HDBSCAN.
            Массив меток размера N.
        """

        assert data.ndim == 2, "data: Ожидался 2D массив"
        cluster = HDBSCANClassifier.get_cluster(
            data, min_cluster_size, min_samples, cluster_selection_epsilon
        )
        labels = HDBSCANClassifier.__get_labels(cluster)
        return cluster, labels
