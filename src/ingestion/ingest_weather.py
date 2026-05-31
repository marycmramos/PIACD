import os
import logging
import cdsapi
from dotenv import load_dotenv
from pathlib import Path

Path("logs").mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/reliability.log"),
        logging.StreamHandler()
    ]
)


def get_cds_client():
    return cdsapi.Client()


def ingest_weather_data(file_path=None):
    if file_path is not None:
        import pandas as pd
        logging.info(f"A carregar dados locais de clima: {file_path}")
        return pd.read_csv(file_path)

    load_dotenv()

    output_dir = "data/raw/weather"
    os.makedirs(output_dir, exist_ok=True)

    logging.info("A iniciar download ERA5 mês a mês...")

    dataset = "reanalysis-era5-single-levels"
    year = "2025"

    try:
        client = get_cds_client()

    except Exception as e:
        logging.error(f"Erro ao inicializar cliente CDS: {e}")
        raise RuntimeError("Falha na inicialização da API CDS") from e

    for month in range(1, 13):

        month_str = str(month).zfill(2)
        output_path = os.path.join(output_dir, f"weather_DE_{year}_{month_str}.nc")

        if os.path.exists(output_path):
            logging.info(f"Mês {month_str} já existe. A saltar.")
            continue

        logging.info(f"A enviar pedido para {month_str}/{year}...")

        request = {
            "product_type": ["reanalysis"],
            "variable": [
                "2m_temperature",
                "maximum_2m_temperature_since_previous_post_processing",
                "minimum_2m_temperature_since_previous_post_processing",
                "mean_evaporation_rate",
                "convective_precipitation",
                "total_precipitation",
                "surface_solar_radiation_downwards",
                "10m_u_component_of_wind",
                "10m_v_component_of_wind"
            ],
            "year": [year],
            "month": [month_str],
            "day": [str(i).zfill(2) for i in range(1, 32)],
            "time": [f"{str(i).zfill(2)}:00" for i in range(24)],
            "data_format": "netcdf",
            "download_format": "unarchived",
            "area": [55, 5.9, 47, 15]
        }

        try:
            client.retrieve(dataset, request, output_path)

            if not os.path.exists(output_path):
                raise IOError(f"Ficheiro não foi criado: {output_path}")

            logging.info(f"Mês {month_str} guardado em {output_path}")

        except Exception as e:
            logging.error(f"Erro no mês {month_str}: {e}")
            raise Exception("Falha de conexão no CDS API")

    logging.info("Ingestão ERA5 concluída com sucesso.")


if __name__ == "__main__":
    ingest_weather_data()
