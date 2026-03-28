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
    EnvelopeAutoencoder,
    LatentTranslator,
    analyze_f0,
    build_enabled_directional_rule_lookup,
    build_output_stem,
    build_summary_row,
    build_smoothing_kernel,
    encode_frames,
    extract_voiced_cepstral_frames,
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
    train_autoencoder,
    write_pack_readme,
    write_summary,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RULE_CONFIG = ROOT / "experiments" / "stage0_baseline" / "v1_full" / "speech_conditioned_neural_envelope_candidate_v1.json"
DEFAULT_INPUT_CSV = ROOT / "experiments" / "fixed_eval" / "v1_2" / "fixed_eval_review_final_v1_2.csv"
DEFAULT_REFERENCE_CSV = ROOT / "data" / "datasets" / "_meta" / "utterance_manifest_clean_speech_v1.csv"
DEFAULT_OUTPUT_DIR = ROOT / "artifacts" / "listening_review" / "stage0_speech_conditioned_neural_envelope_listening_pack" / "v1"


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
    parser.add_argument("--ae-device", default="cpu")
    parser.add_argument("--ae-seed", type=int, default=20260328)
    return parser.parse_args()


def nearest_neighbor_indices(source_matrix: np.ndarray, target_matrix: np.ndarray) -> np.ndarray:
    if source_matrix.ndim != 2 or target_matrix.ndim != 2:
        raise ValueError("nearest_neighbor_indices expects 2D matrices")
    if source_matrix.shape[0] == 0 or target_matrix.shape[0] == 0:
        raise ValueError("nearest_neighbor_indices requires non-empty matrices")
    distances = np.sum((source_matrix[:, None, :] - target_matrix[None, :, :]) ** 2, axis=2)
    return np.argmin(distances, axis=1).astype(np.int64)


def train_translator(
    source_latents: np.ndarray,
    target_latents: np.ndarray,
    *,
    latent_dim: int,
    hidden_dims: list[int],
    train_epochs: int,
    train_batch_size: int,
    learning_rate: float,
    weight_decay: float,
    device: torch.device,
    seed: int,
) -> LatentTranslator:
    if source_latents.shape != target_latents.shape:
        raise ValueError("source_latents and target_latents must have the same shape")
    torch.manual_seed(int(seed))
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(int(seed))

    model = LatentTranslator(latent_dim=int(latent_dim), hidden_dims=hidden_dims).to(device)
    optimizer = optim.AdamW(model.parameters(), lr=float(learning_rate), weight_decay=float(weight_decay))
    loss_fn = nn.MSELoss()
    inputs = torch.from_numpy(source_latents.astype(np.float32)).to(device)
    targets = torch.from_numpy(target_latents.astype(np.float32)).to(device)
    batch_size = max(1, min(int(train_batch_size), int(inputs.shape[0])))

    model.train()
    for epoch_idx in range(max(1, int(train_epochs))):
        generator = torch.Generator(device=device.type if device.type != "cpu" else "cpu")
        generator.manual_seed(int(seed) + epoch_idx)
        permutation = torch.randperm(int(inputs.shape[0]), generator=generator, device=device)
        for start_idx in range(0, int(inputs.shape[0]), batch_size):
            batch_indices = permutation[start_idx : start_idx + batch_size]
            batch_inputs = inputs[batch_indices]
            batch_targets = targets[batch_indices]
            optimizer.zero_grad(set_to_none=True)
            pred = model(batch_inputs)
            loss = loss_fn(pred, batch_targets)
            loss.backward()
            optimizer.step()

    model.eval()
    return model


def build_conditioned_lookup(
    reference_rows: list[dict[str, str]],
    *,
    n_fft: int,
    hop_length: int,
    keep_coeffs: int,
    proxy_coeffs: int,
    latent_dims: int,
    hidden_dims: list[int],
    translator_hidden_dims: list[int],
    train_epochs: int,
    translator_epochs: int,
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
        voiced_frames = extract_voiced_cepstral_frames(
            audio,
            sample_rate=sample_rate,
            n_fft=n_fft,
            hop_length=hop_length,
            keep_coeffs=keep_coeffs,
            world_sr=world_sr,
            frame_period_ms=frame_period_ms,
            frame_stride=frame_stride,
        )
        if voiced_frames is None:
            continue
        frames_by_dataset[row["dataset_name"]].append(voiced_frames)
        frames_by_dataset_gender[(row["dataset_name"], row["gender"])].append(voiced_frames)

    lookup: dict[str, dict[str, object]] = {}
    for dataset_name, dataset_chunks in frames_by_dataset.items():
        all_frames = np.concatenate(dataset_chunks, axis=0).astype(np.float32)
        if all_frames.shape[0] < 4:
            continue
        model, mean_vector, std_vector = train_autoencoder(
            all_frames,
            hidden_dims=hidden_dims,
            latent_dim=latent_dims,
            train_epochs=train_epochs,
            train_batch_size=train_batch_size,
            learning_rate=learning_rate,
            weight_decay=weight_decay,
            device=device,
            seed=seed + stable_name_seed(dataset_name) % 10000,
        )
        latent_stats: dict[str, np.ndarray] = {}
        gender_frames_lookup: dict[str, np.ndarray] = {}
        gender_latents_lookup: dict[str, np.ndarray] = {}
        for gender in ("female", "male"):
            gender_chunks = frames_by_dataset_gender.get((dataset_name, gender), [])
            if not gender_chunks:
                break
            gender_frames = np.concatenate(gender_chunks, axis=0).astype(np.float32)
            gender_frames_lookup[gender] = gender_frames
            normalized = ((gender_frames - mean_vector[None, :]) / std_vector[None, :]).astype(np.float32)
            latents = encode_frames(model, normalized, device=device)
            gender_latents_lookup[gender] = latents
            latent_stats[f"{gender}_centroid"] = np.mean(latents, axis=0).astype(np.float32)
            latent_stats[f"{gender}_std"] = np.maximum(np.std(latents, axis=0), 1e-3).astype(np.float32)
        if "female_centroid" not in latent_stats or "male_centroid" not in latent_stats:
            continue

        translators: dict[str, LatentTranslator] = {}
        for source_gender, target_gender in (("female", "male"), ("male", "female")):
            source_frames = gender_frames_lookup[source_gender]
            target_frames = gender_frames_lookup[target_gender]
            source_latents = gender_latents_lookup[source_gender]
            target_latents = gender_latents_lookup[target_gender]
            used_proxy_coeffs = min(int(proxy_coeffs), int(source_frames.shape[1]), int(target_frames.shape[1]))
            matched_indices = nearest_neighbor_indices(
                source_frames[:, :used_proxy_coeffs],
                target_frames[:, :used_proxy_coeffs],
            )
            translator = train_translator(
                source_latents,
                target_latents[matched_indices],
                latent_dim=latent_dims,
                hidden_dims=translator_hidden_dims,
                train_epochs=translator_epochs,
                train_batch_size=train_batch_size,
                learning_rate=learning_rate,
                weight_decay=weight_decay,
                device=device,
                seed=seed + stable_name_seed(f"{dataset_name}:{source_gender}:{target_gender}") % 10000,
            )
            translators[f"{source_gender}_to_{target_gender}"] = translator

        lookup[dataset_name] = {
            "model": model,
            "mean_vector": mean_vector,
            "std_vector": std_vector,
            "translators": translators,
            **latent_stats,
        }
    return lookup


def apply_conditioned_neural_envelope_shift(
    audio: np.ndarray,
    *,
    sample_rate: int,
    n_fft: int,
    hop_length: int,
    peak_limit: float,
    world_sr: int,
    frame_period_ms: float,
    neural_pack: dict[str, object],
    device: torch.device,
    source_gender: str,
    target_gender: str,
    keep_coeffs: int,
    latent_mix: float,
    blend: float,
    max_envelope_gain_db: float,
    max_frame_delta_l2: float,
    time_smooth_frames: int,
) -> np.ndarray:
    stft = librosa.stft(audio.astype(np.float32), n_fft=n_fft, hop_length=hop_length)
    magnitude = np.abs(stft).astype(np.float32)
    phase = np.angle(stft)
    if magnitude.size == 0:
        return audio.astype(np.float32)

    log_mag = np.log(np.maximum(magnitude, 1e-7))
    cep = scipy.fft.dct(log_mag, type=2, axis=0, norm="ortho").astype(np.float32)

    model = neural_pack["model"]
    assert isinstance(model, EnvelopeAutoencoder)
    mean_vector = np.asarray(neural_pack["mean_vector"], dtype=np.float32)
    std_vector = np.asarray(neural_pack["std_vector"], dtype=np.float32)
    full_coeff_count = min(int(cep.shape[0] - 1), int(mean_vector.shape[0]))
    active_coeff_count = min(int(keep_coeffs), full_coeff_count)
    if full_coeff_count <= 0 or active_coeff_count <= 0:
        return audio.astype(np.float32)

    translators = neural_pack["translators"]
    assert isinstance(translators, dict)
    translator = translators.get(f"{source_gender}_to_{target_gender}")
    if translator is None:
        raise ValueError(f"Missing conditioned translator for {source_gender}->{target_gender}")
    assert isinstance(translator, LatentTranslator)

    f0, world_times_sec = analyze_f0(audio, sample_rate, world_sr, frame_period_ms)
    frame_times_sec = stft_frame_centers_sec(cep.shape[1], n_fft, hop_length, sample_rate)
    voiced_mask = interpolate_voiced_mask(frame_times_sec, world_times_sec, f0)

    frame_delta = np.zeros((full_coeff_count, cep.shape[1]), dtype=np.float32)
    voiced_binary = np.zeros(cep.shape[1], dtype=np.float32)
    with torch.no_grad():
        for frame_idx in range(cep.shape[1]):
            if voiced_mask[frame_idx] < 0.5:
                continue
            current_full = cep[1 : 1 + full_coeff_count, frame_idx].astype(np.float32, copy=False)
            normalized = ((current_full - mean_vector[:full_coeff_count]) / std_vector[:full_coeff_count]).astype(np.float32)
            input_tensor = torch.from_numpy(normalized[None, :]).to(device)
            latent = model.encode(input_tensor)
            latent_np = latent.detach().cpu().numpy()[0].astype(np.float32)
            predicted_target = translator(latent).detach().cpu().numpy()[0].astype(np.float32)
            target_like = latent_np + float(latent_mix) * (predicted_target - latent_np)
            target_tensor = torch.from_numpy(target_like[None, :]).to(device)
            decoded_current = model.decode(latent).detach().cpu().numpy()[0].astype(np.float32)
            decoded_target = model.decode(target_tensor).detach().cpu().numpy()[0].astype(np.float32)
            delta = (decoded_target - decoded_current) * std_vector[:full_coeff_count]
            if active_coeff_count < full_coeff_count:
                delta[active_coeff_count:] = 0.0
            delta_norm = float(np.linalg.norm(delta))
            if delta_norm > max_frame_delta_l2 > 0.0:
                delta = delta * (max_frame_delta_l2 / delta_norm)
            frame_delta[:, frame_idx] = delta
            voiced_binary[frame_idx] = 1.0

    smoothed_delta = smooth_along_time(frame_delta, voiced_binary, build_smoothing_kernel(int(time_smooth_frames)))
    output_cep = np.array(cep, dtype=np.float32, copy=True)
    output_cep[1 : 1 + full_coeff_count, :] += smoothed_delta * voiced_mask[None, :]

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
    if not enabled_rules:
        raise ValueError("No enabled conditioned neural envelope rules found")

    max_keep_coeffs = max(int(rule["method_params"]["keep_coeffs"]) for rule in enabled_rules)
    max_proxy_coeffs = max(int(rule["method_params"]["proxy_coeffs"]) for rule in enabled_rules)
    max_reference_stride = max(int(rule["method_params"].get("reference_frame_stride", 1)) for rule in enabled_rules)
    hidden_dims = parse_hidden_dims(enabled_rules[0]["method_params"]["hidden_dims"])
    latent_dims = int(enabled_rules[0]["method_params"]["latent_dims"])
    translator_hidden_dims = parse_hidden_dims(enabled_rules[0]["method_params"]["translator_hidden_dims"])
    train_epochs = int(enabled_rules[0]["method_params"]["train_epochs"])
    translator_epochs = int(enabled_rules[0]["method_params"]["translator_epochs"])
    train_batch_size = int(enabled_rules[0]["method_params"]["train_batch_size"])
    learning_rate = float(enabled_rules[0]["method_params"]["learning_rate"])
    weight_decay = float(enabled_rules[0]["method_params"].get("weight_decay", 0.0))
    device = resolve_torch_device(args.ae_device)

    reference_rows = select_reference_rows(
        read_reference_rows(resolve_path(args.reference_csv)),
        samples_per_cell=args.reference_samples_per_cell,
    )
    neural_lookup = build_conditioned_lookup(
        reference_rows,
        n_fft=args.n_fft,
        hop_length=args.hop_length,
        keep_coeffs=max_keep_coeffs,
        proxy_coeffs=max_proxy_coeffs,
        latent_dims=latent_dims,
        hidden_dims=hidden_dims,
        translator_hidden_dims=translator_hidden_dims,
        train_epochs=train_epochs,
        translator_epochs=translator_epochs,
        train_batch_size=train_batch_size,
        learning_rate=learning_rate,
        weight_decay=weight_decay,
        world_sr=args.world_sr,
        frame_period_ms=args.frame_period_ms,
        frame_stride=max_reference_stride,
        device=device,
        seed=args.ae_seed,
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
        neural_pack = neural_lookup.get(row["dataset_name"])
        if neural_pack is None:
            raise ValueError(f"Missing conditioned neural envelope model for {row['dataset_name']}")

        input_audio = resolve_path(row["path_raw"])
        stem = build_output_stem(row, target_direction=target_direction, method_token="nlatent")
        original_copy = originals_dir / f"{stem}.{args.audio_format}"
        processed_audio = processed_dir / f"{stem}.{args.audio_format}"

        audio, sample_rate = load_audio(input_audio)
        save_audio(original_copy, audio, sample_rate)
        out = apply_conditioned_neural_envelope_shift(
            audio,
            sample_rate=sample_rate,
            n_fft=args.n_fft,
            hop_length=args.hop_length,
            peak_limit=args.peak_limit,
            world_sr=args.world_sr,
            frame_period_ms=args.frame_period_ms,
            neural_pack=neural_pack,
            device=device,
            source_gender=row["gender"],
            target_gender=target_gender,
            keep_coeffs=int(params["keep_coeffs"]),
            latent_mix=float(params["latent_mix"]),
            blend=float(params["blend"]),
            max_envelope_gain_db=float(params["max_envelope_gain_db"]),
            max_frame_delta_l2=float(params["max_frame_delta_l2"]),
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
        pack_title="Stage0 Speech Conditioned Neural Envelope Listening Pack",
        purpose="conditioned latent predictor / learned decoder probe",
        script_name="build_stage0_speech_conditioned_neural_envelope_listening_pack.py",
        rule_config_path=rule_config_path,
    )
    print(f"Wrote {summary_path}")
    print(f"Reference rows: {len(reference_rows)}")
    print(f"Conditioned models: {len(neural_lookup)}")
    print(f"Selected rows: {len(summary_rows)}")
    print(f"Output dir: {output_dir}")


if __name__ == "__main__":
    main()
