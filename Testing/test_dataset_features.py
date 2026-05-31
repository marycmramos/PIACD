import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from src.features.dataset_features import create_dataset_features

@patch("src.features.dataset_features.pd.DataFrame.to_csv")
@patch("src.features.dataset_features.create_features")
@patch("src.features.dataset_features.pd.read_csv")
def test_create_dataset_features_success(mock_read_csv, mock_create_features, mock_to_csv):
    mock_read_csv.return_value = pd.DataFrame({"dummy_col": [1, 2, 3]})

    mock_create_features.return_value = pd.DataFrame({"dummy_col": [1, 2, 3], "new_feature": [10, 20, 30]})
    create_dataset_features("dummy_in.csv", "dummy_out.csv")
   
    mock_read_csv.assert_called_once_with("dummy_in.csv")
    mock_create_features.assert_called_once()
    mock_to_csv.assert_called_once_with("dummy_out.csv", index=False)


@patch("src.features.dataset_features.pd.read_csv")
def test_create_dataset_features_empty(mock_read_csv):

    mock_read_csv.return_value = pd.DataFrame()

    with pytest.raises(ValueError, match="Merged dataset is empty"):
        create_dataset_features("dummy_in.csv", "dummy_out.csv")


@patch("src.features.dataset_features.pd.read_csv")
def test_create_dataset_features_exception(mock_read_csv):
    mock_read_csv.side_effect = Exception("Erro catastrófico forçado")
  
    with pytest.raises(Exception, match="Erro catastrófico forçado"):
        create_dataset_features("dummy_in.csv", "dummy_out.csv")