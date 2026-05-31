import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch

from src.cleaning.mergeData import (
    convert_timestamps,
    merge_datasets,
    drop_unnecessary_columns,
    sort_dataset,
    merge_pipeline,
    load_datasets,
    validate_inputs,
    save_merged_dataset
)

from unittest.mock import MagicMock

from src.cleaning.cleanWeather import finalize_dataframe


def test_convert_timestamps():
    weather_in = pd.DataFrame({"timestamp": ["2025-01-01 10:00:00", "2025-01-01 11:00:00"]})
    energy_in = pd.DataFrame({"timestamp": ["2025-01-01 10:00:00"]})
    
    w_out, e_out = convert_timestamps(weather_in, energy_in)
    
    assert pd.api.types.is_datetime64_any_dtype(w_out["timestamp"])
    assert pd.api.types.is_datetime64_any_dtype(e_out["timestamp"])


def test_merge_datasets():
    weather_in = pd.DataFrame({
        "timestamp": pd.to_datetime(["2025-01-01 10:00:00", "2025-01-01 11:00:00", "2025-01-01 12:00:00"]),
        "temperature": [10.0, 11.0, 12.0]
    })
    energy_in = pd.DataFrame({
        "timestamp": pd.to_datetime(["2025-01-01 11:00:00", "2025-01-01 12:00:00", "2025-01-01 13:00:00"]),
        "load": [150.0, 160.0, 170.0]
    })
    
    df_merged = merge_datasets(weather_in, energy_in)
    
    assert len(df_merged) == 2
    assert "temperature" in df_merged.columns
    assert "load" in df_merged.columns


def test_drop_unnecessary_columns():
    df_in = pd.DataFrame({
        "timestamp": ["2025-01-01"],
        "latitude": [45.0],
        "longitude": [10.0],
        "temperature": [15.0]
    })
    
    df_out = drop_unnecessary_columns(df_in)
   
    assert "temperature" in df_out.columns
    assert "latitude" not in df_out.columns
    assert "longitude" not in df_out.columns


def test_sort_dataset():
    df_in = pd.DataFrame({
        "timestamp": pd.to_datetime(["2025-01-02", "2025-01-01"]),
        "val": [2, 1]
    })
    
    df_out = sort_dataset(df_in)
    
    assert df_out["val"].iloc[0] == 1 


def test_convert_timestamps_missing_column():
    weather_in = pd.DataFrame({"errado": ["2025-01-01 10:00:00"]})
    energy_in = pd.DataFrame({"timestamp": ["2025-01-01 10:00:00"]})
    
    with pytest.raises(KeyError):
        convert_timestamps(weather_in, energy_in)


def test_merge_pipeline_with_paths(tmp_path):
    weather_file = tmp_path / "weather.csv"
    energy_file = tmp_path / "energy.csv"
    output_file = tmp_path / "out" / "merged.csv"

    weather_df = pd.DataFrame({"timestamp": ["2020-01-01"], "latitude": [1]})
    energy_df = pd.DataFrame({"timestamp": ["2020-01-01"], "value": [10]})

    weather_df.to_csv(weather_file, index=False)
    energy_df.to_csv(energy_file, index=False)

    result = merge_pipeline(weather_file, energy_file, output_file)

    assert not result.empty
    assert output_file.exists()


def test_merge_no_overlap():
    weather = pd.DataFrame({"timestamp": ["2020-01-01"]})
    energy = pd.DataFrame({"timestamp": ["2020-01-02"]})

    weather, energy = convert_timestamps(weather, energy)
    with pytest.raises(ValueError):
        merge_datasets(weather, energy)


def test_drop_columns_not_present():
    df = pd.DataFrame({"timestamp": [1], "value": [10]})
    result = drop_unnecessary_columns(df)

    assert "value" in result.columns


def test_output_directory_created(tmp_path):
    output_file = tmp_path / "new_dir" / "file.csv"

    weather = pd.DataFrame({"timestamp": ["2020-01-01"]})
    energy = pd.DataFrame({"timestamp": ["2020-01-01"]})

    result = merge_pipeline(weather, energy, output_file)

    assert output_file.exists()


def test_invalid_timestamp():
    weather = pd.DataFrame({"timestamp": ["invalid"]})
    energy = pd.DataFrame({"timestamp": ["2020-01-01"]})

    with pytest.raises(Exception):
        convert_timestamps(weather, energy)


def test_finalize_dataframe():
    df = pd.DataFrame({"a": [1.12345], "b": ["x"]})
    result = finalize_dataframe(df)

    assert isinstance(result, pd.DataFrame)
    assert result["a"].iloc[0] == 1.123


@patch("src.cleaning.mergeData.pd.DataFrame.to_csv")
@patch("src.cleaning.mergeData.load_datasets")
def test_merge_pipeline_success(mock_load, mock_to_csv):
    weather_mock = pd.DataFrame({
        "timestamp": ["2025-01-01 10:00:00", "2025-01-01 11:00:00"],
        "temperature": [10.0, 12.0],
        "latitude": [45.0, 45.0]
    })
    energy_mock = pd.DataFrame({
        "timestamp": ["2025-01-01 11:00:00", "2025-01-01 12:00:00"],
        "load": [150.0, 160.0]
    })
    
    mock_load.return_value = (weather_mock, energy_mock)
    
    weather_path = Path("dummy_w.csv")
    energy_path = Path("dummy_e.csv")
    output_path = Path("dummy_out.csv")
    
    df_final = merge_pipeline(weather_path, energy_path, output_path)
    
    assert len(df_final) == 1
    assert "latitude" not in df_final.columns
    assert "temperature" in df_final.columns
    assert "load" in df_final.columns
    
    assert pd.api.types.is_datetime64_any_dtype(df_final["timestamp"])
    
    mock_to_csv.assert_called_once_with(output_path, index=False)


@patch("src.cleaning.mergeData.pd.read_csv")
def test_load_datasets_exception(mock_read_csv):
    mock_read_csv.side_effect = Exception("Erro forçado de leitura CSV")
    with pytest.raises(Exception, match="Erro forçado de leitura CSV"):
        load_datasets(Path("weather.csv"), Path("energy.csv"))

def test_validate_inputs_empty():
    df_valid = pd.DataFrame({"timestamp": ["2025-01-01"]})
    df_empty = pd.DataFrame()
    
    with pytest.raises(ValueError, match="weather dataset is empty"):
        validate_inputs(df_empty, df_valid)
        
    with pytest.raises(ValueError, match="energy dataset is empty"):
        validate_inputs(df_valid, df_empty)

def test_validate_inputs_missing_col():
    df_valid = pd.DataFrame({"timestamp": ["2025-01-01"]})
    df_invalid = pd.DataFrame({"outra_coluna": [1]})
    
    with pytest.raises(ValueError, match="Missing column 'timestamp' in weather dataset"):
        validate_inputs(df_invalid, df_valid)
        
    with pytest.raises(ValueError, match="Missing column 'timestamp' in energy dataset"):
        validate_inputs(df_valid, df_invalid)

@patch("src.cleaning.mergeData.pd.DataFrame.to_csv")
def test_save_merged_dataset_exception(mock_to_csv):
    mock_to_csv.side_effect = Exception("Erro forçado a gravar CSV")
    with pytest.raises(Exception, match="Erro forçado a gravar CSV"):
        save_merged_dataset(pd.DataFrame(), Path("out.csv"))

@patch("src.cleaning.mergeData.validate_inputs")
def test_merge_pipeline_catastrophic_failure(mock_validate):
    mock_validate.side_effect = Exception("Falha catastrófica no merge")
    
    with pytest.raises(Exception, match="Falha catastrófica no merge"):
        merge_pipeline(pd.DataFrame(), pd.DataFrame(), Path("out.csv"))