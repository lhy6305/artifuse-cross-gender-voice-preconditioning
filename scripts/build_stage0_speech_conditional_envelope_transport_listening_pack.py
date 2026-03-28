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
    build_smoothing_kernel,
    interpolate_voiced_mask,
    load_json,
    read_reference_rows,
    safe_rms,
    select_reference_rows,
    smooth_along_time,
    stft_frame_centers_sec,
    write_pack_readme,
    write_summary,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RULE_CONFIG = ROOT / "experiments" / "stage0_baseline" / "v1_full" / "speech_conditional_envelope_transport_candidate_v1.json"
DEFAULT_INPUT_CSV = ROOT / "experiments" / "fixed_eval" / "v1_2" / "fixed_eval_review_final_v1_2.csv"
DEFAULT_REFERENCE_CSV = ROOT / "data" / "datasets" / "_meta" / "utterance_manifest_clean_speech_v1.csv"
DEFAULT_OUTPUT_DIR = ROOT / "artifacts" / "listening_review" / "stage0_speech_conditional_envelope_transport_listening_pack" / "v1"


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


def interpolate_track(frame_times_sec: np.ndarray, world_times_sec: np.ndarray, values: np.ndarray) -> np.ndarray:
    if frame_times_sec.size == 0 or world_times_sec.size == 0 or values.size == 0:
        return np.zeros(frame_times_sec.shape[0], dtype=np.float32)
    return np.interp(frame_times_sec, world_times_sec, values, left=values[0], right=values[-1]).astype(np.float32)


def f0_bucket_name(f0_hz: float, edges_hz: list[float]) -> str:
    for index, edge_hz in enumerate(edges_hz):
        if f0_hz < edge_hz:
            return f"b{index}"
    return f"b{len(edges_hz)}"


def extract_reference_frames(
    audio: np.ndarray,
    *,
    sample_rate: int,
    n_fft: int,
    hop_length: int,
    keep_coeffs: int,
    proxy_coeffs: int,
    world_sr: int,
    frame_period_ms: float,
    frame_stride: int,
    f0_bucket_edges_hz: list[float],
) -> list[tuple[str, np.ndarray, np.ndarray]]:
    stft = librosa.stft(audio.astype(np.float32), n_fft=n_fft, hop_length=hop_length)
    magnitude = np.abs(stft).astype(np.float32)
    if magnitude.size == 0:
        return []
    log_mag = np.log(np.maximum(magnitude, 1e-7))
    cep = scipy.fft.dct(log_mag, type=2, axis=0, norm="ortho").astype(np.float32)
    f0, world_times_sec = analyze_f0(audio, sample_rate, world_sr, frame_period_ms)
    frame_times_sec = stft_frame_centers_sec(cep.shape[1], n_fft, hop_length, sample_rate)
    voiced_mask = interpolate_voiced_mask(frame_times_sec, world_times_sec, f0)
    frame_f0 = interpolate_track(frame_times_sec, world_times_sec, f0)

    coeff_count = min(int(keep_coeffs), int(cep.shape[0] - 1))
    proxy_count = min(int(proxy_coeffs), coeff_count)
    if coeff_count <= 0 or proxy_count <= 0:
        return []

    frames: list[tuple[str, np.ndarray, np.ndarray]] = []
    stride = max(int(frame_stride), 1)
    for frame_idx in range(0, cep.shape[1], stride):
        if voiced_mask[frame_idx] < 0.5:
            continue
        current_f0 = float(frame_f0[frame_idx])
        if current_f0 <= 0.0:
            continue
        full_vector = cep[1 : 1 + coeff_count, frame_idx].astype(np.float32, copy=True)
        proxy_vector = full_vector[:proxy_count].astype(np.float32, copy=True)
        frames.append((f0_bucket_name(current_f0, f0_bucket_edges_hz), proxy_vector, full_vector))
    return frames


def build_reference_bank(
    reference_rows: list[dict[str, str]],
    *,
    n_fft: int,
    hop_length: int,
    keep_coeffs: int,
    proxy_coeffs: int,
    world_sr: int,
    frame_period_ms: float,
    frame_stride: int,
    f0_bucket_edges_hz: list[float],
) -> dict[tuple[str, str, str], dict[str, np.ndarray]]:
    bank: dict[tuple[str, str, str], dict[str, list[np.ndarray]]] = defaultdict(lambda: {"proxy": [], "full": []})
    for row in reference_rows:
        audio, sample_rate = load_audio(resolve_path(row["path_raw"]))
        frames = extract_reference_frames(
            audio,
            sample_rate=sample_rate,
            n_fft=n_fft,
            hop_length=hop_length,
            keep_coeffs=keep_coeffs,
            proxy_coeffs=proxy_coeffs,
            world_sr=world_sr,
            frame_period_ms=frame_period_ms,
            frame_stride=frame_stride,
            f0_bucket_edges_hz=f0_bucket_edges_hz,
        )
        for bucket, proxy_vector, full_vector in frames:
            for key in (
                (row["dataset_name"], row["gender"], bucket),
                (row["dataset_name"], row["gender"], "all"),
            ):
                bank[key]["proxy"].append(proxy_vector)
                bank[key]["full"].append(full_vector)

    packed: dict[tuple[str, str, str], dict[str, np.ndarray]] = {}
    for key, value in bank.items():
        packed[key] = {
            "proxy": np.stack(value["proxy"], axis=0).astype(np.float32),
            "full": np.stack(value["full"], axis=0).astype(np.float32),
        }
    return packed


def nearest_reference_vector(
    current_proxy: np.ndarray,
    *,
    dataset_name: str,
    reference_gender: str,
    bucket: str,
    reference_bank: dict[tuple[str, str, str], dict[str, np.ndarray]],
    nearest_k: int,
) -> np.ndarray | None:
    candidates = [
        reference_bank.get((dataset_name, reference_gender, bucket)),
        reference_bank.get((dataset_name, reference_gender, "all")),
    ]
    bank = next((item for item in candidates if item is not None), None)
    if bank is None:
        return None
    proxy_matrix = bank["proxy"]
    full_matrix = bank["full"]
    if proxy_matrix.size == 0 or full_matrix.size == 0:
        return None

    distances = np.sum(np.square(proxy_matrix - current_proxy[None, :]), axis=1)
    k = max(1, min(int(nearest_k), int(distances.shape[0])))
    nearest_indices = np.argpartition(distances, kth=k - 1)[:k]
    target_vectors = full_matrix[nearest_indices]
    if k == 1:
        return target_vectors[0].astype(np.float32, copy=True)

    weights = 1.0 / np.maximum(distances[nearest_indices], 1e-4)
    weights = weights / np.sum(weights)
    return np.sum(target_vectors * weights[:, None], axis=0).astype(np.float32)


def apply_conditional_envelope_transport(
    audio: np.ndarray,
    *,
    sample_rate: int,
    n_fft: int,
    hop_length: int,
    peak_limit: float,
    world_sr: int,
    frame_period_ms: float,
    dataset_name: str,
    source_gender: str,
    target_gender: str,
    reference_bank: dict[tuple[str, str, str], dict[str, np.ndarray]],
    keep_coeffs: int,
    proxy_coeffs: int,
    nearest_k: int,
    delta_mode: str,
    transport_ratio: float,
    source_anchor_weight: float,
    blend: float,
    max_envelope_gain_db: float,
    max_frame_delta_l2: float,
    time_smooth_frames: int,
    f0_bucket_edges_hz: list[float],
) -> np.ndarray:
    stft = librosa.stft(audio.astype(np.float32), n_fft=n_fft, hop_length=hop_length)
    magnitude = np.abs(stft).astype(np.float32)
    phase = np.angle(stft)
    if magnitude.size == 0:
        return audio.astype(np.float32)

    log_mag = np.log(np.maximum(magnitude, 1e-7))
    cep = scipy.fft.dct(log_mag, type=2, axis=0, norm="ortho").astype(np.float32)
    f0, world_times_sec = analyze_f0(audio, sample_rate, world_sr, frame_period_ms)
    frame_times_sec = stft_frame_centers_sec(cep.shape[1], n_fft, hop_length, sample_rate)
    voiced_mask = interpolate_voiced_mask(frame_times_sec, world_times_sec, f0)
    frame_f0 = interpolate_track(frame_times_sec, world_times_sec, f0)

    coeff_count = min(int(keep_coeffs), int(cep.shape[0] - 1))
    proxy_count = min(int(proxy_coeffs), coeff_count)
    if coeff_count <= 0 or proxy_count <= 0:
        return audio.astype(np.float32)

    frame_delta = np.zeros((coeff_count, cep.shape[1]), dtype=np.float32)
    voiced_binary = np.zeros(cep.shape[1], dtype=np.float32)
    for frame_idx in range(cep.shape[1]):
        if voiced_mask[frame_idx] < 0.5:
            continue
        current_f0 = float(frame_f0[frame_idx])
        if current_f0 <= 0.0:
            continue
        current_full = cep[1 : 1 + coeff_count, frame_idx].astype(np.float32, copy=False)
        bucket = f0_bucket_name(current_f0, f0_bucket_edges_hz)
        target_full = nearest_reference_vector(
            current_full[:proxy_count],
            dataset_name=dataset_name,
            reference_gender=target_gender,
            bucket=bucket,
            reference_bank=reference_bank,
            nearest_k=nearest_k,
        )
        if target_full is None:
            continue
        if delta_mode == "contrastive_anchor":
            source_full = nearest_reference_vector(
                current_full[:proxy_count],
                dataset_name=dataset_name,
                reference_gender=source_gender,
                bucket=bucket,
                reference_bank=reference_bank,
                nearest_k=nearest_k,
            )
            if source_full is None:
                continue
            anchor = float(source_anchor_weight) * source_full[:coeff_count] + (1.0 - float(source_anchor_weight)) * current_full
            delta = (target_full[:coeff_count] - anchor) * float(transport_ratio)
        else:
            delta = (target_full[:coeff_count] - current_full) * float(transport_ratio)
        delta_norm = float(np.linalg.norm(delta))
        if delta_norm > max_frame_delta_l2 > 0.0:
            delta = delta * (max_frame_delta_l2 / delta_norm)
        frame_delta[:, frame_idx] = delta
        voiced_binary[frame_idx] = 1.0

    smoothed_delta = smooth_along_time(frame_delta, voiced_binary, build_smoothing_kernel(int(time_smooth_frames)))
    output_cep = np.array(cep, dtype=np.float32, copy=True)
    output_cep[1 : 1 + coeff_count, :] += smoothed_delta * voiced_mask[None, :]

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
    if peak > peak_limit and peak > 0.0:
        out = out * (peak_limit / peak)
    return out.astype(np.float32)


def main() -> None:
    args = parse_args()
    rule_config_path = resolve_path(args.rule_config)
    rule_config = load_json(rule_config_path)
    rule_lookup = build_enabled_directional_rule_lookup(rule_config)
    selected_rows = select_rows(load_source_rows(resolve_path(args.input_csv)), samples_per_cell=args.samples_per_cell)

    enabled_rules = [rule for rule in rule_config["rules"] if rule.get("enabled", False)]
    max_keep_coeffs = max(int(rule["method_params"]["keep_coeffs"]) for rule in enabled_rules)
    max_proxy_coeffs = max(int(rule["method_params"]["proxy_coeffs"]) for rule in enabled_rules)
    max_reference_stride = max(int(rule["method_params"].get("reference_frame_stride", 1)) for rule in enabled_rules)
    f0_bucket_edges_hz = [float(value) for value in enabled_rules[0]["method_params"]["f0_bucket_edges_hz"]]

    reference_rows = select_reference_rows(
        read_reference_rows(resolve_path(args.reference_csv)),
        samples_per_cell=args.reference_samples_per_cell,
    )
    reference_bank = build_reference_bank(
        reference_rows,
        n_fft=args.n_fft,
        hop_length=args.hop_length,
        keep_coeffs=max_keep_coeffs,
        proxy_coeffs=max_proxy_coeffs,
        world_sr=args.world_sr,
        frame_period_ms=args.frame_period_ms,
        frame_stride=max_reference_stride,
        f0_bucket_edges_hz=f0_bucket_edges_hz,
    )

    output_dir = resolve_path(args.output_dir)
    originals_dir = output_dir / "original"
    processed_dir = output_dir / "processed"
    summary_rows: list[dict[str, str]] = []

    for row in selected_rows:
        target_direction = TARGET_DIRECTION_BY_SOURCE_GENDER[row["gender"]]
        source_gender = row["gender"]
        target_gender = "female" if target_direction == "feminine" else "male"
        rule = rule_lookup[(row["dataset_name"], target_direction)]
        params = rule["method_params"]

        input_audio = resolve_path(row["path_raw"])
        stem = build_output_stem(row, target_direction=target_direction, method_token="cet")
        original_copy = originals_dir / f"{stem}.{args.audio_format}"
        processed_audio = processed_dir / f"{stem}.{args.audio_format}"

        audio, sample_rate = load_audio(input_audio)
        save_audio(original_copy, audio, sample_rate)
        out = apply_conditional_envelope_transport(
            audio,
            sample_rate=sample_rate,
            n_fft=args.n_fft,
            hop_length=args.hop_length,
            peak_limit=args.peak_limit,
            world_sr=args.world_sr,
            frame_period_ms=args.frame_period_ms,
            dataset_name=row["dataset_name"],
            source_gender=source_gender,
            target_gender=target_gender,
            reference_bank=reference_bank,
            keep_coeffs=int(params["keep_coeffs"]),
            proxy_coeffs=int(params["proxy_coeffs"]),
            nearest_k=int(params["nearest_k"]),
            delta_mode=str(params.get("delta_mode", "target_pull")),
            transport_ratio=float(params["transport_ratio"]),
            source_anchor_weight=float(params.get("source_anchor_weight", 1.0)),
            blend=float(params["blend"]),
            max_envelope_gain_db=float(params["max_envelope_gain_db"]),
            max_frame_delta_l2=float(params["max_frame_delta_l2"]),
            time_smooth_frames=int(params["time_smooth_frames"]),
            f0_bucket_edges_hz=[float(value) for value in params["f0_bucket_edges_hz"]],
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
        pack_title="Stage0 Speech Conditional Envelope Transport Listening Pack",
        purpose="content-and-f0-conditioned reference envelope transport probe",
        script_name="build_stage0_speech_conditional_envelope_transport_listening_pack.py",
        rule_config_path=rule_config_path,
    )
    print(f"Wrote {summary_path}")
    print(f"Reference rows: {len(reference_rows)}")
    print(f"Reference banks: {len(reference_bank)}")
    print(f"Selected rows: {len(summary_rows)}")
    print(f"Output dir: {output_dir}")


if __name__ == "__main__":
    main()
