import pandas as pd
import numpy as np
import joblib
import json
import os
import logging
import time
from datetime import datetime

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

BEST_PARAMS_PATH = "data/models/best_params.json"

rel_logger = logging.getLogger("reliability")
perf_logger = logging.getLogger("performance")


def grid_search_already_done():
    return os.path.exists(BEST_PARAMS_PATH)


def run_grid_search():
    if grid_search_already_done():
        print("[GRID SEARCH] Resultados já existem. A carregar...")
        rel_logger.info("Grid search já foi feito. A carregar resultados existentes.")
        return load_best_params()

    print("[GRID SEARCH] A iniciar...")
    rel_logger.info("A iniciar grid search...")
    start_total = time.time()

    # Carregar dados
    print("[GRID SEARCH] A carregar dados...")
    df = pd.read_csv("data/processed/features.csv")
    df = df.iloc[168:].reset_index(drop=True)
    print(f"[GRID SEARCH] Dataset carregado: {len(df)} linhas, {df.shape[1]} colunas")

    X = df.drop(columns=["load"])
    y = df["load"]
    X = X.select_dtypes(include=["number"])
    X = X.drop(columns=["load_diff"], errors="ignore")
    print(f"[GRID SEARCH] Features shape: {X.shape}")

    tscv = TimeSeriesSplit(n_splits=5)

    # Linear Regression
    print("[GRID SEARCH] A correr grid search para Linear Regression...")
    lr_param_grid = {
        "fit_intercept": [True, False],
        "positive": [True, False]
    }

    lr_gs = GridSearchCV(
        LinearRegression(),
        lr_param_grid,
        cv=tscv,
        scoring="neg_mean_absolute_error",
        n_jobs=-1
    )
    lr_gs.fit(X, y)
    print(f"[GRID SEARCH] LR concluído. Melhores params: {lr_gs.best_params_}")

    # Random Forest
    print("[GRID SEARCH] A correr grid search para Random Forest (pode demorar)...")
    rf_param_grid = {
        "n_estimators": [50, 100, 200, 300],
        "max_depth": [5, 10, 15, 20],
        "min_samples_split": [2, 5, 10],
        "min_samples_leaf": [1, 2, 4]
    }

    rf_gs = GridSearchCV(
        RandomForestRegressor(random_state=42, n_jobs=-1),
        rf_param_grid,
        cv=tscv,
        scoring="neg_mean_absolute_error",
        n_jobs=-1
    )
    rf_gs.fit(X, y)
    print(f"[GRID SEARCH] RF concluído. Melhores params: {rf_gs.best_params_}")

    # Avaliar no test set
    print("[GRID SEARCH] A avaliar modelos no test set...")
    split_idx = int(len(X) * 0.8)
    X_test = X.iloc[split_idx:]
    y_test = y.iloc[split_idx:]

    lr_pred = lr_gs.best_estimator_.predict(X_test)
    rf_pred = rf_gs.best_estimator_.predict(X_test)

    lr_mae = mean_absolute_error(y_test, lr_pred)
    rf_mae = mean_absolute_error(y_test, rf_pred)
    print(f"[GRID SEARCH] LR MAE: {lr_mae:.4f} | RF MAE: {rf_mae:.4f}")

    best_model = "random_forest" if rf_mae < lr_mae else "linear_regression"
    print(f"[GRID SEARCH] Melhor modelo: {best_model}")

    elapsed = time.time() - start_total
    print(f"[GRID SEARCH] Tempo total: {elapsed:.2f}s")
    perf_logger.info(f"Grid search completed in {elapsed:.2f}s")

    # Guardar resultados
    print("[GRID SEARCH] A guardar resultados...")
    best_params = {
        "timestamp": datetime.now().isoformat(),
        "best_model": best_model,
        "linear_regression": {
            "params": lr_gs.best_params_,
            "mae": float(lr_mae),
            "rmse": float(np.sqrt(mean_squared_error(y_test, lr_pred))),
            "r2": float(r2_score(y_test, lr_pred))
        },
        "random_forest": {
            "params": rf_gs.best_params_,
            "mae": float(rf_mae),
            "rmse": float(np.sqrt(mean_squared_error(y_test, rf_pred))),
            "r2": float(r2_score(y_test, rf_pred))
        }
    }

    os.makedirs("data/models", exist_ok=True)
    with open(BEST_PARAMS_PATH, "w") as f:
        json.dump(best_params, f, indent=4)
    print(f"[GRID SEARCH] Resultados guardados em {BEST_PARAMS_PATH}")

    joblib.dump(lr_gs.best_estimator_, "data/models/lr_model.pkl")
    joblib.dump(rf_gs.best_estimator_, "data/models/rf_model.pkl")
    print("[GRID SEARCH] Modelos guardados.")

    rel_logger.info(f"Grid search concluído. Melhor modelo: {best_model}")

    return best_params


def load_best_params():
    with open(BEST_PARAMS_PATH, "r") as f:
        return json.load(f)


if __name__ == "__main__":
    results = run_grid_search()
    print(json.dumps(results, indent=4))
