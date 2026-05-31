import time
import logging
import sys
from pathlib import Path

# INGESTION
from src.ingestion.ingest_energy import ingest_entsoe_data

# WEATHER PIPELINE
from src.cleaning.extractionWeather import extract_weather_files
from src.cleaning.organizeWeather import organize_weather_data
from src.cleaning.mergeWeather import merge_weather_pipeline
from src.cleaning.cleanWeather import clean_weather_pipeline

# ENERGY
from src.cleaning.cleanedEnergy import clean_energy_pipeline

# FINAL MERGE
from src.cleaning.mergeData import merge_pipeline

# FEATURES
from src.features.dataset_features import create_dataset_features

# MODELING
from src.models.training_models import train_models
from src.models.evaluate_models import evaluate_models

from src.models.grid_search import run_grid_search

Path("logs").mkdir(exist_ok=True)

# RELIABILITY LOGGER
reliability_logger = logging.getLogger("reliability")
if not reliability_logger.handlers:
    rel_handler = logging.FileHandler("logs/reliability.log")
    rel_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    reliability_logger.addHandler(rel_handler)
reliability_logger.setLevel(logging.INFO)
reliability_logger.propagate = False

# PERFORMANCE LOGGER
performance_logger = logging.getLogger("performance")
if not performance_logger.handlers:
    perf_handler = logging.FileHandler("logs/performance.log")
    perf_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    performance_logger.addHandler(perf_handler)
performance_logger.setLevel(logging.INFO)
performance_logger.propagate = False


def full_pipeline(
    energy_input_path: Path,
    raw_weather_path: Path,
    output_path: Path,
    run_ingestion: bool = False,
    run_modeling: bool = True,
    run_gridsearch: bool = False
):
    total_start = time.time()

    try:

        # 1. INGESTION
        if run_ingestion:
            start = time.time()
            reliability_logger.info("Starting INGESTION pipeline...")

            ingest_entsoe_data()

            performance_logger.info(f"Ingestion: {time.time() - start:.2f}s")
            reliability_logger.info("Ingestion pipeline completed.")

        if not energy_input_path.exists():
            raise FileNotFoundError(f"Energy file not found: {energy_input_path}")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 2. ENERGY CLEAN
        energy_temp = output_path.parent / "energy_clean.csv"

        if energy_temp.exists():
            reliability_logger.info(
                f"Skipping ENERGY cleaning - file already exists: {energy_temp}"
            )

            import pandas as pd
            df_energy_clean = pd.read_csv(energy_temp)

        else:
            reliability_logger.info("Starting ENERGY cleaning pipeline...")
            start = time.time()

            df_energy_clean = clean_energy_pipeline(
                energy_input_path,
                energy_temp
            )

            performance_logger.info(f"Energy cleaning: {time.time() - start:.2f}s")
            reliability_logger.info("Energy cleaning completed.")

        # 3. WEATHER FULL PIPELINE
        weather_clean_path = output_path.parent / "weather_clean.csv"

        if weather_clean_path.exists():
            reliability_logger.info(
                f"Skipping WEATHER pipeline - file already exists: {weather_clean_path}"
            )

            import pandas as pd
            df_weather_clean = pd.read_csv(weather_clean_path)

        else:
            reliability_logger.info("Starting WEATHER pipeline...")
            start = time.time()

            # 3.1 Extraction
            extract_weather_files(raw_weather_path)

            # 3.2 Organize
            organize_weather_data(raw_weather_path, raw_weather_path)

            # 3.3 Merge
            merge_weather_pipeline(raw_weather_path)

            # 3.4 Clean
            df_weather_clean = clean_weather_pipeline(
                raw_weather_path / "weather_2025_full.csv",
                weather_clean_path
            )

            performance_logger.info(f"Weather pipeline: {time.time() - start:.2f}s")
            reliability_logger.info("Weather pipeline completed.")

        # 4. MERGE FINAL
        if output_path.exists():
            reliability_logger.info(
                f"Skipping MERGE pipeline - file already exists: {output_path}"
            )

            import pandas as pd
            df_final = pd.read_csv(output_path)

        else:
            reliability_logger.info("Starting MERGE pipeline...")
            start = time.time()

            df_final = merge_pipeline(
                df_weather_clean,
                df_energy_clean,
                output_path
            )

            performance_logger.info(f"Merge: {time.time() - start:.2f}s")
            reliability_logger.info("Merge pipeline completed.")

        # 5. FEATURE ENGINEERING
        features_path = output_path.parent / "features.csv"

        if features_path.exists():
            reliability_logger.info(
                f"Skipping FEATURE ENGINEERING - file already exists: {features_path}"
            )

        else:
            reliability_logger.info("Starting FEATURE ENGINEERING pipeline...")
            start = time.time()

            create_dataset_features(
                input_path=str(output_path),
                output_path=str(features_path)
            )

            performance_logger.info(f"Feature engineering: {time.time() - start:.2f}s")
            reliability_logger.info("Feature engineering completed.")

        # 6. GRID SEARCH
        if run_modeling and run_gridsearch:

            reliability_logger.info("Starting GRID SEARCH pipeline...")
            start = time.time()

            run_grid_search()

            performance_logger.info(
                f"Grid search: {time.time() - start:.2f}s"
            )

            reliability_logger.info("Grid search completed.")

        # 7. MODEL TRAINING
        if run_modeling:
            reliability_logger.info("Starting MODEL TRAINING pipeline...")
            start = time.time()

            train_models()

            performance_logger.info(f"Model training: {time.time() - start:.2f}s")
            reliability_logger.info("Model training completed.")

            # 7. MODEL EVALUATION

            reliability_logger.info("Starting MODEL EVALUATION pipeline...")
            start = time.time()

            evaluate_models()

            performance_logger.info(f"Model evaluation: {time.time() - start:.2f}s")
            reliability_logger.info("Model evaluation completed.")

        # TOTAL
        performance_logger.info(f"TOTAL PIPELINE: {time.time() - total_start:.2f}s")
        reliability_logger.info("Full pipeline completed successfully.")

        return df_final

    except Exception as e:
        reliability_logger.error(f"Pipeline failed: {e}")
        sys.exit(1)

# INDIVIDUAL PIPELINES


def run_ingestion_only():
    reliability_logger.info("Starting INGESTION ONLY pipeline...")

    ingest_entsoe_data()

    reliability_logger.info("Ingestion only completed.")


def run_processing_only(
    energy_input_path: Path,
    raw_weather_path: Path,
    output_path: Path
):
    reliability_logger.info("Starting PROCESSING ONLY pipeline...")

    if not energy_input_path.exists():
        raise FileNotFoundError(
            f"Energy file not found: {energy_input_path}"
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # ENERGY CLEAN
    energy_temp = output_path.parent / "energy_clean.csv"

    if energy_temp.exists():
        reliability_logger.info(
            f"Skipping ENERGY cleaning - file already exists: {energy_temp}"
        )

        import pandas as pd
        df_energy_clean = pd.read_csv(energy_temp)

    else:
        df_energy_clean = clean_energy_pipeline(
            energy_input_path,
            energy_temp
        )

    # WEATHER
    weather_clean_path = output_path.parent / "weather_clean.csv"

    if weather_clean_path.exists():
        reliability_logger.info(
            f"Skipping WEATHER pipeline - file already exists: {weather_clean_path}"
        )

        import pandas as pd
        df_weather_clean = pd.read_csv(weather_clean_path)

    else:
        extract_weather_files(raw_weather_path)
        organize_weather_data(raw_weather_path, raw_weather_path)
        merge_weather_pipeline(raw_weather_path)

        df_weather_clean = clean_weather_pipeline(
            raw_weather_path / "weather_2025_full.csv",
            weather_clean_path
        )

    # MERGE
    if output_path.exists():
        reliability_logger.info(
            f"Skipping MERGE pipeline - file already exists: {output_path}"
        )

        import pandas as pd
        df_final = pd.read_csv(output_path)

    else:
        df_final = merge_pipeline(
            df_weather_clean,
            df_energy_clean,
            output_path
        )

    # FEATURES
    features_path = output_path.parent / "features.csv"

    if features_path.exists():
        reliability_logger.info(
            f"Skipping FEATURE ENGINEERING - file already exists: {features_path}"
        )

    else:
        create_dataset_features(
            input_path=str(output_path),
            output_path=str(features_path)
        )

    reliability_logger.info("Processing only completed.")

    return df_final


def run_modeling_only(run_gridsearch=False):
    reliability_logger.info("Starting MODELING ONLY pipeline...")

    PROJECT_ROOT = Path().resolve()

    features_path = PROJECT_ROOT / "data/processed/features.csv"

    if not features_path.exists():
        raise FileNotFoundError(
            "features.csv não encontrado. Corre primeiro o processamento."
        )
    if run_gridsearch:
        reliability_logger.info("Starting GRID SEARCH pipeline...")

        run_grid_search()
        reliability_logger.info("Grid search completed.")

    train_models()
    evaluate_models()

    reliability_logger.info("Modeling only completed.")


if __name__ == "__main__":
    PROJECT_ROOT = Path().resolve()

    energy_path = PROJECT_ROOT / "data/raw/energy/load_DE_2025.csv"
    raw_weather_path = PROJECT_ROOT / "data/raw/weather"
    output_path = PROJECT_ROOT / "data/processed/dataset_merged.csv"
    run_gridsearch = "--grid-search" in sys.argv

    # INDIVIDUAL MODES
    if "--only-ingestion" in sys.argv:
        run_ingestion_only()

    elif "--only-processing" in sys.argv:
        run_processing_only(
            energy_input_path=energy_path,
            raw_weather_path=raw_weather_path,
            output_path=output_path
        )

    elif "--only-modeling" in sys.argv:
        run_modeling_only(
            run_gridsearch=run_gridsearch
        )

    # FULL PIPELINE
    else:
        run_ingestion = "--ingestion" in sys.argv

        full_pipeline(
            energy_input_path=energy_path,
            raw_weather_path=raw_weather_path,
            output_path=output_path,
            run_ingestion=run_ingestion,
            run_modeling=True,
            run_gridsearch=run_gridsearch
        )
