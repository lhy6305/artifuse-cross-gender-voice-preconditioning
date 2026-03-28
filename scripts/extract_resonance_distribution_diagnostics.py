from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from pathlib import Path

import librosa
import numpy as np

from apply_stage0_rule_preconditioner import load_audio


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUEUE_CSV = ROOT / "artifacts" / "listening_review" / "stage0_speech_lsf_listening_pack" / "v7" / "listening_review_queue.csv"
DEFAULT_OUTPUT_DIR = ROOT / "artifacts" / "diagnostics" / "lsf_v7_resonance_distribution_v1"


@dataclass
class DistributionFeatures:
    utterance_distribution: np.ndarray
    frame_distributions: np.ndarray
    voiced_mask: np.ndarray
    rms_db: np.ndarray
    sample_rate: int
    f0_median_hz: float
    occupancy_distribution: np.ndarray


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
    return parser.parse_args()


def resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return ROOT / path


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def normalize_distribution(vector: np.ndarray) -> np.ndarray:
    total = float(np.sum(vector))
    if total <= 0.0:
        return np.full_like(vector, 1.0 / max(vector.shape[0], 1), dtype=np.float64)
    return np.asarray(vector / total, dtype=np.float64)


def safe_log(value: float) -> float:
    return math.log(max(value, 1e-12))


def one_dim_emd(left: np.ndarray, right: np.ndarray) -> float:
    left_cdf = np.cumsum(normalize_distribution(left))
    right_cdf = np.cumsum(normalize_distribution(right))
    return float(np.mean(np.abs(left_cdf - right_cdf)))


def core_mask(distribution: np.ndarray, *, energy_threshold: float) -> np.ndarray:
    ordered = np.argsort(distribution)[::-1]
    cumulative = 0.0
    mask = np.zeros_like(distribution, dtype=bool)
    for idx in ordered:
        cumulative += float(distribution[idx])
        mask[idx] = True
        if cumulative >= energy_threshold:
            break
    return mask


def delta_entropy_penalty(delta_distribution: np.ndarray) -> float:
    normalized = normalize_distribution(delta_distribution)
    entropy = -float(np.sum(normalized * np.vectorize(safe_log)(normalized)))
    max_entropy = safe_log(float(normalized.shape[0]))
    if max_entropy <= 0.0:
        return 100.0
    entropy_ratio = entropy / max_entropy
    return clamp((1.0 - entropy_ratio) * 100.0, 0.0, 100.0)


def weighted_average(vectors: list[np.ndarray], weights: list[float]) -> np.ndarray:
    clean_weights = np.asarray(weights, dtype=np.float64)
    if clean_weights.size == 0 or float(np.sum(clean_weights)) <= 0.0:
        return normalize_distribution(np.mean(np.vstack(vectors), axis=0))
    normalized_weights = clean_weights / float(np.sum(clean_weights))
    stacked = np.vstack(vectors)
    return normalize_distribution(np.sum(stacked * normalized_weights[:, None], axis=0))


def weighted_mean(vectors: list[np.ndarray], weights: list[float]) -> np.ndarray:
    clean_weights = np.asarray(weights, dtype=np.float64)
    if clean_weights.size == 0 or float(np.sum(clean_weights)) <= 0.0:
        return np.asarray(np.mean(np.vstack(vectors), axis=0), dtype=np.float64)
    normalized_weights = clean_weights / float(np.sum(clean_weights))
    stacked = np.vstack(vectors)
    return np.asarray(np.sum(stacked * normalized_weights[:, None], axis=0), dtype=np.float64)


def top_energy_mask(distribution: np.ndarray, *, energy_threshold: float) -> np.ndarray:
    return core_mask(distribution, energy_threshold=energy_threshold)


def prototype_weight(
    source: DistributionFeatures,
    target: DistributionFeatures,
) -> float:
    f0_source = max(source.f0_median_hz, 1e-6)
    f0_target = max(target.f0_median_hz, 1e-6)
    f0_distance = abs(math.log(f0_source) - math.log(f0_target))
    shape_distance = one_dim_emd(source.utterance_distribution, target.utterance_distribution)
    f0_weight = math.exp(-f0_distance / 0.35)
    shape_weight = math.exp(-shape_distance / 0.020)
    return float(max(f0_weight * shape_weight, 1e-6))


def build_weighted_target_prototype(
    source: DistributionFeatures,
    candidates: list[DistributionFeatures],
) -> tuple[np.ndarray, np.ndarray, float]:
    weights = [prototype_weight(source, candidate) for candidate in candidates]
    prototype = weighted_average([candidate.utterance_distribution for candidate in candidates], weights)
    occupancy = weighted_mean([candidate.occupancy_distribution for candidate in candidates], weights)
    return prototype, occupancy, float(sum(weights))


def build_distribution_features(
    audio: np.ndarray,
    sample_rate: int,
    *,
    n_fft: int,
    hop_length: int,
    n_mels: int,
    fmin: float,
    fmax: float,
    rms_threshold_db: float,
    frame_core_threshold: float,
) -> DistributionFeatures:
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
    rms = librosa.feature.rms(y=audio.astype(np.float32), frame_length=n_fft, hop_length=hop_length, center=True)[0].astype(np.float64)
    f0, voiced_flag, _ = librosa.pyin(
        audio.astype(np.float32),
        fmin=librosa.note_to_hz("C2"),
        fmax=librosa.note_to_hz("C6"),
        sr=sample_rate,
        frame_length=n_fft,
        hop_length=hop_length,
    )
    voiced_f0 = np.asarray(f0, dtype=np.float64)
    frame_count = min(mel.shape[1], rms.shape[0], voiced_flag.shape[0])
    mel = mel[:, :frame_count]
    rms = rms[:frame_count]
    voiced = np.asarray(np.nan_to_num(voiced_flag[:frame_count].astype(np.float32), nan=0.0) > 0.5, dtype=bool)
    voiced_f0 = voiced_f0[:frame_count]
    if frame_count == 0:
        raise ValueError("No analysis frames available.")

    rms_ref = float(np.max(rms)) if float(np.max(rms)) > 0.0 else 1e-12
    rms_db = librosa.amplitude_to_db(rms, ref=rms_ref)
    active = rms_db >= rms_threshold_db
    usable = voiced & active
    if int(np.sum(usable)) < max(4, frame_count // 20):
        usable = active

    frame_distributions = np.zeros((frame_count, n_mels), dtype=np.float64)
    frame_core_masks = np.zeros((frame_count, n_mels), dtype=np.float64)
    for frame_idx in range(frame_count):
        frame_distributions[frame_idx] = normalize_distribution(mel[:, frame_idx])
        frame_core_masks[frame_idx] = top_energy_mask(frame_distributions[frame_idx], energy_threshold=frame_core_threshold).astype(np.float64)

    usable_frames = frame_distributions[usable]
    usable_core_masks = frame_core_masks[usable]
    if usable_frames.shape[0] == 0:
        usable_frames = frame_distributions
        usable_core_masks = frame_core_masks
    utterance_distribution = normalize_distribution(np.mean(usable_frames, axis=0))
    occupancy_distribution = np.asarray(np.mean(usable_core_masks, axis=0), dtype=np.float64)
    usable_f0 = voiced_f0[usable & np.isfinite(voiced_f0)]
    if usable_f0.size == 0:
        usable_f0 = voiced_f0[np.isfinite(voiced_f0)]
    f0_median_hz = float(np.median(usable_f0)) if usable_f0.size > 0 else 150.0

    return DistributionFeatures(
        utterance_distribution=utterance_distribution,
        frame_distributions=frame_distributions,
        voiced_mask=usable,
        rms_db=np.asarray(rms_db, dtype=np.float64),
        sample_rate=sample_rate,
        f0_median_hz=f0_median_hz,
        occupancy_distribution=occupancy_distribution,
    )


def target_source_gender(target_direction: str) -> str:
    return "male" if target_direction == "masculine" else "female"


def fmt_float(value: float, digits: int = 6) -> str:
    return f"{value:.{digits}f}"


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError("No rows to write.")
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def avg(rows: list[dict[str, str]], field: str) -> float:
    values = [float(row[field]) for row in rows]
    return float(sum(values) / max(len(values), 1))


def write_summary(path: Path, rows: list[dict[str, str]]) -> None:
    by_direction: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_direction.setdefault(row["target_direction"], []).append(row)

    weakest_core = sorted(rows, key=lambda row: float(row["core_resonance_coverage_score"]))[:3]
    weakest_shift = sorted(rows, key=lambda row: float(row["resonance_distribution_shift_score"]))[:3]

    lines = [
        "# Resonance Distribution Diagnostic Summary",
        "",
        f"- rows: `{len(rows)}`",
        f"- avg resonance_distribution_shift_score: `{avg(rows, 'resonance_distribution_shift_score'):.2f}`",
        f"- avg core_resonance_coverage_score: `{avg(rows, 'core_resonance_coverage_score'):.2f}`",
        f"- avg over_localized_edit_penalty: `{avg(rows, 'over_localized_edit_penalty'):.2f}`",
        f"- avg context_consistency_score: `{avg(rows, 'context_consistency_score'):.2f}`",
        f"- avg frame_improvement_mean: `{avg(rows, 'frame_improvement_mean'):.6f}`",
        "",
        "## By Direction",
        "",
    ]
    for direction, direction_rows in sorted(by_direction.items()):
        lines.extend(
            [
                f"### `{direction}`",
                "",
                f"- avg shift score: `{avg(direction_rows, 'resonance_distribution_shift_score'):.2f}`",
                f"- avg core coverage: `{avg(direction_rows, 'core_resonance_coverage_score'):.2f}`",
                f"- avg localization penalty: `{avg(direction_rows, 'over_localized_edit_penalty'):.2f}`",
                f"- avg context consistency: `{avg(direction_rows, 'context_consistency_score'):.2f}`",
                f"- avg frame improvement mean: `{avg(direction_rows, 'frame_improvement_mean'):.6f}`",
                "",
            ]
        )

    lines.extend(["## Lowest Core Coverage Rows", ""])
    for row in weakest_core:
        lines.append(
            f"- `{row['rule_id']}` | coverage=`{row['core_resonance_coverage_score']}` | "
            f"shift=`{row['resonance_distribution_shift_score']}` | "
            f"localization_penalty=`{row['over_localized_edit_penalty']}`"
        )

    lines.extend(["", "## Weakest Shift Rows", ""])
    for row in weakest_shift:
        lines.append(
            f"- `{row['rule_id']}` | shift=`{row['resonance_distribution_shift_score']}` | "
            f"orig_target_emd=`{row['original_to_target_emd']}` | "
            f"proc_target_emd=`{row['processed_to_target_emd']}`"
        )

    lines.extend(
        [
            "",
            "## Diagnostic Reading",
            "",
            "- `resonance_distribution_shift_score` uses a 1D distribution-distance improvement measure toward a weighted target-gender prototype conditioned by F0 proximity and distribution similarity.",
            "- `core_resonance_coverage_score` measures how much of the edit lands inside the combined core support of source and target energy distributions plus persistent occupancy support.",
            "- `over_localized_edit_penalty` is high when the edit mass is too concentrated in a narrow region.",
            "- `context_consistency_score` measures how often frame-level movement toward the target prototype is positive on voiced active frames.",
        ]
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
        original = get_features(row["original_copy"])
        processed = get_features(row["processed_audio"])
        target_key = (row["group_value"], target_source_gender(row["target_direction"]))
        candidates = prototype_rows[target_key]
        target_prototype, target_occupancy, prototype_weight_sum = build_weighted_target_prototype(original, candidates)

        original_to_target = one_dim_emd(original.utterance_distribution, target_prototype)
        processed_to_target = one_dim_emd(processed.utterance_distribution, target_prototype)
        improvement_ratio = 0.0 if original_to_target <= 1e-12 else (original_to_target - processed_to_target) / original_to_target
        shift_score = clamp(50.0 + 50.0 * improvement_ratio, 0.0, 100.0)

        source_core = core_mask(original.utterance_distribution, energy_threshold=args.core_energy_threshold)
        target_core = core_mask(target_prototype, energy_threshold=args.core_energy_threshold)
        source_occupancy_core = original.occupancy_distribution >= args.occupancy_threshold
        target_occupancy_core = target_occupancy >= args.occupancy_threshold
        combined_core = source_core | target_core | source_occupancy_core | target_occupancy_core
        delta_distribution = np.abs(processed.utterance_distribution - original.utterance_distribution)
        delta_total = float(np.sum(delta_distribution))
        if delta_total <= 1e-12:
            core_coverage = 0.0
        else:
            core_coverage = float(np.sum(delta_distribution[combined_core]) / delta_total * 100.0)
        localization_penalty = delta_entropy_penalty(delta_distribution)

        frame_count = min(original.frame_distributions.shape[0], processed.frame_distributions.shape[0], original.voiced_mask.shape[0], processed.voiced_mask.shape[0])
        frame_improvements: list[float] = []
        for frame_idx in range(frame_count):
            if not bool(original.voiced_mask[frame_idx] and processed.voiced_mask[frame_idx]):
                continue
            orig_frame = original.frame_distributions[frame_idx]
            proc_frame = processed.frame_distributions[frame_idx]
            orig_frame_dist = one_dim_emd(orig_frame, target_prototype)
            proc_frame_dist = one_dim_emd(proc_frame, target_prototype)
            frame_improvements.append(orig_frame_dist - proc_frame_dist)
        if frame_improvements:
            context_consistency = float(sum(1 for item in frame_improvements if item > 0.0) / len(frame_improvements) * 100.0)
            frame_improvement_mean = float(sum(frame_improvements) / len(frame_improvements))
        else:
            context_consistency = 0.0
            frame_improvement_mean = 0.0

        output_rows.append(
            {
                "rule_id": row["rule_id"],
                "record_id": row["record_id"],
                "group_value": row["group_value"],
                "source_gender": row["source_gender"],
                "target_direction": row["target_direction"],
                "review_status": row.get("review_status", ""),
                "effect_audible": row.get("effect_audible", ""),
                "strength_fit": row.get("strength_fit", ""),
                "original_to_target_emd": fmt_float(original_to_target),
                "processed_to_target_emd": fmt_float(processed_to_target),
                "resonance_distribution_shift_score": fmt_float(shift_score, digits=2),
                "core_resonance_coverage_score": fmt_float(core_coverage, digits=2),
                "over_localized_edit_penalty": fmt_float(localization_penalty, digits=2),
                "context_consistency_score": fmt_float(context_consistency, digits=2),
                "frame_improvement_mean": fmt_float(frame_improvement_mean),
                "target_prototype_weight_sum": fmt_float(prototype_weight_sum),
                "target_prototype_f0_median_hz": fmt_float(float(np.mean([candidate.f0_median_hz for candidate in candidates]))),
                "core_support_width_bins": str(int(np.sum(combined_core))),
                "delta_mass_in_core_ratio": fmt_float(core_coverage / 100.0),
                "voiced_frame_count_used": str(len(frame_improvements)),
            }
        )

    detail_csv = output_dir / "resonance_distribution_diagnostic_summary.csv"
    summary_md = output_dir / "RESONANCE_DISTRIBUTION_DIAGNOSTIC_SUMMARY.md"
    write_csv(detail_csv, output_rows)
    write_summary(summary_md, output_rows)
    print(f"Wrote {detail_csv}")
    print(f"Wrote {summary_md}")
    print(f"Rows: {len(output_rows)}")


if __name__ == "__main__":
    main()
