from typing import List

from river.base import Classifier, Regressor
from river.metrics import MAE
from river.model_selection.base import ModelSelectionRegressor
from river.tree import HoeffdingTreeClassifier

from kappaml_core.meta.base import MetaEstimator


class MetaRegressor(MetaEstimator, ModelSelectionRegressor):
    """Meta-regressor for model selection using meta-learning.

    This implements a meta-regressor that uses a list of base regressor models
    and a meta learner. The meta learner uses meta features from stream characteristics
    to select the best base regressor at a given point in time.

    Parameters
    ----------
    models: list of Regressor
        A list of base regressor models.
    meta_learner: Classifier
        default=HoeffdingTreeClassifier
        Meta learner used to predict the best base estimator.
    metric: Metric
        default=MAE
        Metric used to evaluate the performance of the base regressors.
    mfe_groups: list (default=['general'])
        Groups of meta-features to use from PyMFE
    window_size: int (default=200)
        The size of the window used for extracting meta-features.
    meta_update_frequency: int (default=50)
        How frequently to extract meta-features and update the meta-learner.
        Higher values mean less frequent updates but more stable meta-model.
    """

    def __init__(
        self,
        models: List[Regressor],
        meta_learner: Classifier = HoeffdingTreeClassifier(),
        metric=MAE(),
        mfe_groups: list = ["general"],
        window_size: int = 200,
        meta_update_frequency: int = 50,
    ):
        super().__init__(
            models, meta_learner, metric, mfe_groups, window_size, meta_update_frequency
        )
