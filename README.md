# Neural Signatures of Song Familiarity: An EEG Decoding Study

The central question of this study was whether trial-level EEG recorded during song listening could predict whether a participant would judge a song as familiar. More specifically, we  are interested not only in whether familiarity could be classified within the dataset, but whether any familiarity-related signal would generalize across participants under participant-aware validation. To address this, we combined a descriptive analysis of the OpenNeuro \texttt{ds005876} dataset with an EEG-only decoding pipeline based on CSP and LDA.

## Team

- Jonah Davis
- Audrey La Guardia
- Suraj Bendi
- Roselyn Gonzalez

## Notebook Workflow

Run the notebooks in this order:

1. [`song_familiarity_dataset_eda.ipynb`](/Users/jonahdavis/COGS-189-Group-Project-WI26/notebooks/song_familiarity_dataset_eda.ipynb)
2. [`song_familiarity_analysis_ready.ipynb`](/Users/jonahdavis/COGS-189-Group-Project-WI26/notebooks/song_familiarity_analysis_ready.ipynb)
3. [`csp_lda_familiarity_modellability.ipynb`](/Users/jonahdavis/COGS-189-Group-Project-WI26/notebooks/csp_lda_familiarity_modellability.ipynb)

## Repository Layout

| Path | Purpose |
|------|---------|
| [`notebooks/`](/Users/jonahdavis/COGS-189-Group-Project-WI26/notebooks) | Primary project analysis notebooks. |
| [`analysis/`](/Users/jonahdavis/COGS-189-Group-Project-WI26/analysis) | Notebook-produced tables, model outputs, and the standalone plot exporter. |
| [`visuals/analysis_ready/`](/Users/jonahdavis/COGS-189-Group-Project-WI26/visuals/analysis_ready) | Combined figures written by the notebooks. |
| [`visuals/figures/notebook_plots/`](/Users/jonahdavis/COGS-189-Group-Project-WI26/visuals/figures/notebook_plots) | One-plot-per-file exports reproduced from notebook analyses. |
| [`archive/legacy_analysis_pipeline/`](/Users/jonahdavis/COGS-189-Group-Project-WI26/archive/legacy_analysis_pipeline) | Older non-notebook analysis pipeline files kept for reference but no longer part of the main workflow. |
| [`paper/`](/Users/jonahdavis/COGS-189-Group-Project-WI26/paper) | Report draft and supporting writeup. |
| [`ds005876/`](/Users/jonahdavis/COGS-189-Group-Project-WI26/ds005876) | Placeholder directory with instructions for retrieving the dataset locally. |

## Data Setup

The dataset is not committed in this branch. To replicate the notebook analysis, retrieve OpenNeuro `ds005876` into the repo as `ds005876/`. See [`ds005876/README.md`](/Users/jonahdavis/COGS-189-Group-Project-WI26/ds005876/README.md) for concrete download options.

## Source Dataset

- OpenNeuro: [ds005876](https://openneuro.org/datasets/ds005876/versions/1.0.1)

## License

Dataset licensing is defined by OpenNeuro. Project code and writing remain subject to the team’s course and collaboration expectations.
