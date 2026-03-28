from __future__ import annotations

import argparse
import math
from pathlib import Path

import librosa
import numpy as np
import pyworld

from apply_stage0_rule_preconditioner import load_audio, resolve_path, save_audio
from build_stage0_speech_listening_pack import TARGET_DIRECTION_BY_SOURCE_GENDER, load_source_rows, select_rows
from stage0_speech_resonance_pack_common import (
    build_enabled_directional_rule_lookup,
    build_output_stem,
    build_summary_row,
    load_json,
    safe_rms,
    write_pack_readme,
    write_summary,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RULE_CONFIG = ROOT / "experiments" / "stage0_baseline" / "v1_full" / "speech_vtl_warping_candidate_v1.json"
DEFAULT_INPUT_CSV = ROOT / "experiments" / "fixed_eval" / "v1_2" / "fixed_eval_review_final_v1_2.csv"
DEFAULT_OUTPUT_DIR = ROOT / "artifacts" / "listening_review" / "stage0_speech_vtl_warping_listening_pack" / "v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rule-config", default=str(DEFAULT_RULE_CONFIG))
    parser.add_argument("--input-csv", default=str(DEFAULT_INPUT_CSV))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--samples-per-cell", type=int, default=2)
    parser.add_argument("--audio-format", choices=["wav", "flac"], default="wav")
    parser.add_argument("--peak-limit", type=float, default=0.98)
    return parser.parse_args()


def analyze_world(
    audio: np.ndarray,
    sample_rate: int,
    *,
    frame_period_ms: float,
    f0_floor_hz: float,
    f0_ceil_hz: float,
) -> tuple[np.ndarray, np.ndarray]:
    audio64 = audio.astype(np.float64)
    f0, time_axis = pyworld.harvest(
        audio64,
        sample_rate,
        frame_period=frame_period_ms,
        f0_floor=f0_floor_hz,
        f0_ceil=f0_ceil_hz,
    )
    f0 = pyworld.stonemask(audio64, f0, time_axis, sample_rate)
    sp = pyworld.cheaptrick(audio64, f0, time_axis, sample_rate)
    return f0, sp


def smooth_1d(values: np.ndarray, width: int) -> np.ndarray:
    width = max(int(width), 1)
    if width <= 1 or values.size == 0:
        return values
    if width % 2 == 0:
        width += 1
    kernel = np.ones(width, dtype=np.float64) / width
    return np.convolve(values, kernel, mode="same")


def build_band_weight(freqs_hz: np.ndarray, active_until_hz: float, taper_end_hz: float) -> np.ndarray:
    active_until_hz = float(active_until_hz)
    taper_end_hz = max(float(taper_end_hz), active_until_hz + 1.0)
    weight = np.zeros_like(freqs_hz, dtype=np.float64)
    full_mask = freqs_hz <= active_until_hz
    weight[full_mask] = 1.0
    taper_mask = (freqs_hz > active_until_hz) & (freqs_hz < taper_end_hz)
    if np.any(taper_mask):
        x = (freqs_hz[taper_mask] - active_until_hz) / (taper_end_hz - active_until_hz)
        weight[taper_mask] = 0.5 * (1.0 + np.cos(math.pi * x))
    return weight


def warp_vtl_delta_db(
    sp: np.ndarray,
    *,
    sample_rate: int,
    warp_ratio: float,
    blend: float,
    max_gain_db: float,
    sp_floor_db: float,
    freq_smooth_bins: int,
    active_until_hz: float,
    taper_end_hz: float,
    preserve_band_energy: bool,
    energy_rebalance_ratio: float,
) -> np.ndarray:
    if sp.size == 0:
        return sp
    freqs_hz = np.linspace(0.0, sample_rate / 2.0, sp.shape[1], dtype=np.float64)
    source_freqs = np.clip(freqs_hz / max(warp_ratio, 1e-6), 0.0, sample_rate / 2.0)
    floor_linear = math.pow(10.0, sp_floor_db / 20.0)
    band_weight = build_band_weight(freqs_hz, active_until_hz=active_until_hz, taper_end_hz=taper_end_hz)
    delta_db = np.empty_like(sp)
    weight_sum = float(np.sum(band_weight))

    for frame_idx in range(sp.shape[0]):
        original = np.maximum(sp[frame_idx], floor_linear)
        warped_frame = np.interp(source_freqs, freqs_hz, original, left=original[0], right=original[-1])
        frame_delta_db = 20.0 * np.log10(np.maximum(warped_frame, floor_linear) / np.maximum(original, floor_linear))
        frame_delta_db = smooth_1d(frame_delta_db, freq_smooth_bins)
        frame_delta_db = frame_delta_db * band_weight
        if preserve_band_energy and weight_sum > 1e-8:
            mean_delta = float(np.sum(frame_delta_db * band_weight) / weight_sum)
            frame_delta_db = (frame_delta_db - mean_delta * float(energy_rebalance_ratio)) * band_weight
        frame_delta_db = np.clip(frame_delta_db * blend, -abs(max_gain_db), abs(max_gain_db))
        delta_db[frame_idx] = frame_delta_db
    return delta_db


def interpolate_time_frames(values: np.ndarray, target_len: int) -> np.ndarray:
    if values.shape[0] == target_len:
        return values
    if values.shape[0] == 0:
        return np.zeros((target_len, values.shape[1]), dtype=np.float64)
    source_x = np.linspace(0.0, 1.0, values.shape[0], dtype=np.float64)
    target_x = np.linspace(0.0, 1.0, target_len, dtype=np.float64)
    output = np.empty((target_len, values.shape[1]), dtype=np.float64)
    for bin_idx in range(values.shape[1]):
        output[:, bin_idx] = np.interp(
            target_x,
            source_x,
            values[:, bin_idx],
            left=values[0, bin_idx],
            right=values[-1, bin_idx],
        )
    return output


def interpolate_mask(values: np.ndarray, target_len: int, smooth_frames: int) -> np.ndarray:
    if values.size == 0:
        return np.zeros(target_len, dtype=np.float64)
    source_x = np.linspace(0.0, 1.0, values.shape[0], dtype=np.float64)
    target_x = np.linspace(0.0, 1.0, target_len, dtype=np.float64)
    output = np.interp(target_x, source_x, values, left=values[0], right=values[-1])
    output = smooth_1d(output, smooth_frames)
    return np.clip(output, 0.0, 1.0)


def apply_vtl_warping(
    audio: np.ndarray,
    *,
    sample_rate: int,
    peak_limit: float,
    warp_ratio: float,
    blend: float,
    wet_mix: float,
    max_gain_db: float,
    sp_floor_db: float,
    f0_floor_hz: float,
    f0_ceil_hz: float,
    frame_period_ms: float,
    voiced_smooth_frames: int,
    freq_smooth_bins: int,
    active_until_hz: float,
    taper_end_hz: float,
    preserve_band_energy: bool,
    energy_rebalance_ratio: float,
) -> np.ndarray:
    f0, sp = analyze_world(
        audio,
        sample_rate,
        frame_period_ms=frame_period_ms,
        f0_floor_hz=f0_floor_hz,
        f0_ceil_hz=f0_ceil_hz,
    )
    if sp.size == 0:
        return audio.astype(np.float32)

    n_fft = max((sp.shape[1] - 1) * 2, 512)
    hop_length = max(int(round(sample_rate * frame_period_ms / 1000.0)), 1)
    stft = librosa.stft(audio.astype(np.float32), n_fft=n_fft, hop_length=hop_length)
    magnitude = np.abs(stft)
    phase = np.angle(stft)

    delta_db_world = warp_vtl_delta_db(
        sp,
        sample_rate=sample_rate,
        warp_ratio=warp_ratio,
        blend=blend,
        max_gain_db=max_gain_db,
        sp_floor_db=sp_floor_db,
        freq_smooth_bins=freq_smooth_bins,
        active_until_hz=active_until_hz,
        taper_end_hz=taper_end_hz,
        preserve_band_energy=preserve_band_energy,
        energy_rebalance_ratio=energy_rebalance_ratio,
    )
    delta_db_stft = interpolate_time_frames(delta_db_world, magnitude.shape[1]).T
    voiced_mask = interpolate_mask((f0 > 0.0).astype(np.float64), magnitude.shape[1], voiced_smooth_frames)
    gain_db = delta_db_stft * voiced_mask[None, :]
    gain = np.power(10.0, gain_db / 20.0)
    processed_mag = magnitude * gain
    processed_stft = processed_mag * np.exp(1j * phase)
    wet = librosa.istft(processed_stft, hop_length=hop_length, length=len(audio)).astype(np.float32)
    output = (1.0 - wet_mix) * audio.astype(np.float32) + wet_mix * wet

    input_rms = safe_rms(audio)
    output_rms = safe_rms(output)
    if input_rms > 1e-8 and output_rms > 1e-8:
        output = output * (input_rms / output_rms)

    peak = float(np.max(np.abs(output))) if output.size else 0.0
    if peak > peak_limit and peak > 0:
        output = output * (peak_limit / peak)
    return output.astype(np.float32)


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
        stem = build_output_stem(row, target_direction=target_direction, method_token="vtl")
        original_copy = originals_dir / f"{stem}.{args.audio_format}"
        processed_audio = processed_dir / f"{stem}.{args.audio_format}"

        audio, sample_rate = load_audio(input_audio)
        audio = audio.astype(np.float32)
        save_audio(original_copy, audio, sample_rate)
        output = apply_vtl_warping(
            audio,
            sample_rate=sample_rate,
            peak_limit=args.peak_limit,
            warp_ratio=float(params["warp_ratio"]),
            blend=float(params["blend"]),
            wet_mix=float(params["wet_mix"]),
            max_gain_db=float(params["max_gain_db"]),
            sp_floor_db=float(params["sp_floor_db"]),
            f0_floor_hz=float(params["f0_floor_hz"]),
            f0_ceil_hz=float(params["f0_ceil_hz"]),
            frame_period_ms=float(params["frame_period_ms"]),
            voiced_smooth_frames=int(params["voiced_smooth_frames"]),
            freq_smooth_bins=int(params["freq_smooth_bins"]),
            active_until_hz=float(params["active_until_hz"]),
            taper_end_hz=float(params["taper_end_hz"]),
            preserve_band_energy=bool(params["preserve_band_energy"]),
            energy_rebalance_ratio=float(
                params.get("energy_rebalance_ratio", 1.0 if params.get("preserve_band_energy", False) else 0.0)
            ),
        )
        save_audio(processed_audio, output, sample_rate)

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
        pack_title="Stage0 Speech VTL Warping Listening Pack",
        purpose="tract-length warp on WORLD envelope with original-phase reconstruction after LSF setback",
        script_name="build_stage0_speech_vtl_warping_listening_pack.py",
        rule_config_path=rule_config_path,
    )
    print(f"Wrote {summary_path}")
    print(f"Selected rows: {len(summary_rows)}")
    print(f"Output dir: {output_dir}")


if __name__ == "__main__":
    main()
