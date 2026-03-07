# Analysis — Song Familiarity Recognition Time

This folder contains the data pipeline and predictive modeling for the COGS 189 song familiarity project.

## Steps

0. **Optional — EEG band-power features:** If raw EEG (`.set`/`.fdt`) are on disk (e.g. after `git annex get` in a DataLad clone, or download from [OpenNeuro ds005876](https://openneuro.org/datasets/ds005876)):
   ```bash
   python analysis/extract_eeg_features.py
   ```
   Writes `eeg_features.csv` (delta, theta, alpha, beta per trial). If data are missing, writes an empty file and the pipeline continues without EEG.

1. **Build trial-level features** (behavioral + event-derived + EEG when available):
   ```bash
   python analysis/build_features.py
   ```
   Reads from `../ds005876/`, merges `eeg_features.csv` if present, writes `trial_features.csv`.

2. **Train models and report CV metrics**:
   ```bash
   pip install -r analysis/requirements.txt
   python analysis/train_model.py
   ```
   Produces `model_results.txt`, `ridge_coefficients.csv`, `rf_feature_importance.csv`.

## Outputs

| File | Description |
|------|-------------|
| `eeg_features.csv` | (Optional) participant_id, trial_index, delta, theta, alpha, beta. |
| `trial_features.csv` | One row per trial: beh + note_count, note_rate, demographics; + EEG bands if available. |
| `model_results.txt` | 5-fold CV MAE and R² for Ridge and RF; coefficients and importance. |
| `ridge_coefficients.csv` | Standardized Ridge coefficients. |
| `rf_feature_importance.csv` | Random Forest feature importances. |

## Predictors

- **songDur** — Song duration (s)  
- **note_count** — Number of note onsets in the trial (from events)  
- **note_rate** — note_count / trial duration (notes/s)  
- **age**, **sex**, **handedness** — Participant demographics  
- **delta**, **theta**, **alpha**, **beta** — (When EEG on disk) Mean band power in first 2 s of trial (1–4, 4–8, 8–13, 13–30 Hz).  

Target: **rt_numeric** (familiarity response time in seconds), only for trials where the participant responded.
