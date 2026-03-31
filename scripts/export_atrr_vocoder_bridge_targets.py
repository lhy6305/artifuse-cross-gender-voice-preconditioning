from __future__ import annotations

import argparse
import csv
from pathlib import Path

import librosa
import numpy as np

from extract_resonance_distribution_diagnostics import (
    DEFAULT_QUEUE_CSV,
    ROOT,
    DistributionFeatures,
    build_distribution_features,
    build_weighted_target_prototype,
    fmt_float,
    load_audio,
    resolve_path,
    target_source_gender,
    write_csv,
)
from simulate_targetward_resonance_residual import (
    build_combined_core_mask,
    simulate_frames,
    summarize_simulation,
)


DEFAULT_OUTPUT_DIR = ROOT / "artifacts" / "diagnostics" / "atrr_vocoder_bridge_target_export_v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue-csv", default=str(DEFAULT_QUEUE_CSV))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--n-fft", type=int, default=2048)
    parser.add_argument("--hop-length", type=int, default=256)
    parser.add_argument("--n-mels", type=int, default=80)
    parser.add_argument("--fmin", type=float, default=50.0)
    parser.add_argument("--fmax", type=float, default=8000.0)
    parser.add_argument("--rms-threshold-db", type=float, default=-40.0)
    parser.add_argument("--core-energy-threshold", type=float, default=0.60)
    parser.add_argument("--frame-core-threshold", type=float, default=0.60)
    parser.add_argument("--occupancy-threshold", type=float, default=0.35)
    parser.add_argument("--core-step-size", type=float, default=0.70)
    parser.add_argument("--off-core-step-size", type=float, default=0.20)
    parser.add_argument("--frame-smoothness-weight", type=float, default=0.30)
    parser.add_argument("--max-bin-step", type=float, default=0.020)
    return parser.parse_args()


def dataset_slug(dataset_name: str) -> str:
    return "libritts_r" if dataset_name == "LibriTTS-R" else "vctk"


def compute_mel_power(
    audio: np.ndarray,
    sample_rate: int,
    *,
    n_fft: int,
    hop_length: int,
    n_mels: int,
    fmin: float,
    fmax: float,
) -> np.ndarray:
    target_fmax = min(float(fmax), sample_rate / 2.0)
    mel = librosa.feature.melspectrogram(
        y=audio.astype(np.float32),
        sr=sample_rate,
        n_fft=n_fft,
        hop_length=hop_length,
        power=2.0,
        n_mels=n_mels,
        fmin=fmin,
        fmax=target_fmax,
    ).astype(np.float64)
    return np.maximum(mel, 1e-12)


def export_target_npz(
    path: Path,
    *,
    row: dict[str, str],
    source_features: DistributionFeatures,
    target_prototype: np.ndarray,
    target_occupancy: np.ndarray,
    edited_frames: np.ndarray,
    source_mel_power: np.ndarray,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame_count = min(source_mel_power.shape[1], edited_frames.shape[0], source_features.voiced_mask.shape[0])
    source_mel_power = source_mel_power[:, :frame_count]
    edited_frames = edited_frames[:frame_count, :]
    voiced_mask = source_features.voiced_mask[:frame_count]

    target_mel_power = np.array(source_mel_power, dtype=np.float64, copy=True)
    source_frame_energy = np.sum(source_mel_power, axis=0)
    for frame_idx in range(frame_count):
        if not bool(voiced_mask[frame_idx]):
            continue
        target_mel_power[:, frame_idx] = np.maximum(edited_frames[frame_idx] * max(source_frame_energy[frame_idx], 1e-12), 1e-12)

    np.savez_compressed(
        path,
        rule_id=row["rule_id"],
        record_id=row["record_id"],
        utt_id=row["utt_id"],
        dataset_name=row["group_value"],
        source_gender=row["source_gender"],
        target_direction=row["target_direction"],
        f0_condition=row["f0_condition"],
        sample_rate=np.asarray([int(source_features.sample_rate)], dtype=np.int32),
        source_log_mel=np.log(source_mel_power).astype(np.float32),
        target_log_mel=np.log(target_mel_power).astype(np.float32),
        source_distribution=source_features.utterance_distribution.astype(np.float32),
        target_distribution=target_prototype.astype(np.float32),
        target_occupancy=target_occupancy.astype(np.float32),
        edited_frame_distributions=edited_frames.astype(np.float32),
        voiced_mask=voiced_mask.astype(np.int8),
    )


def write_summary_md(path: Path, rows: list[dict[str, str]], args: argparse.Namespace) -> None:
    strongest_rows = sorted(
        rows,
        key=lambda row: (
            float(row["sim_resonance_distribution_shift_score"]),
            float(row["sim_frame_improvement_mean"]),
        ),
        reverse=True,
    )[:3]
    weakest_rows = sorted(rows, key=lambda row: float(row["sim_resonance_distribution_shift_score"]))[:3]

    lines = [
        "# ATRR Vocoder Bridge Target Export v1",
        "",
        "## Parameters",
        "",
        f"- core_step_size: `{args.core_step_size:.3f}`",
        f"- off_core_step_size: `{args.off_core_step_size:.3f}`",
        f"- frame_smoothness_weight: `{args.frame_smoothness_weight:.3f}`",
        f"- max_bin_step: `{args.max_bin_step:.4f}`",
        "",
        "## Purpose",
        "",
        "- This export is machine-only.",
        "- It prepares edited target log-mel tensors for a future vocoder-based carrier.",
        "- It does not synthesize audio by itself.",
        "",
        "## Pack Summary",
        "",
        f"- rows: `{len(rows)}`",
        f"- avg simulated shift score: `{sum(float(row['sim_resonance_distribution_shift_score']) for row in rows) / len(rows):.2f}`",
        f"- avg simulated core coverage: `{sum(float(row['sim_core_resonance_coverage_score']) for row in rows) / len(rows):.2f}`",
        "",
        "## Strongest Rows",
        "",
    ]
    for row in strongest_rows:
        lines.append(
            f"- `{row['rule_id']}` | shift=`{row['sim_resonance_distribution_shift_score']}` | "
            f"coverage=`{row['sim_core_resonance_coverage_score']}` | export=`{row['target_npz']}`"
        )
    lines.extend(["", "## Weakest Rows", ""])
    for row in weakest_rows:
        lines.append(
            f"- `{row['rule_id']}` | shift=`{row['sim_resonance_distribution_shift_score']}` | "
            f"coverage=`{row['sim_core_resonance_coverage_score']}` | export=`{row['target_npz']}`"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    queue_csv = resolve_path(args.queue_csv)
    output_dir = resolve_path(args.output_dir)

    with queue_csv.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("Queue is empty.")

    feature_cache: dict[str, DistributionFeatures] = {}
    mel_cache: dict[str, np.ndarray] = {}

    def get_features(path_value: str) -> DistributionFeatures:
        cache_key = str(resolve_path(path_value))
        cached = feature_cache.get(cache_key)
        if cached is not None:
            return cached
        audio, sample_rate = load_audio(Path(cache_key))
        features = build_distribution_features(
            audio=audio,
            sample_rate=sample_rate,
            n_fft=args.n_fft,
            hop_length=args.hop_length,
            n_mels=args.n_mels,
            fmin=args.fmin,
            fmax=args.fmax,
            rms_threshold_db=args.rms_threshold_db,
            frame_core_threshold=args.frame_core_threshold,
        )
        feature_cache[cache_key] = features
        return features

    def get_mel_power(path_value: str) -> np.ndarray:
        cache_key = str(resolve_path(path_value))
        cached = mel_cache.get(cache_key)
        if cached is not None:
            return cached
        audio, sample_rate = load_audio(Path(cache_key))
        mel = compute_mel_power(
            audio,
            sample_rate,
            n_fft=args.n_fft,
            hop_length=args.hop_length,
            n_mels=args.n_mels,
            fmin=args.fmin,
            fmax=args.fmax,
        )
        mel_cache[cache_key] = mel
        return mel

    prototype_rows: dict[tuple[str, str], list[DistributionFeatures]] = {}
    for row in rows:
        original_features = get_features(row["original_copy"])
        key = (row["group_value"], row["source_gender"])
        prototype_rows.setdefault(key, []).append(original_features)

    export_rows: list[dict[str, str]] = []
    target_dir = output_dir / "targets"
    for row in rows:
        source = get_features(row["original_copy"])
        source_mel_power = get_mel_power(row["original_copy"])
        target_key = (row["group_value"], target_source_gender(row["target_direction"]))
        candidates = prototype_rows[target_key]
        target_prototype, target_occupancy, prototype_weight_sum = build_weighted_target_prototype(source, candidates)
        combined_core = build_combined_core_mask(
            source,
            target_prototype,
            target_occupancy,
            core_energy_threshold=args.core_energy_threshold,
            occupancy_threshold=args.occupancy_threshold,
        )
        edited_frames, _ = simulate_frames(
            source,
            target_prototype,
            combined_core,
            core_step_size=args.core_step_size,
            off_core_step_size=args.off_core_step_size,
            frame_smoothness_weight=args.frame_smoothness_weight,
            max_bin_step=args.max_bin_step,
        )

        export_name = f"{dataset_slug(row['group_value'])}__{row['source_gender']}__{row['target_direction']}__{row['utt_id']}.npz"
        export_path = target_dir / export_name
        export_target_npz(
            export_path,
            row=row,
            source_features=source,
            target_prototype=target_prototype,
            target_occupancy=target_occupancy,
            edited_frames=edited_frames,
            source_mel_power=source_mel_power,
        )

        summary_row = summarize_simulation(
            row,
            source,
            target_prototype,
            target_occupancy,
            core_energy_threshold=args.core_energy_threshold,
            occupancy_threshold=args.occupancy_threshold,
            core_step_size=args.core_step_size,
            off_core_step_size=args.off_core_step_size,
            frame_smoothness_weight=args.frame_smoothness_weight,
            max_bin_step=args.max_bin_step,
            prototype_weight_sum=prototype_weight_sum,
        )
        summary_row["target_npz"] = str(export_path)
        summary_row["source_log_mel_shape"] = f"{args.n_mels}x{min(source_mel_power.shape[1], edited_frames.shape[0])}"
        summary_row["target_f0_condition"] = row["f0_condition"]
        export_rows.append(summary_row)

    detail_csv = output_dir / "atrr_vocoder_bridge_target_export.csv"
    summary_md = output_dir / "ATRR_VOCODER_BRIDGE_TARGET_EXPORT.md"
    write_csv(detail_csv, export_rows)
    write_summary_md(summary_md, export_rows, args)
    print(f"Wrote {detail_csv}")
    print(f"Wrote {summary_md}")
    print(f"Targets: {len(export_rows)}")


if __name__ == "__main__":
    main()
