import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock, mock_open

from src.models.grid_search import (
    grid_search_already_done,
    load_best_params,
    run_grid_search
)

@patch("src.models.grid_search.os.path.exists", return_value=True)
def test_grid_search_already_done(mock_exists):
    assert grid_search_already_done() is True

@patch("builtins.open", new_callable=mock_open, read_data='{"best_model": "lr"}')
def test_load_best_params(mock_file):
    params = load_best_params()
    assert params["best_model"] == "lr"

@patch("src.models.grid_search.grid_search_already_done", return_value=True)
@patch("src.models.grid_search.load_best_params", return_value={"mock": "data"})
def test_run_grid_search_already_done(mock_load, mock_check):
    res = run_grid_search()
    assert res == {"mock": "data"}

def mock_read_csv(*args, **kwargs):
    return pd.DataFrame({
        "load": np.random.rand(200),
        "load_diff": np.random.rand(200),
        "feature_num": np.random.rand(200),
        "feature_str": ["string_para_ignorar"] * 200
    })

@patch("src.models.grid_search.GridSearchCV")
@patch("src.models.grid_search.joblib.dump")
@patch("builtins.open", new_callable=mock_open)
@patch("src.models.grid_search.os.makedirs")
@patch("src.models.grid_search.pd.read_csv", side_effect=mock_read_csv)
@patch("src.models.grid_search.grid_search_already_done", return_value=False)
def test_run_grid_search_full(mock_check, mock_read, mock_makedirs, mock_open_file, mock_joblib, mock_gscv):
    mock_gs_instance = MagicMock()
    mock_gs_instance.best_params_ = {"parametro_falso": 10}
    mock_gs_instance.best_estimator_.predict.return_value = np.zeros(7)
    
    mock_gscv.return_value = mock_gs_instance

    results = run_grid_search()

    assert "linear_regression" in results
    assert "random_forest" in results
    assert results["best_model"] in ["random_forest", "linear_regression"]
    assert mock_joblib.call_count == 2
    mock_open_file.assert_called()