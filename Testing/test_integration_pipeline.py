import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.pipeline.full_pipeline import (
    full_pipeline,
    run_ingestion_only,
    run_processing_only,
    run_modeling_only
)

@patch("src.pipeline.full_pipeline.evaluate_models")
@patch("src.pipeline.full_pipeline.train_models")
@patch("src.pipeline.full_pipeline.run_grid_search")
@patch("src.pipeline.full_pipeline.create_dataset_features")
@patch("src.pipeline.full_pipeline.merge_pipeline")
@patch("src.pipeline.full_pipeline.clean_weather_pipeline")
@patch("src.pipeline.full_pipeline.merge_weather_pipeline")
@patch("src.pipeline.full_pipeline.organize_weather_data")
@patch("src.pipeline.full_pipeline.extract_weather_files")
@patch("src.pipeline.full_pipeline.clean_energy_pipeline")
@patch("src.pipeline.full_pipeline.ingest_entsoe_data")
def test_full_pipeline_run_all(
    mock_ingest, mock_clean_energy, mock_extract, mock_organize, mock_merge_weather, 
    mock_clean_weather, mock_merge, mock_features, mock_grid, mock_train, mock_evaluate, tmp_path
):
    energy_file = tmp_path / "energy.csv"
    energy_file.touch()
    
    raw_weather = tmp_path / "weather"
    output_file = tmp_path / "output" / "dataset_merged.csv"
    
    full_pipeline(
        energy_file, raw_weather, output_file,
        run_ingestion=True, run_modeling=True, run_gridsearch=True
    )
    
    mock_ingest.assert_called_once()
    mock_clean_energy.assert_called_once()
    mock_extract.assert_called_once()
    mock_grid.assert_called_once()
    mock_evaluate.assert_called_once()
    
@patch("pandas.read_csv", return_value=pd.DataFrame())
@patch("src.pipeline.full_pipeline.clean_energy_pipeline")
def test_full_pipeline_skip_all(mock_clean_energy, mock_read_csv, tmp_path):
    energy_file = tmp_path / "energy.csv"
    energy_file.touch()
    raw_weather = tmp_path / "weather"
    
    out_dir = tmp_path / "output"
    out_dir.mkdir()
    output_file = out_dir / "dataset_merged.csv"
    output_file.touch()
    
    (out_dir / "energy_clean.csv").touch()
    (out_dir / "weather_clean.csv").touch()
    (out_dir / "features.csv").touch()
    
    full_pipeline(
        energy_file, raw_weather, output_file,
        run_ingestion=False, run_modeling=False, run_gridsearch=False
    )
    
    mock_clean_energy.assert_not_called()
    assert mock_read_csv.call_count == 3 

def test_full_pipeline_energy_not_found(tmp_path):
    energy_file = tmp_path / "non_existent.csv"
    output_file = tmp_path / "out.csv"
    with pytest.raises(SystemExit) as exc_info:
        full_pipeline(energy_file, tmp_path, output_file)
        
    assert exc_info.value.code == 1

@patch("src.pipeline.full_pipeline.ingest_entsoe_data")
def test_run_ingestion_only(mock_ingest):
    run_ingestion_only()
    mock_ingest.assert_called_once()

@patch("src.pipeline.full_pipeline.clean_energy_pipeline")
@patch("src.pipeline.full_pipeline.extract_weather_files")
@patch("src.pipeline.full_pipeline.organize_weather_data")
@patch("src.pipeline.full_pipeline.merge_weather_pipeline")
@patch("src.pipeline.full_pipeline.clean_weather_pipeline")
@patch("src.pipeline.full_pipeline.merge_pipeline")
@patch("src.pipeline.full_pipeline.create_dataset_features")
def test_run_processing_only_run_all(
    mock_feat, mock_merge, mock_clean_w, mock_merge_w, mock_org, mock_ext, mock_clean_e, tmp_path
):
    energy_file = tmp_path / "energy.csv"
    energy_file.touch() 
    out_file = tmp_path / "out" / "final.csv"
    
    run_processing_only(energy_file, tmp_path, out_file)
    
    mock_clean_e.assert_called_once()
    mock_feat.assert_called_once()

def test_run_processing_only_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        run_processing_only(tmp_path / "fake.csv", tmp_path, tmp_path / "out.csv")

@patch("src.pipeline.full_pipeline.Path.exists", return_value=True)
@patch("src.pipeline.full_pipeline.run_grid_search")
@patch("src.pipeline.full_pipeline.train_models")
@patch("src.pipeline.full_pipeline.evaluate_models")
def test_run_modeling_only(mock_eval, mock_train, mock_grid, mock_exists):
    run_modeling_only(run_gridsearch=True)
    
    mock_grid.assert_called_once()
    mock_train.assert_called_once()
    mock_eval.assert_called_once()

@patch("src.pipeline.full_pipeline.Path.exists", return_value=False)
def test_run_modeling_only_not_found(mock_exists):
    with pytest.raises(FileNotFoundError, match="features.csv não encontrado"):
        run_modeling_only()