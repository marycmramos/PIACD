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


def load_weather_files(processed_weather_path: Path) -> dict[str, pd.DataFrame]:
    files = {
        "acc": processed_weather_path / "weather_2025_acc.csv",
        "avg": processed_weather_path / "weather_2025_avg.csv",
        "inst": processed_weather_path / "weather_2025_inst.csv",
        "max": processed_weather_path / "weather_2025_max.csv",
    }

    dfs = {}

    for key, path in files.items():
        try:
            dfs[key] = pd.read_csv(path)
        except FileNotFoundError:
            raise FileNotFoundError(f"Missing weather file: {path}")

    return dfs


def validate_columns(dfs: dict[str, pd.DataFrame]) -> None:
    required_cols = ["valid_time"]

    for key, df in dfs.items():
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing column '{col}' in dataset '{key}'")

        if df.empty:
            raise ValueError(f"Dataset '{key}' is empty")


def drop_irrelevant_columns(dfs: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    drop_cols = ["number", "expver"]

    for key in dfs:
        dfs[key] = dfs[key].drop(columns=drop_cols, errors="ignore")

    return dfs


def remove_duplicate_columns(dfs: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    for key in ["avg", "inst", "max"]:
        dfs[key] = dfs[key].drop(
            columns=["latitude", "longitude"],
            errors="ignore"
        )

    return dfs


def merge_weather_dataframes(dfs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df = dfs["acc"]

    for key in ["avg", "inst", "max"]:
        df = df.merge(dfs[key], on="valid_time", how="inner")

    if df.empty:
        raise ValueError("Merged weather dataset is empty")

    return df


def save_merged_weather(df: pd.DataFrame, output_path: Path):
    try:
        df.to_csv(output_path, index=False)
        logging.info(f"Merged dataset saved: {output_path}")
        logging.info(f"Final shape: {df.shape}")
    except Exception as e:
        logging.error(f"Error saving merged dataset: {e}")
        raise


def merge_weather_pipeline(processed_weather_path: Path):
    try:
        dfs = load_weather_files(processed_weather_path)

        validate_columns(dfs)

        dfs = drop_irrelevant_columns(dfs)
        dfs = remove_duplicate_columns(dfs)

        weather_full = merge_weather_dataframes(dfs)

        output_file = processed_weather_path / "weather_2025_full.csv"
        save_merged_weather(weather_full, output_file)

    except Exception as e:
        logging.error(f"Error in merge_weather_pipeline: {e}")
        raise

    return weather_full


if __name__ == "__main__":
    PROCESSED_WEATHER_PATH = Path("data/raw/weather")
    merge_weather_pipeline(PROCESSED_WEATHER_PATH)
