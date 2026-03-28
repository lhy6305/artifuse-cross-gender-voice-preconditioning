from __future__ import annotations

import argparse
import math
from collections import defaultdict
from pathlib import Path

import librosa
import numpy as np
import scipy.fft
import torch
import torch.nn as nn
import torch.optim as optim

from apply_stage0_rule_preconditioner import load_audio, resolve_path, save_audio
from build_stage0_speech_listening_pack import TARGET_DIRECTION_BY_SOURCE_GENDER, load_source_rows, select_rows
from stage0_speech_envelope_pack_common import (
    GenderProbe,
    analyze_f0,
    build_enabled_directional_rule_lookup,
    build_output_stem,
    build_summary_row,
    build_smoothing_kernel,
    interpolate_voiced_mask,
    load_json,
    parse_hidden_dims,
    read_reference_rows,
    resolve_torch_device,
    safe_rms,
    select_reference_rows,
    smooth_along_time,
    stable_name_seed,
    stft_frame_centers_sec,
    write_pack_readme,
    write_summary,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RULE_CONFIG = ROOT / "experiments" / "stage0_baseline" / "v1_full" / "speech_source_filter_residual_candidate_v1.json"
DEFAULT_INPUT_CSV = ROOT / "experiments" / "fixed_eval" / "v1_2" / "fixed_eval_review_final_v1_2.csv"
DEFAULT_REFERENCE_CSV = ROOT / "data" / "datasets" / "_meta" / "utterance_manifest_clean_speech_v1.csv"
DEFAULT_OUTPUT_DIR = ROOT / "artifacts" / "listening_review" / "stage0_speech_source_filter_residual_listening_pack" / "v1"


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
    parser.add_argument("--probe-device", default="cpu")
    parser.add_argument("--probe-seed", type=int, default=20260328)
    return parser.parse_args()


def band_masks_for_fft(n_fft_bins: int, sample_rate: int, band_edges_hz: list[float]) -> list[np.ndarray]:
    freqs_hz = np.linspace(0.0, sample_rate / 2.0, n_fft_bins, dtype=np.float32)
    masks: list[np.ndarray] = []
    for lower_hz, upper_hz in zip(band_edges_hz[:-1], band_edges_hz[1:]):
        if upper_hz <= lower_hz:
            continue
        mask = (freqs_hz >= float(lower_hz)) & (freqs_hz < float(upper_hz))
        if not np.any(mask):
            nearest_idx = int(np.argmin(np.abs(freqs_hz - (float(lower_hz) + float(upper_hz)) / 2.0)))
            mask[nearest_idx] = True
        masks.append(mask)
    if not masks:
        raise ValueError("No valid residual bands were constructed")
    return masks


def build_envelope_log_mag(log_mag: np.ndarray, keep_coeffs: int) -> tuple[np.ndarray, np.ndarray]:
    cep = scipy.fft.dct(log_mag, type=2, axis=0, norm="ortho").astype(np.float32)
    coeff_count = min(int(keep_coeffs), int(cep.shape[0] - 1))
    env_cep = np.zeros_like(cep)
    env_cep[0, :] = cep[0, :]
    if coeff_count > 0:
        env_cep[1 : 1 + coeff_count, :] = cep[1 : 1 + coeff_count, :]
    envelope_log = scipy.fft.idct(env_cep, type=2, axis=0, norm="ortho").astype(np.float32)
    return cep, envelope_log


def extract_frame_feature_matrix(
    audio: np.ndarray,
    *,
    sample_rate: int,
    n_fft: int,
    hop_length: int,
    keep_coeffs: int,
    detail_band_edges_hz: list[float],
    detail_clip_db: float,
    world_sr: int,
    frame_period_ms: float,
    frame_stride: int,
) -> np.ndarray | None:
    stft = librosa.stft(audio.astype(np.float32), n_fft=n_fft, hop_length=hop_length)
    magnitude = np.abs(stft).astype(np.float32)
    if magnitude.size == 0:
        return None

    log_mag = np.log(np.maximum(magnitude, 1e-7))
    cep, envelope_log = build_envelope_log_mag(log_mag, keep_coeffs)
    coeff_count = min(int(keep_coeffs), int(cep.shape[0] - 1))
    if coeff_count <= 0:
        return None

    detail_ln = np.clip(
        log_mag - envelope_log,
        -(float(detail_clip_db) / 20.0) * math.log(10.0),
        (float(detail_clip_db) / 20.0) * math.log(10.0),
    ).astype(np.float32)
    masks = band_masks_for_fft(magnitude.shape[0], sample_rate, detail_band_edges_hz)

    f0, world_times_sec = analyze_f0(audio, sample_rate, world_sr, frame_period_ms)
    frame_times_sec = stft_frame_centers_sec(cep.shape[1], n_fft, hop_length, sample_rate)
    voiced_mask = interpolate_voiced_mask(frame_times_sec, world_times_sec, f0)
    voiced_indices = np.flatnonzero(voiced_mask >= 0.5)
    if voiced_indices.size == 0:
        return None

    features = np.zeros((voiced_indices.size, coeff_count + len(masks)), dtype=np.float32)
    features[:, :coeff_count] = cep[1 : 1 + coeff_count, voiced_indices].T
    for band_idx, mask in enumerate(masks):
        features[:, coeff_count + band_idx] = np.mean(detail_ln[mask][:, voiced_indices], axis=0)

    stride = max(int(frame_stride), 1)
    return features[::stride].astype(np.float32, copy=True)


def build_probe_lookup(
    reference_rows: list[dict[str, str]],
    *,
    n_fft: int,
    hop_length: int,
    keep_coeffs: int,
    detail_band_edges_hz: list[float],
    detail_clip_db: float,
    hidden_dims: list[int],
    train_epochs: int,
    train_batch_size: int,
    learning_rate: float,
    weight_decay: float,
    world_sr: int,
    frame_period_ms: float,
    frame_stride: int,
    device: torch.device,
    seed: int,
) -> dict[str, dict[str, object]]:
    frames_by_dataset: dict[str, list[np.ndarray]] = defaultdict(list)
    frames_by_dataset_gender: dict[tuple[str, str], list[np.ndarray]] = defaultdict(list)
    for row in reference_rows:
        audio, sample_rate = load_audio(resolve_path(row["path_raw"]))
        feature_frames = extract_frame_feature_matrix(
            audio,
            sample_rate=sample_rate,
            n_fft=n_fft,
            hop_length=hop_length,
            keep_coeffs=keep_coeffs,
            detail_band_edges_hz=detail_band_edges_hz,
            detail_clip_db=detail_clip_db,
            world_sr=world_sr,
            frame_period_ms=frame_period_ms,
            frame_stride=frame_stride,
        )
        if feature_frames is None:
            continue
        frames_by_dataset[row["dataset_name"]].append(feature_frames)
        frames_by_dataset_gender[(row["dataset_name"], row["gender"])].append(feature_frames)

    lookup: dict[str, dict[str, object]] = {}
    for dataset_name, dataset_chunks in frames_by_dataset.items():
        all_frames = np.concatenate(dataset_chunks, axis=0).astype(np.float32)
        if all_frames.shape[0] < 8:
            continue
        mean_vector = np.mean(all_frames, axis=0).astype(np.float32)
        std_vector = np.maximum(np.std(all_frames, axis=0), 1e-3).astype(np.float32)

        feature_list: list[np.ndarray] = []
        label_list: list[np.ndarray] = []
        for gender, label in (("female", 1.0), ("male", 0.0)):
            gender_chunks = frames_by_dataset_gender.get((dataset_name, gender), [])
            if not gender_chunks:
                break
            gender_frames = np.concatenate(gender_chunks, axis=0).astype(np.float32)
            normalized = ((gender_frames - mean_vector[None, :]) / std_vector[None, :]).astype(np.float32)
            feature_list.append(normalized)
            label_list.append(np.full((normalized.shape[0],), float(label), dtype=np.float32))
        if len(feature_list) != 2:
            continue

        features = np.concatenate(feature_list, axis=0).astype(np.float32)
        labels = np.concatenate(label_list, axis=0).astype(np.float32)
        local_seed = int(seed) + stable_name_seed(dataset_name) % 10000
        torch.manual_seed(local_seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(local_seed)

        model = GenderProbe(input_dim=int(features.shape[1]), hidden_dims=hidden_dims).to(device)
        optimizer = optim.AdamW(model.parameters(), lr=float(learning_rate), weight_decay=float(weight_decay))
        loss_fn = nn.BCEWithLogitsLoss()
        inputs = torch.from_numpy(features).to(device)
        targets = torch.from_numpy(labels).to(device)
        batch_size = max(1, min(int(train_batch_size), int(inputs.shape[0])))

        model.train()
        for epoch_idx in range(max(1, int(train_epochs))):
            generator = torch.Generator(device=device.type if device.type != "cpu" else "cpu")
            generator.manual_seed(local_seed + epoch_idx)
            permutation = torch.randperm(int(inputs.shape[0]), generator=generator, device=device)
            for start_idx in range(0, int(inputs.shape[0]), batch_size):
                batch_indices = permutation[start_idx : start_idx + batch_size]
                batch_inputs = inputs[batch_indices]
                batch_targets = targets[batch_indices]
                optimizer.zero_grad(set_to_none=True)
                logits = model(batch_inputs)
                loss = loss_fn(logits, batch_targets)
                loss.backward()
                optimizer.step()
        model.eval()
        lookup[dataset_name] = {
            "probe": model,
            "mean_vector": mean_vector,
            "std_vector": std_vector,
        }
    return lookup


def apply_probe_guided_source_filter_shift(
    audio: np.ndarray,
    *,
    sample_rate: int,
    n_fft: int,
    hop_length: int,
    peak_limit: float,
    world_sr: int,
    frame_period_ms: float,
    probe_pack: dict[str, object],
    device: torch.device,
    target_gender: str,
    keep_coeffs: int,
    detail_band_edges_hz: list[float],
    detail_clip_db: float,
    probe_opt_steps: int,
    probe_step_size: float,
    lambda_l2: float,
    lambda_l1: float,
    envelope_blend: float,
    detail_blend: float,
    max_envelope_gain_db: float,
    max_detail_band_delta_db: float,
    max_feature_delta_l2: float,
    time_smooth_frames: int,
) -> np.ndarray:
    stft = librosa.stft(audio.astype(np.float32), n_fft=n_fft, hop_length=hop_length)
    magnitude = np.abs(stft).astype(np.float32)
    phase = np.angle(stft)
    if magnitude.size == 0:
        return audio.astype(np.float32)

    log_mag = np.log(np.maximum(magnitude, 1e-7))
    cep, envelope_log = build_envelope_log_mag(log_mag, keep_coeffs)
    full_coeff_count = min(int(keep_coeffs), int(cep.shape[0] - 1))
    if full_coeff_count <= 0:
        return audio.astype(np.float32)

    detail_ln = np.clip(
        log_mag - envelope_log,
        -(float(detail_clip_db) / 20.0) * math.log(10.0),
        (float(detail_clip_db) / 20.0) * math.log(10.0),
    ).astype(np.float32)
    band_masks = band_masks_for_fft(magnitude.shape[0], sample_rate, detail_band_edges_hz)

    probe = probe_pack["probe"]
    assert isinstance(probe, GenderProbe)
    mean_vector = np.asarray(probe_pack["mean_vector"], dtype=np.float32)
    std_vector = np.asarray(probe_pack["std_vector"], dtype=np.float32)
    band_count = len(band_masks)
    if mean_vector.shape[0] != full_coeff_count + band_count:
        raise ValueError("Probe feature dimension does not match runtime feature construction")

    f0, world_times_sec = analyze_f0(audio, sample_rate, world_sr, frame_period_ms)
    frame_times_sec = stft_frame_centers_sec(cep.shape[1], n_fft, hop_length, sample_rate)
    voiced_mask = interpolate_voiced_mask(frame_times_sec, world_times_sec, f0)

    frame_cep_delta = np.zeros((full_coeff_count, cep.shape[1]), dtype=np.float32)
    frame_band_delta = np.zeros((band_count, cep.shape[1]), dtype=np.float32)
    voiced_binary = np.zeros(cep.shape[1], dtype=np.float32)
    target_label_value = 1.0 if target_gender == "female" else 0.0
    target_tensor = torch.tensor([target_label_value], dtype=torch.float32, device=device)
    loss_fn = nn.BCEWithLogitsLoss()
    max_detail_ln = (float(max_detail_band_delta_db) / 20.0) * math.log(10.0)

    for frame_idx in range(cep.shape[1]):
        if voiced_mask[frame_idx] < 0.5:
            continue
        current_cep = cep[1 : 1 + full_coeff_count, frame_idx].astype(np.float32, copy=False)
        current_band_values = np.array(
            [float(np.mean(detail_ln[mask, frame_idx])) for mask in band_masks],
            dtype=np.float32,
        )
        current_features = np.concatenate([current_cep, current_band_values], axis=0)
        normalized = ((current_features - mean_vector) / std_vector).astype(np.float32)
        base = torch.from_numpy(normalized[None, :]).to(device)
        candidate = base.clone().detach().requires_grad_(True)
        optimizer = optim.Adam([candidate], lr=float(probe_step_size))
        for _ in range(max(1, int(probe_opt_steps))):
            optimizer.zero_grad(set_to_none=True)
            logits = probe(candidate)
            cls_loss = loss_fn(logits, target_tensor)
            delta = candidate - base
            reg_l2 = torch.mean(delta * delta)
            reg_l1 = torch.mean(torch.abs(delta))
            loss = cls_loss + float(lambda_l2) * reg_l2 + float(lambda_l1) * reg_l1
            loss.backward()
            optimizer.step()

        feature_delta = ((candidate.detach() - base).cpu().numpy()[0] * std_vector).astype(np.float32)
        cep_delta = feature_delta[:full_coeff_count]
        band_delta = feature_delta[full_coeff_count:]
        cep_delta_norm = float(np.linalg.norm(cep_delta))
        if cep_delta_norm > max_feature_delta_l2 > 0.0:
            cep_delta = cep_delta * (float(max_feature_delta_l2) / cep_delta_norm)
        band_delta = np.clip(band_delta, -max_detail_ln, max_detail_ln)
        frame_cep_delta[:, frame_idx] = cep_delta
        frame_band_delta[:, frame_idx] = band_delta
        voiced_binary[frame_idx] = 1.0

    kernel = build_smoothing_kernel(int(time_smooth_frames))
    smoothed_cep_delta = smooth_along_time(frame_cep_delta, voiced_binary, kernel)
    smoothed_band_delta = smooth_along_time(frame_band_delta, voiced_binary, kernel)

    cep_delta_full = np.zeros_like(cep)
    cep_delta_full[1 : 1 + full_coeff_count, :] = smoothed_cep_delta * voiced_mask[None, :]
    envelope_delta_log = scipy.fft.idct(cep_delta_full, type=2, axis=0, norm="ortho").astype(np.float32)

    detail_delta_log = np.zeros_like(log_mag, dtype=np.float32)
    for band_idx, mask in enumerate(band_masks):
        detail_delta_log[mask, :] = smoothed_band_delta[band_idx][None, :] * voiced_mask[None, :]

    max_envelope_ln = (float(max_envelope_gain_db) / 20.0) * math.log(10.0)
    total_delta_log = (
        float(envelope_blend) * np.clip(envelope_delta_log, -max_envelope_ln, max_envelope_ln)
        + float(detail_blend) * np.clip(detail_delta_log, -max_detail_ln, max_detail_ln)
    )
    adjusted_mag = magnitude * np.exp(total_delta_log)
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
    if not enabled_rules:
        raise ValueError("No enabled source-filter residual rules found")

    max_keep_coeffs = max(int(rule["method_params"]["keep_coeffs"]) for rule in enabled_rules)
    max_reference_stride = max(int(rule["method_params"].get("reference_frame_stride", 1)) for rule in enabled_rules)
    hidden_dims = parse_hidden_dims(enabled_rules[0]["method_params"]["hidden_dims"])
    train_epochs = int(enabled_rules[0]["method_params"]["train_epochs"])
    train_batch_size = int(enabled_rules[0]["method_params"]["train_batch_size"])
    learning_rate = float(enabled_rules[0]["method_params"]["learning_rate"])
    weight_decay = float(enabled_rules[0]["method_params"].get("weight_decay", 0.0))
    detail_band_edges_hz = [float(value) for value in enabled_rules[0]["method_params"]["detail_band_edges_hz"]]
    detail_clip_db = float(enabled_rules[0]["method_params"]["detail_clip_db"])
    device = resolve_torch_device(args.probe_device)

    reference_rows = select_reference_rows(
        read_reference_rows(resolve_path(args.reference_csv)),
        samples_per_cell=args.reference_samples_per_cell,
    )
    probe_lookup = build_probe_lookup(
        reference_rows,
        n_fft=args.n_fft,
        hop_length=args.hop_length,
        keep_coeffs=max_keep_coeffs,
        detail_band_edges_hz=detail_band_edges_hz,
        detail_clip_db=detail_clip_db,
        hidden_dims=hidden_dims,
        train_epochs=train_epochs,
        train_batch_size=train_batch_size,
        learning_rate=learning_rate,
        weight_decay=weight_decay,
        world_sr=args.world_sr,
        frame_period_ms=args.frame_period_ms,
        frame_stride=max_reference_stride,
        device=device,
        seed=args.probe_seed,
    )

    output_dir = resolve_path(args.output_dir)
    originals_dir = output_dir / "original"
    processed_dir = output_dir / "processed"
    summary_rows: list[dict[str, str]] = []

    for row in selected_rows:
        target_direction = TARGET_DIRECTION_BY_SOURCE_GENDER[row["gender"]]
        target_gender = "female" if target_direction == "feminine" else "male"
        rule = rule_lookup[(row["dataset_name"], target_direction)]
        params = rule["method_params"]
        probe_pack = probe_lookup.get(row["dataset_name"])
        if probe_pack is None:
            raise ValueError(f"Missing source-filter residual probe for {row['dataset_name']}")

        input_audio = resolve_path(row["path_raw"])
        stem = build_output_stem(row, target_direction=target_direction, method_token="sfres")
        original_copy = originals_dir / f"{stem}.{args.audio_format}"
        processed_audio = processed_dir / f"{stem}.{args.audio_format}"

        audio, sample_rate = load_audio(input_audio)
        save_audio(original_copy, audio, sample_rate)
        out = apply_probe_guided_source_filter_shift(
            audio,
            sample_rate=sample_rate,
            n_fft=args.n_fft,
            hop_length=args.hop_length,
            peak_limit=args.peak_limit,
            world_sr=args.world_sr,
            frame_period_ms=args.frame_period_ms,
            probe_pack=probe_pack,
            device=device,
            target_gender=target_gender,
            keep_coeffs=int(params["keep_coeffs"]),
            detail_band_edges_hz=[float(value) for value in params["detail_band_edges_hz"]],
            detail_clip_db=float(params["detail_clip_db"]),
            probe_opt_steps=int(params["probe_opt_steps"]),
            probe_step_size=float(params["probe_step_size"]),
            lambda_l2=float(params["lambda_l2"]),
            lambda_l1=float(params["lambda_l1"]),
            envelope_blend=float(params["envelope_blend"]),
            detail_blend=float(params["detail_blend"]),
            max_envelope_gain_db=float(params["max_envelope_gain_db"]),
            max_detail_band_delta_db=float(params["max_detail_band_delta_db"]),
            max_feature_delta_l2=float(params["max_feature_delta_l2"]),
            time_smooth_frames=int(params["time_smooth_frames"]),
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
        pack_title="Stage0 Speech Source-Filter Residual Listening Pack",
        purpose="joint probe-guided envelope plus voiced harmonic residual probe after envelope-only exhaustion",
        script_name="build_stage0_speech_source_filter_residual_listening_pack.py",
        rule_config_path=rule_config_path,
    )
    print(f"Wrote {summary_path}")
    print(f"Reference rows: {len(reference_rows)}")
    print(f"Probe models: {len(probe_lookup)}")
    print(f"Selected rows: {len(summary_rows)}")
    print(f"Output dir: {output_dir}")


if __name__ == "__main__":
    main()
