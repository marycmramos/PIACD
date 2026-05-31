import pandas as pd
import numpy as np
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


def load_weather_data(file_path: Path) -> pd.DataFrame:
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        logging.error(f"Error loading weather data: {e}")
        raise

    if df.empty:
        raise ValueError("Weather dataset is empty")

    return df


def convert_time_column(df: pd.DataFrame) -> pd.DataFrame:
    try:
        # Caso 1: timestamp
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

        # Caso 2: valid_time
        elif "valid_time" in df.columns:
            df["valid_time"] = pd.to_datetime(df["valid_time"], utc=True)

        # Caso 3: erro
        else:
            raise ValueError("No valid time column found (expected 'timestamp' or 'valid_time')")

    except Exception as e:
        logging.error(f"Error converting time column: {e}")
        raise

    return df


# média de todos os pontos espaciais por hora
def aggregate_spatial(df: pd.DataFrame) -> pd.DataFrame:
    try:
        time_col = "valid_time" if "valid_time" in df.columns else "timestamp"
        df = df.groupby(time_col).mean(numeric_only=True).reset_index()
    except Exception as e:
        logging.error(f"Error during spatial aggregation: {e}")
        raise

    return df


def convert_units(df: pd.DataFrame) -> pd.DataFrame:
    try:
        for col in ["t2m", "mx2t", "mn2t"]:
            if col in df.columns:
                df[col] = df[col] - 273.15

        for col in ["tp", "cp"]:
            if col in df.columns:
                df[col] = df[col] * 1000
    except Exception as e:
        logging.error(f"Error converting units: {e}")
        raise

    return df


def compute_wind_speed(df: pd.DataFrame) -> pd.DataFrame:
    if "u10" not in df.columns or "v10" not in df.columns:
        raise ValueError("Missing wind components (u10, v10)")

    try:
        df["wind_speed"] = np.sqrt(df["u10"]**2 + df["v10"]**2)
    except Exception as e:
        logging.error(f"Error computing wind speed: {e}")
        raise

    return df


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    try:
        mapping = {
            "valid_time": "timestamp",
            "t2m": "temperature",
            "mx2t": "temp_max",
            "mn2t": "temp_min",
            "tp": "total_precipitation",
            "cp": "convective_precipitation",
            "ssrd": "solar_radiation",
        }

        df = df.rename(columns=mapping)

        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

        if "timestamp" not in df.columns:
            raise ValueError("Timestamp column missing after renaming")

    except Exception as e:
        logging.error(f"Error renaming columns: {e}")
        raise

    return df


# ignorar u10 e v10 após calcular a velocidade do vento
def drop_unused_columns(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df = df.drop(columns=["u10", "v10"], errors="ignore")

    except Exception as e:
        logging.error(f"Error dropping unused columns: {e}")
        raise

    return df


# verificar se timestamp já está ordenado
def sort_and_validate(df: pd.DataFrame) -> pd.DataFrame:
    try:
        if "timestamp" not in df.columns:
            raise ValueError("Missing timestamp column")

        is_sorted = df["timestamp"].is_monotonic_increasing
        logging.info(f"Is timestamp already sorted? {is_sorted}")

        df = df.sort_values("timestamp")

        missing = df.isna().sum()
        logging.info(f"Missing values:\n{missing}")

    except Exception as e:
        logging.error(f"Error sorting and validating dataset: {e}")
        raise

    return df


def finalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    try:
        return df.round(3)
    except Exception as e:
        logging.error(f"Error finalizing dataframe: {e}")
        raise


def save_clean_data(df: pd.DataFrame, output_path: Path):
    try:
        df.to_csv(output_path, index=False)
        logging.info("Clean dataset saved!")
        logging.info(f"Final shape: {df.shape}")
        logging.info(f"Saved to: {output_path}")
    except Exception as e:
        logging.error(f"Error saving clean dataset: {e}")
        raise


def clean_weather_pipeline(input_path: Path, output_path: Path) -> pd.DataFrame:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        df = load_weather_data(input_path)
        logging.info(f"Initial shape: {df.shape}")

        df = convert_time_column(df)
        logging.info(f"After spatial aggregation: {df.shape}")

        df = convert_units(df)

        if "u10" in df.columns and "v10" in df.columns:
            df = compute_wind_speed(df)

        df = rename_columns(df)
        df = drop_unused_columns(df)
        df = sort_and_validate(df)
        df = finalize_dataframe(df)

        save_clean_data(df, output_path)

        return df

    except Exception as e:
        logging.error(f"Error in clean_weather_pipeline: {e}")
        raise


if __name__ == "__main__":
    PROJECT_ROOT = Path().resolve()

    input_file = PROJECT_ROOT / "data" / "raw" / "weather" / "weather_2025_full.csv"
    output_file = PROJECT_ROOT / "data" / "processed" / "weather_2025_clean.csv"

    clean_weather_pipeline(input_file, output_file)
