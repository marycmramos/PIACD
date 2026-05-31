import pytest
import pandas as pd
import numpy as np

from src.features.feature_engineering import create_features


@pytest.fixture
def sample_data():
    dates = pd.date_range(start="2025-01-01 00:00:00", periods=200, freq="h")
    
    df = pd.DataFrame({
        "timestamp": dates,
        "load": np.random.uniform(5000, 8000, 200),
        "temperature": np.random.uniform(-5, 35, 200),
        "temp_max": np.random.uniform(10, 40, 200),
        "temp_min": np.random.uniform(-10, 10, 200)
    })
    return df


def test_create_features_temporal(sample_data):
    df_out = create_features(sample_data.copy())

    assert "hour" in df_out.columns
    assert "day_of_week" in df_out.columns
    assert "is_weekend" in df_out.columns
    assert "hour_sin" in df_out.columns

    assert df_out.loc[0, "day_of_week"] == 2
    assert df_out.loc[0, "is_weekend"] == 0 


def test_create_features_lags(sample_data):
    df_out = create_features(sample_data.copy())

    assert pd.isna(df_out.loc[0, "lag_1h"])
    
    assert df_out.loc[1, "lag_1h"] == sample_data.loc[0, "load"]

    assert pd.isna(df_out.loc[167, "lag_168h"])
    assert df_out.loc[168, "lag_168h"] == sample_data.loc[0, "load"]


def test_create_features_climate(sample_data):
    df_test = sample_data.copy()
    
    df_test.loc[0, "temperature"] = 35  
    df_test.loc[1, "temperature"] = 2  
    
    df_test.loc[0, "timestamp"] = pd.Timestamp("2025-01-01 12:00:00")

    df_out = create_features(df_test)

    assert df_out.loc[0, "heatwave"] == 1
    assert df_out.loc[0, "cold"] == 0
    assert df_out.loc[1, "heatwave"] == 0
    assert df_out.loc[1, "cold"] == 1

    expected_range = df_test.loc[0, "temp_max"] - df_test.loc[0, "temp_min"]
    assert df_out.loc[0, "temp_range"] == expected_range
    
    assert df_out.loc[0, "is_day"] == 1


def test_create_features_missing_columns(sample_data):
    df_incomplete = sample_data.drop(columns=["temperature"])

    with pytest.raises(KeyError):
        create_features(df_incomplete)
