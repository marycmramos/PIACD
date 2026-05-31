import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.cleaning.organizeWeather import (
    get_nc_files,
    group_files_by_variable,
    load_and_concat_datasets,
    cleanup_nc_files,
    organize_weather_data,
    group_files_by_variable,
    load_and_concat_datasets,
    save_variable_dataframe,
    cleanup_nc_files,
    organize_weather_data
)


def test_group_files_by_variable():
    paths = [
        Path("data_stepType-acc.nc"),
        Path("data_stepType-avg.nc"),
        Path("data_stepType-inst.nc"),
        Path("data_stepType-max.nc"),
        Path("data_stepType-lixo.nc"),
        Path("data_stepType-acc_parte2.nc")
    ]
    
    groups = group_files_by_variable(paths)
    
    assert "acc" in groups
    assert "avg" in groups
    assert "lixo" not in groups
    assert len(groups["acc"]) == 2
    assert len(groups["inst"]) == 1


def test_cleanup_nc_files(tmp_path):
    f1 = tmp_path / "test_stepType-acc.nc"
    f1.touch()
    f2 = tmp_path / "test_stepType-avg.nc"
    f2.touch()
    f_keep = tmp_path / "manter_este_ficheiro.txt"
    f_keep.touch()
    
    cleanup_nc_files(tmp_path)
    
    assert not f1.exists()
    assert not f2.exists()
    assert f_keep.exists()


@patch("src.cleaning.organizeWeather.xr.open_dataset")
def test_load_and_concat_datasets(mock_xr_open):
    mock_ds = MagicMock()
    
    mock_df = pd.DataFrame({
        "valid_time": [
            "2025-01-01 10:00:00",
            "2025-01-01 11:00:00"
        ],
        "temperature": [10.0, 12.0]
    })

    mock_ds.to_dataframe.return_value = mock_df
    mock_xr_open.return_value.__enter__.return_value = mock_ds
    
    files = [Path("file1.nc"), Path("file2.nc")]
    
    result_df = load_and_concat_datasets(files)
    
    assert "temperature" in result_df.columns
    assert "valid_time" in result_df.columns
    assert not result_df.empty
    assert mock_xr_open.call_count == 2


@patch("src.cleaning.organizeWeather.cleanup_nc_files")
@patch("src.cleaning.organizeWeather.save_variable_dataframe")
@patch("src.cleaning.organizeWeather.load_and_concat_datasets")
def test_organize_weather_data_success(mock_load, mock_save, mock_cleanup, tmp_path):
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()
    
    (raw_dir / "test_stepType-acc.nc").touch()
    
    mock_load.return_value = pd.DataFrame({"dummy": [1, 2]})
    
    organize_weather_data(raw_dir, processed_dir)
    
    assert processed_dir.exists()
    mock_load.assert_called_once()
    mock_save.assert_called_once()
    mock_cleanup.assert_called_once_with(raw_dir)


def test_cleanup_nc_files_failure_handling(tmp_path):
    
    f1 = tmp_path / "locked_stepType-acc.nc"
    f1.touch()
    
    with patch("pathlib.Path.unlink", side_effect=PermissionError("Acesso negado")):
        try:
            cleanup_nc_files(tmp_path)
        except PermissionError:
            pytest.fail("A função cleanup_nc_files não está a silenciar o erro como deveria no bloco except!")

def test_generic_exceptions_organize_weather():
    bad_input = None

    with pytest.raises(Exception):
        group_files_by_variable(bad_input)

    with pytest.raises(Exception):
        load_and_concat_datasets(bad_input)

    with pytest.raises(Exception):
        save_variable_dataframe(bad_input, Path("out.csv"))

def test_load_and_concat_empty_list():
    with pytest.raises(ValueError, match="No valid NetCDF data found"):
        load_and_concat_datasets([])

@patch("src.cleaning.organizeWeather.xr.open_dataset")
def test_load_and_concat_inner_exceptions(mock_xr_open):
    mock_file = MagicMock(spec=Path)
    mock_file.name = "dummy.nc"

    mock_ds = MagicMock()
    mock_xr_open.return_value.__enter__.return_value = mock_ds
    mock_ds.to_dataframe.return_value = "Not a DataFrame string"
    with pytest.raises(ValueError, match="No valid NetCDF data found"):
        load_and_concat_datasets([mock_file])

    mock_ds.to_dataframe.return_value = pd.DataFrame({"wrong_col": [1]})
    with pytest.raises(ValueError, match="No valid NetCDF data found"):
        load_and_concat_datasets([mock_file])

    mock_xr_open.side_effect = Exception("Erro forçado no xarray")
    with pytest.raises(ValueError, match="No valid NetCDF data found"):
        load_and_concat_datasets([mock_file])

def test_cleanup_nc_files_exception():
    mock_path = MagicMock(spec=Path)
    mock_file = MagicMock()
    mock_file.name = "dummy.nc"
    mock_file.unlink.side_effect = Exception("Acesso Negado")
    
    mock_path.glob.return_value = [mock_file]
    cleanup_nc_files(mock_path)
    mock_file.unlink.assert_called_once()
@patch("src.cleaning.organizeWeather.get_nc_files")
def test_organize_weather_data_exceptions(mock_get_nc):
    mock_get_nc.return_value = []
    organize_weather_data(Path("raw"), Path("proc"))
    mock_get_nc.side_effect = Exception("Pipeline colapsou")
    
    with pytest.raises(Exception, match="Pipeline colapsou"):
        organize_weather_data(Path("raw"), Path("proc"))