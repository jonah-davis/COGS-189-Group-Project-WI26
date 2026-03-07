# ds005876 Song Familiarity — Visuals

All figures are generated from the OpenNeuro dataset in `../ds005876/`.

## Generated files

| File | Description |
|------|-------------|
| **01_demographics_age** | Participant age distribution (histogram). |
| **02_demographics_sex_handedness** | Counts by sex and handedness. |
| **03_response_rate_by_subject** | % of trials where participant indicated familiarity, per subject. |
| **04_rt_distribution** | Response time (s) when they pressed “familiar,” across all trials. |
| **05_mc_accuracy_by_subject** | % correct on multiple-choice song ID, per subject. |
| **06_song_duration_vs_responded** | Song duration (s) by whether they responded (Yes/No). |
| **07_dataset_overview** | 2×2 summary: age, response rate, MC accuracy, RT distribution. |

Each plot is saved as `.png` (150 dpi) and `.pdf`.

## Regenerating

From the project root:

```bash
pip install -r visuals/requirements.txt
python visuals/generate_visuals.py
```
