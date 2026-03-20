# Dataset Placeholder

The OpenNeuro Song Familiarity dataset (`ds005876`) is intentionally not committed in this branch.

To reproduce the notebook analyses, place the dataset at this path:

```bash
COGS-189-Group-Project-WI26/ds005876/
```

## Recommended Retrieval Path

Use the public OpenNeuro dataset mirror and fetch the annexed EEG files:

```bash
git clone https://github.com/OpenNeuroDatasets/ds005876.git /tmp/ds005876-openneuro
cd /tmp/ds005876-openneuro
git annex get sub-*/eeg/*.set sub-*/eeg/*.fdt
```

Then copy the dataset into this repository as `ds005876/`.

## Alternative

Download the dataset directly from OpenNeuro:

- https://openneuro.org/datasets/ds005876/versions/1.0.1

## Notes

- The notebooks expect the folder name `ds005876`.
- The EEG modeling notebooks require the raw `.set` and `.fdt` files to be present locally.
- The CSP/LDA notebook depends on outputs written by `song_familiarity_analysis_ready.ipynb`.
