from typing import Union

import numpy as np
from numpy.typing import NDArray
from sklearn.preprocessing import StandardScaler
from sklearn.utils.validation import FLOAT_DTYPES, check_is_fitted

from .._base import _validate_data
from ._cca import CCA
from ._ccora import CCorA

Ordination = Union[CCA, CCorA]


class StandardScalerWithDOF(StandardScaler):
    def __init__(self, ddof=0):
        super().__init__()
        self.ddof = ddof

    def fit(self, X, y=None):
        scaler = super().fit(X, y)

        X = _validate_data(
            self,
            X=X,
            accept_sparse=False,
            dtype=FLOAT_DTYPES,
            ensure_all_finite="allow-nan",
            reset=False,
            ensure_min_samples=self.ddof + 1,
        )
        scaler.scale_ = np.std(X, axis=0, ddof=self.ddof)
        return scaler


class ComponentReducerMixin:
    """
    Mixin for transformers that allow reduction of the number of components.
    """

    ordination_: Ordination

    def __init__(self, n_components=None):
        self.n_components = n_components

    def get_feature_names_out(self) -> NDArray:
        check_is_fitted(self, "n_components_")
        return np.asarray(
            [
                f"{self.ordination_.__class__.__name__.lower()}{i}"
                for i in range(self.n_components_)
            ],
            dtype=object,
        )

    def set_n_components(self):
        n_components = (
            self.n_components
            if self.n_components is not None
            else self.ordination_.max_components
        )
        if not 0 <= n_components <= self.ordination_.max_components:
            raise ValueError(
                f"n_components={n_components} must be between 0 and "
                f"{self.ordination_.max_components}"
            )
        self.n_components_ = n_components
