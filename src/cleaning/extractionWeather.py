from pathlib import Path
import zipfile
import shutil
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


def is_zip_file(file_path: Path) -> bool:
    try:
        with open(file_path, "rb") as file:
            header = file.read(2)
        return header == b"PK"
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")
        raise


def extract_nc_from_zip(zip_path: Path, output_dir: Path) -> list[Path]:
    extracted_files = []

    logging.info(f"Extracting: {zip_path}")

    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            for name in zip_ref.namelist():
                if name.endswith(".nc"):
                    new_name = f"{zip_path.stem}_{name}"
                    new_path = output_dir / new_name

                    try:
                        with zip_ref.open(name) as source:
                            with open(new_path, "wb") as target:
                                shutil.copyfileobj(source, target)

                        extracted_files.append(new_path)

                    except Exception as e:
                        logging.warning(f"Error extracting {name} from {zip_path}: {e}")
                        continue

    except zipfile.BadZipFile:
        logging.error(f"Invalid ZIP file: {zip_path}")
        raise
    except Exception as e:
        logging.error(f"Error processing ZIP file {zip_path}: {e}")
        raise

    if not extracted_files:
        logging.warning(f"No .nc files found inside {zip_path}")

    return extracted_files


def extract_weather_files(raw_weather_path: Path) -> list[Path]:
    files = list(raw_weather_path.glob("weather_DE_2025_*.nc"))

    if not files:
        logging.error("No weather files found in directory")
        raise FileNotFoundError("No weather files found")

    real_nc_files = []

    for f in files:
        try:
            if is_zip_file(f):
                extracted = extract_nc_from_zip(f, raw_weather_path)
                real_nc_files.extend(extracted)
            else:
                real_nc_files.append(f)

        except Exception as e:
            logging.error(f"Error processing file {f}: {e}")
            continue

    if not real_nc_files:
        logging.error("No valid NetCDF files available after extraction")
        raise ValueError("No usable weather data found")

    logging.info(f"Real NetCDF files: {len(real_nc_files)}")

    return real_nc_files


if __name__ == "__main__":
    PROJECT_ROOT = Path().resolve()
    RAW_WEATHER_PATH = PROJECT_ROOT / "data" / "raw" / "weather"

    extract_weather_files(RAW_WEATHER_PATH)
