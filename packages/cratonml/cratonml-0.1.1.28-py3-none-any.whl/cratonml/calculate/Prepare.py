import numpy as np
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import TomekLinks
from sklearn.covariance import EllipticEnvelope
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import MaxAbsScaler, MinMaxScaler, StandardScaler
from typing_extensions import Optional

RANDOM_STATE = 42


def drop_nan(data: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Удаляет строки в которых присутсвует nan.

    Parameters
    ----------
    data: np.ndarray
        1D или 2D массив значений.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Массив без nan.
        Маска(True - в строке есть nan, False - в строке нет nan), в ввиде 1D массива.
    """

    assert data.ndim == 1 or data.ndim == 2, "data: Ожидался 1D или 2D массив"

    if data.ndim == 1:
        mask = np.isnan(data)
    else:
        mask = np.any(np.isnan(data), axis=1)
    return data[~mask], mask


def max_abs_scaler(
    data: np.ndarray, scaler: MaxAbsScaler = None
) -> tuple[np.ndarray, MaxAbsScaler]:
    """
    Масштабирует массив по его максимальному абсолютному значению. f_norm = f / np.max(abs(f), axis=0)

    Parameters
    ----------
    data: np.ndarray
        Массив значений, размером (N, M).
    scaler: MaxAbsScaler, default=None
        Объект класса MaxAbsScaler.

    Returns
    -------
    tuple[np.ndarray, MaxAbsScaler]
        Преобразованный массив, размером (N, M).
        Объект класса MaxAbsScaler.
    """

    assert data.ndim == 2, "data: Ожидался 2D массив"

    if scaler is None:
        scaler = MaxAbsScaler().fit(data)
    return scaler.transform(data), scaler


def min_max_scaler(
    data: np.ndarray, scaler: MinMaxScaler = None
) -> tuple[np.ndarray, MinMaxScaler]:
    """
    Масштабирует массив до диапазона (0,1). f_norm = (f - f.min(axis=0)) / (f.max(axis=0) - f.min(axis=0))

    Parameters
    ----------
    data: np.ndarray
        Массив значений, размером (N, M).
    scaler: MinMaxScaler, default=None
        Объект класса MinMaxScaler.

    Returns
    -------
    tuple[np.ndarray, MinMaxScaler]
        Преобразованный массив, размером (N, M).
        Объект класса MinMaxScaler.
    """

    assert data.ndim == 2, "data: Ожидался 2D массив"

    if scaler is None:
        scaler = MinMaxScaler().fit(data)
    return scaler.transform(data), scaler


def standard_scaler(
    data: np.ndarray, scaler: StandardScaler = None
) -> tuple[np.ndarray, StandardScaler]:
    """
    Масштабирует массив, удалив среднее значение и увеличив дисперсию до единицы.
    f_norm = (f - np.mean(f, axis=0)) / (np.std(f, axis=0))

    Parameters
    ----------
    data: np.ndarray
        Массив значений, размером (N, M).
    scaler: StandardScaler, default=None
        Объект класса StandardScaler.

    Returns
    -------
    tuple[np.ndarray, StandardScaler]
        Преобразованный массив, размером (N, M).
        Объект класса StandardScaler.
    """

    assert data.ndim == 2, "data: Ожидался 2D массив"

    if scaler is None:
        scaler = StandardScaler().fit(data)
    return scaler.transform(data), scaler


def delete_outliers_LOF(
    data: np.ndarray,
    n_neighbors: int = 20,
    algorithm: str = "auto",
    n_jobs: Optional[int] = None,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Избавляет массив значений от выбросов с помощью локального коэффициента выбросов(Local Outlier Factor).

    Local Outlier Factor (LOF) — это алгоритм для выявления аномальных точек в наборе данных.
    Он делает это путем измерения локальной плотности точек вокруг каждой точки данных и сравнения ее с плотностью точек
    вокруг других точек данных.

    Для вычисления локальной плотности точек вокруг каждой точки данных алгоритм LOF использует меру, называемую
    расстоянием достижимости. Расстояние достижимости точки — это мера того, насколько «сложно» достичь этой точки
    из других точек в наборе данных. Для вычисления расстояния достижимости точки алгоритм LOF сначала определяет
    k ближайших соседей точки, где k — указанный пользователем параметр. Затем он вычисляет расстояние между точкой и
    каждым из ее k ближайших соседей. Расстояние достижимости точки затем определяется как максимальное из этих
    k расстояний. Расстояние достижимости используется для расчета локальной плотности достижимости точки, которая
    представляет собой сумму расстояний между точкой и ее k ближайшими соседями, деленную на k.
    Локальная плотность достижимости точки является мерой локальной плотности точек вокруг точки данных.

    Фактор выброса точки рассчитывается как отношение локальной плотности достижимости точки данных к средней локальной
    плотности достижимости ее k ближайших соседей. Высокий фактор выброса указывает на то, что точка с большей
    вероятностью будет выбросом, тогда как низкий фактор выброса указывает на то, что точка с большей вероятностью
    будет нормальной (не выбросом).

    Parameters
    ----------
    data: np.ndarray
        Массив значений, размером (N, M).
    n_neighbors: int, default=20
        Количество соседей(параметр LocalOutlierFactor).
    algorithm: str, default='auto'
        Алгоритм(параметр LocalOutlierFactor).
    n_jobs: int, default=None
        Количество ядер процессора(параметр LocalOutlierFactor).

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Массив значений без выбросов, размером (X, M).
        Маска(True - значение осталось, False - значение выкинули), размером N.
    """

    assert data.ndim == 2, "data: Ожидался 2D массив"

    clf = LocalOutlierFactor(
        n_neighbors=n_neighbors, algorithm=algorithm, n_jobs=n_jobs
    ).fit(data)
    new_data = clf.fit_predict(data)
    mask = new_data == 1
    return data[mask], mask


def delete_outliers_IsolationForest(
    data: np.ndarray,
    n_estimators: int = 100,
    max_samples: str = "auto",
    n_jobs: Optional[int] = None,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Избавляет массив значений от выбросов с помощью алгоритма Isolation Forest.

    IsolationForest «изолирует» наблюдения, случайным образом выбирая признак, а затем
    случайным образом выбирая значение разделения между максимальным и минимальным значениями выбранного признака.

    Поскольку рекурсивное разбиение можно представить в виде древовидной структуры, количество разбиений,
    необходимых для выделения выборки, эквивалентно длине пути от корневого узла до конечного узла.

    Эта длина пути, усреднённая по лесу из таких случайных деревьев,
    является показателем нормальности и функцией принятия решений.

    При случайном разбиении на разделы, аномалии имеют заметно более короткие пути.

    Parameters
    ----------
    data: np.ndarray
        Массив значений, размером (N, M).
    n_estimators: int, default=100
        Количество базовых оценщиков(параметр IsolationForest).
    max_samples: str, default='auto'
        Количество выборок(параметр IsolationForest).
    n_jobs: int, default=None
        Количество ядер процессора(параметр IsolationForest).

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Массив значений без выбросов, размером (X, M).
        Маска(True - значение осталось, False - значение выкинули), размером N.
    """

    assert data.ndim == 2, "data: Ожидался 2D массив"

    clf = IsolationForest(
        random_state=RANDOM_STATE,
        n_estimators=n_estimators,
        max_samples=max_samples,
        n_jobs=n_jobs,
    ).fit(data)
    new_data = clf.predict(data)
    mask = new_data == 1
    return data[mask], mask


def delete_outliers_EllipticEnvelope(
    data: np.ndarray, support_fraction: Optional[float] = None
) -> tuple[np.ndarray, np.ndarray]:
    """
    Избавляет массив распределенных по гауссу значений от выбросов с помощью EllipticEnvelope.

    Апроксимирует данные многомерным нормальным распределением.
    Чем меньше вероятность, что точка принадлежит распределению, тем больше вероятность, что она аномальная.

    Parameters
    ----------
    data: np.ndarray
        Массив значений, размером (N, M).
    support_fraction: float, default=None
        Доля точек(параметр EllipticEnvelope).

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Массив значений без выбросов, размером (X, M).
        Маска(True - значение осталось, False - значение выкинули), размером N.
    """

    assert data.ndim == 2, "data: Ожидался 2D массив"

    clf = EllipticEnvelope(
        random_state=RANDOM_STATE, support_fraction=support_fraction
    ).fit(data)
    new_data = clf.predict(data)
    mask = new_data == 1
    return data[mask], mask


def tomek_links(
    data: np.ndarray,
    targets: np.ndarray,
    sampling_strategy: str = "auto",
    n_jobs: Optional[int] = None,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Выполняет заниженную выборку путем удаления ссылок Томека.

    Алгоритм находит выборки данных из класса большинства,
    которые имеют наименьшее евклидово расстояние с данными класса меньшинства, а затем удаляет их.

    Parameters
    ----------
    data: np.ndarray
        Массив значений, размера (N1, M1).
    targets: np.ndarray
        Массив меток data, размера N1.
    sampling_strategy: str, default='auto'
        Стратегия выборки(параметр TomekLinks).
    n_jobs: Optional[int], default=None
        Количество ядер процессора(параметр TomekLinks).

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Массив, содержащий данные с повторной выборкой, размера (N2, M2).
        Массив меток, размера N2.
    """

    assert data.ndim == 2, "data: Ожидался 2D массив"
    assert targets.ndim == 1, "targets: Ожидался 1D массив"
    assert (
        data.shape[0] == targets.shape[0]
    ), "Массив targets имеет несоответствующую длину"

    tl = TomekLinks(sampling_strategy=sampling_strategy, n_jobs=n_jobs)
    data_res, targets_res = tl.fit_resample(data, targets)
    return data_res, targets_res


def SMOTE_(
    data: np.ndarray,
    targets: np.ndarray,
    sampling_strategy: str = "auto",
    k_neighbors: int = 5,
    n_jobs: Optional[int] = None,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Выполненяет избыточную выборку с использованием метода синтетической передискретизации меньшинства.

    SMOTE синтезирует элементы в непосредственной близости от уже существующих в меньшем наборе.

    Алгоритм выбирает элементы, которые близки, проводит линию между ними и
    добавляет новый элемент в точке вдоль этой линии.

    Parameters
    ----------
    data: np.ndarray
        Массив значений, размера (N1, M1).
    targets: np.ndarray
        Массив меток data, размера N1.
    sampling_strategy: str, default='auto'
        Стратегия выборки(параметр SMOTE).
    k_neighbors: int, default=5
        Количество ближайших соседей(параметр SMOTE).
    n_jobs: int, default=None
        Количество ядер процессора(параметр SMOTE).

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Массив, содержащий данные с повторной выборкой, размера (N2, M2).
        Массив меток, размера N2.
    """

    assert data.ndim == 2, "data: Ожидался 2D массив"
    assert targets.ndim == 1, "targets: Ожидался 1D массив"
    assert (
        data.shape[0] == targets.shape[0]
    ), "Массив targets имеет несоответствующую длину"

    sm = SMOTE(
        sampling_strategy=sampling_strategy,
        k_neighbors=k_neighbors,
        n_jobs=n_jobs,
        random_state=RANDOM_STATE,
    )
    data_res, targets_res = sm.fit_resample(data, targets)
    return data_res, targets_res
