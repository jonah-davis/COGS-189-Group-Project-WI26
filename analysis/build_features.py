"""
Build trial-level features for ds005876 Song Familiarity.
Merges behavioral data, participant demographics, and event-derived features
(note count / note rate per trial from EEG events).
Output: analysis/trial_features.csv for modeling.
"""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DS_DIR = ROOT / "ds005876"
OUT_DIR = Path(__file__).resolve().parent


def load_participants() -> pd.DataFrame:
    """Load participants.tsv and parse datetime."""
    df = pd.read_csv(DS_DIR / "participants.tsv", sep="\t")
    df["datetime"] = pd.to_datetime(df["datetime"], format="%d-%b-%Y %H:%M:%S")
    return df


def load_all_behavioral() -> pd.DataFrame:
    """Load all subject behavioral TSVs and concatenate with participant_id."""
    frames = []
    for p in sorted(DS_DIR.glob("sub-*/beh/*_beh.tsv")):
        sub_id = p.parent.parent.name
        df = pd.read_csv(p, sep="\t")
        df["participant_id"] = sub_id
        frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def get_note_count_per_trial(events_path: Path) -> list[dict]:
    """
    From one subject's events.tsv, compute note count per trial.
    Trial boundaries: rows with value == 1 and non-null stim_file (trial start).
    Count noteOnset rows between consecutive trial starts.
    Returns list of {trial_index: 0-based, note_count, song_duration_approx} per trial.
    """
    df = pd.read_csv(events_path, sep="\t")
    # Trial starts: value 1 (or "1") and stim_file not n/a
    trial_starts = df[(df["value"].astype(str) == "1") & (df["stim_file"].astype(str) != "n/a")].copy()
    trial_starts = trial_starts.reset_index(drop=True)
    onsets = df["onset"].values
    values = df["value"].astype(str).values

    out = []
    for i in range(len(trial_starts)):
        start_onset = trial_starts.iloc[i]["onset"]
        if i + 1 < len(trial_starts):
            end_onset = trial_starts.iloc[i + 1]["onset"]
        else:
            end_onset = onsets[-1] + 1
        # Count noteOnset between start_onset and end_onset
        mask = (df["value"] == "noteOnset") & (df["onset"] >= start_onset) & (df["onset"] < end_onset)
        note_count = mask.sum()
        # Approximate song duration (until next trial) for note rate
        duration_sec = end_onset - start_onset
        out.append({"trial_index": i, "note_count": int(note_count), "trial_duration_sec": duration_sec})
    return out


def add_note_features_to_behavioral(beh: pd.DataFrame) -> pd.DataFrame:
    """
    For each subject, load events and add note_count and note_rate to each trial.
    Assumes beh has participant_id and trialNum (1-based); we match by order (trial_index = trialNum - 1).
    """
    beh = beh.copy()
    beh["note_count"] = np.nan
    beh["note_rate"] = np.nan  # notes per second

    for sub_id in beh["participant_id"].unique():
        events_path = DS_DIR / sub_id / "eeg" / f"{sub_id}_task-songfamiliarity_events.tsv"
        if not events_path.exists():
            continue
        trial_features = get_note_count_per_trial(events_path)
        sub_mask = beh["participant_id"] == sub_id
        sub_df = beh.loc[sub_mask].sort_values("trialNum").reset_index(drop=True)
        for i, tf in enumerate(trial_features):
            if i >= len(sub_df):
                break
            idx = sub_df.index[i]
            beh.loc[idx, "note_count"] = tf["note_count"]
            dur = tf["trial_duration_sec"]
            beh.loc[idx, "note_rate"] = tf["note_count"] / dur if dur > 0 else np.nan
    return beh


def safe_rt(series):
    """Coerce rt to numeric; 'n/a' and invalid become NaN."""
    return pd.to_numeric(series, errors="coerce")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    participants = load_participants()
    beh = load_all_behavioral()
    if beh.empty:
        raise SystemExit("No behavioral files found.")

    beh = add_note_features_to_behavioral(beh)
    beh["rt_numeric"] = safe_rt(beh["rt"])

    # Merge participant demographics
    merge_cols = ["participant_id", "age", "sex", "handedness"]
    trial_features = beh.merge(participants[merge_cols], on="participant_id", how="left")

    out_path = OUT_DIR / "trial_features.csv"
    trial_features.to_csv(out_path, index=False)
    print(f"Saved {len(trial_features)} rows to {out_path}")

    # Summary for modeling: only trials with a familiarity response
    responded = trial_features[trial_features["responded"] == 1].copy()
    responded = responded.dropna(subset=["rt_numeric"])
    print(f"Trials with valid RT (for regression): {len(responded)}")


if __name__ == "__main__":
    main()
