# Predicting Song Familiarity Recognition Time from Behavioral and Stimulus-Derived Features

**COGS 189 Final Project — Winter 2026**  
**Team:** Jonah Davis, Audrey La Guardia, Suraj Bendi, Roselyn Gonzalez

---

## 1. Introduction and Motivation

Recognizing a familiar melody is a rapid, often automatic process. Understanding which factors shorten or lengthen the time until recognition can inform theories of memory retrieval and auditory cognition, and has practical relevance for interfaces and content design. In this project we asked: **What factors predict how quickly a listener will indicate that a song sounds familiar?**

We used the **Song Familiarity** EEG dataset (OpenNeuro ds005876), in which participants listened to melody clips and pressed a key when the song felt familiar, then identified the song. Our goal was to build a predictive model of **recognition time** (RT) from factors such as **song duration**, **stimulus-derived structure** (note-onset density from experiment events), **participant demographics**, and **EEG-derived band power** (delta, theta, alpha, beta) from the first 2 s of each trial when raw EEG data are available.

---

## 2. Related Work

- **Tip-of-the-tongue and familiarity.** The song familiarity paradigm is related to tip-of-the-tongue states and familiarity judgments in long-term memory. Class readings on memory and retrieval are relevant to why some stimuli are recognized faster than others.

- **Kostic & Cleary (2009).** The stimuli in ds005876 are drawn from the melody set used by Kostic and Cleary (see the [supplement](https://supp.apa.org/psycarticles/supplemental/a0014584/a0014584_supp.html)), who studied familiarity and recall for well-known melodies. Their work supports the use of these melodies as a standardized set for familiarity and recognition.

- **EEG and music.** Recent work has used EEG to study neural correlates of music perception and familiarity (e.g., familiarity-related ERP components, neural entrainment to rhythm). Our project complements such work by focusing on *behavioral* predictors of recognition time; a natural extension would be to add EEG-derived features (e.g., band power, ERPs) as predictors.

- **OpenNeuro ds005876.** The dataset (Girard, Bishop, Hassall; BIDS 1.8.0) provides behavioral responses, event timing (including note onsets), and raw EEG (32 channels, 1000 Hz, EEGLAB format). Our pipeline uses behavioral and event data for all runs, and adds EEG band-power features when the raw .set/.fdt files are available (e.g., after downloading via DataLad or OpenNeuro).

---

## 3. Methods

### 3.1 Dataset and Variables

- **Source:** OpenNeuro ds005876, version 1.0.1 (Song Familiarity).  
- **Participants:** 29 individuals (sub-01 through sub-30, excluding sub-08).  
- **Design:** Each participant completed multiple trials. On each trial, a melody played; participants pressed the spacebar when the song felt familiar (familiarity RT), then identified the song (free recall and multiple choice).  
- **Outcome:** We predicted **familiarity response time (RT)** in seconds, using only trials where the participant responded (i.e., indicated familiarity). Non-responses were excluded from the regression.  
- **Behavioral variables:** From each subject’s `*_beh.tsv`: trial number, song identifier, song duration (`songDur`), whether they responded (`responded`), RT (`rt`), and demographics from `participants.tsv` (age, sex, handedness).  
- **Event-derived features:** From each subject’s `*_events.tsv` we identified trial boundaries (event value 1 with stimulus filename) and counted **note onsets** (`noteOnset`) within each trial. We defined **note count** and **note rate** (notes per second) as proxies for melodic density/tempo.  
- **EEG-derived features (optional):** When raw EEG (`.set`/`.fdt`) are on disk, we run `extract_eeg_features.py`: load continuous EEG with MNE-Python, epoch the first 2 s of each trial from song onset, compute power spectral density (Welch), and average power in four bands—**delta** (1–4 Hz), **theta** (4–8 Hz), **alpha** (8–13 Hz), **beta** (13–30 Hz)—averaged across channels. These are merged onto the trial table by participant and trial index.

### 3.2 Data Pipeline and Feature Construction

1. **Behavioral loading:** All `sub-*/beh/*_beh.tsv` files were concatenated with a participant ID.  
2. **Event processing:** For each participant, we parsed the corresponding `*_events.tsv`, segmented trials by trial-start events, and counted note onsets per trial. We merged these counts (and derived note rate) onto the behavioral table by participant and trial order.  
3. **EEG features (optional):** If `eeg_features.csv` exists (from `extract_eeg_features.py`), we merge delta, theta, alpha, and beta power onto the trial table.  
4. **Numeric RT:** The `rt` column contains `"n/a"` when the participant did not respond; we coerced it to numeric and dropped rows with missing RT for modeling.  
5. **Predictors:** Final feature set: **songDur**, **note_count**, **note_rate**, **age**, **sex**, **handedness**, and when available **delta**, **theta**, **alpha**, **beta**. Sex and handedness were one-hot encoded (reference categories: F, L).  
6. **Missing values:** Missing numeric features were filled with the median per column.

### 3.3 Models and Evaluation

- **Models:** We fit two regressors: **Ridge regression** (L2 penalty, alpha=1.0) and **Random Forest** (100 trees, max depth 10). For Ridge, predictors were standardized (zero mean, unit variance).  
- **Cross-validation:** 5-fold cross-validation (shuffle, random_state=42). We report mean and standard deviation of **mean absolute error (MAE)** in seconds and **R²** across folds.  
- **Interpretation:** For Ridge we report standardized coefficients; for Random Forest we report Gini importance of each feature.

### 3.4 Reproducibility

- Code: `analysis/extract_eeg_features.py` (EEG band power when data on disk), `analysis/build_features.py` (feature construction), `analysis/train_model.py` (training and CV).  
- Input: `ds005876/` (BIDS layout). EEG data (`.set`/`.fdt`) must be retrieved (e.g. `git annex get` in a DataLad clone, or download from OpenNeuro) for EEG features to be included.  
- Output: `analysis/eeg_features.csv` (if EEG run), `analysis/trial_features.csv`, `analysis/model_results.txt`, and coefficient/importance tables.

---

## 4. Results

### 4.1 Data Summary

- Total trials in the merged behavioral table: **2,074**.  
- Trials with a familiarity response and valid numeric RT used for regression: **1,030**.  
- Demographics and response rates are summarized in the project’s visualization scripts (e.g., demographics, response rate by subject, RT distribution).

### 4.2 Predictive Performance (5-fold CV)

| Model | MAE (s) | R² |
|-------|---------|-----|
| Ridge | 1.639 ± 0.099 | 0.114 ± 0.043 |
| Random Forest | 1.549 ± 0.100 | 0.197 ± 0.089 |

Random Forest achieved slightly better MAE and R² than Ridge, but both models explain a modest proportion of variance in recognition time (R² ≈ 0.11–0.20). This is expected given that we did not use raw EEG, spectral features, or song-level identity/familiarity strength.

### 4.3 Feature Importance and Coefficients

- **Ridge (standardized coefficients):** The strongest positive predictor of RT was **song duration** (longer songs associated with longer recognition times). **Age** had a negative coefficient (older participants tended to have shorter RTs in this sample). **Note rate** had a positive coefficient; **note count** a small negative one. **Handedness** and **sex** showed smaller effects.  
- **Random Forest importance:** **Song duration** had by far the highest importance (~0.60), followed by **age** (~0.28). Note rate, note count, sex, and handedness had much smaller importances.

So, in this dataset, **song length** and **participant age** were the main behavioral predictors of recognition time; **note rate** (our proxy for melodic density/tempo) had a modest role.

### 4.4 What Worked and What Did Not

- **Worked:** Building a reproducible pipeline from BIDS behavioral and event files; extracting note-onset-based features; implementing EEG band-power extraction (MNE-Python, 2 s epochs, delta/theta/alpha/beta) and integrating it into the feature table when raw EEG is available; training and cross-validating regression models; obtaining interpretable feature weights.  
- **Reported results:** The performance and feature importance reported above used only behavioral and event-derived predictors, because the EEG files in our working copy were not fully retrieved (Git annex). When EEG data are downloaded and `extract_eeg_features.py` is run, the same pipeline produces band-power features and the model uses them automatically.  
- **Limitations:** We did not use derivative audio for stimulus-level spectral features. Adding stimulus frequency content would require the dataset’s derivative audio or external spectral analysis.

---

## 5. Discussion

### 5.1 Interpretation

- **Song duration** strongly predicted RT: the longer the clip, the longer participants tended to take to press the key. This could reflect both more time needed to recognize less salient melodies and the fact that RT is bounded by how long the clip has been playing.  
- **Age** was associated with shorter RTs in our model, which could reflect cohort familiarity with the stimulus set or other individual differences; the direction should be interpreted cautiously given the sample size and design.  
- **Note rate** (notes per second) had a small positive association with RT in Ridge, suggesting that denser melodies might slightly delay recognition in this task, though the effect was modest compared to duration and age.

### 5.2 Strengths and Limitations

- **Strengths:** Clear question (predictors of recognition time); use of a public, BIDS-formatted dataset; transparent data and code pipeline; cross-validated evaluation; discussion of what was and was not possible with the available data.  
- **Limitations:** No raw EEG or spectral features; no song-level familiarity or genre in the model; modest R²; possible confounds (e.g., trial order, stimulus set composition).

### 5.3 Extensions and Future Work

1. **Expand EEG features.** We now include band power (delta, theta, alpha, beta) from the first 2 s of each trial when EEG is available. Extensions could add ERP components (e.g., P300) in the pre-response window, or longer or variable-length epochs, to capture neural correlates of recognition more directly.  
2. **Song identity and familiarity strength.** Including song ID (or a subject-specific familiarity rating) could capture which melodies are recognized faster across participants. One could also model trial-level accuracy (e.g., multiple-choice outcome) as a secondary outcome or predictor.

---

## References

- Girard, J. R., Bishop, A. M., & Hassall, C. D. Song Familiarity dataset. OpenNeuro. https://openneuro.org/datasets/ds005876/versions/1.0.1  
- Kostic, B., & Cleary, A. M. (2009). Song recognition without identification: When people cannot “name that tune” but can recognize it as familiar. *Journal of Experimental Psychology: General*, with supplemental materials at https://supp.apa.org/psycarticles/supplemental/a0014584/a0014584_supp.html

---

*Code and feature tables are in the repository under `analysis/` and `visuals/`.*
