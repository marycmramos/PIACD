import pandas as pd
import numpy as np
import logging
from pathlib import Path

Path("logs").mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/reliability.log"),
        logging.StreamHandler()
    ]
)


def create_features(df):
    df = df.copy()

    required_cols = ["timestamp", "load", "temperature", "temp_max", "temp_min"]
    for col in required_cols:
        if col not in df.columns:
            raise KeyError(f"Missing required column: {col}")

    try:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # features temporais
        df["hour"] = df["timestamp"].dt.hour
        df["day_of_week"] = df["timestamp"].dt.dayofweek
        df["month"] = df["timestamp"].dt.month

        df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)

        # features cíclicas
        df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
        df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)

        df["dow_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7)
        df["dow_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7)

        # lags
        df["lag_1h"] = df["load"].shift(1)
        df["lag_24h"] = df["load"].shift(24)
        df["lag_168h"] = df["load"].shift(168)

        # rolling features
        df["rolling_load_24h"] = df["load"].rolling(24, min_periods=1).mean()
        df["rolling_temp_24h"] = df["temperature"].rolling(24, min_periods=1).mean()

        # features climáticas
        df["temp_range"] = df["temp_max"] - df["temp_min"]

        df["heatwave"] = (df["temperature"] > 30).astype(int)
        df["cold"] = (df["temperature"] < 5).astype(int)

        df["temp_anomaly"] = df["temperature"] - df["temperature"].rolling(168, min_periods=1).mean()

        df["is_day"] = df["hour"].between(7, 19).astype(int)

        df["load_diff"] = df["load"] - df["lag_1h"]

        # interação
        df["temp_x_hour"] = df["temperature"] * df["hour"]

        logging.info("Feature engineering completed successfully")

    except Exception as e:
        logging.error(f"Erro ao criar features: {e}")
        raise

    return df
