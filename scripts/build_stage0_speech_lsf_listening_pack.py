from __future__ import annotations

import argparse
import math
from pathlib import Path

import librosa
import numpy as np
import scipy.signal

from apply_stage0_rule_preconditioner import load_audio, resolve_path, save_audio
from select_stage0_candidate_rules import parse_float, select_rules
from build_stage0_speech_listening_pack import (
    TARGET_DIRECTION_BY_SOURCE_GENDER,
    load_selection_manifest,
    load_source_rows,
    select_rows,
    select_rows_from_manifest,
)
from stage0_speech_resonance_pack_common import (
    analyze_f0,
    build_output_stem,
    build_summary_row,
    frame_centers_sec,
    interpolate_voiced_mask,
    load_json,
    overlap_add,
    safe_rms,
    stable_lpc,
    write_pack_readme,
    write_summary,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RULE_CONFIG = ROOT / "experiments" / "stage0_baseline" / "v1_full" / "speech_lsf_resonance_candidate_v1.json"
DEFAULT_INPUT_CSV = ROOT / "experiments" / "fixed_eval" / "v1_2" / "fixed_eval_review_final_v1_2.csv"
DEFAULT_OUTPUT_DIR = ROOT / "artifacts" / "listening_review" / "stage0_speech_lsf_listening_pack" / "v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rule-config", default=str(DEFAULT_RULE_CONFIG))
    parser.add_argument("--input-csv", default=str(DEFAULT_INPUT_CSV))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--selection-manifest", default="")
    parser.add_argument("--samples-per-cell", type=int, default=2)
    parser.add_argument("--selection-mode", choices=["central", "f0_span"], default="central")
    parser.add_argument("--audio-format", choices=["wav", "flac"], default="wav")
    parser.add_argument("--peak-limit", type=float, default=0.98)
    parser.add_argument("--world-sr", type=int, default=16000)
    parser.add_argument("--frame-period-ms", type=float, default=10.0)
    return parser.parse_args()


def lpc_to_lsf(coeffs: np.ndarray) -> np.ndarray | None:
    order = coeffs.shape[0] - 1
    if order <= 0 or order % 2 != 0:
        return None
    a = np.concatenate([coeffs.astype(np.float64), [0.0]])
    p_poly = a + a[::-1]
    q_poly = a - a[::-1]
    p_poly, _ = np.polydiv(p_poly, np.array([1.0, 1.0], dtype=np.float64))
    q_poly, _ = np.polydiv(q_poly, np.array([1.0, -1.0], dtype=np.float64))
    roots_p = np.roots(np.asarray(p_poly, dtype=np.float64))
    roots_q = np.roots(np.asarray(q_poly, dtype=np.float64))

    def angles_from_roots(roots: np.ndarray) -> np.ndarray:
        selected = []
        for root in roots:
            if abs(root) <= 1e-8:
                continue
            unit_root = root / abs(root)
            angle = float(np.angle(unit_root))
            if 1e-5 < angle < math.pi - 1e-5:
                selected.append(angle)
        return np.asarray(sorted(selected), dtype=np.float64)

    angles_p = angles_from_roots(roots_p)
    angles_q = angles_from_roots(roots_q)
    lsf = np.sort(np.concatenate([angles_p, angles_q]))
    if lsf.shape[0] != order:
        return None
    return lsf


def lsf_to_lpc(lsf: np.ndarray) -> np.ndarray | None:
    order = lsf.shape[0]
    if order <= 0 or order % 2 != 0:
        return None

    p_angles = lsf[0::2]
    q_angles = lsf[1::2]
    p_roots = np.concatenate([np.exp(1j * p_angles), np.exp(-1j * p_angles)])
    q_roots = np.concatenate([np.exp(1j * q_angles), np.exp(-1j * q_angles)])

    p_poly = np.poly(p_roots).real.astype(np.float64)
    q_poly = np.poly(q_roots).real.astype(np.float64)
    p_poly = np.convolve(p_poly, np.array([1.0, 1.0], dtype=np.float64))
    q_poly = np.convolve(q_poly, np.array([1.0, -1.0], dtype=np.float64))

    a = 0.5 * (p_poly + q_poly)
    coeffs = np.asarray(a[:-1], dtype=np.float64)
    if coeffs.shape[0] != order + 1 or abs(coeffs[0]) <= 1e-8:
        return None
    coeffs = coeffs / coeffs[0]
    roots = np.roots(coeffs)
    if np.any(np.abs(roots) >= 0.999):
        return None
    return coeffs


def enforce_lsf_spacing(lsf: np.ndarray, *, sample_rate: int, min_gap_hz: float, edge_gap_hz: float) -> np.ndarray | None:
    edited = np.sort(np.asarray(lsf, dtype=np.float64).copy())
    min_gap = 2.0 * math.pi * float(min_gap_hz) / sample_rate
    edge_gap = 2.0 * math.pi * float(edge_gap_hz) / sample_rate
    if edited.size == 0:
        return None
    for _ in range(3):
        edited[0] = max(edited[0], edge_gap)
        for idx in range(1, edited.shape[0]):
            edited[idx] = max(edited[idx], edited[idx - 1] + min_gap)
        edited[-1] = min(edited[-1], math.pi - edge_gap)
        for idx in range(edited.shape[0] - 2, -1, -1):
            edited[idx] = min(edited[idx], edited[idx + 1] - min_gap)
    if not np.all(np.diff(edited) > 0):
        return None
    if edited[0] <= 0.0 or edited[-1] >= math.pi:
        return None
    return edited


def edit_lsf_pairs(
    lsf: np.ndarray,
    *,
    sample_rate: int,
    search_ranges_hz: list[list[float]],
    center_shift_ratios: list[float],
    pair_width_ratios: list[float] | None,
    min_gap_hz: float,
    edge_gap_hz: float,
) -> np.ndarray | None:
    edited = np.asarray(lsf, dtype=np.float64).copy()
    lsf_hz = edited * sample_rate / (2.0 * math.pi)
    used_indices: set[int] = set()
    width_ratios = pair_width_ratios if pair_width_ratios is not None else [1.0] * len(search_ranges_hz)

    for search_range_hz, shift_ratio, width_ratio in zip(search_ranges_hz, center_shift_ratios, width_ratios):
        low_hz, high_hz = float(search_range_hz[0]), float(search_range_hz[1])
        range_center = (low_hz + high_hz) / 2.0
        candidate_pairs: list[tuple[float, int, int, float]] = []
        for idx in range(edited.shape[0] - 1):
            if idx in used_indices or (idx + 1) in used_indices:
                continue
            left_hz = lsf_hz[idx]
            right_hz = lsf_hz[idx + 1]
            pair_center = (left_hz + right_hz) / 2.0
            if low_hz <= pair_center <= high_hz:
                candidate_pairs.append((abs(pair_center - range_center), idx, idx + 1, pair_center))
        if not candidate_pairs:
            continue
        _, left_idx, right_idx, pair_center = min(candidate_pairs, key=lambda item: item[0])
        pair_width = max(lsf_hz[right_idx] - lsf_hz[left_idx], 1e-3)
        target_center = min(max(pair_center * float(shift_ratio), low_hz), high_hz)
        target_width = pair_width * float(width_ratio)
        target_left_hz = target_center - target_width / 2.0
        target_right_hz = target_center + target_width / 2.0
        edited[left_idx] = target_left_hz * 2.0 * math.pi / sample_rate
        edited[right_idx] = target_right_hz * 2.0 * math.pi / sample_rate
        constrained = enforce_lsf_spacing(edited, sample_rate=sample_rate, min_gap_hz=min_gap_hz, edge_gap_hz=edge_gap_hz)
        if constrained is None:
            return None
        edited = constrained
        lsf_hz = edited * sample_rate / (2.0 * math.pi)
        used_indices.update({left_idx, right_idx})

    return edited


def blend_original_band(
    original_frame: np.ndarray,
    processed_frame: np.ndarray,
    *,
    sample_rate: int,
    preserve_from_hz: float,
    preserve_full_hz: float,
    preserve_mix: float,
) -> np.ndarray:
    if preserve_mix <= 0.0:
        return processed_frame.astype(np.float32)

    original_spec = np.fft.rfft(original_frame.astype(np.float64))
    processed_spec = np.fft.rfft(processed_frame.astype(np.float64))
    freqs = np.fft.rfftfreq(original_frame.shape[0], d=1.0 / float(sample_rate))

    if preserve_full_hz <= preserve_from_hz:
        weights = np.where(freqs >= preserve_from_hz, 1.0, 0.0)
    else:
        weights = np.clip((freqs - preserve_from_hz) / (preserve_full_hz - preserve_from_hz), 0.0, 1.0)
    weights = np.asarray(weights * preserve_mix, dtype=np.float64)

    merged_spec = processed_spec * (1.0 - weights) + original_spec * weights
    return np.fft.irfft(merged_spec, n=original_frame.shape[0]).astype(np.float32)


def apply_lsf_resonance_shift(
    audio: np.ndarray,
    *,
    sample_rate: int,
    peak_limit: float,
    world_sr: int,
    frame_period_ms: float,
    frame_length: int,
    hop_length: int,
    lpc_order: int,
    search_ranges_hz: list[list[float]],
    center_shift_ratios: list[float],
    pair_width_ratios: list[float] | None,
    blend: float,
    min_gap_hz: float,
    edge_gap_hz: float,
    preserve_original_from_hz: float | None = None,
    preserve_original_full_hz: float | None = None,
    preserve_original_mix: float = 0.0,
) -> np.ndarray:
    if audio.size < frame_length:
        padded = np.pad(audio.astype(np.float32), (0, frame_length - int(audio.size)))
    else:
        padded = audio.astype(np.float32)
    frames = librosa.util.frame(padded, frame_length=frame_length, hop_length=hop_length).T
    f0, world_times_sec = analyze_f0(audio, sample_rate, world_sr, frame_period_ms)
    frame_times = frame_centers_sec(frames.shape[0], frame_length, hop_length, sample_rate)
    voiced_mask = interpolate_voiced_mask(frame_times, world_times_sec, f0)

    analysis_window = np.hanning(frame_length).astype(np.float32)
    out_frames: list[np.ndarray] = []
    for frame, voiced_value in zip(frames, voiced_mask, strict=False):
        if voiced_value < 0.5:
            out_frames.append(frame.astype(np.float32))
            continue
        frame_for_analysis = frame.astype(np.float32) * analysis_window
        coeffs = stable_lpc(frame_for_analysis, lpc_order)
        if coeffs is None:
            out_frames.append(frame.astype(np.float32))
            continue
        lsf = lpc_to_lsf(coeffs)
        if lsf is None:
            out_frames.append(frame.astype(np.float32))
            continue
        edited_lsf = edit_lsf_pairs(
            lsf,
            sample_rate=sample_rate,
            search_ranges_hz=search_ranges_hz,
            center_shift_ratios=center_shift_ratios,
            pair_width_ratios=pair_width_ratios,
            min_gap_hz=min_gap_hz,
            edge_gap_hz=edge_gap_hz,
        )
        if edited_lsf is None:
            out_frames.append(frame.astype(np.float32))
            continue
        edited_coeffs = lsf_to_lpc(edited_lsf)
        if edited_coeffs is None:
            out_frames.append(frame.astype(np.float32))
            continue

        residual = scipy.signal.lfilter(coeffs, [1.0], frame.astype(np.float64))
        synthesized = scipy.signal.lfilter([1.0], edited_coeffs, residual).astype(np.float32)
        synth_rms = safe_rms(synthesized)
        frame_rms = safe_rms(frame)
        if synth_rms > 1e-8 and frame_rms > 1e-8:
            synthesized = synthesized * (frame_rms / synth_rms)
        blended = (1.0 - blend) * frame.astype(np.float32) + blend * synthesized
        if (
            preserve_original_from_hz is not None
            and preserve_original_full_hz is not None
            and preserve_original_mix > 0.0
        ):
            blended = blend_original_band(
                frame.astype(np.float32),
                blended.astype(np.float32),
                sample_rate=sample_rate,
                preserve_from_hz=float(preserve_original_from_hz),
                preserve_full_hz=float(preserve_original_full_hz),
                preserve_mix=float(preserve_original_mix),
            )
            blended_rms = safe_rms(blended)
            if blended_rms > 1e-8 and frame_rms > 1e-8:
                blended = blended * (frame_rms / blended_rms)
        out_frames.append(blended.astype(np.float32))

    out = overlap_add(out_frames, frame_length, hop_length, len(audio))
    in_rms = safe_rms(audio)
    out_rms = safe_rms(out)
    if in_rms > 1e-8 and out_rms > 1e-8:
        out = out * (in_rms / out_rms)
    peak = float(np.max(np.abs(out))) if out.size else 0.0
    if peak > peak_limit and peak > 0:
        out = out * (peak_limit / peak)
    return out.astype(np.float32)


def main() -> None:
    args = parse_args()
    rule_config_path = resolve_path(args.rule_config)
    rule_config = load_json(rule_config_path)
    input_csv_path = resolve_path(args.input_csv)
    selection_manifest_path = resolve_path(args.selection_manifest) if args.selection_manifest else None
    try:
        input_csv_rel = input_csv_path.relative_to(ROOT).as_posix()
    except ValueError:
        input_csv_rel = str(input_csv_path)
    source_rows = load_source_rows(input_csv_path)
    if selection_manifest_path is not None:
        selected_rows = select_rows_from_manifest(source_rows, load_selection_manifest(selection_manifest_path))
        try:
            selection_manifest_rel = selection_manifest_path.relative_to(ROOT).as_posix()
        except ValueError:
            selection_manifest_rel = str(selection_manifest_path)
    else:
        selected_rows = select_rows(
            source_rows,
            samples_per_cell=args.samples_per_cell,
            selection_mode=args.selection_mode,
        )
        selection_manifest_rel = ""
    output_dir = resolve_path(args.output_dir)
    originals_dir = output_dir / "original"
    processed_dir = output_dir / "processed"
    summary_rows: list[dict[str, str]] = []

    for row in selected_rows:
        target_direction = TARGET_DIRECTION_BY_SOURCE_GENDER[row["gender"]]
        matched_rules = select_rules(
            rule_config,
            domain=row["domain"],
            group_value=row["dataset_name"],
            target_direction=target_direction,
            f0_median_hz=parse_float(row.get("f0_median_hz")),
        )
        if not matched_rules:
            raise RuntimeError(
                f"No matching LSF rule for utt_id={row['utt_id']} dataset={row['dataset_name']} "
                f"target={target_direction} f0={row.get('f0_median_hz', '')}"
            )
        rule = matched_rules[0]
        params = rule["method_params"]
        input_audio = resolve_path(row["path_raw"])
        stem = build_output_stem(row, target_direction=target_direction, method_token="lsf")
        original_copy = originals_dir / f"{stem}.{args.audio_format}"
        processed_audio = processed_dir / f"{stem}.{args.audio_format}"

        audio, sample_rate = load_audio(input_audio)
        save_audio(original_copy, audio, sample_rate)
        out = apply_lsf_resonance_shift(
            audio,
            sample_rate=sample_rate,
            peak_limit=args.peak_limit,
            world_sr=args.world_sr,
            frame_period_ms=args.frame_period_ms,
            frame_length=int(params["frame_length"]),
            hop_length=int(params["hop_length"]),
            lpc_order=int(params["lpc_order"]),
            search_ranges_hz=params["search_ranges_hz"],
            center_shift_ratios=[float(value) for value in params["center_shift_ratios"]],
            pair_width_ratios=[float(value) for value in params["pair_width_ratios"]] if "pair_width_ratios" in params else None,
            blend=float(params["blend"]),
            min_gap_hz=float(params["min_gap_hz"]),
            edge_gap_hz=float(params["edge_gap_hz"]),
            preserve_original_from_hz=float(params["preserve_original_from_hz"]) if "preserve_original_from_hz" in params else None,
            preserve_original_full_hz=float(params["preserve_original_full_hz"]) if "preserve_original_full_hz" in params else None,
            preserve_original_mix=float(params.get("preserve_original_mix", 0.0)),
        )
        save_audio(processed_audio, out, sample_rate)

        summary_rows.append(
            build_summary_row(
                row,
                rule=rule,
                target_direction=target_direction,
                input_audio=input_audio,
                original_copy=original_copy,
                processed_audio=processed_audio,
            )
        )

    summary_path = output_dir / "listening_pack_summary.csv"
    write_summary(summary_path, summary_rows)
    write_pack_readme(
        output_dir / "README.md",
        rows=summary_rows,
        pack_title="Stage0 Speech LSF Listening Pack",
        purpose="lsf pair-shift residual-preserving probe after lpc pole-edit rejection",
        script_name="build_stage0_speech_lsf_listening_pack.py",
        rule_config_path=rule_config_path,
        rebuild_extra_lines=(
            [
                f"  --input-csv {input_csv_rel} `",
                f"  --selection-manifest {selection_manifest_rel} `",
            ]
            if selection_manifest_rel
            else [
                f"  --input-csv {input_csv_rel} `",
                f"  --samples-per-cell {args.samples_per_cell} `",
                f"  --selection-mode {args.selection_mode} `",
            ]
        ),
    )
    print(f"Wrote {summary_path}")
    print(f"Selected rows: {len(summary_rows)}")
    print(f"Output dir: {output_dir}")


if __name__ == "__main__":
    main()
