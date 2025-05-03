from typing import Tuple

import numpy as np
from sklearn.inspection import permutation_importance
from sklearn.metrics import precision_recall_fscore_support
from sklearn.model_selection import KFold, cross_val_score

RANDOM_STATE = 42


def calculate_metrics(
    y_true: np.ndarray, y_pred: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    precision, recall, fbeta_score, support = precision_recall_fscore_support(
        y_true, y_pred
    )
    return precision, recall, fbeta_score, support


def k_fold(
    y_train: np.ndarray, x_train: np.ndarray, model: object, n_epochs: int = 10
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    kf = KFold(n_splits=min(len(y_train), n_epochs))
    if x_train.ndim == 1:
        x_train = x_train.reshape(-1, 1)
    precision = cross_val_score(
        model, x_train, y_train.reshape(-1, 1), cv=kf, scoring="precision_weighted"
    )
    recall = cross_val_score(
        model, x_train, y_train.reshape(-1, 1), cv=kf, scoring="recall_weighted"
    )
    accuracy = cross_val_score(
        model, x_train, y_train.reshape(-1, 1), cv=kf, scoring="accuracy"
    )
    f1 = cross_val_score(
        model, x_train, y_train.reshape(-1, 1), cv=kf, scoring="f1_weighted"
    )
    return precision, recall, accuracy, f1


def feature_importanse(
    model: object, x_test: np.ndarray, y_test: np.ndarray
) -> np.ndarray:
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    else:
        results = permutation_importance(
            model, x_test, y_test, n_repeats=30, random_state=RANDOM_STATE
        )
        importances = results.importances_mean
    return importances
