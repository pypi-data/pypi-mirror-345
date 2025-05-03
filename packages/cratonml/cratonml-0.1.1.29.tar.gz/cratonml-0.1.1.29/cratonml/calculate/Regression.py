import numpy as np
from sklearn import linear_model


class RANSACRegression:
    """Класс для RANdom SAmple Consensus регрессии"""

    @staticmethod
    def get_model(
        x_train: np.ndarray, y_train: np.ndarray
    ) -> linear_model.RANSACRegressor:
        """
        Возвращает модель обученную на тренировочных данных.

        Parameters
        ----------
        x_train: np.ndarray
            Массив значений размера (n_samples, n_features).
            Где n_samples - количество образцов, n_features - количество признаков.
        y_train: np.ndarray
            Массив значений размера (n_samples, n_targets) или (n_samples,).
            Где n_samples - количество образцов, n_targets - количество целевых переменных.

        Returns
        -------
        RANSACRegressor
            Обученная модель.
        """
        assert x_train.ndim == 2, "x_train: Ожидался 2D массив"
        assert (
            y_train.ndim == 1 or y_train.ndim == 2
        ), "y_train: Ожидался 1D или 2D массив"
        assert (
            x_train.shape[0] == y_train.shape[0]
        ), "Длина массивов x_train и y_train должна быть равна"

        model = linear_model.RANSACRegressor()
        model.fit(x_train, y_train)
        return model

    @staticmethod
    def predict(model: linear_model.RANSACRegressor, x_test: np.ndarray) -> np.ndarray:
        """
         Прогнозирует значения для тестового набора данных.

        Parameters
        ----------
        model: RANSACRegressor
            Обученная модель.
        x_test: np.ndarray
            Массив значений размера (n_samples, n_features).
            Где n_samples - количество образцов, n_features - количество признаков.

        Returns
        -------
        np.ndarray
            Массив предсказанных значений размера (n_samples, n_targets) или (n_samples,). Где n_targets - количество целевых переменных.
        """

        assert x_test.ndim == 2, "x_test: Ожидался 2D массив"

        prediction = model.predict(x_test)
        return prediction

    @staticmethod
    def get_coeffs(
        model: linear_model.RANSACRegressor,
    ) -> tuple[np.ndarray, float | np.ndarray]:
        """
         Получает коэффициенты линейной регрессии.

        Parameters
        ----------
        model: RANSACRegressor
            Обученная модель.

        Returns
        -------
        tuple[np.ndarray, float | np.ndarray]
            Массив коэффициентов, отвечающих за наклон. Если n_targets = 1 то размер (n_features,). Иначе размер(n_targets, n_features).
                (n_features - количество признаков, n_targets - количество целевых переменных)
            Массив коэффициентов или коэффициент, отвечающий за смещение. Если n_targets = 1 то float. Иначе размер массива (n_targets,).
        """

        a = model.estimator_.coef_
        b = model.estimator_.intercept_
        return a, b


class LinearRegression:
    """Класс для линейной регрессии"""

    @staticmethod
    def get_model(
        x_train: np.ndarray, y_train: np.ndarray
    ) -> linear_model.LinearRegression:
        """
        Возвращает модель обученную на тренировочных данных.

        Parameters
        ----------
        x_train: np.ndarray
            Массив значений размера (n_samples, n_features).
            Где n_samples - количество образцов, n_features - количество признаков.
        y_train: np.ndarray
            Массив значений размера (n_samples, n_targets) или (n_samples,).
            Где n_samples - количество образцов, n_targets - количество целевых переменных.

        Returns
        -------
        LinearRegression
            Обученная модель.
        """
        assert x_train.ndim == 2, "x_train: Ожидался 2D массив"
        assert (
            y_train.ndim == 1 or y_train.ndim == 2
        ), "y_train: Ожидался 1D или 2D массив"
        assert (
            x_train.shape[0] == y_train.shape[0]
        ), "Длина массивов x_train и y_train должна быть равна"

        model = linear_model.LinearRegression()
        model.fit(x_train, y_train)
        return model

    @staticmethod
    def predict(model: linear_model.LinearRegression, x_test: np.ndarray) -> np.ndarray:
        """
         Прогнозирует значения для тестового набора данных.

        Parameters
        ----------
        model: RANSACRegressor
            Обученная модель.
        x_test: np.ndarray
            Массив значений размера (n_samples, n_features).
            Где n_samples - количество образцов, n_features - количество признаков.

        Returns
        -------
        np.ndarray
            Массив предсказанных значений размера (n_samples,).
        """

        assert x_test.ndim == 2, "x_test: Ожидался 2D массив"

        prediction = model.predict(x_test)
        return prediction

    @staticmethod
    def get_coeffs(
        model: linear_model.LinearRegression,
    ) -> tuple[np.ndarray, float | np.ndarray]:
        """
         Получает коэффициенты линейной регрессии.

        Parameters
        ----------
        model: LinearRegression
            Обученная модель.

        Returns
        -------
        tuple[np.ndarray, float | np.ndarray]
            Массив коэффициентов, отвечающих за наклон. Если n_targets = 1 то размер (n_features,). Иначе размер(n_targets, n_features).
                (n_features - количество признаков, n_targets - количество целевых переменных)
            Массив коэффициентов или коэффициент, отвечающий за смещение. Если n_targets = 1 то float. Иначе размер массива (n_targets,).
        """

        a = model.coef_
        b = model.intercept_
        return a, b
