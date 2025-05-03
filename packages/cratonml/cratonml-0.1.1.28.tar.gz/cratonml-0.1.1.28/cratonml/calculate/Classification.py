import numpy as np
from sklearn.ensemble import RandomForestClassifier as RandomForest
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier as DecisionTree
from typing_extensions import Optional


class GaussianNaiveBayesClassifier:
    """Класс для классификации алгоритмом Gaussian Naive Bayes."""

    @staticmethod
    def get_model(x_train: np.ndarray, y_train: np.ndarray) -> GaussianNB:
        """
        Возвращает модель обученную на тренировочных данных.

        Parameters
        ----------
        x_train: np.ndarray
            Массив значений размера (N, M). Где N - количество точек, M - количество атрибутов.
        y_train: np.ndarray
            Массив значений размера N.

        Returns
        -------
        GaussianNB
            Обученная модель.
        """

        assert x_train.ndim == 2, "x_train: Ожидался 2D массив"
        assert y_train.ndim == 1, "y_train: Ожидался 1D массив"
        assert (
            x_train.shape[0] == y_train.shape[0]
        ), "Массив y_train имеет несоответствующую длину"

        model = GaussianNB()
        model.fit(x_train, y_train)
        return model

    @staticmethod
    def predict(model: GaussianNB, x_test: np.ndarray) -> np.ndarray:
        """
         Прогнозирует метки для тестового набора данных.

        Parameters
        ----------
        model: GaussianNB
            Обученная модель.
        x_test: np.ndarray
            Массив значений размера (N, M). Где N - количество точек, M - количество атрибутов.

        Returns
        -------
        np.ndarray
            Массив меток размера N.
        """

        assert x_test.ndim == 2, "x_test: Ожидался 2D массив"

        prediction = model.predict(x_test)
        return prediction


class LogisticRegressionClassifier:
    """Класс для классификации алгоритмом Logistic Regression."""

    @staticmethod
    def get_model(x_train: np.ndarray, y_train: np.ndarray) -> LogisticRegression:
        """
        Возвращает модель обученную на тренировочных данных.

        Parameters
        ----------
        x_train: np.ndarray
            Массив значений размера (N, M). Где N - количество точек, M - количество атрибутов.
        y_train: np.ndarray
            Массив значений размера N.

        Returns
        -------
        LogisticRegression
            Обученная модель.
        """

        assert x_train.ndim == 2, "x_train: Ожидался 2D массив"
        assert y_train.ndim == 1, "y_train: Ожидался 1D массив"
        assert (
            x_train.shape[0] == y_train.shape[0]
        ), "Массив y_train имеет несоответствующую длину"

        model = LogisticRegression()
        model.fit(x_train, y_train)
        return model

    @staticmethod
    def predict(model: LogisticRegression, x_test: np.ndarray) -> np.ndarray:
        """
         Прогнозирует метки для тестового набора данных.

        Parameters
        ----------
        model: LogisticRegression
            Обученная модель.
        x_test: np.ndarray
            Массив значений размера (N, M). Где N - количество точек, M - количество атрибутов.

        Returns
        -------
        np.ndarray
            Массив меток размера N.
        """

        assert x_test.ndim == 2, "x_test: Ожидался 2D массив"

        prediction = model.predict(x_test)
        return prediction


class DecisionTreeClassifier:
    """Класс для классификации Decision Tree."""

    @staticmethod
    def get_model(
        x_train: np.ndarray,
        y_train: np.ndarray,
        min_samples_split: Optional[int] = 2,
        max_depth: Optional[int] = None,
    ) -> DecisionTree:
        """
        Возвращает модель обученную на тренировочных данных.

        Parameters
        ----------
        x_train: np.ndarray
            Массив значений размера (N, M). Где N - количество точек, M - количество атрибутов.
        y_train: np.ndarray
            Массив значений размера N.
        min_samples_split: int or float = 2
            Минимальное количество выборок, необходимое для разделения внутреннего узла.(параметр DecisionTree).
        max_depth: int = None
            Максимальная глубина дерева(параметр DecisionTree).

        Returns
        -------
        DecisionTree
            Обученная модель.
        """

        assert x_train.ndim == 2, "x_train: Ожидался 2D массив"
        assert y_train.ndim == 1, "y_train: Ожидался 1D массив"
        assert (
            x_train.shape[0] == y_train.shape[0]
        ), "Массив y_train имеет несоответствующую длину"

        model = DecisionTree(min_samples_split=min_samples_split, max_depth=max_depth)
        model.fit(x_train, y_train)
        return model

    @staticmethod
    def predict(model: DecisionTree, x_test: np.ndarray) -> np.ndarray:
        """
         Прогнозирует метки для тестового набора данных.

        Parameters
        ----------
        model: DecisionTree
            Обученная модель.
        x_test: np.ndarray
            Массив значений размера (N, M). Где N - количество точек, M - количество атрибутов.

        Returns
        -------
        np.ndarray
            Массив меток размера N.
        """

        assert x_test.ndim == 2, "x_test: Ожидался 2D массив"

        prediction = model.predict(x_test)
        return prediction


class RandomForestClassifier:
    """Класс для классификации Random Forest."""

    @staticmethod
    def get_model(
        x_train: np.ndarray,
        y_train: np.ndarray,
        n_estimators: int = 100,
        max_depth: Optional[int] = None,
    ) -> RandomForest:
        """
        Возвращает модель обученную на тренировочных данных.

        Parameters
        ----------
        x_train: np.ndarray
            Массив значений размера (N, M). Где N - количество точек, M - количество атрибутов.
        y_train: np.ndarray
            Массив значений размера N.
        n_estimators: int = 100
            Количество деревьев в лесу.(параметр RandomForest).
        max_depth: int = None
            Максимальная глубина дерева(параметр RandomForest).
        Returns
        -------
        RandomForest
            Обученная модель.
        """

        assert x_train.ndim == 2, "x_train: Ожидался 2D массив"
        assert y_train.ndim == 1, "y_train: Ожидался 1D массив"
        assert (
            x_train.shape[0] == y_train.shape[0]
        ), "Массив y_train имеет несоответствующую длину"

        model = RandomForest(n_estimators=n_estimators, max_depth=max_depth)
        model.fit(x_train, y_train)
        return model

    @staticmethod
    def predict(model: RandomForest, x_test: np.ndarray) -> np.ndarray:
        """
         Прогнозирует метки для тестового набора данных.

        Parameters
        ----------
        model: RandomForest
            Обученная модель.
        x_test: np.ndarray
            Массив значений размера (N, M). Где N - количество точек, M - количество атрибутов.

        Returns
        -------
        np.ndarray
            Массив меток размера N.
        """

        assert x_test.ndim == 2, "x_test: Ожидался 2D массив"

        prediction = model.predict(x_test)
        return prediction
