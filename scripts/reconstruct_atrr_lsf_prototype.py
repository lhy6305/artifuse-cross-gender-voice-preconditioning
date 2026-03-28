from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import librosa
import numpy as np
import scipy.signal

from apply_stage0_rule_preconditioner import load_audio, resolve_path, save_audio
from build_stage0_rule_review_queue import (
    band_share_db,
    delta,
    feature_map,
    fmt_float,
    pct_delta,
    stft_logmag_l1,
    waveform_diff,
)
from build_stage0_speech_lsf_listening_pack import edit_lsf_pairs, lpc_to_lsf, lsf_to_lpc
from extract_resonance_distribution_diagnostics import (
    DEFAULT_QUEUE_CSV,
    DistributionFeatures,
    build_distribution_features,
    build_weighted_target_prototype,
    delta_entropy_penalty,
    normalize_distribution,
    one_dim_emd,
    write_csv,
)
from simulate_targetward_resonance_residual import build_combined_core_mask, simulate_frames
from stage0_speech_resonance_pack_common import (
    analyze_f0,
    build_enabled_directional_rule_lookup,
    frame_centers_sec,
    interpolate_voiced_mask,
    load_json,
    overlap_add,
    safe_rms,
    stable_lpc,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RULE_CONFIG = ROOT / "experiments" / "stage0_baseline" / "v1_full" / "speech_lsf_resonance_candidate_v7.json"
DEFAULT_OUTPUT_DIR = ROOT / "artifacts" / "diagnostics" / "atrr_lsf_reconstruction_prototype_v1"
DEFAULT_OBSERVED_DIAGNOSTICS = ROOT / "artifacts" / "diagnostics" / "lsf_v7_resonance_distribution_v2" / "resonance_distribution_diagnostic_summary.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue-csv", default=str(DEFAULT_QUEUE_CSV))
    parser.add_argument("--rule-config", default=str(DEFAULT_RULE_CONFIG))
    parser.add_argument("--observed-diagnostics-csv", default=str(DEFAULT_OBSERVED_DIAGNOSTICS))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--audio-format", choices=["wav", "flac"], default="wav")
    parser.add_argument("--n-fft", type=int, default=2048)
    parser.add_argument("--hop-length", type=int, default=256)
    parser.add_argument("--n-mels", type=int, default=80)
    parser.add_argument("--fmin", type=float, default=50.0)
    parser.add_argument("--fmax", type=float, default=8000.0)
    parser.add_argument("--rms-threshold-db", type=float, default=-40.0)
    parser.add_argument("--frame-core-threshold", type=float, default=0.60)
    parser.add_argument("--core-energy-threshold", type=float, default=0.60)
    parser.add_argument("--occupancy-threshold", type=float, default=0.35)
    parser.add_argument("--core-step-size", type=float, default=0.50)
    parser.add_argument("--off-core-step-size", type=float, default=0.15)
    parser.add_argument("--frame-smoothness-weight", type=float, default=0.30)
    parser.add_argument("--max-bin-step", type=float, default=0.0085)
    parser.add_argument("--peak-limit", type=float, default=0.98)
    parser.add_argument("--world-sr", type=int, default=16000)
    parser.add_argument("--frame-period-ms", type=float, default=10.0)
    parser.add_argument("--preserve-highband-from-hz", type=float, default=3000.0)
    return parser.parse_args()


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("Queue is empty.")
    return rows


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def nearest_indices(source_times: np.ndarray, target_times: np.ndarray) -> np.ndarray:
    if source_times.size == 0 or target_times.size == 0:
        return np.zeros(target_times.shape[0], dtype=np.int64)
    insertion = np.searchsorted(source_times, target_times, side="left")
    insertion = np.clip(insertion, 0, source_times.shape[0] - 1)
    previous = np.clip(insertion - 1, 0, source_times.shape[0] - 1)
    choose_previous = np.abs(target_times - source_times[previous]) <= np.abs(source_times[insertion] - target_times)
    return np.where(choose_previous, previous, insertion).astype(np.int64)


def weighted_centroid_and_width(freqs_hz: np.ndarray, values: np.ndarray) -> tuple[float, float]:
    total = float(np.sum(values))
    if total <= 1e-12:
        return float(np.mean(freqs_hz)), 1.0
    centroid = float(np.sum(freqs_hz * values) / total)
    variance = float(np.sum(values * np.square(freqs_hz - centroid)) / total)
    return centroid, math.sqrt(max(variance, 1.0))


def damp_ratio(value: float, factor: float) -> float:
    return 1.0 + factor * (value - 1.0)


def build_dynamic_pair_controls(
    *,
    source_distribution: np.ndarray,
    target_distribution: np.ndarray,
    mel_freqs_hz: np.ndarray,
    search_ranges_hz: list[list[float]],
    default_center_shift_ratios: list[float],
    default_pair_width_ratios: list[float] | None,
    damping: float,
) -> tuple[list[float], list[float]]:
    width_defaults = default_pair_width_ratios if default_pair_width_ratios is not None else [1.0] * len(search_ranges_hz)
    center_ratios: list[float] = []
    width_ratios: list[float] = []
    for search_range_hz, default_center_ratio, default_width_ratio in zip(
        search_ranges_hz,
        default_center_shift_ratios,
        width_defaults,
        strict=False,
    ):
        low_hz, high_hz = float(search_range_hz[0]), float(search_range_hz[1])
        mask = (mel_freqs_hz >= low_hz) & (mel_freqs_hz <= high_hz)
        if not np.any(mask):
            center_ratios.append(1.0)
            width_ratios.append(1.0)
            continue
        source_slice = source_distribution[mask]
        target_slice = target_distribution[mask]
        slice_freqs_hz = mel_freqs_hz[mask]
        slice_delta = float(np.sum(np.abs(target_slice - source_slice)))
        local_strength = clamp(slice_delta / 0.12, 0.0, 1.0)
        source_centroid, source_width = weighted_centroid_and_width(slice_freqs_hz, source_slice)
        target_centroid, target_width = weighted_centroid_and_width(slice_freqs_hz, target_slice)
        raw_center_ratio = target_centroid / max(source_centroid, 1.0)
        raw_width_ratio = target_width / max(source_width, 1.0)
        dynamic_center_ratio = 1.0 + local_strength * clamp(raw_center_ratio - 1.0, -0.12, 0.12)
        dynamic_width_ratio = 1.0 + local_strength * clamp(raw_width_ratio - 1.0, -0.18, 0.18)
        if default_center_ratio > 1.0:
            dynamic_center_ratio = clamp(dynamic_center_ratio, 1.0, max(1.0, default_center_ratio))
        elif default_center_ratio < 1.0:
            dynamic_center_ratio = clamp(dynamic_center_ratio, min(1.0, default_center_ratio), 1.0)
        else:
            dynamic_center_ratio = clamp(dynamic_center_ratio, 0.94, 1.06)
        if default_width_ratio > 1.0:
            dynamic_width_ratio = clamp(dynamic_width_ratio, 1.0, max(1.0, default_width_ratio))
        elif default_width_ratio < 1.0:
            dynamic_width_ratio = clamp(dynamic_width_ratio, min(1.0, default_width_ratio), 1.0)
        else:
            dynamic_width_ratio = clamp(dynamic_width_ratio, 0.92, 1.08)
        center_ratios.append(damp_ratio(dynamic_center_ratio, damping))
        width_ratios.append(damp_ratio(dynamic_width_ratio, damping))
    return center_ratios, width_ratios


def build_mel_filter(
    *,
    sample_rate: int,
    n_fft: int,
    n_mels: int,
    fmin: float,
    fmax: float,
) -> tuple[np.ndarray, np.ndarray]:
    target_fmax = min(float(fmax), sample_rate / 2.0)
    mel_filter = librosa.filters.mel(
        sr=sample_rate,
        n_fft=n_fft,
        n_mels=n_mels,
        fmin=fmin,
        fmax=target_fmax,
        norm="slaney",
    ).astype(np.float64)
    mel_freqs_hz = librosa.mel_frequencies(n_mels=n_mels, fmin=fmin, fmax=target_fmax).astype(np.float64)
    return mel_filter, mel_freqs_hz


def lpc_response_distribution(
    coeffs: np.ndarray,
    *,
    sample_rate: int,
    n_fft: int,
    mel_filter: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    _, response = scipy.signal.freqz([1.0], coeffs.astype(np.float64), worN=n_fft // 2 + 1, fs=sample_rate)
    power = np.square(np.abs(response)).astype(np.float64)
    mel_power = np.dot(mel_filter, power)
    distribution = normalize_distribution(np.maximum(mel_power, 1e-12))
    log_power = np.log(np.maximum(power, 1e-12))
    return distribution, log_power


def weighted_l1(left: np.ndarray, right: np.ndarray, weights: np.ndarray | None = None) -> float:
    delta_values = np.abs(np.asarray(left, dtype=np.float64) - np.asarray(right, dtype=np.float64))
    if weights is None:
        return float(np.mean(delta_values))
    clean_weights = np.asarray(weights, dtype=np.float64)
    weight_sum = float(np.sum(clean_weights))
    if weight_sum <= 1e-12:
        return float(np.mean(delta_values))
    return float(np.sum(delta_values * clean_weights) / weight_sum)


def synthesize_frame(
    frame: np.ndarray,
    *,
    original_coeffs: np.ndarray,
    edited_coeffs: np.ndarray,
    blend: float,
) -> np.ndarray:
    residual = scipy.signal.lfilter(original_coeffs, [1.0], frame.astype(np.float64))
    synthesized = scipy.signal.lfilter([1.0], edited_coeffs, residual).astype(np.float32)
    synth_rms = safe_rms(synthesized)
    frame_rms = safe_rms(frame)
    if synth_rms > 1e-8 and frame_rms > 1e-8:
        synthesized = synthesized * (frame_rms / synth_rms)
    return ((1.0 - blend) * frame.astype(np.float32) + blend * synthesized).astype(np.float32)


def avg(values: list[float]) -> float:
    return float(sum(values) / max(len(values), 1))


def row_mean(values: list[list[float]], index: int) -> float:
    selected = [row[index] for row in values if len(row) > index]
    return avg(selected) if selected else 1.0


def try_fit_lsf_frame(
    *,
    frame: np.ndarray,
    coeffs: np.ndarray,
    lsf: np.ndarray,
    source_distribution: np.ndarray,
    target_distribution: np.ndarray,
    combined_core: np.ndarray,
    rule_params: dict,
    sample_rate: int,
    n_fft: int,
    mel_filter: np.ndarray,
    mel_freqs_hz: np.ndarray,
    preserve_highband_from_hz: float,
) -> dict[str, object]:
    original_distribution, original_log_power = lpc_response_distribution(
        coeffs,
        sample_rate=sample_rate,
        n_fft=n_fft,
        mel_filter=mel_filter,
    )
    original_fit = weighted_l1(original_distribution, target_distribution)
    original_core_fit = weighted_l1(original_distribution, target_distribution, weights=combined_core)
    original_objective = original_fit + 0.4 * original_core_fit

    best: dict[str, object] | None = None
    default_centers = [float(value) for value in rule_params["center_shift_ratios"]]
    default_widths = [float(value) for value in rule_params["pair_width_ratios"]] if "pair_width_ratios" in rule_params else None

    for damping in [1.0, 0.8, 0.6, 0.4]:
        center_ratios, width_ratios = build_dynamic_pair_controls(
            source_distribution=source_distribution,
            target_distribution=target_distribution,
            mel_freqs_hz=mel_freqs_hz,
            search_ranges_hz=rule_params["search_ranges_hz"],
            default_center_shift_ratios=default_centers,
            default_pair_width_ratios=default_widths,
            damping=damping,
        )
        edited_lsf = edit_lsf_pairs(
            lsf,
            sample_rate=sample_rate,
            search_ranges_hz=rule_params["search_ranges_hz"],
            center_shift_ratios=center_ratios,
            pair_width_ratios=width_ratios if default_widths is not None else None,
            min_gap_hz=float(rule_params["min_gap_hz"]),
            edge_gap_hz=float(rule_params["edge_gap_hz"]),
        )
        if edited_lsf is None:
            continue
        edited_coeffs = lsf_to_lpc(edited_lsf)
        if edited_coeffs is None:
            continue
        edited_distribution, edited_log_power = lpc_response_distribution(
            edited_coeffs,
            sample_rate=sample_rate,
            n_fft=n_fft,
            mel_filter=mel_filter,
        )
        fit_error = weighted_l1(edited_distribution, target_distribution)
        core_fit_error = weighted_l1(edited_distribution, target_distribution, weights=combined_core)
        freqs_hz = np.linspace(0.0, sample_rate / 2.0, edited_log_power.shape[0], dtype=np.float64)
        highband_mask = freqs_hz >= preserve_highband_from_hz
        if np.any(highband_mask):
            highband_error = float(np.mean(np.abs(edited_log_power[highband_mask] - original_log_power[highband_mask])))
        else:
            highband_error = 0.0
        lsf_movement_hz = float(np.mean(np.abs((edited_lsf - lsf) * sample_rate / (2.0 * math.pi))))
        objective = fit_error + 0.4 * core_fit_error + 0.08 * highband_error + 0.0007 * lsf_movement_hz
        candidate = {
            "edited_coeffs": edited_coeffs,
            "edited_distribution": edited_distribution,
            "fit_error": fit_error,
            "core_fit_error": core_fit_error,
            "highband_error": highband_error,
            "lsf_movement_hz": lsf_movement_hz,
            "objective": objective,
            "center_ratios": center_ratios,
            "width_ratios": width_ratios,
            "damping": damping,
        }
        if best is None or float(candidate["objective"]) < float(best["objective"]):
            best = candidate

    if best is None or float(best["objective"]) >= original_objective * 0.995:
        return {
            "success": False,
            "output_frame": frame.astype(np.float32),
            "fit_error": original_fit,
            "core_fit_error": original_core_fit,
            "highband_error": 0.0,
            "lsf_movement_hz": 0.0,
            "edited_distribution": original_distribution,
            "center_ratios": [1.0] * len(rule_params["search_ranges_hz"]),
            "width_ratios": [1.0] * len(rule_params["search_ranges_hz"]),
            "damping": 0.0,
        }

    output_frame = synthesize_frame(
        frame,
        original_coeffs=coeffs,
        edited_coeffs=np.asarray(best["edited_coeffs"], dtype=np.float64),
        blend=float(rule_params.get("blend", 1.0)),
    )
    return {
        "success": True,
        "output_frame": output_frame,
        "fit_error": float(best["fit_error"]),
        "core_fit_error": float(best["core_fit_error"]),
        "highband_error": float(best["highband_error"]),
        "lsf_movement_hz": float(best["lsf_movement_hz"]),
        "edited_distribution": np.asarray(best["edited_distribution"], dtype=np.float64),
        "center_ratios": [float(value) for value in best["center_ratios"]],
        "width_ratios": [float(value) for value in best["width_ratios"]],
        "damping": float(best["damping"]),
    }


def compute_reconstruction_diagnostics(
    *,
    original_features: DistributionFeatures,
    reconstructed_features: DistributionFeatures,
    target_prototype: np.ndarray,
    combined_core: np.ndarray,
) -> dict[str, float]:
    original_to_target = one_dim_emd(original_features.utterance_distribution, target_prototype)
    reconstructed_to_target = one_dim_emd(reconstructed_features.utterance_distribution, target_prototype)
    improvement_ratio = 0.0 if original_to_target <= 1e-12 else (original_to_target - reconstructed_to_target) / original_to_target
    shift_score = clamp(50.0 + 50.0 * improvement_ratio, 0.0, 100.0)

    delta_distribution = np.abs(reconstructed_features.utterance_distribution - original_features.utterance_distribution)
    delta_total = float(np.sum(delta_distribution))
    if delta_total <= 1e-12:
        core_coverage = 0.0
    else:
        core_coverage = float(np.sum(delta_distribution[combined_core > 0.5]) / delta_total * 100.0)
    localization_penalty = delta_entropy_penalty(delta_distribution)

    frame_count = min(
        original_features.frame_distributions.shape[0],
        reconstructed_features.frame_distributions.shape[0],
        original_features.voiced_mask.shape[0],
        reconstructed_features.voiced_mask.shape[0],
    )
    frame_improvements: list[float] = []
    for frame_idx in range(frame_count):
        if not bool(original_features.voiced_mask[frame_idx] and reconstructed_features.voiced_mask[frame_idx]):
            continue
        original_frame = original_features.frame_distributions[frame_idx]
        reconstructed_frame = reconstructed_features.frame_distributions[frame_idx]
        original_distance = one_dim_emd(original_frame, target_prototype)
        reconstructed_distance = one_dim_emd(reconstructed_frame, target_prototype)
        frame_improvements.append(original_distance - reconstructed_distance)
    if frame_improvements:
        context_consistency = float(sum(1 for value in frame_improvements if value > 0.0) / len(frame_improvements) * 100.0)
        frame_improvement_mean = float(sum(frame_improvements) / len(frame_improvements))
    else:
        context_consistency = 0.0
        frame_improvement_mean = 0.0

    return {
        "original_to_target_emd": original_to_target,
        "reconstructed_to_target_emd": reconstructed_to_target,
        "reconstructed_resonance_distribution_shift_score": shift_score,
        "reconstructed_core_resonance_coverage_score": core_coverage,
        "reconstructed_over_localized_edit_penalty": localization_penalty,
        "reconstructed_context_consistency_score": context_consistency,
        "reconstructed_frame_improvement_mean": frame_improvement_mean,
    }


def observed_lookup(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return {(row["rule_id"], row["record_id"]): row for row in rows}


def write_summary_md(path: Path, rows: list[dict[str, str]]) -> None:
    by_direction: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_direction.setdefault(row["target_direction"], []).append(row)

    def avg_field(subset: list[dict[str, str]], field: str) -> float:
        return avg([float(row[field]) for row in subset])

    strongest = sorted(rows, key=lambda row: float(row["reconstructed_resonance_distribution_shift_score"]), reverse=True)[:3]
    weakest_fit = sorted(rows, key=lambda row: float(row["fit_success_rate"]))[:3]

    lines = [
        "# ATRR LSF Reconstruction Prototype Summary",
        "",
        f"- rows: `{len(rows)}`",
        f"- avg fit_success_rate: `{avg_field(rows, 'fit_success_rate'):.4f}`",
        f"- avg frame_passthrough_rate: `{avg_field(rows, 'frame_passthrough_rate'):.4f}`",
        f"- avg mean_target_fit_l1: `{avg_field(rows, 'mean_target_fit_l1'):.6f}`",
        f"- avg mean_core_fit_l1: `{avg_field(rows, 'mean_core_fit_l1'):.6f}`",
        f"- avg mean_highband_preservation_error: `{avg_field(rows, 'mean_highband_preservation_error'):.6f}`",
        f"- avg reconstructed shift score: `{avg_field(rows, 'reconstructed_resonance_distribution_shift_score'):.2f}`",
        f"- avg reconstructed core coverage: `{avg_field(rows, 'reconstructed_core_resonance_coverage_score'):.2f}`",
        f"- avg reconstructed localization penalty: `{avg_field(rows, 'reconstructed_over_localized_edit_penalty'):.2f}`",
        f"- avg reconstructed frame improvement mean: `{avg_field(rows, 'reconstructed_frame_improvement_mean'):.6f}`",
        "",
        "## By Direction",
        "",
    ]
    for direction, direction_rows in sorted(by_direction.items()):
        lines.extend(
            [
                f"### `{direction}`",
                "",
                f"- avg fit success rate: `{avg_field(direction_rows, 'fit_success_rate'):.4f}`",
                f"- avg shift score: `{avg_field(direction_rows, 'reconstructed_resonance_distribution_shift_score'):.2f}`",
                f"- avg core coverage: `{avg_field(direction_rows, 'reconstructed_core_resonance_coverage_score'):.2f}`",
                f"- avg localization penalty: `{avg_field(direction_rows, 'reconstructed_over_localized_edit_penalty'):.2f}`",
                f"- avg frame improvement mean: `{avg_field(direction_rows, 'reconstructed_frame_improvement_mean'):.6f}`",
                "",
            ]
        )

    lines.extend(["## Strongest Rows", ""])
    for row in strongest:
        lines.append(
            f"- `{row['rule_id']}` | shift=`{row['reconstructed_resonance_distribution_shift_score']}` | "
            f"fit_success=`{row['fit_success_rate']}` | fit_l1=`{row['mean_target_fit_l1']}`"
        )

    lines.extend(["", "## Lowest Fit Success Rows", ""])
    for row in weakest_fit:
        lines.append(
            f"- `{row['rule_id']}` | fit_success=`{row['fit_success_rate']}` | "
            f"passthrough=`{row['frame_passthrough_rate']}` | fit_l1=`{row['mean_target_fit_l1']}`"
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    queue_csv = resolve_path(args.queue_csv)
    rule_config_path = resolve_path(args.rule_config)
    output_dir = resolve_path(args.output_dir)
    reconstructed_dir = output_dir / "reconstructed"

    rows = load_rows(queue_csv)
    observed_rows = observed_lookup(resolve_path(args.observed_diagnostics_csv))
    rule_lookup = build_enabled_directional_rule_lookup(load_json(rule_config_path))

    original_feature_cache: dict[str, DistributionFeatures] = {}

    def get_distribution_features(path_value: str) -> DistributionFeatures:
        cache_key = str(resolve_path(path_value))
        cached = original_feature_cache.get(cache_key)
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
        original_feature_cache[cache_key] = features
        return features

    prototype_rows: dict[tuple[str, str], list[DistributionFeatures]] = {}
    for row in rows:
        features = get_distribution_features(row["original_copy"])
        prototype_rows.setdefault((row["group_value"], row["source_gender"]), []).append(features)

    output_rows: list[dict[str, str]] = []
    for row in rows:
        source_audio, sample_rate = load_audio(resolve_path(row["original_copy"]))
        source_features = get_distribution_features(row["original_copy"])
        rule = rule_lookup[(row["group_value"], row["target_direction"])]
        rule_params = rule["method_params"]
        target_gender = "male" if row["target_direction"] == "masculine" else "female"
        target_candidates = prototype_rows[(row["group_value"], target_gender)]
        target_prototype, target_occupancy, prototype_weight_sum = build_weighted_target_prototype(source_features, target_candidates)
        combined_core = build_combined_core_mask(
            source_features,
            target_prototype,
            target_occupancy,
            core_energy_threshold=args.core_energy_threshold,
            occupancy_threshold=args.occupancy_threshold,
        )
        target_frames, _ = simulate_frames(
            source_features,
            target_prototype,
            combined_core,
            core_step_size=args.core_step_size,
            off_core_step_size=args.off_core_step_size,
            frame_smoothness_weight=args.frame_smoothness_weight,
            max_bin_step=args.max_bin_step,
        )

        frame_length = int(rule_params["frame_length"])
        hop_length = int(rule_params["hop_length"])
        lpc_order = int(rule_params["lpc_order"])
        if source_audio.size < frame_length:
            padded_audio = np.pad(source_audio.astype(np.float32), (0, frame_length - int(source_audio.size)))
        else:
            padded_audio = source_audio.astype(np.float32)
        frames = librosa.util.frame(padded_audio, frame_length=frame_length, hop_length=hop_length).T
        recon_frame_times = frame_centers_sec(frames.shape[0], frame_length, hop_length, sample_rate)
        source_frame_times = frame_centers_sec(source_features.frame_distributions.shape[0], args.n_fft, args.hop_length, sample_rate)
        target_indices = nearest_indices(source_frame_times, recon_frame_times)
        mapped_source_distributions = source_features.frame_distributions[target_indices]
        mapped_target_distributions = target_frames[target_indices]

        f0, world_times_sec = analyze_f0(source_audio, sample_rate, args.world_sr, args.frame_period_ms)
        voiced_mask = interpolate_voiced_mask(recon_frame_times, world_times_sec, f0)
        analysis_window = np.hanning(frame_length).astype(np.float32)
        mel_filter, mel_freqs_hz = build_mel_filter(
            sample_rate=sample_rate,
            n_fft=args.n_fft,
            n_mels=args.n_mels,
            fmin=args.fmin,
            fmax=args.fmax,
        )

        output_frames: list[np.ndarray] = []
        fit_errors: list[float] = []
        core_fit_errors: list[float] = []
        highband_errors: list[float] = []
        lsf_movements_hz: list[float] = []
        success_count = 0
        passthrough_count = 0
        center_ratio_rows: list[list[float]] = []
        width_ratio_rows: list[list[float]] = []

        for frame_idx, frame in enumerate(frames):
            if frame_idx >= mapped_target_distributions.shape[0] or voiced_mask[frame_idx] < 0.5:
                output_frames.append(frame.astype(np.float32))
                continue

            frame_for_analysis = frame.astype(np.float32) * analysis_window
            coeffs = stable_lpc(frame_for_analysis, lpc_order)
            if coeffs is None:
                passthrough_count += 1
                output_frames.append(frame.astype(np.float32))
                continue
            lsf = lpc_to_lsf(coeffs)
            if lsf is None:
                passthrough_count += 1
                output_frames.append(frame.astype(np.float32))
                continue

            fit_result = try_fit_lsf_frame(
                frame=frame.astype(np.float32),
                coeffs=coeffs,
                lsf=lsf,
                source_distribution=mapped_source_distributions[frame_idx],
                target_distribution=mapped_target_distributions[frame_idx],
                combined_core=combined_core,
                rule_params=rule_params,
                sample_rate=sample_rate,
                n_fft=args.n_fft,
                mel_filter=mel_filter,
                mel_freqs_hz=mel_freqs_hz,
                preserve_highband_from_hz=args.preserve_highband_from_hz,
            )
            output_frames.append(np.asarray(fit_result["output_frame"], dtype=np.float32))
            fit_errors.append(float(fit_result["fit_error"]))
            core_fit_errors.append(float(fit_result["core_fit_error"]))
            highband_errors.append(float(fit_result["highband_error"]))
            lsf_movements_hz.append(float(fit_result["lsf_movement_hz"]))
            center_ratio_rows.append([float(value) for value in fit_result["center_ratios"]])
            width_ratio_rows.append([float(value) for value in fit_result["width_ratios"]])
            if bool(fit_result["success"]):
                success_count += 1
            else:
                passthrough_count += 1

        reconstructed_audio = overlap_add(output_frames, frame_length, hop_length, len(source_audio))
        in_rms = safe_rms(source_audio)
        out_rms = safe_rms(reconstructed_audio)
        if in_rms > 1e-8 and out_rms > 1e-8:
            reconstructed_audio = reconstructed_audio * (in_rms / out_rms)
        peak = float(np.max(np.abs(reconstructed_audio))) if reconstructed_audio.size else 0.0
        if peak > args.peak_limit and peak > 0.0:
            reconstructed_audio = reconstructed_audio * (args.peak_limit / peak)

        output_stem = Path(row["original_copy"]).stem.replace("__lsf__", "__atrr_lsf__")
        reconstructed_path = reconstructed_dir / f"{output_stem}.{args.audio_format}"
        save_audio(reconstructed_path, reconstructed_audio.astype(np.float32), sample_rate)

        reconstructed_features = build_distribution_features(
            audio=reconstructed_audio.astype(np.float32),
            sample_rate=sample_rate,
            n_fft=args.n_fft,
            hop_length=args.hop_length,
            n_mels=args.n_mels,
            fmin=args.fmin,
            fmax=args.fmax,
            rms_threshold_db=args.rms_threshold_db,
            frame_core_threshold=args.frame_core_threshold,
        )
        reconstruction_diag = compute_reconstruction_diagnostics(
            original_features=source_features,
            reconstructed_features=reconstructed_features,
            target_prototype=target_prototype,
            combined_core=combined_core,
        )

        original_audio_features = feature_map(source_audio, sample_rate, f0_sr=args.world_sr, frame_period_ms=args.frame_period_ms)
        reconstructed_audio_features = feature_map(reconstructed_audio, sample_rate, f0_sr=args.world_sr, frame_period_ms=args.frame_period_ms)
        original_bands = band_share_db(source_audio, sample_rate, n_fft=args.n_fft, hop_length=args.hop_length)
        reconstructed_bands = band_share_db(reconstructed_audio, sample_rate, n_fft=args.n_fft, hop_length=args.hop_length)
        diff_metrics = waveform_diff(source_audio, reconstructed_audio)
        spectral_distance = stft_logmag_l1(source_audio, reconstructed_audio, n_fft=args.n_fft, hop_length=args.hop_length)

        fit_frame_count = len(fit_errors)
        fit_success_rate = 0.0 if fit_frame_count == 0 else success_count / fit_frame_count
        passthrough_rate = 0.0 if fit_frame_count == 0 else passthrough_count / fit_frame_count
        observed_row = observed_rows.get((row["rule_id"], row["record_id"]), {})

        output_rows.append(
            {
                "rule_id": row["rule_id"],
                "record_id": row["record_id"],
                "group_value": row["group_value"],
                "source_gender": row["source_gender"],
                "target_direction": row["target_direction"],
                "original_copy": row["original_copy"],
                "observed_processed_audio": row["processed_audio"],
                "reconstructed_audio": str(reconstructed_path),
                "core_step_size": fmt_float(args.core_step_size, digits=3),
                "off_core_step_size": fmt_float(args.off_core_step_size, digits=3),
                "frame_smoothness_weight": fmt_float(args.frame_smoothness_weight, digits=3),
                "max_bin_step": fmt_float(args.max_bin_step, digits=4),
                "prototype_weight_sum": fmt_float(prototype_weight_sum),
                "fit_voiced_frame_count": str(fit_frame_count),
                "fit_success_rate": fmt_float(fit_success_rate, digits=4),
                "frame_passthrough_rate": fmt_float(passthrough_rate, digits=4),
                "mean_target_fit_l1": fmt_float(avg(fit_errors)),
                "mean_core_fit_l1": fmt_float(avg(core_fit_errors)),
                "mean_highband_preservation_error": fmt_float(avg(highband_errors)),
                "mean_lsf_movement_hz": fmt_float(avg(lsf_movements_hz)),
                "mean_pair1_center_ratio": fmt_float(row_mean(center_ratio_rows, 0), digits=4),
                "mean_pair2_center_ratio": fmt_float(row_mean(center_ratio_rows, 1), digits=4),
                "mean_pair3_center_ratio": fmt_float(row_mean(center_ratio_rows, 2), digits=4),
                "mean_pair1_width_ratio": fmt_float(row_mean(width_ratio_rows, 0), digits=4),
                "mean_pair2_width_ratio": fmt_float(row_mean(width_ratio_rows, 1), digits=4),
                "mean_pair3_width_ratio": fmt_float(row_mean(width_ratio_rows, 2), digits=4),
                "original_to_target_emd": fmt_float(reconstruction_diag["original_to_target_emd"]),
                "reconstructed_to_target_emd": fmt_float(reconstruction_diag["reconstructed_to_target_emd"]),
                "reconstructed_resonance_distribution_shift_score": fmt_float(reconstruction_diag["reconstructed_resonance_distribution_shift_score"], digits=2),
                "reconstructed_core_resonance_coverage_score": fmt_float(reconstruction_diag["reconstructed_core_resonance_coverage_score"], digits=2),
                "reconstructed_over_localized_edit_penalty": fmt_float(reconstruction_diag["reconstructed_over_localized_edit_penalty"], digits=2),
                "reconstructed_context_consistency_score": fmt_float(reconstruction_diag["reconstructed_context_consistency_score"], digits=2),
                "reconstructed_frame_improvement_mean": fmt_float(reconstruction_diag["reconstructed_frame_improvement_mean"]),
                "observed_resonance_distribution_shift_score": observed_row.get("resonance_distribution_shift_score", ""),
                "observed_core_resonance_coverage_score": observed_row.get("core_resonance_coverage_score", ""),
                "observed_over_localized_edit_penalty": observed_row.get("over_localized_edit_penalty", ""),
                "observed_context_consistency_score": observed_row.get("context_consistency_score", ""),
                "observed_frame_improvement_mean": observed_row.get("frame_improvement_mean", ""),
                "delta_shift_vs_observed": fmt_float(
                    delta(reconstruction_diag["reconstructed_resonance_distribution_shift_score"], float(observed_row["resonance_distribution_shift_score"])) if observed_row.get("resonance_distribution_shift_score") else None,
                    digits=2,
                ),
                "delta_coverage_vs_observed": fmt_float(
                    delta(reconstruction_diag["reconstructed_core_resonance_coverage_score"], float(observed_row["core_resonance_coverage_score"])) if observed_row.get("core_resonance_coverage_score") else None,
                    digits=2,
                ),
                "delta_penalty_vs_observed": fmt_float(
                    delta(reconstruction_diag["reconstructed_over_localized_edit_penalty"], float(observed_row["over_localized_edit_penalty"])) if observed_row.get("over_localized_edit_penalty") else None,
                    digits=2,
                ),
                "delta_frame_improvement_vs_observed": fmt_float(
                    delta(reconstruction_diag["reconstructed_frame_improvement_mean"], float(observed_row["frame_improvement_mean"])) if observed_row.get("frame_improvement_mean") else None,
                ),
                "original_rms_dbfs": fmt_float(original_audio_features.get("rms_dbfs")),
                "reconstructed_rms_dbfs": fmt_float(reconstructed_audio_features.get("rms_dbfs")),
                "delta_rms_dbfs": fmt_float(delta(reconstructed_audio_features.get("rms_dbfs"), original_audio_features.get("rms_dbfs"))),
                "original_f0_voiced_ratio": fmt_float(original_audio_features.get("f0_voiced_ratio")),
                "reconstructed_f0_voiced_ratio": fmt_float(reconstructed_audio_features.get("f0_voiced_ratio")),
                "delta_f0_voiced_ratio": fmt_float(delta(reconstructed_audio_features.get("f0_voiced_ratio"), original_audio_features.get("f0_voiced_ratio"))),
                "original_f0_median_hz": fmt_float(original_audio_features.get("f0_median_hz")),
                "reconstructed_f0_median_hz": fmt_float(reconstructed_audio_features.get("f0_median_hz")),
                "delta_f0_median_hz": fmt_float(delta(reconstructed_audio_features.get("f0_median_hz"), original_audio_features.get("f0_median_hz"))),
                "delta_f0_median_pct": fmt_float(pct_delta(reconstructed_audio_features.get("f0_median_hz"), original_audio_features.get("f0_median_hz")), digits=3),
                "original_spectral_centroid_hz_mean": fmt_float(original_audio_features.get("spectral_centroid_hz_mean")),
                "reconstructed_spectral_centroid_hz_mean": fmt_float(reconstructed_audio_features.get("spectral_centroid_hz_mean")),
                "delta_spectral_centroid_hz_mean": fmt_float(delta(reconstructed_audio_features.get("spectral_centroid_hz_mean"), original_audio_features.get("spectral_centroid_hz_mean"))),
                "original_presence_1500_3000_share_db": fmt_float(original_bands["presence_1500_3000_share_db"]),
                "reconstructed_presence_1500_3000_share_db": fmt_float(reconstructed_bands["presence_1500_3000_share_db"]),
                "delta_presence_1500_3000_share_db": fmt_float(delta(reconstructed_bands["presence_1500_3000_share_db"], original_bands["presence_1500_3000_share_db"])),
                "original_brilliance_3000_8000_share_db": fmt_float(original_bands["brilliance_3000_8000_share_db"]),
                "reconstructed_brilliance_3000_8000_share_db": fmt_float(reconstructed_bands["brilliance_3000_8000_share_db"]),
                "delta_brilliance_3000_8000_share_db": fmt_float(delta(reconstructed_bands["brilliance_3000_8000_share_db"], original_bands["brilliance_3000_8000_share_db"])),
                "waveform_mean_abs_diff": fmt_float(diff_metrics["waveform_mean_abs_diff"]),
                "waveform_max_abs_diff": fmt_float(diff_metrics["waveform_max_abs_diff"]),
                "stft_logmag_l1": fmt_float(spectral_distance),
            }
        )

    detail_csv = output_dir / "atrr_lsf_reconstruction_summary.csv"
    summary_md = output_dir / "ATRR_LSF_RECONSTRUCTION_SUMMARY.md"
    write_csv(detail_csv, output_rows)
    write_summary_md(summary_md, output_rows)
    print(f"Wrote {detail_csv}")
    print(f"Wrote {summary_md}")
    print(f"Rows: {len(output_rows)}")


if __name__ == "__main__":
    main()
