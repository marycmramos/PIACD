import pytest
import zipfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import shutil

from src.cleaning.extractionWeather import (
    is_zip_file,
    extract_nc_from_zip,
    extract_weather_files
)

def test_is_zip_file_true(tmp_path):
    fake_zip = tmp_path / "test.zip"
    fake_zip.write_bytes(b"PK\x03\x04algum_lixo_binario")
    

    assert is_zip_file(fake_zip) is True

def test_is_zip_file_false(tmp_path):
    fake_nc = tmp_path / "test.nc"
    fake_nc.write_bytes(b"CDF\x01lixo_binario")
    
    assert is_zip_file(fake_nc) is False

def test_is_zip_file_failure():

    missing_file = Path("does_not_exist.zip")

    with pytest.raises(FileNotFoundError):
        is_zip_file(missing_file)


def test_extract_nc_from_zip(tmp_path):

    zip_path = tmp_path / "weather_data.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("dados_validos.nc", b"conteudo_nc")
        zf.writestr("ignorar_isto.txt", b"texto_inutil")
        
    output_dir = tmp_path / "extracted"
    output_dir.mkdir()
    
    extracted = extract_nc_from_zip(zip_path, output_dir)
  
    assert len(extracted) == 1
    assert extracted[0].name == "weather_data_dados_validos.nc"
    assert extracted[0].exists()
    assert extracted[0].read_bytes() == b"conteudo_nc"
    

def test_extract_weather_files(tmp_path):

    real_nc = tmp_path / "weather_DE_2025_01.nc"
    real_nc.write_bytes(b"CDF\x01_dados_reais")
    
    fake_nc_zip = tmp_path / "weather_DE_2025_02.nc"
    with zipfile.ZipFile(fake_nc_zip, "w") as zf:
        zf.writestr("interno.nc", b"dados_extraidos")

    ignorar = tmp_path / "weather_PT_2025_01.nc"
    ignorar.write_bytes(b"CDF")

    result_files = extract_weather_files(tmp_path)
   
    assert len(result_files) == 2

    assert real_nc in result_files

    extracted_expected_name = tmp_path / "weather_DE_2025_02_interno.nc"
    assert extracted_expected_name in result_files

@patch("builtins.open", side_effect=Exception("Erro forçado de leitura"))
def test_is_zip_file_exception(mock_open):
    with pytest.raises(Exception, match="Erro forçado de leitura"):
        is_zip_file(Path("dummy.txt"))

@patch("src.cleaning.extractionWeather.zipfile.ZipFile")
def test_extract_nc_from_zip_bad_zip(mock_zipfile):
    mock_zipfile.side_effect = zipfile.BadZipFile("Bad zip")
    with pytest.raises(zipfile.BadZipFile):
        extract_nc_from_zip(Path("bad.zip"), Path("out"))

@patch("src.cleaning.extractionWeather.zipfile.ZipFile")
def test_extract_nc_from_zip_generic_exception(mock_zipfile):
    mock_zipfile.side_effect = Exception("Generic zip error")
    with pytest.raises(Exception, match="Generic zip error"):
        extract_nc_from_zip(Path("error.zip"), Path("out"))

@patch("src.cleaning.extractionWeather.zipfile.ZipFile")
def test_extract_nc_from_zip_no_nc_files(mock_zipfile):
    mock_zip_instance = MagicMock()
    mock_zip_instance.namelist.return_value = ["file.txt", "image.png"]
    mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
    
    extracted = extract_nc_from_zip(Path("no_nc.zip"), Path("out"))
    assert len(extracted) == 0

@patch("src.cleaning.extractionWeather.shutil.copyfileobj")
@patch("src.cleaning.extractionWeather.zipfile.ZipFile")
def test_extract_nc_from_zip_inner_extraction_error(mock_zipfile, mock_copy):
    mock_zip_instance = MagicMock()
    mock_zip_instance.namelist.return_value = ["file.nc"]
    mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
    
    mock_copy.side_effect = Exception("Copy error")
    
    extracted = extract_nc_from_zip(Path("inner_error.zip"), Path("out"))
    assert len(extracted) == 0 

def test_extract_weather_files_no_files(tmp_path):
    with pytest.raises(FileNotFoundError, match="No weather files found"):
        extract_weather_files(tmp_path)

@patch("src.cleaning.extractionWeather.Path.glob")
@patch("src.cleaning.extractionWeather.is_zip_file")
def test_extract_weather_files_inner_error_and_empty_result(mock_is_zip, mock_glob):
    mock_glob.return_value = [Path("weather_DE_2025_01.nc")]
    
    mock_is_zip.side_effect = Exception("is_zip_file error")
    
    with pytest.raises(ValueError, match="No usable weather data found"):
        extract_weather_files(Path("dummy_dir"))