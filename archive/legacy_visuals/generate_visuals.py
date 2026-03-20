"""
Generate all visualizations for ds005876 (Song Familiarity) OpenNeuro dataset.
Saves figures into the same folder as this script (visuals/).
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Paths: dataset root is one level up from visuals/
ROOT = Path(__file__).resolve().parent.parent
DS_DIR = ROOT / "ds005876"
OUT_DIR = Path(__file__).resolve().parent

# Style: distinct, readable, not default "AI slop"
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.size"] = 10
PALETTE = ["#2d5a27", "#7cb342", "#1a237e", "#7986cb", "#b71c1c", "#e57373"]
sns.set_theme(style="whitegrid", palette=PALETTE, font_scale=1.05)


def load_participants() -> pd.DataFrame:
    """Load participants.tsv and parse datetime."""
    df = pd.read_csv(DS_DIR / "participants.tsv", sep="\t")
    df["datetime"] = pd.to_datetime(df["datetime"], format="%d-%b-%Y %H:%M:%S")
    return df


def load_all_behavioral() -> pd.DataFrame:
    """Load all subject behavioral TSVs and concatenate with participant_id."""
    beh_dir = DS_DIR
    frames = []
    for p in sorted(beh_dir.glob("sub-*/beh/*_beh.tsv")):
        sub_id = p.parent.parent.name  # e.g. sub-01
        df = pd.read_csv(p, sep="\t")
        df["participant_id"] = sub_id
        frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def safe_numeric(series, default=float("nan")):
    """Coerce to numeric, invalid -> NaN."""
    return pd.to_numeric(series, errors="coerce")


def plot_demographics_age(participants: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(6, 3.5))
    participants["age"].hist(bins=12, ax=ax, color=PALETTE[0], edgecolor="white", linewidth=0.8)
    ax.set_xlabel("Age (years)")
    ax.set_ylabel("Count")
    ax.set_title("Participant age distribution")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "01_demographics_age.png", dpi=150, bbox_inches="tight")
    fig.savefig(OUT_DIR / "01_demographics_age.pdf", bbox_inches="tight")
    plt.close()


def plot_demographics_sex_handedness(participants: pd.DataFrame) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3.5))
    sex_counts = participants["sex"].value_counts()
    ax1.bar(sex_counts.index, sex_counts.values, color=[PALETTE[0], PALETTE[2]])
    ax1.set_xlabel("Sex")
    ax1.set_ylabel("Count")
    ax1.set_title("Sex")
    hand_counts = participants["handedness"].value_counts()
    ax2.bar(range(len(hand_counts)), hand_counts.values, color=PALETTE[: len(hand_counts)])
    ax2.set_xticks(range(len(hand_counts)))
    ax2.set_xticklabels(hand_counts.index)
    ax2.set_xlabel("Handedness")
    ax2.set_ylabel("Count")
    ax2.set_title("Handedness")
    fig.suptitle("Demographics: sex and handedness", y=1.02)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "02_demographics_sex_handedness.png", dpi=150, bbox_inches="tight")
    fig.savefig(OUT_DIR / "02_demographics_sex_handedness.pdf", bbox_inches="tight")
    plt.close()


def plot_response_rate_by_subject(beh: pd.DataFrame) -> None:
    responded = beh.groupby("participant_id").agg(
        responded_pct=("responded", lambda x: 100 * x.mean()),
        n_trials=("responded", "count"),
    ).reset_index()
    responded = responded.sort_values("responded_pct")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.barh(responded["participant_id"], responded["responded_pct"], color=PALETTE[1])
    ax.set_xlabel("% trials with familiarity response")
    ax.set_ylabel("Participant")
    ax.set_title("Familiarity response rate by participant")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "03_response_rate_by_subject.png", dpi=150, bbox_inches="tight")
    fig.savefig(OUT_DIR / "03_response_rate_by_subject.pdf", bbox_inches="tight")
    plt.close()


def plot_rt_distribution(beh: pd.DataFrame) -> None:
    rt_series = safe_numeric(beh["rt"], default=float("nan"))
    rt_valid = rt_series.dropna()
    if rt_valid.empty:
        return
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.hist(rt_valid, bins=30, color=PALETTE[2], edgecolor="white", linewidth=0.6)
    ax.axvline(rt_valid.median(), color=PALETTE[4], linestyle="--", label=f"Median = {rt_valid.median():.1f}s")
    ax.set_xlabel("Response time (s)")
    ax.set_ylabel("Count")
    ax.set_title("Familiarity response time (when responded)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT_DIR / "04_rt_distribution.png", dpi=150, bbox_inches="tight")
    fig.savefig(OUT_DIR / "04_rt_distribution.pdf", bbox_inches="tight")
    plt.close()


def plot_mc_accuracy_by_subject(beh: pd.DataFrame) -> None:
    # outcomeMC: 0 = incorrect, 1 = correct
    acc = beh.groupby("participant_id").agg(
        accuracy_pct=("outcomeMC", lambda x: 100 * x.mean()),
        n=("outcomeMC", "count"),
    ).reset_index()
    acc = acc.sort_values("accuracy_pct")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.barh(acc["participant_id"], acc["accuracy_pct"], color=PALETTE[0])
    ax.set_xlabel("% correct (multiple choice)")
    ax.set_ylabel("Participant")
    ax.set_title("Multiple-choice song identification accuracy by participant")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "05_mc_accuracy_by_subject.png", dpi=150, bbox_inches="tight")
    fig.savefig(OUT_DIR / "05_mc_accuracy_by_subject.pdf", bbox_inches="tight")
    plt.close()


def plot_song_duration_vs_responded(beh: pd.DataFrame) -> None:
    beh = beh.copy()
    beh["Responded"] = beh["responded"].map({0: "No", 1: "Yes"})
    fig, ax = plt.subplots(figsize=(6, 3.5))
    sns.boxplot(data=beh, x="Responded", y="songDur", hue="Responded", ax=ax, palette=[PALETTE[3], PALETTE[1]], legend=False)
    ax.set_ylabel("Song duration (s)")
    ax.set_xlabel("Familiarity response")
    ax.set_title("Song duration by whether participant responded (familiar)")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "06_song_duration_vs_responded.png", dpi=150, bbox_inches="tight")
    fig.savefig(OUT_DIR / "06_song_duration_vs_responded.pdf", bbox_inches="tight")
    plt.close()


def plot_overview_panel(participants: pd.DataFrame, beh: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(9, 7))
    # Age
    axes[0, 0].hist(participants["age"], bins=12, color=PALETTE[0], edgecolor="white")
    axes[0, 0].set_title("Age distribution")
    axes[0, 0].set_xlabel("Age")
    # Response rate overall
    axes[0, 1].bar(
        ["Responded", "No response"],
        [beh["responded"].mean() * 100, (1 - beh["responded"].mean()) * 100],
        color=[PALETTE[1], PALETTE[3]],
    )
    axes[0, 1].set_title("% trials: familiarity response")
    axes[0, 1].set_ylabel("%")
    # MC outcome
    axes[1, 0].bar(
        ["Correct", "Incorrect"],
        [beh["outcomeMC"].mean() * 100, (1 - beh["outcomeMC"].mean()) * 100],
        color=[PALETTE[0], PALETTE[4]],
    )
    axes[1, 0].set_title("% trials: MC correct")
    axes[1, 0].set_ylabel("%")
    # RT (valid only)
    rt = safe_numeric(beh["rt"]).dropna()
    if not rt.empty:
        axes[1, 1].hist(rt, bins=25, color=PALETTE[2])
        axes[1, 1].set_title("RT when responded (s)")
        axes[1, 1].set_xlabel("RT (s)")
    else:
        axes[1, 1].text(0.5, 0.5, "No RT data", ha="center", va="center")
    fig.suptitle("ds005876 Song Familiarity — dataset overview", y=1.02)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "07_dataset_overview.png", dpi=150, bbox_inches="tight")
    fig.savefig(OUT_DIR / "07_dataset_overview.pdf", bbox_inches="tight")
    plt.close()


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    participants = load_participants()
    beh = load_all_behavioral()
    if beh.empty:
        raise SystemExit("No behavioral files found.")
    plot_demographics_age(participants)
    plot_demographics_sex_handedness(participants)
    plot_response_rate_by_subject(beh)
    plot_rt_distribution(beh)
    plot_mc_accuracy_by_subject(beh)
    plot_song_duration_vs_responded(beh)
    plot_overview_panel(participants, beh)
    print(f"Saved all figures to {OUT_DIR}")


if __name__ == "__main__":
    main()
