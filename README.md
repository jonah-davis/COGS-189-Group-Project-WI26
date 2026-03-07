# COGS 189 — Song Familiarity Recognition Time (WI26)

Predicting **how quickly listeners recognize a familiar song** using the OpenNeuro Song Familiarity dataset (ds005876). We use behavioral data and event-derived features (note density) to model recognition time; the report discusses limitations and extensions (e.g., EEG and spectral features).

## Team

- **Jonah Davis** — Data analysis, technical writing, literature review  
- **Audrey La Guardia** — Analysis, data cleaning, visualization  
- **Suraj Bendi** — Dataset structure, file organization, experiment event labels  
- **Roselyn Gonzalez** — Feature extraction  

## Repository layout

| Path | Contents |
|------|----------|
| **ds005876/** | OpenNeuro dataset (BIDS): participants, `sub-XX/beh/`, `sub-XX/eeg/` (events + metadata). See `ds005876/DATASET_INDEX.md`. |
| **visuals/** | Scripts to generate demographics, RT, accuracy, and overview figures. Run: `pip install -r visuals/requirements.txt && python visuals/generate_visuals.py` |
| **analysis/** | Feature building and regression. Run `build_features.py` then `train_model.py`. See `analysis/README.md`. |
| **paper/** | Final written report: `paper/paper.md` (Introduction, Related work, Methods, Results, Discussion). |

## Quick start

```bash
# Visualizations (figures in visuals/)
pip install -r visuals/requirements.txt
python visuals/generate_visuals.py

# Analysis (features + model)
pip install -r analysis/requirements.txt
python analysis/build_features.py
python analysis/train_model.py
```

## Dataset

- **OpenNeuro:** [ds005876](https://openneuro.org/datasets/ds005876/versions/1.0.1) — Song Familiarity (EEG + behavior).  
- **Stimuli:** Melodies from Kostic & Cleary (2009); participants pressed a key when the song felt familiar, then identified it.

## License

Dataset: CC0 (see OpenNeuro). Project code: use per your course and group agreement.
