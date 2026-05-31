import pandas as pd
import logging
from src.features.feature_engineering import create_features
from pathlib import Path

Path("logs").mkdir(exist_ok=True)

rel_logger = logging.getLogger("reliability")
rel_logger.setLevel(logging.INFO)
rel_logger.propagate = False

if not rel_logger.handlers:
    rel_handler = logging.FileHandler("logs/reliability.log")
    rel_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    rel_logger.addHandler(rel_handler)


def create_dataset_features(
    input_path="data/processed/dataset_merged.csv",
    output_path="data/processed/features.csv"
):
    try:
        logging.info(f"A carregar dataset: {input_path}")

        df = pd.read_csv(input_path)

        if df.empty:
            raise ValueError("Merged dataset is empty")

        df_features = create_features(df)

        df_features.to_csv(output_path, index=False)

        logging.info(f"Dataset com features criado com sucesso: {output_path}")
        logging.info(f"Shape final: {df_features.shape}")

    except Exception as e:
        logging.error(f"Erro ao criar dataset com features: {e}")
        raise


if __name__ == "__main__":
    create_dataset_features()
