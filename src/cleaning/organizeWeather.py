import pandas as pd
import xarray as xr
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


def get_nc_files(raw_weather_path: Path) -> list[Path]:
    return list(raw_weather_path.glob("*stepType*.nc"))


def group_files_by_variable(nc_files: list[Path]) -> dict[str, list[Path]]:
    groups = {}

    try:
        for f in nc_files:
            name = f.name

            if "stepType-acc" in name:
                key = "acc"
            elif "stepType-avg" in name:
                key = "avg"
            elif "stepType-inst" in name:
                key = "inst"
            elif "stepType-max" in name:
                key = "max"
            else:
                continue

            groups.setdefault(key, []).append(f)
    except Exception as e:
        logging.error(f"Error grouping files: {e}")
        raise

    return groups


def load_and_concat_datasets(files: list[Path]) -> pd.DataFrame:
    dfs = []

    try:
        for f in sorted(files):
            logging.info(f"Opening: {f.name}")

            try:
                with xr.open_dataset(f) as ds:
                    df = ds.to_dataframe().reset_index()

                if not isinstance(df, pd.DataFrame):
                    raise TypeError("Invalid dataset conversion")

                if "valid_time" not in df.columns:
                    raise ValueError("Missing 'valid_time' column")

                df = df.groupby("valid_time").mean(numeric_only=True).reset_index()

            except Exception as e:
                logging.error(f"Error opening {f.name}: {e}")
                continue

            dfs.append(df)

        if not dfs:
            logging.error("No datasets were loaded successfully")
            raise ValueError("No valid NetCDF data found")

    except Exception as e:
        logging.error(f"Error loading and concatenating datasets: {e}")
        raise

    return pd.concat(dfs, ignore_index=True)


def save_variable_dataframe(df: pd.DataFrame, output_path: Path):
    try:
        df.to_csv(output_path, index=False)
        logging.info(f"Saved: {output_path}")
        logging.info(f"Shape: {df.shape}")

    except Exception as e:
        logging.error(f"Error saving dataframe: {e}")
        raise


def cleanup_nc_files(raw_weather_path: Path):
    for f in raw_weather_path.glob("*stepType*.nc"):
        try:
            f.unlink()
            print("Removed temporary file:", f.name)
        except Exception as e:
            print("Could not remove:", f.name, e)


def organize_weather_data(raw_weather_path: Path, processed_weather_path: Path):
    processed_weather_path.mkdir(parents=True, exist_ok=True)

    nc_files = get_nc_files(raw_weather_path)

    try:
        if not nc_files:
            logging.error("No NetCDF files found")
            raise FileNotFoundError("No .nc files found")

        groups = group_files_by_variable(nc_files)

        for var, files in groups.items():
            print(f"\nProcessing variable: {var}")

            full_df = load_and_concat_datasets(files)

            out_file = processed_weather_path / f"weather_2025_{var}.csv"
            save_variable_dataframe(full_df, out_file)

        cleanup_nc_files(raw_weather_path)
    except Exception as e:
        logging.error(f"Error in organize_weather_data: {e}")


if __name__ == "__main__":
    PROJECT_ROOT = Path().resolve()

    RAW_WEATHER_PATH = PROJECT_ROOT / "data" / "raw" / "weather"
    PROCESSED_WEATHER_PATH = PROJECT_ROOT / "data" / "raw" / "weather"

    organize_weather_data(RAW_WEATHER_PATH, PROCESSED_WEATHER_PATH)
