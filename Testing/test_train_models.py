import pytest
import pandas as pd
import numpy as np
import json
from unittest.mock import patch, MagicMock, mock_open

from src.models.training_models import (
    load_config,
    get_config_hashes,
    load_results,
    get_existing_hashes,
    create_split,
    train_models
)

@patch("builtins.open", new_callable=mock_open, read_data='{"split": {"test_size": 0.2}}')
def test_load_config_success(mock_file):
    config = load_config("dummy.json")
    assert "split" in config

@patch("builtins.open", side_effect=Exception("Erro Simulado na Config"))
def test_load_config_exception(mock_file):
    with pytest.raises(Exception, match="Erro Simulado na Config"):
        load_config("dummy.json")

def test_get_config_hashes():
    config = {"split": {}, "linear_regression": {}, "random_forest": {}}
    hashes = get_config_hashes(config)
    assert len(hashes) == 3
    assert "lr" in hashes
    assert "rf" in hashes

@patch("src.models.training_models.os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data='[{"hashes": {"split": "hash123"}}]')
def test_load_results_success(mock_file, mock_exists):
    res = load_results()
    assert len(res) == 1

@patch("src.models.training_models.os.path.exists", return_value=False)
def test_load_results_not_exists(mock_exists):
    assert load_results() == []

@patch("src.models.training_models.os.path.exists", side_effect=Exception("Erro de Permissões"))
def test_load_results_exception(mock_exists):
    assert load_results() == []

@patch("src.models.training_models.load_results", return_value=[{"hashes": {"split": "abc"}}])
def test_get_existing_hashes(mock_load):
    hashes = get_existing_hashes()
    assert hashes["split"] == "abc"

@patch("src.models.training_models.load_results", return_value=[])
def test_get_existing_hashes_empty(mock_load):
    assert get_existing_hashes() == {}

def test_create_split_success():
    X = pd.DataFrame({"feat": range(10)})
    y = pd.Series(range(10))
    X_train, X_test, y_train, y_test = create_split(X, y, 0.8)
    assert len(X_train) == 8
    assert len(X_test) == 2

def test_create_split_empty():
    with pytest.raises(ValueError, match="Input dataset is empty before split"):
        create_split(pd.DataFrame(), pd.Series())

# Testes da Pipeline Principal

def mock_features_df():
    return pd.DataFrame({
        "timestamp": pd.date_range("2025-01-01", periods=200),
        "load": np.random.rand(200),
        "feature1": np.random.rand(200),
        "load_diff": np.random.rand(200)
    })

@patch("src.models.training_models.sys.exit", side_effect=SystemExit)
@patch("src.models.training_models.get_existing_hashes")
@patch("src.models.training_models.get_config_hashes")
@patch("src.models.training_models.load_config", return_value={})
def test_train_models_no_change(mock_config, mock_hashes, mock_existing, mock_exit):
    mock_hashes.return_value = {"split": "1", "lr": "2", "rf": "3"}
    mock_existing.return_value = {"split": "1", "lr": "2", "rf": "3"}
    with pytest.raises(SystemExit):
        train_models()
        
    mock_exit.assert_called_once()

@patch("src.models.training_models.joblib.dump")
@patch("src.models.training_models.os.makedirs")
@patch("src.models.training_models.pd.read_csv", return_value=mock_features_df())
@patch("src.models.training_models.get_existing_hashes")
@patch("src.models.training_models.get_config_hashes")
@patch("src.models.training_models.load_config", return_value={})
def test_train_models_split_changed(mock_config, mock_hashes, mock_existing, mock_read_csv, mock_makedirs, mock_dump):
    mock_hashes.return_value = {"split": "new", "lr": "new", "rf": "new"}
    mock_existing.return_value = {"split": "old", "lr": "old", "rf": "old"}
    
    train_models()
    assert mock_dump.call_count == 8

@patch("src.models.training_models.joblib.load")
@patch("src.models.training_models.joblib.dump")
@patch("src.models.training_models.os.makedirs")
@patch("src.models.training_models.pd.read_csv", return_value=mock_features_df())
@patch("src.models.training_models.get_existing_hashes")
@patch("src.models.training_models.get_config_hashes")
@patch("src.models.training_models.load_config", return_value={})
def test_train_models_lr_only(mock_config, mock_hashes, mock_existing, mock_read_csv, mock_makedirs, mock_dump, mock_load):
    mock_hashes.return_value = {"split": "same", "lr": "new", "rf": "same"}
    mock_existing.return_value = {"split": "same", "lr": "old", "rf": "same"}
    
    mock_load.side_effect = [
        pd.DataFrame({"feat": [1, 2, 3]}),
        pd.DataFrame({"feat": [4, 5]}),
        pd.Series([10, 20, 30]),
        pd.Series([40, 50])
    ]
    
    train_models()
    
    assert mock_dump.call_count == 1
    args, _ = mock_dump.call_args
    assert "lr_model.pkl" in args[1]

@patch("src.models.training_models.os.makedirs")
@patch("src.models.training_models.pd.read_csv", return_value=pd.DataFrame())
@patch("src.models.training_models.get_existing_hashes")
@patch("src.models.training_models.get_config_hashes")
@patch("src.models.training_models.load_config", return_value={})
def test_train_models_empty_dataset(mock_config, mock_hashes, mock_existing, mock_read, mock_makedirs):

    mock_hashes.return_value = {"split": "new", "lr": "new", "rf": "new"}
    mock_existing.return_value = {}
    
    with pytest.raises(ValueError, match="Loaded dataset is empty"):
        train_models()