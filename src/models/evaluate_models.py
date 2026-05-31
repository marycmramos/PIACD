import pandas as pd
import numpy as np
import joblib
import json
import os
import hashlib
import time
import logging
from pathlib import Path

from datetime import datetime
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


CONFIG_PATH = "src/utils/model_config.json"
EXPERIMENTS_PATH = "data/experiments/experiments.json"
RESULTS_DIR = "data/results/"


# loggin setup

Path("logs").mkdir(exist_ok=True)

perf_logger = logging.getLogger("performance")
perf_logger.setLevel(logging.INFO)
perf_logger.propagate = False

if not perf_logger.handlers:
    perf_handler = logging.FileHandler("logs/performance.log")
    perf_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    perf_logger.addHandler(perf_handler)

rel_logger = logging.getLogger("reliability")
rel_logger.setLevel(logging.INFO)
rel_logger.propagate = False

if not rel_logger.handlers:
    rel_handler = logging.FileHandler("logs/reliability.log")
    rel_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    rel_logger.addHandler(rel_handler)


# -------------------------------
def log_time(start, label):
    elapsed = time.time() - start
    msg = f"{label}: {elapsed:.4f} seconds"

    print(f"[TIME] {msg}")
    perf_logger.info(msg)


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


def load_experiments():
    try:
        if not os.path.exists(EXPERIMENTS_PATH):
            rel_logger.warning("Experiments file not found.")
            return []

        with open(EXPERIMENTS_PATH, "r") as f:
            return json.load(f)

    except Exception as e:
        rel_logger.error(f"Error loading experiments: {e}")
        return []


def save_experiments(data):
    try:
        with open(EXPERIMENTS_PATH, "w") as f:
            json.dump(data, f, indent=4)
        rel_logger.info("Experiments saved successfully.")
    except Exception as e:
        rel_logger.error(f"Error saving experiments: {e}")


def evaluate(name, y_true, y_pred):
    try:
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        r2 = r2_score(y_true, y_pred)

        print(f"\n{name}")
        print(f"MAE: {mae:.4f}")
        print(f"RMSE: {rmse:.4f}")
        print(f"R²: {r2:.4f}")

        rel_logger.info(f"{name} evaluated successfully.")

        return mae, rmse, r2

    except Exception as e:
        rel_logger.error(f"Error evaluating {name}: {e}")
        raise


# -------------------------------
def evaluate_models():

    start_total = time.time()

    try:
        # load dataset
        start = time.time()

        os.makedirs(RESULTS_DIR, exist_ok=True)

        BASE_DIR = Path(__file__).resolve().parents[2]

        df = pd.read_csv(BASE_DIR / "data/processed/features.csv")

        if df.empty:
            raise ValueError("Dataset is empty")

        log_time(start, "Load dataset")
        rel_logger.info(f"Dataset loaded with {len(df)} rows.")

        df = df.iloc[168:].reset_index(drop=True)

        # splits
        X_test = joblib.load("data/models/X_test.pkl")
        y_test = joblib.load("data/models/y_test.pkl")
        X_train = joblib.load("data/models/X_train.pkl")
        y_train = joblib.load("data/models/y_train.pkl")

        if len(X_test) == 0:
            raise ValueError("Test set is empty")

        rel_logger.info(f"Train size: {len(X_train)}, Test size: {len(X_test)}")

        # baseline naive (lag_1h)
        start = time.time()

        if "lag_1h" not in X_test.columns:
            raise ValueError("Missing lag_1h feature for baseline")

        baseline_pred = X_test["lag_1h"]

        baseline_mae, baseline_rmse, baseline_r2 = evaluate(
            "Baseline (lag_1h)", y_test, baseline_pred
        )

        log_time(start, "Baseline evaluation")

        # load models
        start = time.time()

        lr_model = joblib.load("data/models/lr_model.pkl")
        rf_model = joblib.load("data/models/rf_model.pkl")

        log_time(start, "Load models")
        rel_logger.info("Models loaded successfully.")

        # predictions
        start = time.time()

        lr_pred = lr_model.predict(X_test)
        rf_pred = rf_model.predict(X_test)

        log_time(start, "Model predictions")

        # metrics
        start = time.time()

        lr_mae, lr_rmse, lr_r2 = evaluate("Linear Regression", y_test, lr_pred)
        rf_mae, rf_rmse, rf_r2 = evaluate("Random Forest", y_test, rf_pred)

        log_time(start, "Compute metrics")

        # residuals
        residuals = y_test - rf_pred

        residual_analysis = {
            "mean": float(residuals.mean()),
            "std": float(residuals.std()),
            "min": float(residuals.min()),
            "max": float(residuals.max())
        }

        # save residuals full
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        residuals_df = pd.DataFrame({
            "actual": y_test.values,
            "predicted": rf_pred,
            "residual": residuals.values
        })

        residuals_df.to_json(f"{RESULTS_DIR}/residuals_{run_id}.json", orient="records")

        rel_logger.info("Residual analysis computed.")

        # overfitting
        rf_train_pred = rf_model.predict(X_train)

        overfitting_analysis = {
            "train": {
                "mae": float(mean_absolute_error(y_train, rf_train_pred)),
                "rmse": float(np.sqrt(mean_squared_error(y_train, rf_train_pred))),
                "r2": float(r2_score(y_train, rf_train_pred))
            },
            "test": {
                "mae": float(rf_mae),
                "rmse": float(rf_rmse),
                "r2": float(rf_r2)
            }
        }

        rel_logger.info("Overfitting analysis computed.")

        # feature importance
        feature_importance = dict(zip(X_train.columns, rf_model.feature_importances_))

        # save predictions for dashboard
        ts_test = joblib.load("data/models/ts_test.pkl")

        test_predictions_df = pd.DataFrame({
            "Timestamp": ts_test.values,
            "Actual Demand (MW)": y_test.values,
            "Predicted LR": lr_pred,
            "Predicted RF": rf_pred
        })

        predictions_path = f"{RESULTS_DIR}/test_predictions.json"
        test_predictions_df.to_json(predictions_path, orient="records")

        feature_cols = X_train.columns

        df_full = pd.read_csv('data/processed/features.csv')
        X_full = df_full.reindex(columns=feature_cols)
        mask = X_full.notna().all(axis=1)

        X_full = X_full[mask]
        df_full = df_full.loc[mask]

        ts_full = df_full["Timestamp"] if "Timestamp" in df_full.columns else df_full.iloc[:, 0]

        # usa exatamente as mesmas features do treino
        feature_cols = X_train.columns
        X_full = df_full[feature_cols]

        lr_pred_full = lr_model.predict(X_full)
        rf_pred_full = rf_model.predict(X_full)

        full_predictions_df = pd.DataFrame({
            "Timestamp": ts_full,
            "Actual Demand (MW)": df_full["load"].values,
            "Predicted LR": lr_pred_full,
            "Predicted RF": rf_pred_full
        })

        full_predictions_path = f"{RESULTS_DIR}/full_predictions.json"
        full_predictions_df.to_json(full_predictions_path, orient="records")

        rel_logger.info(f"Full predictions saved to {full_predictions_path}")

        rel_logger.info(f"Dashboard predictions saved to {predictions_path}")

        # save results
        config = load_config()
        hashes = get_config_hashes(config)

        results = {
            "run_id": run_id,
            "hashes": hashes,
            "config_hash": hashes["rf"] + hashes["lr"],
            "config": {
                "linear_regression": config.get("linear_regression", {}),
                "random_forest": config.get("random_forest", {})
            },
            "baseline": {
                "mae": float(baseline_mae),
                "rmse": float(baseline_rmse),
                "r2": float(baseline_r2)
            },
            "linear_regression": {
                "mae": float(lr_mae),
                "rmse": float(lr_rmse),
                "r2": float(lr_r2)
            },
            "random_forest": {
                "mae": float(rf_mae),
                "rmse": float(rf_rmse),
                "r2": float(rf_r2)
            },
            "improvement_vs_baseline": {
                "lr": float(baseline_mae - lr_mae),
                "rf": float(baseline_mae - rf_mae)
            },
            "residual_analysis": residual_analysis,
            "overfitting_analysis": overfitting_analysis,
            "feature_importance": feature_importance
        }

        results_path = f"{RESULTS_DIR}/results_{run_id}.json"

        with open(results_path, "w") as f:
            json.dump(results, f, indent=4)

        rel_logger.info("Results saved successfully.")

        # save experiment summary
        experiment = {
            "run_id": run_id,
            "config_hash": hashes,
            "timestamp": datetime.now().isoformat(),
            "baseline_mae": float(baseline_mae),
            "lr_mae": float(lr_mae),
            "rf_mae": float(rf_mae),
            "best_model": "random_forest" if rf_mae < lr_mae else "linear_regression"
        }

        experiments = load_experiments()
        experiments.append(experiment)
        save_experiments(experiments)

        # total
        log_time(start_total, "TOTAL EVALUATION PIPELINE")

        print("\n--- FINAL CONCLUSION ---")

        if min(lr_mae, rf_mae) < baseline_mae:
            print("At least one model beats baseline")
        else:
            print("No model beats baseline")

        rel_logger.info("Evaluation pipeline completed successfully.")

    except Exception as e:
        rel_logger.error(f"Evaluation pipeline failed: {e}")
        raise


if __name__ == "__main__":
    evaluate_models()
