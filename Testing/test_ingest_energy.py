import pytest
from unittest.mock import patch, MagicMock
from src.ingestion.ingest_energy import ingest_entsoe_data


@patch('src.ingestion.ingest_energy.os.getenv')
@patch('src.ingestion.ingest_energy.load_dotenv')
def test_ingest_energy_missing_token(mock_load, mock_getenv):
    mock_getenv.return_value = None

    with pytest.raises(ValueError, match="Token da ENTSO-E não encontrado"):
        ingest_entsoe_data()


@patch('src.ingestion.ingest_energy.os.getenv')
@patch('src.ingestion.ingest_energy.load_dotenv')
@patch('src.ingestion.ingest_energy.EntsoePandasClient')
@patch('src.ingestion.ingest_energy.os.makedirs')
def test_ingest_energy_success(mock_makedirs, mock_client_class, mock_load, mock_getenv):
    mock_getenv.return_value = 'token_falso'

    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    mock_ts = MagicMock()
    mock_ts.empty = False
    mock_client.query_load.return_value = mock_ts

    ingest_entsoe_data()

    mock_makedirs.assert_called_once_with('data/raw/energy', exist_ok=True)
    mock_client.query_load.assert_called_once()
    mock_ts.to_csv.assert_called_once()


@patch('src.ingestion.ingest_energy.os.getenv')
@patch('src.ingestion.ingest_energy.load_dotenv')
@patch('src.ingestion.ingest_energy.EntsoePandasClient')
def test_ingest_energy_api_failure(mock_client_class, mock_load, mock_getenv):
    mock_getenv.return_value = 'token_falso'

    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    mock_client.query_load.side_effect = Exception("Erro interno da API ENTSO-E")

    with pytest.raises(RuntimeError, match="Falha na ingestão ENTSO-E"):
        ingest_entsoe_data()
