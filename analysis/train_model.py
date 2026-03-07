"""
Train a regression model to predict familiarity recognition time (rt_numeric)
from trial-level features. Reports metrics and feature importance for the paper.
"""
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import cross_val_predict, cross_validate, KFold
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parent
FEATURES_PATH = ROOT / "trial_features.csv"
OUT_DIR = ROOT


def load_modeling_data() -> tuple[pd.DataFrame, pd.Series]:
    """Load trial features and return X (features) and y (rt_numeric) for responded trials with valid RT."""
    df = pd.read_csv(FEATURES_PATH)
    df = df[(df["responded"] == 1)].dropna(subset=["rt_numeric"])
    y = df["rt_numeric"]
    return df, y


def get_feature_matrix(df: pd.DataFrame) -> tuple[pd.DataFrame, list]:
    """
    Build feature matrix. Numeric: songDur, note_count, note_rate, age, and EEG bands if present.
    Categorical: sex, handedness.
    """
    base_numeric = ["songDur", "note_count", "note_rate", "age"]
    eeg_bands = [c for c in ("delta", "theta", "alpha", "beta") if c in df.columns]
    numeric_cols = base_numeric + eeg_bands
    cat_cols = ["sex", "handedness"]
    for c in base_numeric:
        if c not in df.columns:
            raise ValueError(f"Missing column: {c}")
    X_num = df[numeric_cols].copy()
    X_num = X_num.fillna(X_num.median())
    X_cat = df[cat_cols].astype(str).fillna("missing")
    X = X_num.copy()
    for col in cat_cols:
        dummies = pd.get_dummies(X_cat[col], prefix=col, drop_first=True)
        X = pd.concat([X, dummies], axis=1)
    return X, list(X.columns)


def main() -> None:
    df, y = load_modeling_data()
    X, feature_names = get_feature_matrix(df)
    n_samples = len(X)
    print(f"Training on {n_samples} trials (responded with valid RT).")
    print(f"Features: {feature_names}")

    # Scale numeric features for Ridge; RF is scale-invariant
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled = pd.DataFrame(X_scaled, columns=feature_names, index=X.index)

    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    results = {}

    # Ridge regression
    ridge = Ridge(alpha=1.0, random_state=42)
    ridge_scores = cross_validate(ridge, X_scaled, y, cv=cv, scoring=("neg_mean_absolute_error", "r2"))
    results["Ridge"] = {
        "MAE": -ridge_scores["test_neg_mean_absolute_error"].mean(),
        "MAE_std": ridge_scores["test_neg_mean_absolute_error"].std(),
        "R2": ridge_scores["test_r2"].mean(),
        "R2_std": ridge_scores["test_r2"].std(),
    }
    ridge.fit(X_scaled, y)
    coef = pd.Series(ridge.coef_, index=feature_names).iloc[np.argsort(np.abs(ridge.coef_))[::-1]]
    results["Ridge_coef"] = coef

    # Random Forest (feature importance)
    rf = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    rf_scores = cross_validate(rf, X, y, cv=cv, scoring=("neg_mean_absolute_error", "r2"))
    results["RF"] = {
        "MAE": -rf_scores["test_neg_mean_absolute_error"].mean(),
        "MAE_std": rf_scores["test_neg_mean_absolute_error"].std(),
        "R2": rf_scores["test_r2"].mean(),
        "R2_std": rf_scores["test_r2"].std(),
    }
    rf.fit(X, y)
    imp = pd.Series(rf.feature_importances_, index=feature_names).sort_values(ascending=False)
    results["RF_importance"] = imp

    # Print and save summary
    summary_lines = [
        "Model performance (5-fold CV)",
        "-----------------------------",
        f"Ridge:  MAE = {results['Ridge']['MAE']:.3f} ± {results['Ridge']['MAE_std']:.3f} s,  R² = {results['Ridge']['R2']:.4f} ± {results['Ridge']['R2_std']:.4f}",
        f"RF:     MAE = {results['RF']['MAE']:.3f} ± {results['RF']['MAE_std']:.3f} s,  R² = {results['RF']['R2']:.4f} ± {results['RF']['R2_std']:.4f}",
        "",
        "Ridge coefficients (standardized predictors):",
    ]
    for name, val in results["Ridge_coef"].items():
        summary_lines.append(f"  {name}: {val:.4f}")
    summary_lines.extend(["", "Random Forest feature importance:", ""])
    for name, val in results["RF_importance"].items():
        summary_lines.append(f"  {name}: {val:.4f}")

    summary_text = "\n".join(summary_lines)
    print(summary_text)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "model_results.txt").write_text(summary_text)

    # Save coefficients and importance for paper
    results["Ridge_coef"].to_csv(OUT_DIR / "ridge_coefficients.csv")
    results["RF_importance"].to_csv(OUT_DIR / "rf_feature_importance.csv")
    print(f"\nResults saved to {OUT_DIR}")


if __name__ == "__main__":
    main()
