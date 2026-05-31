import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from unittest.mock import patch

from src.cleaning.cleanWeather import (
    convert_units,
    compute_wind_speed,
    aggregate_spatial,
    clean_weather_pipeline,
    load_weather_data,
    convert_time_column,
    rename_columns,
    drop_unused_columns,
    sort_and_validate,
    finalize_dataframe,
    save_clean_data
)

def test_convert_units():

    data = {
        "t2m": [273.15, 300.15],  
        "mx2t": [283.15, 293.15], 
        "mn2t": [263.15, 273.15],
        "tp": [0.001, 0.005],    
        "cp": [0.002, 0.000]      
    }
    df_in = pd.DataFrame(data)

    df_out = convert_units(df_in)


    assert df_out["t2m"].iloc[0] == 0.0
    assert df_out["t2m"].iloc[1] == 27.0
    assert df_out["tp"].iloc[0] == 1.0
    assert df_out["cp"].iloc[0] == 2.0

def test_compute_wind_speed():

    df_in = pd.DataFrame({"u10": [3.0, 0.0], "v10": [4.0, 10.0]})

    df_out = compute_wind_speed(df_in)

    assert "wind_speed" in df_out.columns
    assert df_out["wind_speed"].iloc[0] == 5.0
    assert df_out["wind_speed"].iloc[1] == 10.0

def test_aggregate_spatial():
  
    data = {
        "valid_time": ["2025-01-01 12:00:00", "2025-01-01 12:00:00"],
        "t2m": [10.0, 20.0]
    }
    df_in = pd.DataFrame(data)

    df_out = aggregate_spatial(df_in)
    assert len(df_out) == 1
    assert df_out["t2m"].iloc[0] == 15.0


def test_compute_wind_speed_missing_columns():

    df_invalid = pd.DataFrame({"u10": [3.0]})

    with pytest.raises(ValueError):
        compute_wind_speed(df_invalid)


@patch("src.cleaning.cleanWeather.pd.DataFrame.to_csv")
@patch("src.cleaning.cleanWeather.load_weather_data")
def test_clean_weather_pipeline_success(mock_load, mock_to_csv):

    mock_data = pd.DataFrame({
        "valid_time": ["2025-01-01 10:00:00Z", "2025-01-01 10:00:00Z"],
        "t2m": [283.15, 293.15],  
        "mx2t": [283.15, 293.15],
        "mn2t": [283.15, 293.15],
        "tp": [0.001, 0.003],     
        "cp": [0.000, 0.000],
        "ssrd": [500.0, 600.0],
        "u10": [3.0, 3.0],
        "v10": [4.0, 4.0]    
    })

    mock_load.return_value = mock_data
    input_path = Path("dummy_weather_in.csv")
    output_path = Path("dummy_weather_out.csv")

    df_final = clean_weather_pipeline(input_path, output_path)

    assert len(df_final) == 2

    assert "timestamp" in df_final.columns
    assert "temperature" in df_final.columns
    assert "u10" not in df_final.columns

    assert df_final["temperature"].iloc[0] == 10.0
    assert df_final["temperature"].iloc[1] == 20.0

    assert df_final["total_precipitation"].iloc[0] == 1.0
    assert df_final["total_precipitation"].iloc[1] == 3.0

    assert df_final["wind_speed"].iloc[0] == 5.0

    mock_to_csv.assert_called_once_with(output_path, index=False)


@patch("src.cleaning.cleanWeather.pd.read_csv")
def test_load_weather_data_empty(mock_read_csv):
    mock_read_csv.return_value = pd.DataFrame()
    with pytest.raises(ValueError, match="Weather dataset is empty"):
        load_weather_data(Path("dummy.csv"))

def test_convert_time_column_branches():
    df_ts = pd.DataFrame({"timestamp": ["2025-01-01"]})
    res1 = convert_time_column(df_ts)
    assert pd.api.types.is_datetime64_any_dtype(res1["timestamp"])

    df_vt = pd.DataFrame({"valid_time": ["2025-01-01"]})
    res2 = convert_time_column(df_vt)
    assert pd.api.types.is_datetime64_any_dtype(res2["valid_time"])

    df_err = pd.DataFrame({"wrong_col": [1]})
    with pytest.raises(ValueError, match="No valid time column found"):
        convert_time_column(df_err)

def test_rename_columns_missing_timestamp():
    df = pd.DataFrame({"random_col": [1]})
    with pytest.raises(KeyError):
            rename_columns(df)

def test_sort_and_validate_error():
    df = pd.DataFrame({"wrong": [1]})
    with pytest.raises(ValueError, match="Missing timestamp column"):
        sort_and_validate(df)

@patch("src.cleaning.cleanWeather.pd.DataFrame.to_csv")
def test_save_clean_data(mock_to_csv):
    df = pd.DataFrame({"col": [1]})
    save_clean_data(df, Path("out.csv"))
    mock_to_csv.assert_called_once()

def test_generic_exceptions_for_coverage():
    bad_input = None  

    with pytest.raises(Exception):
        convert_time_column(bad_input)

    with pytest.raises(Exception):
        convert_units(bad_input)

    with pytest.raises(Exception):
        rename_columns(bad_input)

    with pytest.raises(Exception):
        drop_unused_columns(bad_input)

    with pytest.raises(Exception):
        sort_and_validate(bad_input)

    with pytest.raises(Exception):
        finalize_dataframe(bad_input)

@patch("src.cleaning.cleanWeather.load_weather_data")
def test_pipeline_catastrophic_failure(mock_load):
    mock_load.side_effect = Exception("Pipeline estoirou")
    with pytest.raises(Exception, match="Pipeline estoirou"):
        clean_weather_pipeline(Path("in.csv"), Path("out.csv"))