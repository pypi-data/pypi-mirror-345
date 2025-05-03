import numpy as np
from sklearn.decomposition import PCA

RANDOM_STATE = 42


def get_pca_statistics(data: np.ndarray) -> np.ndarray:
    """
    Считает долю дисперсии для каждого компонента.

    Parameters
    ----------
    data: np.ndarray
        Массив значений, размера (N, M).

    Returns
    -------
    np.ndarray
        Массив доль дисперсии, размера N.
    """

    assert data.ndim == 2, "data: Ожидался 2D массив"

    pca = PCA(n_components=data.shape[1], random_state=RANDOM_STATE)
    pca.fit(data)
    return pca.explained_variance_ratio_


def pca_transform(data: np.ndarray, n_components: int) -> np.ndarray:
    """
    Понижение размерности с помощью PCA путём проецирования данных на главные (собственные) вектора.

    Parameters
    ----------
    data: np.ndarray
        Массив значений, размера (N, M).
    n_components: int
        Количество сохраняемых компонентов.

    Returns
    -------
    np.ndarray
        Преобразованный массив, размера (N, n_components).
    """

    assert data.ndim == 2, "data: Ожидался 2D массив"
    assert (
        n_components > 0
    ), "Параметр n_components должен принимать положительное значение"

    return PCA(n_components=n_components, random_state=RANDOM_STATE).fit_transform(data)
