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


def load_energy_data(file_path: Path) -> pd.DataFrame:
    try:
        df = pd.read_csv(file_path, index_col=0)
    except Exception as e:
        logging.error(f"Error loading energy data: {e}")
        raise

    if df.empty:
        raise ValueError("Energy dataset is empty")

    return df


def convert_index_to_datetime(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df.index = pd.to_datetime(df.index)
    except Exception as e:
        logging.error(f"Error converting index to datetime: {e}")
        raise

    return df


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={"Actual Load": "load"})

    if "load" not in df.columns:
        raise ValueError("Missing 'load' column after renaming")

    return df


def reset_index_to_timestamp(df: pd.DataFrame) -> pd.DataFrame:
    df = df.reset_index()
    df = df.rename(columns={"index": "timestamp"})

    if "timestamp" not in df.columns:
        raise ValueError("Missing timestamp column")

    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates(subset="timestamp")


def sort_by_timestamp(df: pd.DataFrame) -> pd.DataFrame:
    return df.sort_values("timestamp")


def convert_timezone_to_utc(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    except Exception as e:
        logging.error(f"Error converting timezone: {e}")
        raise

    return df


def resample_hourly(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df = df.set_index("timestamp")
        df = df.resample("1h").mean()
        df = df.reset_index()
    except Exception as e:
        logging.error(f"Error during resampling: {e}")
        raise

    return df


def validate_missing(df: pd.DataFrame) -> pd.DataFrame:
    missing = df.isnull().sum()
    logging.info(f"Missing values:\n{missing}")
    return df


def finalize_energy(df: pd.DataFrame) -> pd.DataFrame:
    if "load" not in df.columns:
        raise ValueError("Missing 'load' column in final dataset")

    try:
        df["load"] = df["load"].round(2)
    except Exception as e:
        logging.error(f"Error rounding load values: {e}")
        raise

    return df


def save_energy_data(df: pd.DataFrame, output_path: Path):
    try:
        df.to_csv(output_path, index=False)
        logging.info(f"Rows final: {len(df)}")
        logging.info("Energy dataset cleaned and saved.")
    except Exception as e:
        logging.error(f"Error saving energy dataset: {e}")
        raise


def clean_energy_pipeline(input_path: Path, output_path: Path) -> pd.DataFrame:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        df = load_energy_data(input_path)
        logging.info(f"Rows original: {len(df)}")

        df = convert_index_to_datetime(df)
        df = rename_columns(df)
        df = reset_index_to_timestamp(df)
        df = remove_duplicates(df)
        df = sort_by_timestamp(df)
        df = convert_timezone_to_utc(df)
        df = resample_hourly(df)
        df = validate_missing(df)
        df = finalize_energy(df)

        save_energy_data(df, output_path)

        return df

    except Exception as e:
        logging.error(f"Error in clean_energy_pipeline: {e}")
        raise


if __name__ == "__main__":
    CURRENT_DIR = Path(__file__).resolve().parent
    PROJECT_ROOT = CURRENT_DIR.parent.parent

    RAW_PATH = PROJECT_ROOT / "data" / "raw" / "energy" / "load_DE_2025.csv"
    PROCESSED_PATH = PROJECT_ROOT / "data" / "processed" / "energy_clean.csv"

    clean_energy_pipeline(RAW_PATH, PROCESSED_PATH)
