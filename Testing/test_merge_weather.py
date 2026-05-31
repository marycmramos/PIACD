import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch

from src.cleaning.mergeWeather import (
    drop_irrelevant_columns,
    remove_duplicate_columns,
    merge_weather_dataframes,
    merge_weather_pipeline
)


def test_drop_irrelevant_columns():
    dfs_in = {
        "acc": pd.DataFrame({"number": [1], "expver": [1], "tp": [0.5]}),
        "avg": pd.DataFrame({"number": [1], "expver": [5], "t2m": [290.0]})
    }
    
    dfs_out = drop_irrelevant_columns(dfs_in)
    
    assert "number" not in dfs_out["acc"].columns
    assert "expver" not in dfs_out["acc"].columns
    assert "tp" in dfs_out["acc"].columns
    
    assert "number" not in dfs_out["avg"].columns
    assert "t2m" in dfs_out["avg"].columns


def test_remove_duplicate_columns():
    dfs_in = {
        "acc": pd.DataFrame({"valid_time": ["T1"], "latitude": [40], "longitude": [-8], "tp": [1]}),
        "avg": pd.DataFrame({"valid_time": ["T1"], "latitude": [40], "longitude": [-8], "t2m": [15]}),
        "inst": pd.DataFrame({"valid_time": ["T1"], "latitude": [40], "longitude": [-8], "u10": [5]}),
        "max": pd.DataFrame({"valid_time": ["T1"], "latitude": [40], "longitude": [-8], "mx2t": [20]}),
    }
    
    dfs_out = remove_duplicate_columns(dfs_in)
    
    assert "valid_time" in dfs_out["acc"].columns
    assert "latitude" in dfs_out["acc"].columns
    
    for key in ["avg", "inst", "max"]:
        assert "valid_time" in dfs_out[key].columns
        assert "latitude" not in dfs_out[key].columns
        assert "longitude" not in dfs_out[key].columns


def test_merge_weather_dataframes():
    dfs_in= {"acc": pd.DataFrame({"valid_time": ["T1", "T2"],"tp": [1, 2]}),
              "avg": pd.DataFrame({"valid_time": ["T1", "T2"],"t2m": [15, 16]}),
              "inst": pd.DataFrame({"valid_time": ["T1", "T2"],"u10": [5, 6]}),
              "max": pd.DataFrame({"valid_time": ["T1", "T2"],"mx2t": [20, 21]}),
            }
    
    df_merged = merge_weather_dataframes(dfs_in)
    
    assert len(df_merged) == 2
    assert len(df_merged.columns) == 5
    assert "valid_time" in df_merged.columns
    assert "tp" in df_merged.columns
    assert "t2m" in df_merged.columns
    assert df_merged["t2m"].iloc[1] == 16


def test_drop_irrelevant_columns_missing():
    dfs_in = {
        "acc": pd.DataFrame({"tp": [0.5]}) 
    }

    try:
        dfs_out = drop_irrelevant_columns(dfs_in)
        assert "tp" in dfs_out["acc"].columns
    except KeyError:
        pytest.fail("A função não deveria estourar se as colunas já não existirem no dataset!")


@patch("src.cleaning.mergeWeather.pd.read_csv")
@patch("src.cleaning.mergeWeather.pd.DataFrame.to_csv")
def test_merge_weather_pipeline_success(mock_to_csv, mock_read_csv):
    mock_read_csv.side_effect = [
        pd.DataFrame({"valid_time": ["T1"], "latitude": [40], "number": [1], "tp": [0.5]}), 
        pd.DataFrame({"valid_time": ["T1"], "latitude": [40], "expver": [1], "t2m": [15.0]}), 
        pd.DataFrame({"valid_time": ["T1"], "latitude": [40], "u10": [3.0]}), 
        pd.DataFrame({"valid_time": ["T1"], "latitude": [40], "mx2t": [20.0]}) 
    ]
    
    fake_path = Path("fake_dir")
    
    df_final = merge_weather_pipeline(fake_path)

    assert "valid_time" in df_final.columns
    assert "number" not in df_final.columns 
    assert "expver" not in df_final.columns
    
    assert list(df_final.columns).count("latitude") == 1
    
    assert all(col in df_final.columns for col in ["tp", "t2m", "u10", "mx2t"])
    
    mock_to_csv.assert_called_once()
    assert mock_to_csv.call_args[0][0] == fake_path / "weather_2025_full.csv"
