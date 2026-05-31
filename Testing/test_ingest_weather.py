import pytest
from unittest.mock import patch, MagicMock
from src.ingestion.ingest_weather import ingest_weather_data


@patch('src.ingestion.ingest_weather.load_dotenv')
@patch('src.ingestion.ingest_weather.cdsapi.Client')
@patch('src.ingestion.ingest_weather.os.makedirs')
@patch('src.ingestion.ingest_weather.os.path.exists')
def test_ingest_weather_success(mock_exists, mock_makedirs, mock_client_class, mock_load_dotenv):
   
    mock_exists.side_effect = [False, True] * 12

    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    ingest_weather_data()

    mock_makedirs.assert_called_once_with('data/raw/weather', exist_ok=True)
    assert 0 < mock_client.retrieve.call_count <= 12


@patch('src.ingestion.ingest_weather.load_dotenv')
@patch('src.ingestion.ingest_weather.cdsapi.Client')
@patch('src.ingestion.ingest_weather.os.makedirs')
@patch('src.ingestion.ingest_weather.os.path.exists')
def test_ingest_weather_skip_existing(mock_exists, mock_makedirs, mock_client_class, mock_load_dotenv):
    mock_exists.return_value = True

    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    ingest_weather_data()

    mock_client.retrieve.assert_not_called()


@patch('src.ingestion.ingest_weather.load_dotenv')
@patch('src.ingestion.ingest_weather.cdsapi.Client')
@patch('src.ingestion.ingest_weather.os.path.exists')
def test_ingest_weather_api_failure(mock_exists, mock_client_class, mock_load_dotenv):
    mock_exists.return_value = False

    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    mock_client.retrieve.side_effect = Exception("Falha de conexão no CDS API")

    with pytest.raises(Exception, match="Falha de conexão no CDS API"):
        ingest_weather_data()
