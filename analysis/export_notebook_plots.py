from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import nbformat
import numpy as np
import pandas as pd
import seaborn as sns
from mne.viz import plot_topomap
from sklearn.metrics import ConfusionMatrixDisplay, RocCurveDisplay


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = ROOT / "notebooks"
OUTPUT_DIR = ROOT / "visuals" / "figures" / "notebook_plots"
PALETTE = ["#16324F", "#2A9D8F", "#E9C46A", "#E76F51", "#6D597A", "#264653"]


def slugify(value: str) -> str:
    return (
        "".join(ch.lower() if ch.isalnum() else "_" for ch in value).strip("_").replace("__", "_")
        or "plot"
    )


def save_figure(fig: Figure, output_path: Path) -> None:
    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def execute_notebook(notebook_name: str) -> dict:
    notebook_path = NOTEBOOK_DIR / notebook_name
    notebook = nbformat.read(notebook_path, as_version=4)
    namespace = {"__name__": "__main__"}

    original_show = plt.show
    original_savefig = Figure.savefig

    def patched_show(*args, **kwargs):
        plt.close("all")

    def patched_savefig(self, *args, **kwargs):
        return None

    plt.show = patched_show
    Figure.savefig = patched_savefig

    try:
        for cell in notebook.cells:
            if cell.cell_type != "code":
                continue
            source = cell.source.strip()
            if source:
                exec(compile(source, str(notebook_path), "exec"), namespace)
    finally:
        plt.show = original_show
        Figure.savefig = original_savefig
        plt.close("all")

    return namespace


def export_dataset_eda(namespace: dict, output_dir: Path) -> int:
    count = 0
    participants = namespace["participants"]
    behavior = namespace["behavior"]
    subject_level = namespace["subject_level"]
    frequent_songs = namespace["frequent_songs"]
    behavior_with_events = namespace["behavior_with_events"]
    responded_with_events = namespace["responded_with_events"]
    eeg_metadata = namespace["eeg_metadata"]
    recording_vs_trials = namespace["recording_vs_trials"]
    REAL_EEG_SUBJECTS = namespace["REAL_EEG_SUBJECTS"]

    def out(name: str) -> Path:
        nonlocal count
        count += 1
        return output_dir / f"song_familiarity_dataset_eda_{count:02d}_{slugify(name)}.png"

    fig, ax = plt.subplots(figsize=(5, 4))
    sns.histplot(participants, x="age", bins=10, color=PALETTE[0], edgecolor="white", ax=ax)
    ax.set_title("Age distribution")
    ax.set_xlabel("Age")
    save_figure(fig, out("Age distribution"))

    fig, ax = plt.subplots(figsize=(5, 4))
    sns.countplot(data=participants, x="sex", order=participants["sex"].value_counts().index, color=PALETTE[1], ax=ax)
    ax.set_title("Sex")
    ax.set_xlabel("Sex")
    save_figure(fig, out("Sex"))

    fig, ax = plt.subplots(figsize=(5, 4))
    sns.countplot(
        data=participants,
        x="handedness",
        order=participants["handedness"].value_counts().index,
        color=PALETTE[4],
        ax=ax,
    )
    ax.set_title("Handedness")
    ax.set_xlabel("Handedness")
    save_figure(fig, out("Handedness"))

    ordered_response = subject_level.sort_values("response_rate")
    fig, ax = plt.subplots(figsize=(7, 7))
    sns.barplot(data=ordered_response, y="participant_id", x="response_rate", color=PALETTE[1], ax=ax)
    ax.set_title("Familiarity response rate by participant")
    ax.set_xlabel("Response rate")
    ax.set_ylabel("Participant")
    save_figure(fig, out("Familiarity response rate by participant"))

    fig, ax = plt.subplots(figsize=(7, 5))
    sns.histplot(behavior.dropna(subset=["rt_numeric"]), x="rt_numeric", bins=30, color=PALETTE[0], edgecolor="white", ax=ax)
    ax.axvline(behavior["rt_numeric"].median(), color=PALETTE[3], linestyle="--")
    ax.set_title("Familiarity RT distribution")
    ax.set_xlabel("RT (seconds)")
    save_figure(fig, out("Familiarity RT distribution"))

    ordered_accuracy = subject_level.sort_values("mc_accuracy")
    fig, ax = plt.subplots(figsize=(7, 7))
    sns.barplot(data=ordered_accuracy, y="participant_id", x="mc_accuracy", color=PALETTE[4], ax=ax)
    ax.set_title("Multiple-choice accuracy by participant")
    ax.set_xlabel("Accuracy")
    ax.set_ylabel("Participant")
    save_figure(fig, out("Multiple-choice accuracy by participant"))

    song_duration_plot = behavior.copy()
    song_duration_plot["responded_label"] = song_duration_plot["responded"].map({0: "No", 1: "Yes"})
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.boxplot(data=song_duration_plot, x="responded_label", y="songDur", palette=[PALETTE[2], PALETTE[1]], ax=ax)
    ax.set_title("Song duration by familiarity response")
    ax.set_xlabel("Responded as familiar")
    ax.set_ylabel("Song duration (seconds)")
    save_figure(fig, out("Song duration by familiarity response"))

    top_songs = frequent_songs.sort_values("response_rate", ascending=False).head(12).sort_values("response_rate")
    fig, ax = plt.subplots(figsize=(8, 8))
    sns.barplot(data=top_songs, y="songFileName", x="response_rate", color=PALETTE[1], ax=ax)
    ax.set_title("Most familiar songs in the sample")
    ax.set_xlabel("Response rate")
    ax.set_ylabel("Song")
    save_figure(fig, out("Most familiar songs in the sample"))

    bottom_songs = frequent_songs.sort_values("response_rate", ascending=True).head(12).sort_values("response_rate")
    fig, ax = plt.subplots(figsize=(8, 8))
    sns.barplot(data=bottom_songs, y="songFileName", x="response_rate", color=PALETTE[3], ax=ax)
    ax.set_title("Least familiar songs in the sample")
    ax.set_xlabel("Response rate")
    ax.set_ylabel("Song")
    save_figure(fig, out("Least familiar songs in the sample"))

    fig, ax = plt.subplots(figsize=(7, 5))
    sns.histplot(behavior_with_events, x="note_rate", bins=30, color=PALETTE[4], edgecolor="white", ax=ax)
    ax.set_title("Distribution of note onset rate")
    ax.set_xlabel("Note onsets per second")
    save_figure(fig, out("Distribution of note onset rate"))

    fig, ax = plt.subplots(figsize=(7, 5))
    sns.regplot(
        data=responded_with_events,
        x="note_rate",
        y="rt_numeric",
        scatter_kws={"alpha": 0.25, "s": 24, "color": PALETTE[0]},
        line_kws={"color": PALETTE[3]},
        ax=ax,
    )
    ax.set_title("Note rate vs familiarity RT")
    ax.set_xlabel("Note onsets per second")
    ax.set_ylabel("RT (seconds)")
    save_figure(fig, out("Note rate vs familiarity RT"))

    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    sns.histplot(eeg_metadata, x="recording_duration_sec", bins=12, color=PALETTE[5], edgecolor="white", ax=ax)
    ax.set_title("EEG recording duration")
    ax.set_xlabel("Duration (seconds)")
    save_figure(fig, out("EEG recording duration"))

    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    sns.scatterplot(data=recording_vs_trials, x="recording_duration_sec", y="n_trials", hue="response_rate", palette="viridis", s=70, ax=ax)
    ax.set_title("Recording duration vs behavioral trial count")
    ax.set_xlabel("Recording duration (seconds)")
    ax.set_ylabel("Behavioral trials")
    save_figure(fig, out("Recording duration vs behavioral trial count"))

    if REAL_EEG_SUBJECTS:
        participant_mean_df = namespace["participant_mean_df"]
        grand_evokeds = namespace["grand_evokeds"]
        common_channels = namespace["common_channels"]
        selected_channels = namespace["selected_channels"]
        condition_colors = {"familiar": PALETTE[1], "not_familiar": PALETTE[3]}

        for condition in ["familiar", "not_familiar"]:
            fig, ax = plt.subplots(figsize=(7.5, 4.5))
            condition_df = participant_mean_df[participant_mean_df["condition"] == condition]
            for _, participant_df in condition_df.groupby("participant_id"):
                ax.plot(participant_df["time_sec"], participant_df["amplitude_uv"], color=condition_colors[condition], alpha=0.15, linewidth=0.8)
            grand_trace = grand_evokeds[condition].data.mean(axis=0) * 1e6
            ax.plot(grand_evokeds[condition].times, grand_trace, color=condition_colors[condition], linewidth=2.5)
            ax.axvline(0, color="black", linestyle="--", linewidth=1)
            ax.axhline(0, color="black", linestyle=":", linewidth=0.8)
            ax.set_title(f"{condition.replace('_', ' ').title()} trials mean across {len(common_channels)} channels")
            ax.set_xlabel("Time from stimulus onset (s)")
            ax.set_ylabel("Amplitude (uV)")
            save_figure(fig, out(f"{condition} participant average EEG"))

        for channel in selected_channels:
            fig, ax = plt.subplots(figsize=(8, 4))
            for condition in ["familiar", "not_familiar"]:
                if condition not in grand_evokeds:
                    continue
                trace = grand_evokeds[condition].copy().pick([channel]).data[0] * 1e6
                ax.plot(
                    grand_evokeds[condition].times,
                    trace,
                    color=condition_colors[condition],
                    linewidth=2,
                    label=condition.replace("_", " ").title(),
                )
            ax.axvline(0, color="black", linestyle="--", linewidth=1)
            ax.axhline(0, color="black", linestyle=":", linewidth=0.8)
            ax.set_title(f"Grand-average EEG at {channel}")
            ax.set_ylabel("Amplitude (uV)")
            ax.set_xlabel("Time from stimulus onset (s)")
            ax.legend(loc="upper right")
            save_figure(fig, out(f"Grand-average EEG at {channel}"))

        if {"familiar", "not_familiar"}.issubset(grand_evokeds):
            difference_evoked = namespace["difference_evoked"]
            difference_df = namespace["difference_df"]
            fig, ax = plt.subplots(figsize=(14, max(6, len(common_channels) * 0.22)))
            sns.heatmap(difference_df, cmap="RdBu_r", center=0, cbar_kws={"label": "Amplitude (uV)"}, ax=ax)
            ax.set_title("Grand-average difference wave across channels (familiar - not familiar)")
            ax.set_xlabel("Time from stimulus onset (s)")
            ax.set_ylabel("Channel")
            save_figure(fig, out("Grand-average difference wave across channels"))

    return count


def export_analysis_ready(namespace: dict, output_dir: Path) -> int:
    count = 0
    participant_summary = namespace["participant_summary"]
    responded_trials = namespace["responded_trials"]
    frequent_songs = namespace["frequent_songs"]
    responded_eeg_trials = namespace["responded_eeg_trials"]
    eeg_ready_trials = namespace["eeg_ready_trials"]
    trial_df = namespace["trial_df"]

    def out(name: str) -> Path:
        nonlocal count
        count += 1
        return output_dir / f"song_familiarity_analysis_ready_{count:02d}_{slugify(name)}.png"

    ordered_participants = participant_summary.sort_values("participant_response_rate")
    fig, ax = plt.subplots(figsize=(8, 8))
    sns.barplot(data=ordered_participants, y="participant_id", x="participant_response_rate", color=PALETTE[1], ax=ax)
    ax.set_title("Familiarity response rate by participant")
    save_figure(fig, out("Familiarity response rate by participant"))

    fig, ax = plt.subplots(figsize=(7, 5))
    sns.histplot(responded_trials, x="rt_numeric", bins=30, color=PALETTE[0], edgecolor="white", ax=ax)
    ax.set_title("Distribution of familiarity response times")
    save_figure(fig, out("Distribution of familiarity response times"))

    fig, ax = plt.subplots(figsize=(7, 5))
    sns.scatterplot(
        data=participant_summary,
        x="age",
        y="participant_response_rate",
        size="participant_mc_accuracy",
        sizes=(50, 220),
        hue="participant_mc_accuracy",
        palette="viridis",
        ax=ax,
    )
    ax.set_title("Age vs familiarity response rate")
    save_figure(fig, out("Age vs familiarity response rate"))

    fig, ax = plt.subplots(figsize=(7, 5))
    sns.scatterplot(
        data=participant_summary,
        x="mean_global_field_power",
        y="participant_response_rate",
        hue="log_mean_alpha_power",
        palette="mako",
        s=90,
        ax=ax,
    )
    ax.set_title("Mean GFP vs familiarity response rate")
    save_figure(fig, out("Mean GFP vs familiarity response rate"))

    top_songs = frequent_songs.sort_values("song_response_rate", ascending=False).head(12).sort_values("song_response_rate")
    fig, ax = plt.subplots(figsize=(8, 8))
    sns.barplot(data=top_songs, y="song_name_clean", x="song_response_rate", color=PALETTE[1], ax=ax)
    ax.set_title("Most familiar songs")
    save_figure(fig, out("Most familiar songs"))

    bottom_songs = frequent_songs.sort_values("song_response_rate", ascending=True).head(12).sort_values("song_response_rate")
    fig, ax = plt.subplots(figsize=(8, 8))
    sns.barplot(data=bottom_songs, y="song_name_clean", x="song_response_rate", color=PALETTE[3], ax=ax)
    ax.set_title("Least familiar songs")
    save_figure(fig, out("Least familiar songs"))

    fig, ax = plt.subplots(figsize=(7, 5))
    sns.regplot(
        data=responded_trials,
        x="note_rate",
        y="rt_numeric",
        scatter_kws={"alpha": 0.25, "s": 22, "color": PALETTE[0]},
        line_kws={"color": PALETTE[3]},
        ax=ax,
    )
    ax.set_title("Note rate vs familiarity RT")
    save_figure(fig, out("Note rate vs familiarity RT"))

    fig, ax = plt.subplots(figsize=(7, 5))
    sns.scatterplot(
        data=frequent_songs.dropna(subset=["song_mean_rt"]),
        x="song_response_rate",
        y="song_mean_rt",
        size="song_sample_n",
        sizes=(40, 220),
        hue="song_mean_alpha_power",
        palette="crest",
        ax=ax,
    )
    ax.set_title("Song familiarity vs mean RT")
    save_figure(fig, out("Song familiarity vs mean RT"))

    heatmap_songs = frequent_songs.sort_values(["song_sample_n", "song_response_rate"], ascending=[False, False]).head(18)["songFileName"]
    heatmap_df = trial_df[trial_df["songFileName"].isin(heatmap_songs)].pivot_table(
        index="participant_id",
        columns="song_name_clean",
        values="responded",
        aggfunc="mean",
    )
    heatmap_df = heatmap_df.loc[:, heatmap_df.mean().sort_values(ascending=False).index]
    fig, ax = plt.subplots(figsize=(16, 8))
    sns.heatmap(heatmap_df, cmap="YlGnBu", vmin=0, vmax=1, cbar_kws={"label": "Response rate"}, ax=ax)
    ax.set_title("Participant familiarity responses for high-coverage songs")
    save_figure(fig, out("Participant familiarity responses for high-coverage songs"))

    fig, ax = plt.subplots(figsize=(7, 5))
    sns.regplot(
        data=responded_eeg_trials,
        x="log_alpha_power",
        y="rt_numeric",
        scatter_kws={"alpha": 0.2, "s": 20, "color": PALETTE[0]},
        line_kws={"color": PALETTE[3]},
        ax=ax,
    )
    ax.set_title("Log alpha power vs familiarity RT")
    save_figure(fig, out("Log alpha power vs familiarity RT"))

    fig, ax = plt.subplots(figsize=(7, 5))
    sns.regplot(
        data=responded_eeg_trials,
        x="log_beta_power",
        y="rt_numeric",
        scatter_kws={"alpha": 0.2, "s": 20, "color": PALETTE[5]},
        line_kws={"color": PALETTE[2]},
        ax=ax,
    )
    ax.set_title("Log beta power vs familiarity RT")
    save_figure(fig, out("Log beta power vs familiarity RT"))

    fig, ax = plt.subplots(figsize=(6, 5))
    sns.boxplot(data=eeg_ready_trials, x="responded_label", y="global_field_power", palette=[PALETTE[3], PALETTE[1]], ax=ax)
    ax.set_title("Global field power by familiarity judgment")
    save_figure(fig, out("Global field power by familiarity judgment"))

    fig, ax = plt.subplots(figsize=(7, 5))
    sns.scatterplot(
        data=responded_eeg_trials,
        x="note_rate",
        y="log_alpha_power",
        hue="responded_label",
        palette=[PALETTE[3], PALETTE[1]],
        alpha=0.45,
        s=30,
        ax=ax,
    )
    ax.set_title("Note rate vs log alpha power")
    save_figure(fig, out("Note rate vs log alpha power"))

    participant_band_heatmap = participant_summary.set_index("participant_id")[
        ["log_mean_alpha_power", "log_mean_beta_power", "mean_global_field_power"]
    ].sort_values("log_mean_alpha_power", ascending=False)
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(participant_band_heatmap, cmap="mako", cbar_kws={"label": "Feature value"}, ax=ax)
    ax.set_title("Participant-level EEG feature summary")
    save_figure(fig, out("Participant-level EEG feature summary"))

    return count


def export_csp_lda(namespace: dict, output_dir: Path) -> int:
    count = 0

    def out(name: str) -> Path:
        nonlocal count
        count += 1
        return output_dir / f"csp_lda_familiarity_modellability_{count:02d}_{slugify(name)}.png"

    participant_summary = namespace["participant_summary"]
    label_styles = namespace["label_styles"]
    times = namespace["times"]
    gfp_summary = namespace["gfp_summary"]
    familiar_avg_uv = namespace["familiar_avg_uv"]
    not_familiar_avg_uv = namespace["not_familiar_avg_uv"]
    diff_avg_uv = namespace["diff_avg_uv"]
    focus_channels = namespace["focus_channels"]
    channel_names = namespace["channel_names"]
    info_template = namespace["info_template"]
    time_indices = namespace["time_indices"]
    topography_rows = namespace["topography_rows"]
    tuning_df = namespace["tuning_df"]
    best_n_components = namespace["best_n_components"]
    grouped_df = namespace["grouped_df"]
    y = namespace["y"]
    oof_prob = namespace["oof_prob"]
    prediction_df = namespace["prediction_df"]
    loso_df = namespace["loso_df"]
    valid_within_df = namespace["valid_within_df"]

    fig, ax = plt.subplots(figsize=(8, 7))
    sns.barplot(data=participant_summary, x="familiar_rate", y="participant_id", color="#457b9d", ax=ax)
    ax.set_title("Participant familiarity rate before modeling")
    ax.set_xlabel("Proportion of trials labeled familiar")
    ax.set_ylabel("Participant")
    ax.set_xlim(0, 1)
    save_figure(fig, out("Participant familiarity rate before modeling"))

    fig, ax = plt.subplots(figsize=(8, 5))
    for label_value, summary in gfp_summary.items():
        style = summary["style"]
        ax.plot(times, summary["mean"], color=style["color"], linewidth=2, label=style["name"])
        ax.fill_between(times, summary["mean"] - summary["sem"], summary["mean"] + summary["sem"], color=style["color"], alpha=0.18)
    ax.set_title("Global field power over the 2 s stimulus window")
    ax.set_xlabel("Time from song onset (s)")
    ax.set_ylabel("Global field power (uV)")
    ax.legend(frameon=True)
    save_figure(fig, out("Global field power over the 2 s stimulus window"))

    fig, ax = plt.subplots(figsize=(8, 5))
    channel_palette = ["#264653", "#e76f51", "#577590"]
    for color, channel_name in zip(channel_palette, focus_channels):
        channel_idx = int(np.where(channel_names == channel_name)[0][0])
        ax.plot(times, familiar_avg_uv[channel_idx], color=color, linewidth=2, label=f"{channel_name} familiar")
        ax.plot(times, not_familiar_avg_uv[channel_idx], color=color, linestyle="--", linewidth=1.8, label=f"{channel_name} not familiar")
    ax.axhline(0, color="black", linewidth=0.8, linestyle=":")
    ax.set_title("Representative channel-averaged waveforms")
    ax.set_xlabel("Time from song onset (s)")
    ax.set_ylabel("Mean amplitude (uV)")
    ax.legend(ncol=2, fontsize=9)
    save_figure(fig, out("Representative channel-averaged waveforms"))

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(diff_avg_uv, cmap="RdBu_r", center=0, cbar_kws={"label": "Familiar - not familiar (uV)"}, ax=ax)
    ax.set_title("Channel-by-time average difference map")
    ax.set_xlabel("Time from song onset (s)")
    ax.set_ylabel("Channel")
    xticks = np.linspace(0, len(times) - 1, 5, dtype=int)
    ax.set_xticks(xticks + 0.5)
    ax.set_xticklabels([f"{times[idx]:.2f}" for idx in xticks])
    yticks = np.arange(0, len(channel_names), 4)
    ax.set_yticks(yticks + 0.5)
    ax.set_yticklabels(channel_names[yticks], rotation=0)
    save_figure(fig, out("Channel-by-time average difference map"))

    for row_label, scalp_data, vmax in topography_rows:
        vmax = float(vmax) if np.isfinite(vmax) and vmax > 0 else 1.0
        for time_idx in time_indices:
            fig, ax = plt.subplots(figsize=(4.5, 4.5))
            image, _ = plot_topomap(
                scalp_data[:, time_idx],
                info_template,
                axes=ax,
                cmap="RdBu_r",
                vlim=(-vmax, vmax),
                contours=6,
                show=False,
            )
            ax.set_title(f"{row_label} {times[time_idx]:.2f} s")
            fig.colorbar(image, ax=ax, shrink=0.8, label="Mean amplitude (uV)")
            save_figure(fig, out(f"{row_label} {times[time_idx]:.2f} s topography"))

    tuning_plot_df = tuning_df.sort_values("n_components").reset_index(drop=True)
    metric_specs = [
        ("roc_auc_mean", "ROC AUC", "#1d3557"),
        ("balanced_accuracy_mean", "Balanced accuracy", "#457b9d"),
        ("accuracy_mean", "Accuracy", "#2a9d8f"),
        ("f1_mean", "F1", "#e76f51"),
    ]
    fig, ax = plt.subplots(figsize=(8, 5.5))
    for metric_name, metric_label, metric_color in metric_specs:
        ax.plot(tuning_plot_df["n_components"], tuning_plot_df[metric_name], marker="o", linewidth=2, color=metric_color, label=metric_label)
    ax.fill_between(
        tuning_plot_df["n_components"],
        tuning_plot_df["roc_auc_mean"] - tuning_plot_df["roc_auc_std"],
        tuning_plot_df["roc_auc_mean"] + tuning_plot_df["roc_auc_std"],
        color="#a8dadc",
        alpha=0.35,
        label="ROC AUC +/- 1 SD",
    )
    ax.axhline(0.5, linestyle="--", linewidth=1, color="black")
    ax.axvline(best_n_components, linestyle=":", linewidth=1.2, color="#264653")
    ax.set_title("Grouped CV metric sweep across CSP component counts")
    ax.set_xlabel("CSP components")
    ax.set_ylabel("Cross-validated score")
    ax.legend(frameon=True, fontsize=9)
    save_figure(fig, out("Grouped CV metric sweep across CSP component counts"))

    grouped_plot_df = grouped_df[["model", "roc_auc_mean", "balanced_accuracy_mean", "accuracy_mean", "f1_mean"]].melt(
        id_vars="model", var_name="metric", value_name="score"
    )
    grouped_plot_df["metric"] = grouped_plot_df["metric"].map(
        {
            "roc_auc_mean": "ROC AUC",
            "balanced_accuracy_mean": "Balanced accuracy",
            "accuracy_mean": "Accuracy",
            "f1_mean": "F1",
        }
    )
    fig, ax = plt.subplots(figsize=(8, 5.5))
    sns.barplot(data=grouped_plot_df, x="metric", y="score", hue="model", ax=ax)
    ax.axhline(0.5, linestyle="--", linewidth=1, color="black")
    ax.set_title("Best grouped model versus dummy baseline")
    ax.set_xlabel("")
    ax.set_ylabel("Cross-validated score")
    ax.legend(title="Model", frameon=True)
    save_figure(fig, out("Best grouped model versus dummy baseline"))

    fig, ax = plt.subplots(figsize=(7, 5))
    RocCurveDisplay.from_predictions(y, oof_prob, ax=ax, color="#1d3557", name="LOSO OOF")
    ax.plot([0, 1], [0, 1], linestyle="--", linewidth=1, color="black")
    ax.set_title("Out-of-fold ROC curve across held-out participants")
    save_figure(fig, out("Out-of-fold ROC curve across held-out participants"))

    fig, ax = plt.subplots(figsize=(6, 5))
    ConfusionMatrixDisplay.from_predictions(y, prediction_df["predicted_label"], normalize="true", ax=ax, colorbar=False, cmap="Blues")
    ax.set_title("Normalized LOSO confusion matrix")
    save_figure(fig, out("Normalized LOSO confusion matrix"))

    subject_accuracy_df = loso_df.sort_values("accuracy", ascending=True)
    fig, ax = plt.subplots(figsize=(8, 7))
    sns.barplot(data=subject_accuracy_df, x="accuracy", y="participant_id", color="#2a9d8f", ax=ax)
    ax.axvline(0.5, linestyle="--", linewidth=1, color="black")
    ax.set_title("Held-out subject accuracy by participant")
    ax.set_xlabel("Accuracy")
    ax.set_ylabel("Participant")
    save_figure(fig, out("Held-out subject accuracy by participant"))

    fig, ax = plt.subplots(figsize=(7, 5))
    sns.boxplot(data=prediction_df, x="true_label_name", y="predicted_probability_familiar", palette=["#6d597a", "#2a9d8f"], ax=ax)
    sns.stripplot(
        data=prediction_df.sample(min(len(prediction_df), 500), random_state=42),
        x="true_label_name",
        y="predicted_probability_familiar",
        color="black",
        alpha=0.22,
        size=2.3,
        ax=ax,
    )
    ax.axhline(0.5, linestyle="--", linewidth=1, color="black")
    ax.set_title("LOSO predicted familiarity probability by true label")
    ax.set_xlabel("")
    ax.set_ylabel("Predicted P(familiar)")
    save_figure(fig, out("LOSO predicted familiarity probability by true label"))

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(tuning_df["n_components"], tuning_df["roc_auc_mean"], marker="o", color="#1d3557")
    ax.fill_between(
        tuning_df["n_components"],
        tuning_df["roc_auc_mean"] - tuning_df["roc_auc_std"],
        tuning_df["roc_auc_mean"] + tuning_df["roc_auc_std"],
        alpha=0.2,
        color="#457b9d",
    )
    ax.axhline(0.5, linestyle="--", linewidth=1, color="black")
    ax.set_title("Grouped 5-fold ROC AUC by CSP component count")
    ax.set_xlabel("CSP components")
    ax.set_ylabel("ROC AUC")
    save_figure(fig, out("Grouped 5-fold ROC AUC by CSP component count"))

    summary_grouped_plot_df = grouped_df[["model", "roc_auc_mean", "balanced_accuracy_mean", "accuracy_mean"]].melt(
        id_vars="model", var_name="metric", value_name="score"
    )
    summary_grouped_plot_df["metric"] = summary_grouped_plot_df["metric"].str.replace("_mean", "", regex=False)
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.barplot(data=summary_grouped_plot_df, x="metric", y="score", hue="model", ax=ax)
    ax.axhline(0.5, linestyle="--", linewidth=1, color="black")
    ax.set_title("Grouped 5-fold metrics: dummy vs CSP+LDA")
    ax.set_xlabel("")
    ax.set_ylabel("Score")
    save_figure(fig, out("Grouped 5-fold metrics dummy vs CSP LDA"))

    fig, ax = plt.subplots(figsize=(7, 5))
    sns.histplot(valid_within_df["roc_auc_mean"], bins=12, color="#2a9d8f", edgecolor="white", ax=ax)
    ax.axvline(0.5, linestyle="--", linewidth=1, color="black")
    ax.set_title("Within-subject ROC AUC distribution")
    ax.set_xlabel("ROC AUC")
    save_figure(fig, out("Within-subject ROC AUC distribution"))

    fig, ax = plt.subplots(figsize=(7, 5))
    sns.scatterplot(
        data=valid_within_df,
        x="familiar_rate",
        y="roc_auc_mean",
        size="n_trials",
        sizes=(40, 220),
        color="#e76f51",
        ax=ax,
    )
    ax.axhline(0.5, linestyle="--", linewidth=1, color="black")
    ax.set_title("Within-subject ROC AUC vs familiarity rate")
    ax.set_xlabel("Participant familiarity rate")
    ax.set_ylabel("Within-subject ROC AUC")
    save_figure(fig, out("Within-subject ROC AUC vs familiarity rate"))

    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Export each notebook plot as its own PNG.")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    sns.set_theme(style="whitegrid", context="notebook", palette=PALETTE)

    eda_ns = execute_notebook("song_familiarity_dataset_eda.ipynb")
    analysis_ns = execute_notebook("song_familiarity_analysis_ready.ipynb")
    csp_ns = execute_notebook("csp_lda_familiarity_modellability.ipynb")

    counts = {
        "song_familiarity_dataset_eda.ipynb": export_dataset_eda(eda_ns, output_dir),
        "song_familiarity_analysis_ready.ipynb": export_analysis_ready(analysis_ns, output_dir),
        "csp_lda_familiarity_modellability.ipynb": export_csp_lda(csp_ns, output_dir),
    }

    for name, count in counts.items():
        print(f"{name}: exported {count} standalone plots")
    print(f"Output directory: {output_dir}")


if __name__ == "__main__":
    main()
