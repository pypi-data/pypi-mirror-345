import numpy as np
from scipy import stats


def correlation_coefficient(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """
    Считает коэффициент корреляции Пирсона и p-значение.

    Коэффициент корреляции Пирсона измеряет линейную зависимость между двумя наборами данных.
    Изменяется в диапазоне от -1 до +1, где 0 означает отсутствие корреляции.
    Корреляция, равная -1 или +1, означает точную линейную зависимость.
    Положительная корреляция означает, что по мере увеличения x увеличивается и y.
    Отрицательная корреляция означает, что по мере увеличения x уменьшается и y.

    p-значение - это вероятность того, что некоррелированная система создаст наборы данных,
    корреляция Пирсона в которых будет как минимум такой же сильной, как в этих наборах данных.

    Parameters
    ----------
    x: np.ndarray
        1D массив значений.
    y: np.ndarray
        1D массив значений.

    Returns
    -------
    tuple[float, float]
        Коэффициент корреляции и вероятность получения наблюдаемых результатов.
    """

    assert x.ndim == 1, "x: Ожидался 1D массив"
    assert y.ndim == 1, "y: Ожидался 1D массив"
    assert x.shape == y.shape, "x и y должны иметь одинаковую длину"

    result = stats.pearsonr(x, y)
    corr_coef = result.statistic
    p_value = result.pvalue
    return corr_coef, p_value


def spearman_correlation_coefficient(
    x: np.ndarray, y: np.ndarray
) -> tuple[float, float]:
    """
    Считает коэффициент корреляции Спирмена и p-значение.

    Коэффициент корреляции Спирмена — это непараметрическая мера монотонности взаимосвязи между двумя наборами данных.
    Изменяется в диапазоне от -1 до +1, где 0 означает отсутствие корреляции.
    Корреляция, равная -1 или +1, означает точную монотонную взаимосвязь.
    Положительная корреляция означает, что по мере увеличения x увеличивается и y.
    Отрицательная корреляция означает, что по мере увеличения x уменьшается и y.

    p-значение - это вероятность того, что некоррелированная система создаст наборы данных,
    корреляция Спирмена в которых будет как минимум такой же сильной, как в этих наборах данных.

    Parameters
    ----------
    x: np.ndarray
        1D массив значений.
    y: np.ndarray
        1D массив значений.

    Returns
    -------
    tuple[float, float]
        Коэффициент корреляции и вероятность получения наблюдаемых результатов.
    """

    assert x.ndim == 1, "x: Ожидался 1D массив"
    assert y.ndim == 1, "y: Ожидался 1D массив"
    assert x.shape == y.shape, "x и y должны иметь одинаковую длину"

    result = stats.spearmanr(x, y)
    corr_coef = result.statistic
    p_value = result.pvalue
    return corr_coef, p_value


def correlation_coefficients_matrix(data: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Считает матрицу корреляции Пирсона и матрицу p-значений.

    Коэффициент корреляции Пирсона измеряет линейную зависимость между двумя наборами данных.
    Изменяется в диапазоне от -1 до +1, где 0 означает отсутствие корреляции.
    Корреляция, равная -1 или +1, означает точную линейную зависимость.
    Положительная корреляция означает, что по мере увеличения x увеличивается и y.
    Отрицательная корреляция означает, что по мере увеличения x уменьшается и y.

    p-значение - это вероятность того, что некоррелированная система создаст наборы данных,
    корреляция Пирсона в которых будет как минимум такой же сильной, как в этих наборах данных.

    Parameters
    ----------
    data: np.ndarray
        Массив значений, размера (N, M).

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Матрица корреляции(размера (N, N)) и матрица вероятностей получения наблюдаемых результатов(размера (N, N)).
    """

    assert data.ndim == 2, "data: Ожидался 2D массив"
    assert data.shape[1] >= 2, "data: Ожидался массив с элементами длинной не менее 2"

    matrix = np.zeros((data.shape[0], data.shape[0]), dtype=float)
    p_matrix = np.zeros((data.shape[0], data.shape[0]), dtype=float)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[0]):
            matrix[i, j], p_matrix[i, j] = correlation_coefficient(data[i], data[j])
    return matrix, p_matrix


def spearman_correlation_coefficients_matrix(
    data: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Считает матрицу корреляции Спирмена и матрицу p-значений.

    Коэффициент корреляции Спирмена — это непараметрическая мера монотонности взаимосвязи между двумя наборами данных.
    Изменяется в диапазоне от -1 до +1, где 0 означает отсутствие корреляции.
    Корреляция, равная -1 или +1, означает точную монотонную взаимосвязь.
    Положительная корреляция означает, что по мере увеличения x увеличивается и y.
    Отрицательная корреляция означает, что по мере увеличения x уменьшается и y.

    p-значение - это вероятность того, что некоррелированная система создаст наборы данных,
    корреляция Спирмена в которых будет как минимум такой же сильной, как в этих наборах данных.

    Parameters
    ----------
    data: np.ndarray
        Массив значений, размера (N, M).

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Матрица корреляции(размера (M, M)) и матрица вероятностей получения наблюдаемых результатов(размера (M, M)).
    """

    assert data.ndim == 2, "data: Ожидался 2D массив"
    assert data.shape[1] >= 2, "data: Ожидался массив с элементами длинной не менее 2"

    matrix = np.zeros((data.shape[0], data.shape[0]), dtype=float)
    p_matrix = np.zeros((data.shape[0], data.shape[0]), dtype=float)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[0]):
            matrix[i, j], p_matrix[i, j] = spearman_correlation_coefficient(
                data[i], data[j]
            )
    return matrix, p_matrix


def confusion_matrix(
    true_labels: np.ndarray, predict_labels: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """
    Считает матрицу ошибок(несоответствий).

    Матрица ошибок — матрица, в которой отображается количество предсказанных и фактических классов.
    Строки представляют истинные классы, а столбцы представляют предсказанные классы.
    Если uniq_labels - это массив уникальных классов, то значение элемента (i, j) в матрице ошибок - это количество раз,
    когда предсказан класс uniq_labels[j], а истинное значение класса uniq_labels[i].

    Parameters
    ----------
    true_labels: np.ndarray
        1D массив истинных классов, длины M.
    predict_labels: np.ndarray
        1D массив предсказанных классов, длины M.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Матрица ошибок, размера (M, M).
        Массив уникальных классов, длины M.
    """

    assert true_labels.ndim == 1, "true_labels: Ожидался 1D массив"
    assert predict_labels.ndim == 1, "predict_labels: Ожидался 1D массив"
    assert (
        true_labels.shape == predict_labels.shape
    ), "true_labels и predict_labels должны иметь одинаковую длину"

    uniq_labels = np.unique(np.hstack((true_labels, predict_labels)))
    matrix = np.zeros((len(uniq_labels), len(uniq_labels)))
    for i in range(len(true_labels)):
        first_idx = int(np.where(uniq_labels == true_labels[i])[0][0])
        second_idx = int(np.where(uniq_labels == predict_labels[i])[0][0])
        matrix[first_idx][second_idx] += 1
    return matrix.astype(int), uniq_labels
