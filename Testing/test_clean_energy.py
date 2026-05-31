import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch

from src.cleaning.cleanedEnergy import (
    load_energy_data,
    convert_index_to_datetime,
    reset_index_to_timestamp,
    resample_hourly,
    save_energy_data,
    remove_duplicates,
    rename_columns,
    convert_timezone_to_utc,
    finalize_energy,
    clean_energy_pipeline
)

def test_remove_duplicates():
    data = {
        "timestamp": ["2025-01-01 10:00:00", "2025-01-01 10:00:00", "2025-01-01 11:00:00"],
        "load": [100.0, 100.0, 150.0]
    }
    df_in = pd.DataFrame(data)

    df_out = remove_duplicates(df_in)

    assert len(df_out) == 2
    assert df_out["load"].iloc[1] == 150.0

def test_rename_columns():
    df_in = pd.DataFrame({"Actual Load": [250.5, 300.2]})
    
    df_out = rename_columns(df_in)

    assert "load" in df_out.columns
    assert "Actual Load" not in df_out.columns

def test_finalize_energy_missing_column():
    df_invalid = pd.DataFrame({"wrong_column": [100.0]})
    
    with pytest.raises(ValueError):
        finalize_energy(df_invalid)

@patch("src.cleaning.cleanedEnergy.pd.DataFrame.to_csv")
@patch("src.cleaning.cleanedEnergy.load_energy_data")
def test_clean_energy_pipeline_success(mock_load, mock_to_csv):

    mock_data = pd.DataFrame({
        "Actual Load": [100.555, 100.555, 200.111],
    }, index=["2025-01-01 10:00:00", "2025-01-01 10:00:00", "2025-01-01 11:00:00"])
    
    mock_load.return_value = mock_data
    
    input_path = Path("dummy_in.csv")
    output_path = Path("dummy_out.csv")

    df_final = clean_energy_pipeline(input_path, output_path)

    assert len(df_final) == 2  
    assert "load" in df_final.columns 
    assert "timestamp" in df_final.columns 
    assert df_final["load"].iloc[0] == 100.56  
   
    mock_to_csv.assert_called_once()


@patch("src.cleaning.cleanedEnergy.pd.read_csv")
def test_load_energy_data_empty(mock_read_csv):
    mock_read_csv.return_value = pd.DataFrame()
    with pytest.raises(ValueError, match="Energy dataset is empty"):
        load_energy_data(Path("dummy.csv"))

@patch("src.cleaning.cleanedEnergy.pd.read_csv")
def test_load_energy_data_exception(mock_read_csv):
    mock_read_csv.side_effect = Exception("Erro de leitura forçado")
    with pytest.raises(Exception, match="Erro de leitura forçado"):
        load_energy_data(Path("dummy.csv"))

def test_convert_index_to_datetime_exception():
    with pytest.raises(Exception):
        convert_index_to_datetime(None)

def test_rename_columns_missing_load():
    df = pd.DataFrame({"coluna_errada": [1, 2]})
    with pytest.raises(ValueError, match="Missing 'load' column after renaming"):
        rename_columns(df)

def test_reset_index_to_timestamp_missing():
    df = pd.DataFrame({"A": [1]})
    df.index.name = "meu_index_esquisito" 
    with pytest.raises(ValueError, match="Missing timestamp column"):
        reset_index_to_timestamp(df)

def test_resample_hourly_exception():
    df = pd.DataFrame({"wrong_col": [1]})
    with pytest.raises(Exception):
        resample_hourly(df)
def test_finalize_energy_rounding_exception():
    df = pd.DataFrame({"load": [{"erro": "forçado"}]})
    with pytest.raises(Exception):
        finalize_energy(df)

@patch("src.cleaning.cleanedEnergy.pd.DataFrame.to_csv")
def test_save_energy_data_exception(mock_to_csv):
    mock_to_csv.side_effect = Exception("Erro ao gravar")
    with pytest.raises(Exception, match="Erro ao gravar"):
        save_energy_data(pd.DataFrame(), Path("out.csv"))