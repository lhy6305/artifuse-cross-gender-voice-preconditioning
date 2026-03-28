from __future__ import annotations

import argparse
import math
from collections import defaultdict
from pathlib import Path

import librosa
import numpy as np
import scipy.fft

from apply_stage0_rule_preconditioner import load_audio, resolve_path, save_audio
from build_stage0_speech_listening_pack import TARGET_DIRECTION_BY_SOURCE_GENDER, load_source_rows, select_rows
from stage0_speech_envelope_pack_common import (
    analyze_f0,
    build_enabled_directional_rule_lookup,
    build_output_stem,
    build_summary_row,
    interpolate_voiced_mask,
    load_json,
    read_reference_rows,
    safe_rms,
    select_reference_rows,
    stft_frame_centers_sec,
    write_pack_readme,
    write_summary,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RULE_CONFIG = ROOT / "experiments" / "stage0_baseline" / "v1_full" / "speech_cepstral_envelope_candidate_v1.json"
DEFAULT_INPUT_CSV = ROOT / "experiments" / "fixed_eval" / "v1_2" / "fixed_eval_review_final_v1_2.csv"
DEFAULT_REFERENCE_CSV = ROOT / "data" / "datasets" / "_meta" / "utterance_manifest_clean_speech_v1.csv"
DEFAULT_OUTPUT_DIR = ROOT / "artifacts" / "listening_review" / "stage0_speech_cepstral_listening_pack" / "v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rule-config", default=str(DEFAULT_RULE_CONFIG))
    parser.add_argument("--input-csv", default=str(DEFAULT_INPUT_CSV))
    parser.add_argument("--reference-csv", default=str(DEFAULT_REFERENCE_CSV))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--samples-per-cell", type=int, default=2)
    parser.add_argument("--reference-samples-per-cell", type=int, default=24)
    parser.add_argument("--audio-format", choices=["wav", "flac"], default="wav")
    parser.add_argument("--n-fft", type=int, default=2048)
    parser.add_argument("--hop-length", type=int, default=256)
    parser.add_argument("--peak-limit", type=float, default=0.98)
    parser.add_argument("--world-sr", type=int, default=16000)
    parser.add_argument("--frame-period-ms", type=float, default=10.0)
    return parser.parse_args()


def extract_cepstral_centroid(
    audio: np.ndarray,
    *,
    sample_rate: int,
    n_fft: int,
    hop_length: int,
    keep_coeffs: int,
    world_sr: int,
    frame_period_ms: float,
) -> np.ndarray | None:
    stft = librosa.stft(audio.astype(np.float32), n_fft=n_fft, hop_length=hop_length)
    magnitude = np.abs(stft).astype(np.float32)
    if magnitude.size == 0:
        return None
    log_mag = np.log(np.maximum(magnitude, 1e-7))
    cep = scipy.fft.dct(log_mag, type=2, axis=0, norm="ortho")
    f0, world_times_sec = analyze_f0(audio, sample_rate, world_sr, frame_period_ms)
    frame_times_sec = stft_frame_centers_sec(cep.shape[1], n_fft, hop_length, sample_rate)
    voiced_mask = interpolate_voiced_mask(frame_times_sec, world_times_sec, f0)
    voiced_frames = cep[1 : 1 + keep_coeffs, voiced_mask >= 0.5]
    if voiced_frames.size == 0:
        return None
    return np.mean(voiced_frames, axis=1).astype(np.float32)


def build_reference_delta_lookup(
    reference_rows: list[dict[str, str]],
    *,
    n_fft: int,
    hop_length: int,
    keep_coeffs: int,
    world_sr: int,
    frame_period_ms: float,
) -> dict[tuple[str, str], np.ndarray]:
    centroids_by_group: dict[tuple[str, str], list[np.ndarray]] = defaultdict(list)
    for row in reference_rows:
        audio, sample_rate = load_audio(resolve_path(row["path_raw"]))
        centroid = extract_cepstral_centroid(
            audio,
            sample_rate=sample_rate,
            n_fft=n_fft,
            hop_length=hop_length,
            keep_coeffs=keep_coeffs,
            world_sr=world_sr,
            frame_period_ms=frame_period_ms,
        )
        if centroid is None:
            continue
        centroids_by_group[(row["dataset_name"], row["gender"])].append(centroid)

    output: dict[tuple[str, str], np.ndarray] = {}
    for dataset_name in sorted({key[0] for key in centroids_by_group}):
        female_vectors = centroids_by_group.get((dataset_name, "female"), [])
        male_vectors = centroids_by_group.get((dataset_name, "male"), [])
        if not female_vectors or not male_vectors:
            continue
        female_mean = np.mean(np.stack(female_vectors, axis=0), axis=0)
        male_mean = np.mean(np.stack(male_vectors, axis=0), axis=0)
        output[(dataset_name, "feminine")] = (female_mean - male_mean).astype(np.float32)
        output[(dataset_name, "masculine")] = (male_mean - female_mean).astype(np.float32)
    return output


def apply_cepstral_envelope_shift(
    audio: np.ndarray,
    *,
    sample_rate: int,
    n_fft: int,
    hop_length: int,
    peak_limit: float,
    world_sr: int,
    frame_period_ms: float,
    cepstral_delta: np.ndarray,
    keep_coeffs: int,
    delta_scale: float,
    blend: float,
    max_envelope_gain_db: float,
) -> np.ndarray:
    stft = librosa.stft(audio.astype(np.float32), n_fft=n_fft, hop_length=hop_length)
    magnitude = np.abs(stft).astype(np.float32)
    phase = np.angle(stft)
    if magnitude.size == 0:
        return audio.astype(np.float32)

    log_mag = np.log(np.maximum(magnitude, 1e-7))
    cep = scipy.fft.dct(log_mag, type=2, axis=0, norm="ortho")
    f0, world_times_sec = analyze_f0(audio, sample_rate, world_sr, frame_period_ms)
    frame_times_sec = stft_frame_centers_sec(cep.shape[1], n_fft, hop_length, sample_rate)
    voiced_mask = interpolate_voiced_mask(frame_times_sec, world_times_sec, f0)

    output_cep = np.array(cep, dtype=np.float32, copy=True)
    coeff_count = min(int(keep_coeffs), int(cepstral_delta.shape[0]), int(output_cep.shape[0] - 1))
    if coeff_count <= 0:
        return audio.astype(np.float32)

    output_cep[1 : 1 + coeff_count, :] += (
        float(delta_scale) * cepstral_delta[:coeff_count, None] * voiced_mask[None, :]
    )
    modified_log_mag = scipy.fft.idct(output_cep, type=2, axis=0, norm="ortho").astype(np.float32)
    max_delta_ln = max_envelope_gain_db / 20.0 * math.log(10.0)
    delta_log_mag = np.clip(modified_log_mag - log_mag, -max_delta_ln, max_delta_ln)
    adjusted_mag = magnitude * np.exp(float(blend) * delta_log_mag)
    out = librosa.istft(adjusted_mag * np.exp(1j * phase), hop_length=hop_length, length=len(audio))

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

    reference_rows = select_reference_rows(
        read_reference_rows(resolve_path(args.reference_csv)),
        samples_per_cell=args.reference_samples_per_cell,
    )
    max_keep_coeffs = max(int(rule["method_params"]["keep_coeffs"]) for rule in rule_config["rules"] if rule.get("enabled", False))
    reference_delta_lookup = build_reference_delta_lookup(
        reference_rows,
        n_fft=args.n_fft,
        hop_length=args.hop_length,
        keep_coeffs=max_keep_coeffs,
        world_sr=args.world_sr,
        frame_period_ms=args.frame_period_ms,
    )

    output_dir = resolve_path(args.output_dir)
    originals_dir = output_dir / "original"
    processed_dir = output_dir / "processed"
    summary_rows: list[dict[str, str]] = []

    for row in selected_rows:
        target_direction = TARGET_DIRECTION_BY_SOURCE_GENDER[row["gender"]]
        rule = rule_lookup[(row["dataset_name"], target_direction)]
        params = rule["method_params"]
        cepstral_delta = reference_delta_lookup.get((row["dataset_name"], target_direction))
        if cepstral_delta is None:
            raise ValueError(f"Missing cepstral reference delta for {(row['dataset_name'], target_direction)}")

        input_audio = resolve_path(row["path_raw"])
        stem = build_output_stem(row, target_direction=target_direction, method_token="cep")
        original_copy = originals_dir / f"{stem}.{args.audio_format}"
        processed_audio = processed_dir / f"{stem}.{args.audio_format}"

        audio, sample_rate = load_audio(input_audio)
        save_audio(original_copy, audio, sample_rate)
        out = apply_cepstral_envelope_shift(
            audio,
            sample_rate=sample_rate,
            n_fft=args.n_fft,
            hop_length=args.hop_length,
            peak_limit=args.peak_limit,
            world_sr=args.world_sr,
            frame_period_ms=args.frame_period_ms,
            cepstral_delta=cepstral_delta,
            keep_coeffs=int(params["keep_coeffs"]),
            delta_scale=float(params["delta_scale"]),
            blend=float(params["blend"]),
            max_envelope_gain_db=float(params["max_envelope_gain_db"]),
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
        pack_title="Stage0 Speech Cepstral Listening Pack",
        purpose="low-order cepstral envelope edit probe after LPC pole-edit rejection",
        script_name="build_stage0_speech_cepstral_listening_pack.py",
        rule_config_path=rule_config_path,
    )
    print(f"Wrote {summary_path}")
    print(f"Reference rows: {len(reference_rows)}")
    print(f"Selected rows: {len(summary_rows)}")
    print(f"Output dir: {output_dir}")


if __name__ == "__main__":
    main()
