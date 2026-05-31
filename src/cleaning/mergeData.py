import pandas as pd
from pathlib import Path
import logging

Path("logs").mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/reliability.log"),
        logging.StreamHandler()
    ]
)


def load_datasets(weather_path: Path, energy_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    try:
        weather = pd.read_csv(weather_path)
        energy = pd.read_csv(energy_path)
    except Exception as e:
        logging.error(f"Error loading datasets: {e}")
        raise

    return weather, energy


def validate_inputs(weather: pd.DataFrame, energy: pd.DataFrame) -> None:
    required_cols = ["timestamp"]

    for name, df in [("weather", weather), ("energy", energy)]:
        if df.empty:
            raise ValueError(f"{name} dataset is empty")

        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing column '{col}' in {name} dataset")


def convert_timestamps(weather: pd.DataFrame, energy: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    try:
        weather["timestamp"] = pd.to_datetime(weather["timestamp"]).dt.tz_localize(None)
        energy["timestamp"] = pd.to_datetime(energy["timestamp"]).dt.tz_localize(None)
    except Exception as e:
        logging.error(f"Error converting timestamps: {e}")
        raise

    return weather, energy


def merge_datasets(weather: pd.DataFrame, energy: pd.DataFrame) -> pd.DataFrame:
    df = pd.merge(
        energy,
        weather,
        on="timestamp",
        how="inner"
    )

    if df.empty:
        raise ValueError("Merged dataset is empty")

    return df


def drop_unnecessary_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop(columns=["latitude", "longitude", "avg_ie"], errors="ignore")


def sort_dataset(df: pd.DataFrame) -> pd.DataFrame:
    return df.sort_values("timestamp")


def save_merged_dataset(df: pd.DataFrame, output_path: Path):
    try:
        df.to_csv(output_path, index=False)
        logging.info(f"Merged dataset saved: {output_path}")
        logging.info(f"Final shape: {df.shape}")
    except Exception as e:
        logging.error(f"Error saving dataset: {e}")
        raise


def merge_pipeline(df_weather, df_energy, output_file: Path) -> pd.DataFrame:

    output_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        # aceitar tanto paths como dataframes
        if isinstance(df_weather, Path) and isinstance(df_energy, Path):
            df_weather, df_energy = load_datasets(df_weather, df_energy)

        validate_inputs(df_weather, df_energy)

        df_weather, df_energy = convert_timestamps(df_weather, df_energy)

        df = merge_datasets(df_weather, df_energy)
        logging.info(f"Shape after merge: {df.shape}")

        df = drop_unnecessary_columns(df)
        df = sort_dataset(df)

        save_merged_dataset(df, output_file)

        return df

    except Exception as e:
        logging.error(f"Error in merge_pipeline: {e}")
        raise


if __name__ == "__main__":
    PROJECT_ROOT = Path().resolve()

    WEATHER_FILE = PROJECT_ROOT / "data" / "processed" / "weather_2025_clean.csv"
    ENERGY_FILE = PROJECT_ROOT / "data" / "processed" / "energy_clean.csv"
    OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "dataset_merged.csv"

    df_weather = pd.read_csv(WEATHER_FILE)
    df_energy = pd.read_csv(ENERGY_FILE)

    merge_pipeline(df_weather, df_energy, OUTPUT_FILE)
