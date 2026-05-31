import os
import pandas as pd
import logging
from entsoe import EntsoePandasClient
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


def ingest_entsoe_data(file_path=None):
    if file_path is not None:
        logging.info(f"A carregar dados locais de energia: {file_path}")
        return pd.read_csv(file_path)

    load_dotenv()

    api_token = os.getenv('ENTSOE_TOKEN')
    if not api_token:
        raise ValueError("Token da ENTSO-E não encontrado no ficheiro .env")

    country_code = 'DE'

    start = pd.Timestamp('2025-01-01', tz='Europe/Berlin')
    end = pd.Timestamp('2026-01-01', tz='Europe/Berlin')

    logging.info(f"A extrair dados para {country_code}...")

    try:
        client = EntsoePandasClient(api_key=api_token)

        ts = client.query_load(country_code, start=start, end=end)

        if ts is None or (hasattr(ts, "empty") and ts.empty):
            raise ValueError("Dados de energia vazios ou inválidos")

        output_dir = 'data/raw/energy'
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, f'load_{country_code}_2025.csv')

        if hasattr(ts, "to_csv"):
            ts.to_csv(output_path)
        else:
            raise TypeError("Formato inesperado dos dados retornados")

        logging.info(f"Dados guardados em: {output_path}")

        return ts

    except Exception as e:
        logging.error(f"Erro na ingestão ENTSO-E: {e}")
        raise RuntimeError("Falha na ingestão ENTSO-E") from e


if __name__ == '__main__':
    ingest_entsoe_data()
