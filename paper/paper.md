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
- Input: `ds005876/` (BIDS layout). EEG data (`.set`/`.fdt`) must be retrieved (e.g., `git annex get` in a DataLad clone, or download from OpenNeuro) for EEG features to be included.  
- Output: `analysis/eeg_features.csv` (if EEG run), `analysis/trial_features.csv`, `analysis/model_results.txt`, and coefficient/importance tables.

---

## 4. Results

### 4.1 Data Summary

Across all participants we obtained **2,074** total trials in the merged behavioral table. Of these, **1,030** trials contained a familiarity response with a valid numeric reaction time, meaning that roughly half of the melodies prompted listeners to indicate that the song felt familiar. This proportion seems reasonable for a mix of well-known and less familiar tunes: some clips are recognized quickly, others never quite cross the familiarity threshold within the time window.

Descriptive plots (generated by the scripts in `visuals/`) show that the age distribution is fairly typical for an undergraduate sample, and that no single participant overwhelmingly dominates the trial count. Reaction times have the expected long right tail, with many responses clustered in the first several seconds and a smaller number of very late keypresses. Together, these patterns suggest that the dataset is reasonably well-behaved and suitable for modeling.

### 4.2 Predictive Performance (5-fold CV)

We evaluated both regression models using 5-fold cross-validation on the 1,030 responded trials:

| Model | MAE (s) | R² |
|-------|---------|-----|
| Ridge | 1.639 ± 0.099 | 0.114 ± 0.043 |
| Random Forest | 1.549 ± 0.100 | 0.197 ± 0.089 |

In absolute terms, both models produced prediction errors of roughly **1.6 seconds** (MAE = 1.639 s for Ridge, 1.549 s for Random Forest). This is not trivial relative to typical reaction times in the task, but it seems plausible given that the models only see a small set of behavioral and event-derived features. The **Random Forest** achieved consistently lower MAE and higher R² than Ridge, suggesting that it is able to capture some nonlinear structure in the data that the linear model misses.

At the same time, the **R² values are modest** (about 0.11 for Ridge and 0.20 for Random Forest, with noticeable variability across folds). This pattern indicates that the current feature set explains only a relatively small portion of the variability in recognition time. That outcome is not too surprising: we do not yet include EEG signals, detailed properties of the audio stimuli, or explicit song identity, all of which likely carry additional information about when a melody will “click” for a listener.

### 4.3 Feature Importance and Coefficients

Inspection of the fitted models reveals a consistent picture about which predictors matter most.

In the **Ridge** model (with standardized predictors), **song duration** has the largest positive coefficient. Longer clips are associated with longer reaction times, which makes intuitive sense because listeners may need to hear more of a melody before recognizing it, especially for tunes that are not instantly obvious. **Age** shows a negative coefficient, suggesting that older participants in this sample tended to recognize melodies slightly faster than younger ones. One possible explanation is that older participants may simply be more familiar with a larger portion of the stimulus set, although we cannot confirm that directly here.

The two note-based measures contribute more subtle effects. **Note rate** (notes per second) has a small positive weight, whereas **note count** has a small negative weight. This combination appears to suggest that denser melodies may slightly delay recognition, perhaps because there is more information to process in a short time window, but that the total number of notes within a trial is less important once duration is taken into account. Dummy variables for **sex** and **handedness** have comparatively small coefficients, implying that they play only a minor role in predicting RT in this dataset.

The **Random Forest** feature importance scores tell a very similar story. **Song duration** accounts for the majority of the importance (around 0.60), followed by **age** (around 0.28), while all other predictors—note rate, note count, sex, and handedness—contribute only small additional amounts. This pattern reinforces the idea that, within the limited set of features we used, **how long the song has been playing** and **who is listening** are the primary drivers of recognition time, whereas our simple proxy for melodic density plays a secondary role.

### 4.4 What Worked and What Did Not

From a pipeline perspective, several pieces worked as intended. We were able to go from raw BIDS behavioral and event files to a clean trial-level table, attach interpretable features, and run cross-validated models whose performance and direction of effects pass basic sanity checks. We also implemented an EEG band-power extraction step (using MNE-Python to compute delta, theta, alpha, and beta power in the first 2 seconds of each trial) that integrates cleanly into the same feature table when the underlying `.set`/`.fdt` files are available.

However, the specific results reported in this section use only behavioral and event-derived predictors. In our working copy of the dataset, the large EEG files are stored in git-annex and were not fully retrieved, so `extract_eeg_features.py` produced an empty EEG feature table. As a result, we cannot yet say whether adding neural measures would meaningfully improve prediction over the behavioral features alone. We also did not incorporate any stimulus-level spectral information from the audio (for example, tempo or spectral centroid), which likely captures additional aspects of how easy or hard a melody is to recognize.

Taken together, the results suggest that a simple behavioral model can recover sensible effects of song duration and participant age, but that a large portion of the variance in recognition time remains unexplained. This gap likely reflects both unmeasured stimulus properties and individual differences, and it points toward EEG and richer audio features as promising next steps rather than as guarantees of success.

---

## 5. Discussion

### 5.1 Interpretation

- **Song duration** strongly predicted RT: the longer the clip, the longer participants tended to take to press the key. This could reflect both more time needed to recognize less salient melodies and the fact that RT is bounded by how long the clip has been playing.  
- **Age** was associated with shorter RTs in our model, which could reflect cohort familiarity with the stimulus set or other individual differences; the direction should be interpreted cautiously given the sample size and design.  
- **Note rate** (notes per second) had a small positive association with RT in Ridge, suggesting that denser melodies might slightly delay recognition in this task, though the effect was modest compared to duration and age.

### 5.2 Strengths and Limitations

- **Strengths:** Clear question (predictors of recognition time); use of a public, BIDS-formatted dataset; transparent data and code pipeline; cross-validated evaluation; discussion of what was and was not possible with the available data.  
- **Limitations:** No raw EEG or spectral features in the reported results; no song-level familiarity or genre in the model; modest R²; possible confounds (e.g., trial order, stimulus set composition).

### 5.3 Extensions and Future Work

1. **Expand EEG features.** We now include band power (delta, theta, alpha, beta) from the first 2 s of each trial when EEG is available. Extensions could add ERP components (e.g., P300) in the pre-response window, or longer or variable-length epochs, to capture neural correlates of recognition more directly.  
2. **Song identity and familiarity strength.** Including song ID (or a subject-specific familiarity rating) could capture which melodies are recognized faster across participants. One could also model trial-level accuracy (e.g., multiple-choice outcome) as a secondary outcome or predictor.

---

## References

- Girard, J. R., Bishop, A. M., & Hassall, C. D. Song Familiarity dataset. OpenNeuro. https://openneuro.org/datasets/ds005876/versions/1.0.1  
- Kostic, B., & Cleary, A. M. (2009). Song recognition without identification: When people cannot “name that tune” but can recognize it as familiar. *Journal of Experimental Psychology: General*, with supplemental materials at https://supp.apa.org/psycarticles/supplemental/a0014584/a0014584_supp.html

---

*Code and feature tables are in the repository under `analysis/` and `visuals/`.*
