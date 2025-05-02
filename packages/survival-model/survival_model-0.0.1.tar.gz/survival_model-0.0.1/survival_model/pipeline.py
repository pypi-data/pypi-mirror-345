import sys
from pathlib import Path
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))


from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from survival_model.config.core import config
from survival_model.processing.features import OutlierHandler

outlier_colms = ['creatinine_phosphokinase', 'ejection_fraction', 'platelets', 'serum_creatinine', 'serum_sodium']

xgb_classifier = Pipeline([
    ('outlier_handler', OutlierHandler(columns = outlier_colms)),
    ('regressor', XGBClassifier(
        n_estimators=config.model_config_.n_estimators,
        max_depth=config.model_config_.max_depth,
        max_leaves=config.model_config_.max_leaves,
        random_state=config.model_config_.random_state
    ))
])