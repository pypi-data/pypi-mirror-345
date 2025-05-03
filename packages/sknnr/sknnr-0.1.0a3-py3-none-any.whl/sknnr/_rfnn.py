from __future__ import annotations

from typing import Callable, Literal

from numpy.random import RandomState
from sklearn.base import TransformerMixin

from ._base import TransformedKNeighborsRegressor, YFitMixin
from .transformers import RFNodeTransformer


class RFNNRegressor(YFitMixin, TransformedKNeighborsRegressor):
    """
    Regression using Random Forest Nearest Neighbors (RFNN) imputation.

    The target is predicted by similarity of its node indexes to training set
    node indexes when run through multiple univariate random forests.  A
    random forest is fit to each feature in the training set and node indexes are
    captured for each tree in each forest for each training sample.  Node
    indexes are then captured for targets and distance is calculated as the
    dissimilarity between node indexes.

    See `sklearn.neighbors.KNeighborsRegressor` for more detail on
    parameters associated with nearest neighbors and
    `sklearn.ensemble.RandomForestRegressor` for more detail on parameters
    associated with random forests.

    Parameters
    ----------
    n_estimators : int, default=50
        The number of trees in _each_ random forest.  Typically, this parameter
        is applied to a single random forest.  However, in `RFNNRegressor`,
        this parameter is applied to each random forest for every feature in
        the training set.
    criterion : {"squared_error", "absolute_error", "friedman_mse", "poisson"},
        default="squared_error"
        The function to measure the quality of a split.
    max_depth : int, default=None
        The maximum depth of the tree.
    min_samples_split : int or float, default=2
        The minimum number of samples required to split an internal node.
    min_samples_leaf : int of float, default=5
        The minimum number of samples required to be at a leaf node.
    min_weight_fraction_leaf : float, default=0.0
        The minimum weighted fraction of the sum total of weights (of all the
        input samples) required to be at a leaf node.
    max_features : {“sqrt”, “log2”, None}, int or float, default=1.0
        The number of features to consider when looking for the best split.
    max_leaf_nodes : int, default=None
        Grow trees with max_leaf_nodes in best-first fashion.
    min_impurity_decrease : float, default=0.0
        A node will be split if this split induces a decrease of the impurity
        greater than or equal to this value.
    bootstrap : bool, default=True
        Whether bootstrap samples are used when building trees.
    oob_score : bool or callable, default=False
        Whether to use out-of-bag samples to estimate the generalization score.
    n_jobs : int, default=None
        The number of jobs to run in parallel.
    random_state : int, RandomState instance or None, default=None
        Controls both the randomness of the bootstrapping of the samples
        used when building trees (if `bootstrap=True`) and the sampling of the
        features to consider when looking for the best split at each node
        (if `max_features < n_features`).
    verbose : int, default=0
        Controls the verbosity when fitting and predicting.
    warm_start : bool, default=False
        When set to `True`, reuse the solution of the previous call to fit and
        add more estimators to the ensemble, otherwise, just fit a whole
        new forest.
    ccp_alpha : non-negative float, default=0.0
        Complexity parameter used for Minimal Cost-Complexity Pruning.
    max_samples : int or float, default=None
        If bootstrap is `True`, the number of samples to draw from X to
        train each base estimator.
    monotonic_cst : array-like of int of shape (n_features), default=None
        Indicates the monotonicity constraint to enforce on each feature.
    n_neighbors : int, default=5
        Number of neighbors to use by default for `kneighbors` queries.
    weights : {"uniform", "distance"}, callable or None, default="uniform"
        Weight function used in prediction.
    algorithm : {"auto", "ball_tree", "kd_tree", "brute"}, default="auto"
        Algorithm used to compute the nearest neighbors.
    leaf_size : int, default=30
        Leaf size passed to `BallTree` or `KDTree`.

    Attributes
    ----------
    effective_metric_ : str
        Always set to 'hamming'.
    effective_metric_params_ : dict
        Always empty.
    independent_prediction_ : np.array
        When `fit`, provides the prediction for training data not allowing
        self-assignment during neighbor search.
    independent_score_ : double
        When `fit`, the mean coefficient of determination of the independent
        prediction across all features.
    n_features_in_ : int
        Number of features that the transformer outputs.  This is equal to the
        number of features in `y` (or `y_fit`) * `n_estimators_per_forest`.
    n_samples_fit_ : int
        Number of samples in the fitted data.
    transformer_ : RFNodeTransformer
        The fitted transformer which holds the built random forests for each
        feature.
    y_fit_ : np.array or pd.DataFrame
        When `y_fit` is passed to `fit`, the data used to construct the
        individual random forests.  Note that all `y` data is used for
        prediction.

    Notes
    -----
    `n_jobs` is used as a parameter in both `RandomForestRegressor` and
    `KNeighborsRegressor`.  The value specified for this parameter will be
    passed to both estimators.

    References
    ----------
    Crookston, NL, Finley, AO. 2008. yaImpute: an R package for kNN imputation.
    Journal of Statistical Software, 23, pp.1-16.
    """

    transformer_: TransformerMixin

    def __init__(
        self,
        *,
        n_estimators: int = 50,
        criterion: Literal[
            "squared_error", "absolute_error", "friedman_mse", "poisson"
        ] = "squared_error",
        max_depth: int | None = None,
        min_samples_split: int | float = 2,
        min_samples_leaf: int | float = 5,
        min_weight_fraction_leaf: float = 0.0,
        max_features: Literal["sqrt", "log2"] | int | float | None = 1.0,
        max_leaf_nodes: int | None = None,
        min_impurity_decrease: float = 0.0,
        bootstrap: bool = True,
        oob_score: bool | Callable = False,
        n_jobs: int | None = None,
        random_state: int | RandomState | None = None,
        verbose: int = 0,
        warm_start: bool = False,
        ccp_alpha: float = 0.0,
        max_samples: int | float | None = None,
        monotonic_cst: list[int] | None = None,
        n_neighbors: int = 5,
        weights: Literal["uniform", "distance"] | Callable = "uniform",
        algorithm: Literal["auto", "ball_tree", "kd_tree", "brute"] = "auto",
        leaf_size: int = 30,
    ):
        self.n_estimators = n_estimators
        self.criterion = criterion
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.min_weight_fraction_leaf = min_weight_fraction_leaf
        self.max_features = max_features
        self.max_leaf_nodes = max_leaf_nodes
        self.min_impurity_decrease = min_impurity_decrease
        self.bootstrap = bootstrap
        self.oob_score = oob_score
        self.n_jobs = n_jobs
        self.random_state = random_state
        self.verbose = verbose
        self.warm_start = warm_start
        self.ccp_alpha = ccp_alpha
        self.max_samples = max_samples
        self.monotonic_cst = monotonic_cst

        super().__init__(
            n_neighbors=n_neighbors,
            weights=weights,
            algorithm=algorithm,
            leaf_size=leaf_size,
            metric="hamming",
            n_jobs=self.n_jobs,
        )

    def _get_transformer(self) -> TransformerMixin:
        return RFNodeTransformer(
            n_estimators=self.n_estimators,
            criterion=self.criterion,
            max_depth=self.max_depth,
            min_samples_split=self.min_samples_split,
            min_samples_leaf=self.min_samples_leaf,
            min_weight_fraction_leaf=self.min_weight_fraction_leaf,
            max_features=self.max_features,
            max_leaf_nodes=self.max_leaf_nodes,
            min_impurity_decrease=self.min_impurity_decrease,
            bootstrap=self.bootstrap,
            oob_score=self.oob_score,
            n_jobs=self.n_jobs,
            random_state=self.random_state,
            verbose=self.verbose,
            warm_start=self.warm_start,
            ccp_alpha=self.ccp_alpha,
            max_samples=self.max_samples,
            monotonic_cst=self.monotonic_cst,
        )
