# modules/ml_model.py
# ============================================================
# ML MODEL TRAINING MODULE
# Trains a Linear Regression model on the student performance
# dataset to predict Final_Score.
# ============================================================

import os
import pickle
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score

# Paths
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH  = os.path.join(BASE_DIR, 'data', 'student_performance.csv')
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'lr_model.pkl')
SCALER_PATH= os.path.join(BASE_DIR, 'models', 'scaler.pkl')

FEATURE_COLS = ['Study_Hours', 'Attendance', 'Previous_Marks', 'Assignment_Score']
TARGET_COL   = 'Final_Score'


def train_model(force: bool = False) -> tuple[LinearRegression, StandardScaler, dict]:
    """
    Train (or reload) the Linear Regression model.

    Parameters
    ----------
    force : if True, retrain even if a saved model exists.

    Returns
    -------
    (model, scaler, metrics_dict)
    """
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    # Return cached model unless force-retrain requested
    if not force and os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
        return load_model()

    # ── Load dataset ─────────────────────────────────────────
    df = pd.read_csv(DATA_PATH)
    X  = df[FEATURE_COLS].values
    y  = df[TARGET_COL].values

    # ── Train / test split ───────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # ── Feature scaling ──────────────────────────────────────
    scaler  = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test  = scaler.transform(X_test)

    # ── Train Linear Regression ──────────────────────────────
    model = LinearRegression()
    model.fit(X_train, y_train)

    # ── Evaluate ─────────────────────────────────────────────
    y_pred  = model.predict(X_test)
    mse     = mean_squared_error(y_test, y_pred)
    r2      = r2_score(y_test, y_pred)
    metrics = {
        'mse':  round(mse, 4),
        'rmse': round(np.sqrt(mse), 4),
        'r2':   round(r2, 4),
    }

    # ── Save artefacts ───────────────────────────────────────
    with open(MODEL_PATH,  'wb') as f: pickle.dump(model,  f)
    with open(SCALER_PATH, 'wb') as f: pickle.dump(scaler, f)

    return model, scaler, metrics


def load_model() -> tuple[LinearRegression, StandardScaler, dict]:
    """Load a previously saved model and scaler from disk."""
    with open(MODEL_PATH,  'rb') as f: model  = pickle.load(f)
    with open(SCALER_PATH, 'rb') as f: scaler = pickle.load(f)
    return model, scaler, {}


def get_feature_importance(model: LinearRegression) -> dict[str, float]:
    """Return a dict mapping feature names → regression coefficients."""
    return {col: round(coef, 4)
            for col, coef in zip(FEATURE_COLS, model.coef_)}
