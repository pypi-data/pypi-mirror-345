import numpy as np
from scipy.signal import find_peaks


def remove_given_width_peaks(
    data: np.ndarray, peaks: np.ndarray, width: int
) -> np.ndarray:
    """Удаляет из массива data пики по индексам peaks с разрешенной минимальной шириной width."""

    window_size = width + width // 2 + width % 2
    filled_data = np.copy(data)
    for i in peaks:
        peak_left = 0
        peak_right = len(data)
        for j in range(1, width + 1):
            if i - j >= 0 and peak_left == 0:
                if data[i] != data[i - j]:
                    peak_left = i - j + 1
            if i + j < len(data) and peak_right == len(data):
                if data[i] != data[i + j]:
                    peak_right = i + j
        left = max(0, i - window_size)
        right = min(len(data) - 1, i + window_size + 1)

        unique, counts = np.unique(filled_data[left:right], return_counts=True)
        val = unique[np.where(counts == max(counts))[0][0]]
        filled_data[peak_left:peak_right] = val
    return filled_data.astype("int")


def get_peaks(curve: np.ndarray, width: int) -> np.ndarray:
    """Находит пики в кривой curve с шириной не более width. Возвращает индексы пиков."""

    peaks = []
    for i in range(np.max(curve) + 1):
        data = np.zeros(curve.shape)
        mask = curve == i
        data[mask] = 1
        new_peaks, _ = find_peaks(data, width=[0, width])
        if i == 0:
            peaks = new_peaks
        peaks = np.unique(np.hstack((new_peaks, peaks)))

    for i in range(1, width):
        if curve[0] != curve[i]:
            peaks = np.unique(np.hstack(([i // 2], peaks)))
            break
    for i in range(1, width):
        if curve[len(curve) - 1] != curve[len(curve) - 1 - i]:
            peaks = np.unique(np.hstack(([len(curve) - 1 - i // 2], peaks)))
            break

    peaks_array = np.asarray(peaks)
    return peaks_array
