# Analysis — Song Familiarity Recognition Time

This folder contains the data pipeline and predictive modeling for the COGS 189 song familiarity project.

## Steps

1. **Build trial-level features** (behavioral + event-derived note count/rate):
   ```bash
   python analysis/build_features.py
   ```
   Reads from `../ds005876/`, writes `trial_features.csv`.

2. **Train models and report CV metrics**:
   ```bash
   pip install -r analysis/requirements.txt
   python analysis/train_model.py
   ```
   Produces `model_results.txt`, `ridge_coefficients.csv`, `rf_feature_importance.csv`.

## Outputs

| File | Description |
|------|-------------|
| `trial_features.csv` | One row per trial: beh + note_count, note_rate, demographics. |
| `model_results.txt` | 5-fold CV MAE and R² for Ridge and RF; coefficients and importance. |
| `ridge_coefficients.csv` | Standardized Ridge coefficients. |
| `rf_feature_importance.csv` | Random Forest feature importances. |

## Predictors

- **songDur** — Song duration (s)  
- **note_count** — Number of note onsets in the trial (from events)  
- **note_rate** — note_count / trial duration (notes/s)  
- **age**, **sex**, **handedness** — Participant demographics  

Target: **rt_numeric** (familiarity response time in seconds), only for trials where the participant responded.
