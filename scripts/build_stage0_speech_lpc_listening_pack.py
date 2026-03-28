from __future__ import annotations

import argparse
import math
from pathlib import Path

import librosa
import numpy as np
import scipy.signal

from apply_stage0_rule_preconditioner import load_audio, resolve_path, save_audio
from build_stage0_speech_listening_pack import TARGET_DIRECTION_BY_SOURCE_GENDER, load_source_rows, select_rows
from stage0_speech_resonance_pack_common import (
    analyze_f0,
    build_enabled_directional_rule_lookup,
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
DEFAULT_RULE_CONFIG = ROOT / "experiments" / "stage0_baseline" / "v1_full" / "speech_lpc_resonance_candidate_v1.json"
DEFAULT_INPUT_CSV = ROOT / "experiments" / "fixed_eval" / "v1_2" / "fixed_eval_review_final_v1_2.csv"
DEFAULT_OUTPUT_DIR = ROOT / "artifacts" / "listening_review" / "stage0_speech_lpc_listening_pack" / "v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rule-config", default=str(DEFAULT_RULE_CONFIG))
    parser.add_argument("--input-csv", default=str(DEFAULT_INPUT_CSV))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--samples-per-cell", type=int, default=2)
    parser.add_argument("--audio-format", choices=["wav", "flac"], default="wav")
    parser.add_argument("--peak-limit", type=float, default=0.98)
    parser.add_argument("--world-sr", type=int, default=16000)
    parser.add_argument("--frame-period-ms", type=float, default=10.0)
    return parser.parse_args()


def select_positive_roots(roots: np.ndarray) -> list[tuple[int, float, float]]:
    selected: list[tuple[int, float, float]] = []
    for idx, root in enumerate(roots):
        if np.imag(root) <= 1e-6:
            continue
        selected.append((idx, abs(root), float(np.angle(root))))
    selected.sort(key=lambda item: item[2])
    return selected


def find_conjugate_index(roots: np.ndarray, target_idx: int) -> int | None:
    target = np.conjugate(roots[target_idx])
    best_idx = None
    best_dist = float("inf")
    for idx, root in enumerate(roots):
        if idx == target_idx:
            continue
        dist = abs(root - target)
        if dist < best_dist:
            best_dist = dist
            best_idx = idx
    return best_idx if best_dist < 1e-3 else None


def edit_lpc_roots(
    coeffs: np.ndarray,
    *,
    sample_rate: int,
    search_ranges_hz: list[list[float]],
    shift_ratios: list[float],
) -> np.ndarray | None:
    roots = np.roots(coeffs)
    if roots.size == 0:
        return None
    edited = roots.astype(np.complex128).copy()
    positive_roots = select_positive_roots(roots)
    nyquist_hz = sample_rate / 2.0

    for search_range_hz, shift_ratio in zip(search_ranges_hz, shift_ratios):
        low_hz, high_hz = float(search_range_hz[0]), float(search_range_hz[1])
        candidate = None
        for idx, radius, angle in positive_roots:
            freq_hz = angle * sample_rate / (2.0 * math.pi)
            if low_hz <= freq_hz <= high_hz:
                candidate = (idx, radius, angle, freq_hz)
                break
        if candidate is None:
            continue
        idx, radius, angle, freq_hz = candidate
        target_hz = min(max(freq_hz * float(shift_ratio), low_hz), min(high_hz * 1.35, nyquist_hz * 0.94))
        target_angle = target_hz * 2.0 * math.pi / sample_rate
        edited[idx] = radius * np.exp(1j * target_angle)
        conj_idx = find_conjugate_index(roots, idx)
        if conj_idx is not None:
            edited[conj_idx] = np.conjugate(edited[idx])

    new_coeffs = np.poly(edited).real.astype(np.float64)
    if abs(new_coeffs[0]) <= 1e-8:
        return None
    new_coeffs = new_coeffs / new_coeffs[0]
    new_roots = np.roots(new_coeffs)
    if np.any(np.abs(new_roots) >= 0.999):
        clipped = []
        for root in new_roots:
            radius = min(abs(root), 0.995)
            clipped.append(radius * np.exp(1j * np.angle(root)))
        new_coeffs = np.poly(np.array(clipped, dtype=np.complex128)).real.astype(np.float64)
        new_coeffs = new_coeffs / new_coeffs[0]
    return new_coeffs


def apply_lpc_resonance_shift(
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
    shift_ratios: list[float],
    blend: float,
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
        edited_coeffs = edit_lpc_roots(
            coeffs,
            sample_rate=sample_rate,
            search_ranges_hz=search_ranges_hz,
            shift_ratios=shift_ratios,
        )
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
    rule_lookup = build_enabled_directional_rule_lookup(rule_config)
    selected_rows = select_rows(load_source_rows(resolve_path(args.input_csv)), samples_per_cell=args.samples_per_cell)
    output_dir = resolve_path(args.output_dir)
    originals_dir = output_dir / "original"
    processed_dir = output_dir / "processed"
    summary_rows: list[dict[str, str]] = []

    for row in selected_rows:
        target_direction = TARGET_DIRECTION_BY_SOURCE_GENDER[row["gender"]]
        rule = rule_lookup[(row["dataset_name"], target_direction)]
        params = rule["method_params"]
        input_audio = resolve_path(row["path_raw"])
        stem = build_output_stem(row, target_direction=target_direction, method_token="lpc")
        original_copy = originals_dir / f"{stem}.{args.audio_format}"
        processed_audio = processed_dir / f"{stem}.{args.audio_format}"

        audio, sample_rate = load_audio(input_audio)
        save_audio(original_copy, audio, sample_rate)
        out = apply_lpc_resonance_shift(
            audio,
            sample_rate=sample_rate,
            peak_limit=args.peak_limit,
            world_sr=args.world_sr,
            frame_period_ms=args.frame_period_ms,
            frame_length=int(params["frame_length"]),
            hop_length=int(params["hop_length"]),
            lpc_order=int(params["lpc_order"]),
            search_ranges_hz=params["search_ranges_hz"],
            shift_ratios=[float(value) for value in params["shift_ratios"]],
            blend=float(params["blend"]),
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
        pack_title="Stage0 Speech LPC Listening Pack",
        purpose="lpc residual-preserving pole edit probe after representation-layer pivot",
        script_name="build_stage0_speech_lpc_listening_pack.py",
        rule_config_path=rule_config_path,
    )
    print(f"Wrote {summary_path}")
    print(f"Selected rows: {len(summary_rows)}")
    print(f"Output dir: {output_dir}")


if __name__ == "__main__":
    main()
