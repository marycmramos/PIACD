import pandas as pd
import json
import os
import hashlib
import sys
import joblib
import time
import logging
from pathlib import Path

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor


CONFIG_PATH = "src/utils/model_config.json"
RESULTS_PATH = "data/experiments/experiments.json"


# logging setup

Path("logs").mkdir(exist_ok=True)

# performance logger
perf_logger = logging.getLogger("performance")
perf_logger.setLevel(logging.INFO)
perf_logger.propagate = False

if not perf_logger.handlers:
    perf_handler = logging.FileHandler("logs/performance.log")
    perf_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    perf_logger.addHandler(perf_handler)

# reliability logger
rel_logger = logging.getLogger("reliability")
rel_logger.setLevel(logging.INFO)

if not rel_logger.handlers:
    rel_handler = logging.FileHandler("logs/reliability.log")
    rel_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    rel_logger.addHandler(rel_handler)


# -------------------------------
def load_config(path=CONFIG_PATH):
    try:
        with open(path, "r") as f:
            config = json.load(f)
            rel_logger.info("Config loaded successfully.")
            return config
    except Exception as e:
        rel_logger.error(f"Error loading config: {e}")
        raise


def get_config_hashes(config):
    return {
        "split":  hashlib.sha256(json.dumps(config.get("split", {}),              sort_keys=True).encode()).hexdigest(),
        "lr":     hashlib.sha256(json.dumps(config.get("linear_regression", {}),  sort_keys=True).encode()).hexdigest(),
        "rf":     hashlib.sha256(json.dumps(config.get("random_forest", {}),      sort_keys=True).encode()).hexdigest(),
    }


def load_results():
    try:
        if not os.path.exists(RESULTS_PATH):
            rel_logger.warning("Experiments file not found. Returning empty list.")
            return []

        with open(RESULTS_PATH, "r") as f:
            return json.load(f)

    except Exception as e:
        rel_logger.error(f"Error loading results: {e}")
        return []


def get_existing_hashes():
    """Devolve os hashes guardados do último experiment."""
    experiments = load_results()
    if not experiments:
        return {}
    # pega no mais recente
    last = experiments[-1]
    return last.get("hashes", {})


def create_split(X, y, split_ratio=0.8):
    try:
        if len(X) == 0:
            raise ValueError("Input dataset is empty before split")

        split_idx = int(len(X) * split_ratio)

        X_train = X.iloc[:split_idx]
        X_test = X.iloc[split_idx:]

        y_train = y.iloc[:split_idx]
        y_test = y.iloc[split_idx:]

        return X_train, X_test, y_train, y_test

    except Exception as e:
        rel_logger.error(f"Error creating train/test split: {e}")
        raise


def log_time(start, label):
    elapsed = time.time() - start
    msg = f"{label}: {elapsed:.4f} seconds"

    print(f"[TIME] {msg}")
    perf_logger.info(msg)


# ------------------------------
def train_models():
    start_total = time.time()
    try:
        config = load_config()
        hashes = get_config_hashes(config)
        existing = get_existing_hashes()

        split_changed = hashes["split"] != existing.get("split")
        lr_changed = hashes["lr"] != existing.get("lr")
        rf_changed = hashes["rf"] != existing.get("rf")

        if not split_changed and not lr_changed and not rf_changed:
            print("Configuração já existe. Skipping training.")
            rel_logger.info("Training skipped - config unchanged.")
            sys.exit()

        os.makedirs("data/models", exist_ok=True)

        # Load data
        df = pd.read_csv("data/processed/features.csv")
        if df.empty:
            raise ValueError("Loaded dataset is empty")

        df = df.iloc[168:].reset_index(drop=True)
        TARGET = "load"

        X = df.drop(columns=[TARGET])
        y = df[TARGET]
        X = X.select_dtypes(include=["number"])
        X = X.drop(columns=["load_diff"], errors="ignore")

        # Split - só re-faz se o split mudou
        if split_changed:
            print("[SPLIT] A fazer novo split...")
            X_train, X_test, y_train, y_test = create_split(X, y)

            timestamps = df["timestamp"]
            split_idx = int(len(df) * 0.8)
            ts_train = timestamps.iloc[:split_idx]
            ts_test = timestamps.iloc[split_idx:]

            joblib.dump(X_train, "data/models/X_train.pkl")
            joblib.dump(X_test,  "data/models/X_test.pkl")
            joblib.dump(y_train, "data/models/y_train.pkl")
            joblib.dump(y_test,  "data/models/y_test.pkl")
            joblib.dump(ts_train, "data/models/ts_train.pkl")
            joblib.dump(ts_test,  "data/models/ts_test.pkl")
        else:
            print("[SPLIT] Split não mudou, a reutilizar...")
            X_train = joblib.load("data/models/X_train.pkl")
            X_test = joblib.load("data/models/X_test.pkl")
            y_train = joblib.load("data/models/y_train.pkl")
            y_test = joblib.load("data/models/y_test.pkl")

        # Linear Regression - só treina se LR ou split mudou
        if lr_changed or split_changed:
            print("[LR] A treinar Linear Regression...")
            start = time.time()
            lr_params = config.get("linear_regression", {})
            lr_model = LinearRegression(
                fit_intercept=lr_params.get("fit_intercept", True),
                positive=lr_params.get("positive", False)
            )
            lr_model.fit(X_train, y_train)
            joblib.dump(lr_model, "data/models/lr_model.pkl")
            log_time(start, "Train Linear Regression")
        else:
            print("[LR] Hiperparâmetros não mudaram, a reutilizar modelo...")

        # Random Forest - só treina se RF ou split mudou
        if rf_changed or split_changed:
            print("[RF] A treinar Random Forest...")
            start = time.time()
            rf_params = config.get("random_forest", {})
            rf_model = RandomForestRegressor(
                n_estimators=rf_params.get("n_estimators", 100),
                max_depth=rf_params.get("max_depth", 10),
                min_samples_split=rf_params.get("min_samples_split", 2),
                min_samples_leaf=rf_params.get("min_samples_leaf", 1),
                random_state=rf_params.get("random_state", 42),
                n_jobs=-1
            )
            rf_model.fit(X_train, y_train)
            joblib.dump(rf_model, "data/models/rf_model.pkl")
            log_time(start, "Train Random Forest")
        else:
            print("[RF] Hiperparâmetros não mudaram, a reutilizar modelo...")

        log_time(start_total, "TOTAL TRAINING PIPELINE")
        rel_logger.info("Training pipeline completed successfully.")

    except Exception as e:
        rel_logger.error(f"Training pipeline failed: {e}")
        raise


if __name__ == "__main__":
    train_models()
