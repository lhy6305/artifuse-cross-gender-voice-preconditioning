from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np

from extract_resonance_distribution_diagnostics import (
    DEFAULT_QUEUE_CSV,
    ROOT,
    DistributionFeatures,
    build_distribution_features,
    build_weighted_target_prototype,
    clamp,
    core_mask,
    delta_entropy_penalty,
    fmt_float,
    load_audio,
    normalize_distribution,
    one_dim_emd,
    resolve_path,
    target_source_gender,
    write_csv,
)


DEFAULT_OUTPUT_DIR = ROOT / "artifacts" / "diagnostics" / "atrr_offline_simulator_v1"


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


def build_combined_core_mask(
    source: DistributionFeatures,
    target_prototype: np.ndarray,
    target_occupancy: np.ndarray,
    *,
    core_energy_threshold: float,
    occupancy_threshold: float,
) -> np.ndarray:
    source_core = core_mask(source.utterance_distribution, energy_threshold=core_energy_threshold)
    target_core = core_mask(target_prototype, energy_threshold=core_energy_threshold)
    source_occupancy_core = source.occupancy_distribution >= occupancy_threshold
    target_occupancy_core = target_occupancy >= occupancy_threshold
    return np.asarray(
        source_core | target_core | source_occupancy_core | target_occupancy_core,
        dtype=np.float64,
    )


def apply_targetward_step(
    source_distribution: np.ndarray,
    target_distribution: np.ndarray,
    core_mask_values: np.ndarray,
    *,
    core_step_size: float,
    off_core_step_size: float,
    max_bin_step: float,
) -> tuple[np.ndarray, np.ndarray]:
    target_delta = np.asarray(target_distribution - source_distribution, dtype=np.float64)
    step_scale = (core_step_size * core_mask_values) + (off_core_step_size * (1.0 - core_mask_values))
    residual = np.asarray(step_scale * target_delta, dtype=np.float64)
    residual = np.clip(residual, -max_bin_step, max_bin_step)
    edited = np.clip(source_distribution + residual, 1e-9, None)
    return normalize_distribution(edited), residual


def simulate_frames(
    source: DistributionFeatures,
    target_prototype: np.ndarray,
    core_mask_values: np.ndarray,
    *,
    core_step_size: float,
    off_core_step_size: float,
    frame_smoothness_weight: float,
    max_bin_step: float,
) -> tuple[np.ndarray, np.ndarray]:
    frame_count = source.frame_distributions.shape[0]
    edited_frames = np.asarray(source.frame_distributions.copy(), dtype=np.float64)
    residual_frames = np.zeros_like(edited_frames)
    previous_residual: np.ndarray | None = None

    smoothness = clamp(frame_smoothness_weight, 0.0, 0.95)
    for frame_idx in range(frame_count):
        if not bool(source.voiced_mask[frame_idx]):
            continue
        frame_source = source.frame_distributions[frame_idx]
        _, raw_residual = apply_targetward_step(
            frame_source,
            target_prototype,
            core_mask_values,
            core_step_size=core_step_size,
            off_core_step_size=off_core_step_size,
            max_bin_step=max_bin_step,
        )
        if previous_residual is None:
            smoothed_residual = raw_residual
        else:
            smoothed_residual = ((1.0 - smoothness) * raw_residual) + (smoothness * previous_residual)
        edited_frames[frame_idx] = normalize_distribution(np.clip(frame_source + smoothed_residual, 1e-9, None))
        residual_frames[frame_idx] = smoothed_residual
        previous_residual = smoothed_residual

    return edited_frames, residual_frames


def summarize_simulation(
    row: dict[str, str],
    source: DistributionFeatures,
    target_prototype: np.ndarray,
    target_occupancy: np.ndarray,
    *,
    core_energy_threshold: float,
    occupancy_threshold: float,
    core_step_size: float,
    off_core_step_size: float,
    frame_smoothness_weight: float,
    max_bin_step: float,
    prototype_weight_sum: float,
) -> dict[str, str]:
    combined_core = build_combined_core_mask(
        source,
        target_prototype,
        target_occupancy,
        core_energy_threshold=core_energy_threshold,
        occupancy_threshold=occupancy_threshold,
    )
    edited_frames, residual_frames = simulate_frames(
        source,
        target_prototype,
        combined_core,
        core_step_size=core_step_size,
        off_core_step_size=off_core_step_size,
        frame_smoothness_weight=frame_smoothness_weight,
        max_bin_step=max_bin_step,
    )

    usable_frames = edited_frames[source.voiced_mask]
    if usable_frames.shape[0] == 0:
        usable_frames = edited_frames
    edited_distribution = normalize_distribution(np.mean(usable_frames, axis=0))

    original_to_target = one_dim_emd(source.utterance_distribution, target_prototype)
    edited_to_target = one_dim_emd(edited_distribution, target_prototype)
    improvement_ratio = 0.0 if original_to_target <= 1e-12 else (original_to_target - edited_to_target) / original_to_target
    shift_score = clamp(50.0 + 50.0 * improvement_ratio, 0.0, 100.0)

    delta_distribution = np.abs(edited_distribution - source.utterance_distribution)
    delta_total = float(np.sum(delta_distribution))
    if delta_total <= 1e-12:
        core_coverage = 0.0
    else:
        core_coverage = float(np.sum(delta_distribution[combined_core > 0.5]) / delta_total * 100.0)
    localization_penalty = delta_entropy_penalty(delta_distribution)

    frame_improvements: list[float] = []
    frame_residual_norms: list[float] = []
    for frame_idx in range(source.frame_distributions.shape[0]):
        if not bool(source.voiced_mask[frame_idx]):
            continue
        source_frame = source.frame_distributions[frame_idx]
        edited_frame = edited_frames[frame_idx]
        source_distance = one_dim_emd(source_frame, target_prototype)
        edited_distance = one_dim_emd(edited_frame, target_prototype)
        frame_improvements.append(source_distance - edited_distance)
        frame_residual_norms.append(float(np.sum(np.abs(residual_frames[frame_idx]))))

    if frame_improvements:
        context_consistency = float(sum(1 for value in frame_improvements if value > 0.0) / len(frame_improvements) * 100.0)
        frame_improvement_mean = float(sum(frame_improvements) / len(frame_improvements))
    else:
        context_consistency = 0.0
        frame_improvement_mean = 0.0

    if frame_residual_norms:
        mean_frame_residual_l1 = float(sum(frame_residual_norms) / len(frame_residual_norms))
    else:
        mean_frame_residual_l1 = 0.0

    return {
        "rule_id": row["rule_id"],
        "record_id": row["record_id"],
        "group_value": row["group_value"],
        "source_gender": row["source_gender"],
        "target_direction": row["target_direction"],
        "prototype_weight_sum": fmt_float(prototype_weight_sum),
        "core_step_size": fmt_float(core_step_size, digits=3),
        "off_core_step_size": fmt_float(off_core_step_size, digits=3),
        "frame_smoothness_weight": fmt_float(frame_smoothness_weight, digits=3),
        "max_bin_step": fmt_float(max_bin_step, digits=4),
        "sim_original_to_target_emd": fmt_float(original_to_target),
        "sim_edited_to_target_emd": fmt_float(edited_to_target),
        "sim_resonance_distribution_shift_score": fmt_float(shift_score, digits=2),
        "sim_core_resonance_coverage_score": fmt_float(core_coverage, digits=2),
        "sim_over_localized_edit_penalty": fmt_float(localization_penalty, digits=2),
        "sim_context_consistency_score": fmt_float(context_consistency, digits=2),
        "sim_frame_improvement_mean": fmt_float(frame_improvement_mean),
        "sim_mean_frame_residual_l1": fmt_float(mean_frame_residual_l1),
        "sim_core_support_width_bins": str(int(np.sum(combined_core > 0.5))),
        "sim_delta_mass_in_core_ratio": fmt_float(core_coverage / 100.0),
        "sim_voiced_frame_count_used": str(len(frame_improvements)),
    }


def avg(rows: list[dict[str, str]], field: str) -> float:
    values = [float(row[field]) for row in rows]
    return float(sum(values) / max(len(values), 1))


def write_summary(path: Path, rows: list[dict[str, str]], args: argparse.Namespace) -> None:
    by_direction: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_direction.setdefault(row["target_direction"], []).append(row)

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
        "# ATRR Offline Simulator Summary",
        "",
        "## Parameters",
        "",
        f"- core_step_size: `{args.core_step_size:.3f}`",
        f"- off_core_step_size: `{args.off_core_step_size:.3f}`",
        f"- frame_smoothness_weight: `{args.frame_smoothness_weight:.3f}`",
        f"- max_bin_step: `{args.max_bin_step:.4f}`",
        "",
        "## Pack Summary",
        "",
        f"- rows: `{len(rows)}`",
        f"- avg sim_resonance_distribution_shift_score: `{avg(rows, 'sim_resonance_distribution_shift_score'):.2f}`",
        f"- avg sim_core_resonance_coverage_score: `{avg(rows, 'sim_core_resonance_coverage_score'):.2f}`",
        f"- avg sim_over_localized_edit_penalty: `{avg(rows, 'sim_over_localized_edit_penalty'):.2f}`",
        f"- avg sim_context_consistency_score: `{avg(rows, 'sim_context_consistency_score'):.2f}`",
        f"- avg sim_frame_improvement_mean: `{avg(rows, 'sim_frame_improvement_mean'):.6f}`",
        "",
        "## By Direction",
        "",
    ]

    for direction, direction_rows in sorted(by_direction.items()):
        lines.extend(
            [
                f"### `{direction}`",
                "",
                f"- avg shift score: `{avg(direction_rows, 'sim_resonance_distribution_shift_score'):.2f}`",
                f"- avg core coverage: `{avg(direction_rows, 'sim_core_resonance_coverage_score'):.2f}`",
                f"- avg localization penalty: `{avg(direction_rows, 'sim_over_localized_edit_penalty'):.2f}`",
                f"- avg context consistency: `{avg(direction_rows, 'sim_context_consistency_score'):.2f}`",
                f"- avg frame improvement mean: `{avg(direction_rows, 'sim_frame_improvement_mean'):.6f}`",
                "",
            ]
        )

    lines.extend(["## Strongest Rows", ""])
    for row in strongest_rows:
        lines.append(
            f"- `{row['rule_id']}` | shift=`{row['sim_resonance_distribution_shift_score']}` | "
            f"frame_improvement=`{row['sim_frame_improvement_mean']}` | "
            f"coverage=`{row['sim_core_resonance_coverage_score']}`"
        )

    lines.extend(["", "## Weakest Rows", ""])
    for row in weakest_rows:
        lines.append(
            f"- `{row['rule_id']}` | shift=`{row['sim_resonance_distribution_shift_score']}` | "
            f"frame_improvement=`{row['sim_frame_improvement_mean']}` | "
            f"coverage=`{row['sim_core_resonance_coverage_score']}`"
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

    prototype_rows: dict[tuple[str, str], list[DistributionFeatures]] = {}
    for row in rows:
        original_features = get_features(row["original_copy"])
        key = (row["group_value"], row["source_gender"])
        prototype_rows.setdefault(key, []).append(original_features)

    output_rows: list[dict[str, str]] = []
    for row in rows:
        source = get_features(row["original_copy"])
        target_key = (row["group_value"], target_source_gender(row["target_direction"]))
        candidates = prototype_rows[target_key]
        target_prototype, target_occupancy, prototype_weight_sum = build_weighted_target_prototype(source, candidates)
        output_rows.append(
            summarize_simulation(
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
        )

    detail_csv = output_dir / "atrr_offline_simulation_summary.csv"
    summary_md = output_dir / "ATRR_OFFLINE_SIMULATION_SUMMARY.md"
    write_csv(detail_csv, output_rows)
    write_summary(summary_md, output_rows, args)
    print(f"Wrote {detail_csv}")
    print(f"Wrote {summary_md}")
    print(f"Rows: {len(output_rows)}")


if __name__ == "__main__":
    main()
