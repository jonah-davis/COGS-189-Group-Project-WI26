# ds005876 — Song Familiarity (OpenNeuro)

**Location:** `ds005876/` in your workspace  
**DOI:** [10.18112/openneuro.ds005876.v1.0.1](https://doi.org/10.18112/openneuro.ds005876.v1.0.1)  
**License:** CC0  
**BIDS version:** 1.8.0

---

## What this dataset is

**Song Familiarity** — EEG and behavioral data from 29 participants who listened to song melodies and responded when the song felt familiar, then identified the song (title/artist/lyrics) and chose from four titles with feedback.

- **Authors:** Jared R. Girard, Aaron M. Bishop, Cameron D. Hassall  
- **Stimuli:** From Kostic & Cleary (2009); see [supplement](https://supp.apa.org/psycarticles/supplemental/a0014584/a0014584_supp.html)  
- **Synchronized audio:** In `/derivatives` (reconstruction of what participants heard, aligned with EEG)

---

## How it’s organized

| Path | Contents |
|------|----------|
| **Root** | `dataset_description.json`, `participants.tsv`, `participants.json`, `README`, `task-songfamiliarity_events.json` |
| **sub-XX/** | One folder per participant (sub-01 … sub-30; sub-08 missing) |
| **sub-XX/beh/** | Behavioral data: `*_task-songfamiliarity_beh.json`, `*_task-songfamiliarity_beh.tsv` |
| **sub-XX/eeg/** | EEG data: `*_task-songfamiliarity_eeg.json`, `*_task-songfamiliarity_events.tsv` |
| **.datalad/** | DataLad config (for optional data retrieval) |

---

## Participants

- **Count:** 29 (participant IDs sub-01 through sub-30, excluding sub-08)  
- **Metadata:** `participants.tsv` — `participant_id`, `datetime`, `age`, `sex`, `handedness`, `cch`

---

## Quick file reference

| File type | Description |
|-----------|-------------|
| `dataset_description.json` | Dataset name, authors, BIDS version, DOI |
| `participants.tsv` | Demographics and session info |
| `*_beh.tsv` / `*_beh.json` | Trial-level behavioral responses |
| `*_eeg.json` | EEG recording metadata |
| `*_events.tsv` | Event timing for EEG (e.g. stimulus onsets) |
| `task-songfamiliarity_events.json` | Task/event definitions |

---

## Browse in Cursor

- **Dataset root:** [ds005876](ds005876/)
- **Description:** [dataset_description.json](ds005876/dataset_description.json)
- **Participants:** [participants.tsv](ds005876/participants.tsv)
- **Example subject:** [sub-01](ds005876/sub-01/) (beh + eeg)

The dataset is BIDS-compliant; use `participants.tsv` and the `sub-XX/` folders to loop over subjects and load EEG + behavioral data by subject and modality.
