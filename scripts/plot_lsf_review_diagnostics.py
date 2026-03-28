from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import librosa
import matplotlib
import numpy as np

from apply_stage0_rule_preconditioner import load_audio


matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUEUE_CSV = ROOT / "artifacts" / "listening_review" / "stage0_speech_lsf_listening_pack" / "v3" / "listening_review_queue.csv"
DEFAULT_OUTPUT_DIR = ROOT / "artifacts" / "diagnostics" / "lsf_review_v3"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue-csv", default=str(DEFAULT_QUEUE_CSV))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--n-fft", type=int, default=2048)
    parser.add_argument("--hop-length", type=int, default=256)
    parser.add_argument("--max-rows", type=int, default=0, help="0 means all rows.")
    return parser.parse_args()


def resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return ROOT / path


def short_slug(text: str) -> str:
    keep = []
    for ch in text:
        if ch.isalnum() or ch in {"-", "_"}:
            keep.append(ch)
        else:
            keep.append("_")
    return "".join(keep).strip("_")


def db_floor(values: np.ndarray, floor_db: float = -80.0) -> np.ndarray:
    return np.maximum(values, floor_db)


def long_term_average_db(audio: np.ndarray, *, sample_rate: int, n_fft: int, hop_length: int) -> tuple[np.ndarray, np.ndarray]:
    stft = librosa.stft(audio.astype(np.float32), n_fft=n_fft, hop_length=hop_length)
    mag = np.abs(stft)
    mean_mag = np.mean(mag, axis=1)
    freqs = librosa.fft_frequencies(sr=sample_rate, n_fft=n_fft)
    ltas_db = librosa.amplitude_to_db(np.maximum(mean_mag, 1e-8), ref=np.max)
    return freqs, ltas_db


def delta_spectrogram_db(
    original: np.ndarray,
    processed: np.ndarray,
    *,
    sample_rate: int,
    n_fft: int,
    hop_length: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    length = min(len(original), len(processed))
    original = original[:length].astype(np.float32)
    processed = processed[:length].astype(np.float32)
    stft_orig = librosa.stft(original, n_fft=n_fft, hop_length=hop_length)
    stft_proc = librosa.stft(processed, n_fft=n_fft, hop_length=hop_length)
    mag_orig = librosa.amplitude_to_db(np.maximum(np.abs(stft_orig), 1e-8), ref=np.max)
    mag_proc = librosa.amplitude_to_db(np.maximum(np.abs(stft_proc), 1e-8), ref=np.max)
    delta_db = mag_proc - mag_orig
    times = librosa.frames_to_time(np.arange(delta_db.shape[1]), sr=sample_rate, hop_length=hop_length, n_fft=n_fft)
    freqs = librosa.fft_frequencies(sr=sample_rate, n_fft=n_fft)
    return times, freqs, delta_db


def band_energy_db(audio: np.ndarray, *, sample_rate: int, n_fft: int, hop_length: int) -> dict[str, float]:
    stft = librosa.stft(audio.astype(np.float32), n_fft=n_fft, hop_length=hop_length)
    power = np.mean(np.abs(stft) ** 2, axis=1)
    freqs = librosa.fft_frequencies(sr=sample_rate, n_fft=n_fft)
    total = max(float(np.sum(power)), 1e-12)

    def share(low_hz: float, high_hz: float) -> float:
        mask = (freqs >= low_hz) & (freqs < high_hz)
        value = float(np.sum(power[mask]))
        return 10.0 * math.log10(max(value, 1e-12) / total)

    return {
        "0-1.5k": share(0.0, 1500.0),
        "1.5-3k": share(1500.0, 3000.0),
        "3-8k": share(3000.0, min(8000.0, sample_rate / 2.0)),
    }


def plot_row(
    row: dict[str, str],
    *,
    output_dir: Path,
    n_fft: int,
    hop_length: int,
) -> dict[str, str]:
    original_path = resolve_path(row["original_copy"])
    processed_path = resolve_path(row["processed_audio"])
    original, original_sr = load_audio(original_path)
    processed, processed_sr = load_audio(processed_path)
    if original_sr != processed_sr:
        raise ValueError(f"Sample rate mismatch: {original_sr} vs {processed_sr}")

    freqs, orig_ltas = long_term_average_db(original, sample_rate=original_sr, n_fft=n_fft, hop_length=hop_length)
    _, proc_ltas = long_term_average_db(processed, sample_rate=original_sr, n_fft=n_fft, hop_length=hop_length)
    times, spec_freqs, delta_db = delta_spectrogram_db(original, processed, sample_rate=original_sr, n_fft=n_fft, hop_length=hop_length)

    orig_bands = band_energy_db(original, sample_rate=original_sr, n_fft=n_fft, hop_length=hop_length)
    proc_bands = band_energy_db(processed, sample_rate=original_sr, n_fft=n_fft, hop_length=hop_length)
    delta_bands = {key: proc_bands[key] - orig_bands[key] for key in orig_bands}

    stem = short_slug(f"{row['target_direction']}_{row['group_value']}_{row['utt_id']}")
    figure_path = output_dir / f"{stem}.png"

    fig, axes = plt.subplots(3, 1, figsize=(11, 12), constrained_layout=True)

    ax = axes[0]
    ax.plot(freqs, db_floor(orig_ltas), label="original", linewidth=1.5)
    ax.plot(freqs, db_floor(proc_ltas), label="processed", linewidth=1.5)
    ax.set_title(
        f"{row['utt_id']} | {row['group_value']} | {row['source_gender']} -> {row['target_direction']}"
    )
    ax.set_xlim(0.0, min(8000.0, original_sr / 2.0))
    ax.set_ylim(-80.0, 5.0)
    ax.set_ylabel("LTAS dB")
    ax.grid(alpha=0.2)
    ax.legend()

    ax = axes[1]
    image = ax.imshow(
        delta_db,
        origin="lower",
        aspect="auto",
        extent=[times[0] if times.size else 0.0, times[-1] if times.size else 0.0, spec_freqs[0], spec_freqs[-1]],
        cmap="coolwarm",
        vmin=-8.0,
        vmax=8.0,
    )
    ax.set_ylim(0.0, min(8000.0, original_sr / 2.0))
    ax.set_ylabel("Hz")
    ax.set_title("Processed - Original Spectrogram (dB)")
    fig.colorbar(image, ax=ax, pad=0.01, label="dB")

    ax = axes[2]
    labels = list(delta_bands.keys())
    values = [delta_bands[key] for key in labels]
    colors = ["#c44e52" if value < 0 else "#4c72b0" for value in values]
    ax.bar(labels, values, color=colors)
    ax.axhline(0.0, color="black", linewidth=1.0)
    ax.set_ylabel("Delta share dB")
    ax.set_title("Band Energy Share Delta")
    for idx, value in enumerate(values):
        ax.text(idx, value + (0.08 if value >= 0 else -0.18), f"{value:.2f}", ha="center", va="bottom" if value >= 0 else "top")
    ax.grid(axis="y", alpha=0.2)

    fig.savefig(figure_path, dpi=150)
    plt.close(fig)

    return {
        "utt_id": row["utt_id"],
        "group_value": row["group_value"],
        "target_direction": row["target_direction"],
        "effect_audible": row.get("effect_audible", ""),
        "artifact_issue": row.get("artifact_issue", ""),
        "strength_fit": row.get("strength_fit", ""),
        "delta_band_0_1p5k_db": f"{delta_bands['0-1.5k']:.2f}",
        "delta_band_1p5_3k_db": f"{delta_bands['1.5-3k']:.2f}",
        "delta_band_3_8k_db": f"{delta_bands['3-8k']:.2f}",
        "figure_path": str(figure_path),
    }


def write_summary(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    lines = [
        "# LSF Review Diagnostics",
        "",
        "Each figure includes:",
        "",
        "- original vs processed long-term average spectrum",
        "- processed minus original spectrogram in dB",
        "- 3-band energy-share delta",
        "",
    ]
    for row in rows:
        lines.extend(
            [
                f"## `{row['utt_id']}`",
                "",
                f"- group: `{row['group_value']}`",
                f"- target_direction: `{row['target_direction']}`",
                f"- review: effect=`{row['effect_audible']}` artifact=`{row['artifact_issue']}` strength=`{row['strength_fit']}`",
                f"- band delta 0-1.5k / 1.5-3k / 3-8k: `{row['delta_band_0_1p5k_db']}` / `{row['delta_band_1p5_3k_db']}` / `{row['delta_band_3_8k_db']}`",
                f"- figure: `{Path(row['figure_path']).name}`",
                "",
            ]
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    queue_path = resolve_path(args.queue_csv)
    output_dir = resolve_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with queue_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if args.max_rows > 0:
        rows = rows[: args.max_rows]
    if not rows:
        raise ValueError("No rows found.")

    summary_rows = [
        plot_row(row, output_dir=output_dir, n_fft=args.n_fft, hop_length=args.hop_length)
        for row in rows
    ]
    write_summary(output_dir / "diagnostic_summary.csv", summary_rows)
    write_markdown(output_dir / "DIAGNOSTIC_SUMMARY.md", summary_rows)
    print(f"Wrote {output_dir / 'diagnostic_summary.csv'}")
    print(f"Wrote {output_dir / 'DIAGNOSTIC_SUMMARY.md'}")
    print(f"Figures: {len(summary_rows)}")


if __name__ == "__main__":
    main()
