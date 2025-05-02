import sys
from pathlib import Path
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score

from survival_model.config.core import config
from survival_model.pipeline import xgb_classifier
from survival_model.processing.data_manager import load_dataset, save_pipeline

def run_training() -> None:
    
    
    """
    Train the model.
    """

    # read training data
    data = load_dataset(file_name = config.app_config_.training_data_file)
    
    print("Training data shape:", data.shape)
    
    # divide train and test
    X_train, X_test, y_train, y_test = train_test_split(
        
        data[config.model_config_.features],     # predictors
        data[config.model_config_.target],       # target
        test_size = config.model_config_.test_size,
        random_state=config.model_config_.random_state,   # set the random seed here for reproducibility
    )

    # Pipeline fitting
    xgb_classifier.fit(X_train, y_train)

    
    train_accuracy = accuracy_score(y_train, xgb_classifier.predict(X_train))
    test_accuracy = accuracy_score(y_test, xgb_classifier.predict(X_test))
    print("Training accuracy score:", round(train_accuracy, 2))
    print("Test accuracy score:", round(test_accuracy, 2))
    
    train_f1 = f1_score(y_train, xgb_classifier.predict(X_train), average='weighted')
    test_f1 = f1_score(y_test, xgb_classifier.predict(X_test), average='weighted')
    print("Training f1 score:", round(train_f1, 2))
    print("Test f1 score:", round(test_f1, 2))


    # persist trained model
    save_pipeline(pipeline_to_persist = xgb_classifier)
    
if __name__ == "__main__":
    run_training()

