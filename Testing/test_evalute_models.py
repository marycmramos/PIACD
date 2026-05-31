import pytest
import numpy as np
import pandas as pd
import json
from unittest.mock import patch, MagicMock, mock_open

from src.models.evaluate_models import (
    evaluate, 
    get_config_hashes, 
    load_config, 
    load_experiments, 
    save_experiments, 
    evaluate_models
)

def test_evaluate_metrics_perfect_prediction():
    y_true = np.array([1, 2, 3])
    y_pred = np.array([1, 2, 3])
    mae, rmse, r2 = evaluate("test", y_true, y_pred)
    assert mae == 0
    assert rmse == 0
    assert r2 == 1

def test_evaluate_metrics_non_perfect():
    y_true = np.array([1, 2, 3])
    y_pred = np.array([2, 2, 2])
    mae, rmse, r2 = evaluate("test", y_true, y_pred)
    assert mae > 0
    assert rmse > 0
    assert r2 < 1

def test_baseline_column_exists():
    df = pd.DataFrame({"lag_1h": [1, 2, 3]})
    assert "lag_1h" in df.columns

def test_baseline_missing_column():
    df = pd.DataFrame({"other_feature": [1, 2, 3]})
    with pytest.raises(KeyError):
        _ = df["lag_1h"]

def test_experiment_hashes_structure():
    config = {
        "split": {"test_size": 0.2},
        "linear_regression": {"fit_intercept": True},
        "random_forest": {"n_estimators": 100}
    }
    hashes = get_config_hashes(config)
    assert set(hashes.keys()) == {"split", "lr", "rf"}
    assert all(len(v) == 64 for v in hashes.values())

@patch("builtins.open", new_callable=mock_open, read_data='{"split": {}}')
def test_load_config_success(mock_file):
    config = load_config("dummy")
    assert "split" in config

@patch("builtins.open", side_effect=Exception("Read error"))
def test_load_config_exception(mock_file):
    with pytest.raises(Exception, match="Read error"):
        load_config("dummy")

@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data='[{"run_id": "123"}]')
def test_load_experiments_exists(mock_file, mock_exists):
    assert len(load_experiments()) == 1

@patch("os.path.exists", return_value=False)
def test_load_experiments_not_exists(mock_exists):
    assert load_experiments() == []

@patch("os.path.exists", side_effect=Exception("OS Error"))
def test_load_experiments_exception(mock_exists):
    assert load_experiments() == []

@patch("builtins.open", new_callable=mock_open)
def test_save_experiments_success(mock_file):
    save_experiments([{"run": 1}])
    mock_file.assert_called_once()

@patch("builtins.open", side_effect=Exception("Write Error"))
def test_save_experiments_exception(mock_file):
    save_experiments([{"run": 1}])
    mock_file.assert_called_once()  

@patch("src.models.evaluate_models.mean_absolute_error", side_effect=Exception("Eval Error"))
def test_evaluate_exception(mock_mae):
    with pytest.raises(Exception, match="Eval Error"):
        evaluate("test", [1], [1])

def mock_joblib_load(filepath):
    path_str = str(filepath)
    if "X_test" in path_str:
        return pd.DataFrame({"lag_1h": [10, 20], "feature": [1, 2]})
    elif "y_test" in path_str:
        return pd.Series([12, 22])
    elif "X_train" in path_str:
        return pd.DataFrame({"lag_1h": [10, 20, 30], "feature": [1, 2, 3]})
    elif "y_train" in path_str:
        return pd.Series([12, 22, 32])
    elif "ts_test" in path_str:
        return pd.Series(["2025-01-01", "2025-01-02"])
    elif "lr_model" in path_str or "rf_model" in path_str:
        mock_model = MagicMock()
        mock_model.predict.side_effect = lambda X: np.zeros(len(X))
        mock_model.feature_importances_ = [0.5, 0.5]
        return mock_model
    return None

@patch("src.models.evaluate_models.pd.DataFrame.to_json")
@patch("src.models.evaluate_models.save_experiments")
@patch("src.models.evaluate_models.load_experiments", return_value=[])
@patch("builtins.open", new_callable=mock_open)
@patch("src.models.evaluate_models.load_config", return_value={"split": {}})
@patch("src.models.evaluate_models.joblib.load", side_effect=mock_joblib_load)
@patch("src.models.evaluate_models.pd.read_csv", return_value=pd.DataFrame(
    np.zeros((200, 3)),
    columns=["lag_1h", "feature", "load"]
))
@patch("src.models.evaluate_models.os.makedirs")
def test_evaluate_models_success(mock_makedirs, mock_read_csv, mock_joblib, mock_config, mock_open, mock_load_exp, mock_save_exp, mock_to_json):
    evaluate_models()
    mock_save_exp.assert_called_once()

@patch("src.models.evaluate_models.pd.read_csv", return_value=pd.DataFrame())
@patch("src.models.evaluate_models.os.makedirs")
def test_evaluate_models_empty_dataset(mock_makedirs, mock_read_csv):
    with pytest.raises(ValueError, match="Dataset is empty"):
        evaluate_models()

@patch("src.models.evaluate_models.joblib.load", return_value=pd.DataFrame())
@patch("src.models.evaluate_models.pd.read_csv", return_value=pd.DataFrame(np.zeros((200, 3)), columns=["lag_1h", "feature", "load"]))
@patch("src.models.evaluate_models.os.makedirs")
def test_evaluate_models_empty_test_set(mock_makedirs, mock_read_csv, mock_joblib):
    with pytest.raises(ValueError, match="Test set is empty"):
        evaluate_models()

def mock_joblib_load_missing_lag(filepath):
    if "X_test" in str(filepath):
        return pd.DataFrame({"wrong_column": [10, 20]})
    return pd.Series([1, 2]) 

@patch("src.models.evaluate_models.joblib.load", side_effect=mock_joblib_load_missing_lag)
@patch("src.models.evaluate_models.pd.read_csv", return_value=pd.DataFrame(np.zeros((200, 3)), columns=["lag_1h", "feature", "load"]))
@patch("src.models.evaluate_models.os.makedirs")
def test_evaluate_models_missing_lag(mock_makedirs, mock_read_csv, mock_joblib):
    with pytest.raises(ValueError, match="Missing lag_1h feature for baseline"):
        evaluate_models()

@patch("src.models.evaluate_models.pd.read_csv", side_effect=Exception("Falha Catastrófica"))
@patch("src.models.evaluate_models.os.makedirs")
def test_evaluate_models_catastrophic_failure(mock_makedirs, mock_read_csv):
    with pytest.raises(Exception, match="Falha Catastrófica"):
        evaluate_models()