"""
Extract EEG band-power features per trial from ds005876.
Requires: MNE-Python, and EEG data ( .set/.fdt ) available.
If data are in Git annex, run: git annex get ds005876/sub-*/eeg/*.set ds005876/sub-*/eeg/*.fdt
(or download from OpenNeuro).
Writes: analysis/eeg_features.csv (participant_id, trial_index, delta, theta, alpha, beta).
"""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DS_DIR = ROOT / "ds005876"
OUT_DIR = Path(__file__).resolve().parent

# Epoch: first 2 s of each trial (from song onset)
EPOCH_TMIN = 0.0
EPOCH_TMAX = 2.0
# Band power ranges (Hz)
BANDS = {"delta": (1, 4), "theta": (4, 8), "alpha": (8, 13), "beta": (13, 30)}


def get_trial_onset_times(events_path: Path) -> np.ndarray:
    """Return trial onset times in seconds (for trials with stim_file)."""
    df = pd.read_csv(events_path, sep="\t")
    trial_starts = df[
        (df["value"].astype(str) == "1") & (df["stim_file"].astype(str) != "n/a")
    ]
    return trial_starts["onset"].values.astype(float)


def extract_subject_eeg_features(sub_id: str) -> pd.DataFrame | None:
    """Load one subject's EEG, epoch around trial onsets, compute band power. Returns DataFrame or None on failure."""
    try:
        import mne
    except ImportError:
        print("MNE-Python not installed. pip install mne")
        return None

    set_path = DS_DIR / sub_id / "eeg" / f"{sub_id}_task-songfamiliarity_eeg.set"
    events_path = DS_DIR / sub_id / "eeg" / f"{sub_id}_task-songfamiliarity_events.tsv"
    if not set_path.exists() or not events_path.exists():
        return None
    # Resolve symlink; MNE needs a path that points to existing file
    set_resolved = set_path.resolve()
    if not set_resolved.exists():
        print(f"  {sub_id}: EEG data not on disk (annex/LFS?). Skipping.")
        return None

    onsets_sec = get_trial_onset_times(events_path)
    if len(onsets_sec) == 0:
        return None

    raw = mne.io.read_raw_eeglab(set_path, preload=True, verbose=False)
    sfreq = raw.info["sfreq"]
    # Build events array (sample, 0, event_id) for trial onsets
    events = np.column_stack([
        (onsets_sec * sfreq).astype(int),
        np.zeros(len(onsets_sec), dtype=int),
        np.ones(len(onsets_sec), dtype=int),
    ])
    epochs = mne.Epochs(
        raw,
        events,
        event_id=1,
        tmin=EPOCH_TMIN,
        tmax=EPOCH_TMAX,
        baseline=None,
        preload=True,
        verbose=False,
    )
    if len(epochs) == 0:
        return None

    # PSD per epoch (welch), then average power in bands
    spectrum = epochs.compute_psd(method="welch", fmin=1, fmax=40, verbose=False)
    psds, freqs = spectrum.get_data(return_freqs=True)

    rows = []
    for i in range(psds.shape[0]):
        # psds shape: (n_epochs, n_channels, n_freqs); average over channels
        p = psds[i].mean(axis=0)
        row = {"participant_id": sub_id, "trial_index": i}
        for band_name, (lo, hi) in BANDS.items():
            mask = (freqs >= lo) & (freqs < hi)
            row[band_name] = np.mean(p[mask])
        rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    subject_dirs = sorted(DS_DIR.glob("sub-*/eeg"))
    subject_ids = [d.parent.name for d in subject_dirs if d.parent.name != "sub-08"]

    all_dfs = []
    for sub_id in subject_ids:
        df = extract_subject_eeg_features(sub_id)
        if df is not None:
            all_dfs.append(df)
        else:
            pass  # skip silently or already printed

    if not all_dfs:
        print("No EEG data could be loaded. Ensure .set/.fdt are on disk (e.g. git annex get).")
        print("Writing empty eeg_features.csv so build_features still runs.")
        empty = pd.DataFrame(columns=["participant_id", "trial_index"] + list(BANDS.keys()))
        empty.to_csv(OUT_DIR / "eeg_features.csv", index=False)
        return

    eeg = pd.concat(all_dfs, ignore_index=True)
    out_path = OUT_DIR / "eeg_features.csv"
    eeg.to_csv(out_path, index=False)
    print(f"Saved EEG features for {eeg['participant_id'].nunique()} subjects, {len(eeg)} trials -> {out_path}")


if __name__ == "__main__":
    main()
