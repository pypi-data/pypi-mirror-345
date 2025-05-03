import numpy as np

from .curve_utils import get_peaks, remove_given_width_peaks


def fill_with_value_by_mask(
    data: np.ndarray, mask: np.ndarray, blank_code: float
) -> np.ndarray:
    """
    Востанавливает массив, заполняя кодом бланковки по маске.

    Parameters
    ----------
    data: np.ndarray
        Массив значений, размером N.
    mask: np.ndarray
        Маска(True - в строке был nan, False - в строке не было nan), размером M >= N.
    blank_code: float
        Код бланковки.

    Returns
    -------
    np.ndarray
        Востановленный массив, размером M.
    """

    assert data.ndim == 1, "data: Ожидался 1D массив"
    assert mask.ndim == 1, "mask: Ожидался 1D массив"
    assert (
        mask.shape[0] >= data.shape[0]
    ), "Длина массива mask должна быть не меньше длины data"

    data_with_blank_code = np.zeros(mask.shape[0])
    data_with_blank_code[mask] = blank_code
    data_with_blank_code[~mask] = data
    return data_with_blank_code


def curve_peaks_processing(
    curve: np.ndarray, depth: np.ndarray, minimal_width_in_meter: float
) -> np.ndarray:
    """
    Обработка пиков кривой. Удаление пиков, которые меньше заданной ширины (minimal_width_in_meter).

    Parameters
    ----------
    curve: np.ndarray
        Массив значений кривой, размером N.
    depth: np.ndarray
        Массив глубин кривой, размером N.
    minimal_width_in_meter: float
        Минимальная ширина пиков в метрах.

    Returns
    -------
    np.ndarray
        Обработанная кривая, размером N.
    """

    assert curve.ndim == 1, "curve: Ожидался 1D массив"
    assert depth.ndim == 1, "depth: Ожидался 1D массив"
    assert (
        minimal_width_in_meter > 0
    ), "Параметр minimal_width_in_meter должен принимать положительное значение"

    dz = np.diff(depth)[0]
    minimal_width_in_sample = int(minimal_width_in_meter / dz)

    given_width_peaks = get_peaks(curve, minimal_width_in_sample)
    filled_curve = remove_given_width_peaks(
        curve, given_width_peaks, minimal_width_in_sample
    )
    if np.unique(filled_curve).size == 2:
        filled_curve = abs(filled_curve - 1)
    return filled_curve
