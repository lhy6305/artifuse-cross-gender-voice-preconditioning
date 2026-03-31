from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

import librosa
import numpy as np
import pyworld
import soundfile as sf
import torch

from apply_stage0_rule_preconditioner import load_audio
from extract_resonance_distribution_diagnostics import (
    ROOT,
    build_distribution_features,
    fmt_float,
    one_dim_emd,
    resolve_path,
    write_csv,
)


DEFAULT_TARGET_DIR = ROOT / "artifacts" / "diagnostics" / "atrr_vocoder_bridge_target_export" / "v1_fixed8_v9a" / "targets"
DEFAULT_QUEUE_CSV = ROOT / "artifacts" / "listening_review" / "stage0_speech_lsf_machine_sweep_v9_fixed8" / "split_core_focus_v9a" / "listening_review_queue.csv"
DEFAULT_OUTPUT_DIR = ROOT / "artifacts" / "diagnostics" / "atrr_vocoder_carrier_adapter" / "v1_fixed8_v9a_gl_probe"
DEFAULT_RVC_ROOT = ROOT / "Retrieval-based-Voice-Conversion-WebUI-7ef1986"
DEFAULT_RVC_CONFIG = DEFAULT_RVC_ROOT / "configs" / "v1" / "48k.json"
DEFAULT_RVC_WEIGHTS = DEFAULT_RVC_ROOT / "assets" / "pretrained" / "f0G48k.pth"
DEFAULT_BIGVGAN_ROOT = ROOT / "external_models" / "bigvgan_v2_22khz_80band_fmax8k_256x"
DEFAULT_VOCOS_ROOT = ROOT / "external_models" / "vocos-mel-24khz"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-dir", default=str(DEFAULT_TARGET_DIR))
    parser.add_argument("--queue-csv", default=str(DEFAULT_QUEUE_CSV))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--backend", choices=["griffinlim_mel_probe", "rvc_f0_posterior_bridge_v1", "torchaudio_wavernn_bridge_v1", "bigvgan_local_v1", "vocos_local_v1"], default="griffinlim_mel_probe")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--target-pattern", action="append", default=[])
    parser.add_argument("--n-fft", type=int, default=2048)
    parser.add_argument("--hop-length", type=int, default=256)
    parser.add_argument("--n-mels", type=int, default=80)
    parser.add_argument("--fmin", type=float, default=50.0)
    parser.add_argument("--fmax", type=float, default=8000.0)
    parser.add_argument("--rms-threshold-db", type=float, default=-40.0)
    parser.add_argument("--frame-core-threshold", type=float, default=0.60)
    parser.add_argument("--griffinlim-iter", type=int, default=64)
    parser.add_argument("--clip-threshold", type=float, default=0.999)
    parser.add_argument("--match-source-rms", action="store_true")
    parser.add_argument("--pitch-correct-source-median", action="store_true")
    parser.add_argument("--pitch-correct-voiced-only", action="store_true")
    parser.add_argument("--pitch-correct-min-drift-cents", type=float, default=25.0)
    parser.add_argument("--pitch-correct-max-cents", type=float)
    parser.add_argument("--pitch-correct-crossfade-ms", type=float, default=25.0)
    parser.add_argument("--pitch-correct-min-span-ms", type=float, default=80.0)
    parser.add_argument("--voiced-target-blend-alpha", type=float, default=1.0)
    parser.add_argument("--frame-distribution-anchor-alpha", type=float, default=1.0)
    parser.add_argument("--frame-anchor-l1-threshold", type=float)
    parser.add_argument("--frame-anchor-min-alpha", type=float, default=0.0)
    parser.add_argument("--target-bin-delta-threshold", type=float)
    parser.add_argument("--target-bin-delta-threshold-masculine", type=float)
    parser.add_argument("--target-bin-delta-threshold-feminine", type=float)
    parser.add_argument("--target-bin-delta-threshold-masculine-low-f0", type=float)
    parser.add_argument("--target-bin-delta-threshold-masculine-mid-f0", type=float)
    parser.add_argument("--target-bin-delta-threshold-masculine-high-f0", type=float)
    parser.add_argument("--target-bin-delta-threshold-feminine-low-f0", type=float)
    parser.add_argument("--target-bin-delta-threshold-feminine-mid-f0", type=float)
    parser.add_argument("--target-bin-delta-threshold-feminine-high-f0", type=float)
    parser.add_argument("--target-bin-shape-topk-count", type=int, default=3)
    parser.add_argument("--target-bin-shape-topk-sum-cutoff", type=float)
    parser.add_argument("--target-bin-delta-threshold-feminine-sharp", type=float)
    parser.add_argument("--target-bin-source-emd-cutoff", type=float)
    parser.add_argument("--target-bin-delta-threshold-masculine-weak", type=float)
    parser.add_argument("--target-bin-delta-threshold-feminine-weak", type=float)
    parser.add_argument("--target-bin-record-override", action="append", default=[])
    parser.add_argument("--target-bin-record-veto", action="append", default=[])
    parser.add_argument("--target-bin-occupancy-threshold", type=float)
    parser.add_argument("--rvc-root", default=str(DEFAULT_RVC_ROOT))
    parser.add_argument("--rvc-config", default=str(DEFAULT_RVC_CONFIG))
    parser.add_argument("--rvc-weights", default=str(DEFAULT_RVC_WEIGHTS))
    parser.add_argument("--rvc-sid", type=int, default=0)
    parser.add_argument("--rvc-device", default="auto")
    parser.add_argument("--rvc-f0-min", type=float, default=50.0)
    parser.add_argument("--rvc-f0-max", type=float, default=1100.0)
    parser.add_argument("--wavernn-device", default="auto")
    parser.add_argument("--bigvgan-root", default=str(DEFAULT_BIGVGAN_ROOT))
    parser.add_argument("--bigvgan-device", default="auto")
    parser.add_argument("--vocos-root", default=str(DEFAULT_VOCOS_ROOT))
    parser.add_argument("--vocos-device", default="auto")
    return parser.parse_args()


def scalar_string(value: np.ndarray) -> str:
    if isinstance(value, np.ndarray):
        if value.shape == ():
            return str(value.item())
        if value.size == 1:
            return str(value.reshape(-1)[0])
    return str(value)


def parse_record_threshold_overrides(items: list[str]) -> dict[str, float]:
    overrides: dict[str, float] = {}
    for item in items:
        if not item:
            continue
        if "=" not in item:
            raise ValueError(f"Invalid record override '{item}'. Expected record_id=value.")
        record_id, value_text = item.split("=", 1)
        key = record_id.strip()
        if not key:
            raise ValueError(f"Invalid record override '{item}'. Empty record_id.")
        overrides[key] = float(value_text)
    return overrides


def safe_rms_db(audio: np.ndarray) -> float:
    rms = float(np.sqrt(np.mean(np.square(audio.astype(np.float64)))))
    return 20.0 * math.log10(max(rms, 1e-12))


def match_rms(audio: np.ndarray, reference_audio: np.ndarray) -> np.ndarray:
    target_rms = float(np.sqrt(np.mean(np.square(reference_audio.astype(np.float64)))))
    source_rms = float(np.sqrt(np.mean(np.square(audio.astype(np.float64)))))
    if source_rms <= 1e-12 or target_rms <= 1e-12:
        return np.asarray(audio, dtype=np.float32)
    return np.asarray(audio, dtype=np.float32) * float(target_rms / source_rms)


def clipping_ratio(audio: np.ndarray, threshold: float) -> float:
    if audio.size == 0:
        return 0.0
    return float(np.mean(np.abs(audio) >= threshold))


def estimate_f0_median_hz(
    audio: np.ndarray,
    sample_rate: int,
    *,
    n_fft: int,
    hop_length: int,
) -> tuple[float, float]:
    if audio.size < n_fft:
        return float("nan"), 0.0
    f0, voiced_flag, _ = librosa.pyin(
        audio.astype(np.float32),
        fmin=librosa.note_to_hz("C2"),
        fmax=librosa.note_to_hz("C6"),
        sr=sample_rate,
        frame_length=n_fft,
        hop_length=hop_length,
    )
    voiced_mask = np.isfinite(f0)
    if not np.any(voiced_mask):
        return float("nan"), 0.0
    voiced_ratio = float(np.mean(voiced_mask))
    return float(np.median(f0[voiced_mask])), voiced_ratio


def cents_difference(source_hz: float, target_hz: float) -> float:
    if not math.isfinite(source_hz) or not math.isfinite(target_hz):
        return float("nan")
    if source_hz <= 0.0 or target_hz <= 0.0:
        return float("nan")
    return float(abs(1200.0 * math.log2(target_hz / source_hz)))


def pitch_correct_to_reference_median(
    audio: np.ndarray,
    reference_audio: np.ndarray,
    sample_rate: int,
    *,
    n_fft: int,
    hop_length: int,
    min_drift_cents: float,
    max_correction_cents: float | None,
) -> np.ndarray:
    reference_hz, _ = estimate_f0_median_hz(
        reference_audio,
        sample_rate,
        n_fft=n_fft,
        hop_length=hop_length,
    )
    probe_hz, _ = estimate_f0_median_hz(
        audio,
        sample_rate,
        n_fft=n_fft,
        hop_length=hop_length,
    )
    drift_cents = cents_difference(reference_hz, probe_hz)
    if not math.isfinite(drift_cents) or drift_cents < min_drift_cents:
        return np.asarray(audio, dtype=np.float32)
    if not math.isfinite(reference_hz) or not math.isfinite(probe_hz):
        return np.asarray(audio, dtype=np.float32)
    if reference_hz <= 0.0 or probe_hz <= 0.0:
        return np.asarray(audio, dtype=np.float32)
    correction_cents = float(1200.0 * math.log2(reference_hz / probe_hz))
    if max_correction_cents is not None and math.isfinite(max_correction_cents):
        capped = max(-float(max_correction_cents), min(float(max_correction_cents), correction_cents))
        correction_cents = capped
    n_steps = float(correction_cents / 100.0)
    corrected = librosa.effects.pitch_shift(
        np.asarray(audio, dtype=np.float32),
        sr=sample_rate,
        n_steps=n_steps,
        bins_per_octave=12,
    )
    return librosa.util.fix_length(corrected.astype(np.float32), size=audio.shape[0])


def contiguous_true_spans(mask: np.ndarray) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    start: int | None = None
    for idx, value in enumerate(np.asarray(mask, dtype=bool)):
        if value and start is None:
            start = idx
        elif not value and start is not None:
            spans.append((start, idx))
            start = None
    if start is not None:
        spans.append((start, int(mask.shape[0])))
    return spans


def sample_mask_from_frame_voicing(
    frame_voiced_mask: np.ndarray,
    audio_length: int,
    *,
    hop_length: int,
) -> np.ndarray:
    frame_mask = np.asarray(frame_voiced_mask, dtype=np.float64).reshape(-1)
    target_frames = max(1, int(math.ceil(audio_length / float(hop_length))))
    aligned = align_vector_length(frame_mask, target_frames) > 0.5
    sample_mask = np.repeat(aligned.astype(np.bool_), hop_length)
    return sample_mask[:audio_length]


def pitch_correct_to_reference_median_voiced_only(
    audio: np.ndarray,
    reference_audio: np.ndarray,
    sample_rate: int,
    *,
    frame_voiced_mask: np.ndarray,
    hop_length: int,
    n_fft: int,
    min_drift_cents: float,
    max_correction_cents: float | None,
    crossfade_ms: float,
    min_span_ms: float,
) -> np.ndarray:
    reference_hz, _ = estimate_f0_median_hz(
        reference_audio,
        sample_rate,
        n_fft=n_fft,
        hop_length=hop_length,
    )
    probe_hz, _ = estimate_f0_median_hz(
        audio,
        sample_rate,
        n_fft=n_fft,
        hop_length=hop_length,
    )
    drift_cents = cents_difference(reference_hz, probe_hz)
    if not math.isfinite(drift_cents) or drift_cents < min_drift_cents:
        return np.asarray(audio, dtype=np.float32)
    if not math.isfinite(reference_hz) or not math.isfinite(probe_hz):
        return np.asarray(audio, dtype=np.float32)
    if reference_hz <= 0.0 or probe_hz <= 0.0:
        return np.asarray(audio, dtype=np.float32)

    correction_cents = float(1200.0 * math.log2(reference_hz / probe_hz))
    if max_correction_cents is not None and math.isfinite(max_correction_cents):
        correction_cents = max(-float(max_correction_cents), min(float(max_correction_cents), correction_cents))
    n_steps = float(correction_cents / 100.0)

    sample_mask = sample_mask_from_frame_voicing(
        frame_voiced_mask,
        audio.shape[0],
        hop_length=hop_length,
    )
    spans = contiguous_true_spans(sample_mask)
    if not spans:
        return np.asarray(audio, dtype=np.float32)

    crossfade_samples = max(0, int(round(sample_rate * crossfade_ms / 1000.0)))
    min_span_samples = max(1, int(round(sample_rate * min_span_ms / 1000.0)))
    output = np.asarray(audio, dtype=np.float32).copy()

    for start, end in spans:
        if end - start < min_span_samples:
            continue
        span_start = max(0, start - crossfade_samples)
        span_end = min(audio.shape[0], end + crossfade_samples)
        segment = np.asarray(audio[span_start:span_end], dtype=np.float32)
        if segment.size < max(32, 2 * crossfade_samples + 8):
            continue
        corrected = librosa.effects.pitch_shift(
            segment,
            sr=sample_rate,
            n_steps=n_steps,
            bins_per_octave=12,
        )
        corrected = librosa.util.fix_length(corrected.astype(np.float32), size=segment.shape[0])

        weights = np.zeros(segment.shape[0], dtype=np.float32)
        core_start = start - span_start
        core_end = end - span_start
        weights[core_start:core_end] = 1.0

        if core_start > 0:
            left = np.linspace(0.0, 1.0, num=core_start, endpoint=False, dtype=np.float32)
            weights[:core_start] = left
        if core_end < segment.shape[0]:
            right_len = segment.shape[0] - core_end
            right = np.linspace(1.0, 0.0, num=right_len, endpoint=False, dtype=np.float32)
            weights[core_end:] = right

        output[span_start:span_end] = (
            output[span_start:span_end] * (1.0 - weights) + corrected * weights
        ).astype(np.float32)
    return output


def align_time_axis(matrix: np.ndarray, target_frames: int) -> np.ndarray:
    source = np.asarray(matrix, dtype=np.float64)
    if source.ndim != 2:
        raise ValueError("Expected a 2D time-frequency matrix.")
    if target_frames <= 0:
        raise ValueError("target_frames must be positive.")
    if source.shape[1] == target_frames:
        return source
    if source.shape[1] == 1:
        return np.repeat(source, target_frames, axis=1)
    x_old = np.linspace(0.0, 1.0, num=source.shape[1], endpoint=True)
    x_new = np.linspace(0.0, 1.0, num=target_frames, endpoint=True)
    aligned = np.empty((source.shape[0], target_frames), dtype=np.float64)
    for row_idx in range(source.shape[0]):
        aligned[row_idx] = np.interp(x_new, x_old, source[row_idx])
    return aligned


def align_vector_length(vector: np.ndarray, target_length: int) -> np.ndarray:
    source = np.asarray(vector, dtype=np.float64).reshape(-1)
    if target_length <= 0:
        raise ValueError("target_length must be positive.")
    if source.shape[0] == target_length:
        return source
    if source.shape[0] <= 1:
        fill_value = float(source[0]) if source.shape[0] == 1 else 0.0
        return np.full(target_length, fill_value, dtype=np.float64)
    x_old = np.linspace(0.0, 1.0, num=source.shape[0], endpoint=True)
    x_new = np.linspace(0.0, 1.0, num=target_length, endpoint=True)
    return np.interp(x_new, x_old, source).astype(np.float64)


def normalize_frame_distributions(frames: np.ndarray) -> np.ndarray:
    clean = np.maximum(np.asarray(frames, dtype=np.float64), 1e-12)
    totals = np.sum(clean, axis=1, keepdims=True)
    totals = np.where(totals <= 0.0, 1.0, totals)
    return clean / totals


def align_distribution_bins(frames: np.ndarray, target_bins: int) -> np.ndarray:
    source = np.asarray(frames, dtype=np.float64)
    if source.ndim != 2:
        raise ValueError("Expected a 2D frame-distribution matrix.")
    if target_bins <= 0:
        raise ValueError("target_bins must be positive.")
    if source.shape[1] == target_bins:
        return source
    if source.shape[1] == 1:
        return np.repeat(source, target_bins, axis=1)
    x_old = np.linspace(0.0, 1.0, num=source.shape[1], endpoint=True)
    x_new = np.linspace(0.0, 1.0, num=target_bins, endpoint=True)
    aligned = np.empty((source.shape[0], target_bins), dtype=np.float64)
    for frame_idx in range(source.shape[0]):
        aligned[frame_idx] = np.interp(x_new, x_old, source[frame_idx])
    return aligned


def inverse_log_mel(
    log_mel: np.ndarray,
    sample_rate: int,
    *,
    n_fft: int,
    hop_length: int,
    fmin: float,
    fmax: float,
    griffinlim_iter: int,
    target_length: int | None,
) -> np.ndarray:
    mel_power = np.maximum(np.exp(np.asarray(log_mel, dtype=np.float64)), 1e-12)
    return librosa.feature.inverse.mel_to_audio(
        mel_power,
        sr=sample_rate,
        n_fft=n_fft,
        hop_length=hop_length,
        win_length=n_fft,
        power=2.0,
        n_iter=griffinlim_iter,
        length=target_length,
        fmin=fmin,
        fmax=min(float(fmax), sample_rate / 2.0),
    ).astype(np.float32)


def compute_mel_custom(
    audio: np.ndarray,
    sample_rate: int,
    *,
    n_fft: int,
    hop_length: int,
    win_length: int,
    n_mels: int,
    fmin: float,
    fmax: float,
    power: float,
    center: bool,
) -> np.ndarray:
    target_fmax = min(float(fmax), sample_rate / 2.0)
    mel = librosa.feature.melspectrogram(
        y=audio.astype(np.float32),
        sr=sample_rate,
        n_fft=n_fft,
        hop_length=hop_length,
        win_length=win_length,
        window="hann",
        center=center,
        power=power,
        n_mels=n_mels,
        fmin=fmin,
        fmax=target_fmax,
    ).astype(np.float64)
    return np.maximum(mel, 1e-12)


def estimate_harvest_f0(
    audio: np.ndarray,
    sample_rate: int,
    *,
    hop_length: int,
    f0_min: float,
    f0_max: float,
) -> np.ndarray:
    frame_period = 1000.0 * hop_length / sample_rate
    f0, time_axis = pyworld.harvest(
        audio.astype(np.float64),
        fs=sample_rate,
        f0_floor=f0_min,
        f0_ceil=f0_max,
        frame_period=frame_period,
    )
    return pyworld.stonemask(audio.astype(np.float64), f0, time_axis, sample_rate).astype(np.float64)


def f0_to_coarse(f0_hz: np.ndarray, *, f0_min: float, f0_max: float) -> np.ndarray:
    mel_min = 1127.0 * np.log(1.0 + f0_min / 700.0)
    mel_max = 1127.0 * np.log(1.0 + f0_max / 700.0)
    f0 = np.asarray(f0_hz, dtype=np.float64)
    f0_mel = 1127.0 * np.log(1.0 + np.maximum(f0, 0.0) / 700.0)
    voiced_mask = f0 > 0.0
    f0_mel[voiced_mask] = (f0_mel[voiced_mask] - mel_min) * 254.0 / (mel_max - mel_min) + 1.0
    f0_mel[~voiced_mask] = 1.0
    return np.rint(np.clip(f0_mel, 1.0, 255.0)).astype(np.int64)


def choose_device(device_name: str) -> str:
    if device_name != "auto":
        return device_name
    return "cuda" if torch.cuda.is_available() else "cpu"


def load_torch_checkpoint(path: Path) -> dict:
    try:
        return torch.load(path, map_location="cpu", weights_only=True)
    except TypeError:
        return torch.load(path, map_location="cpu")


def build_rvc_backend(args: argparse.Namespace) -> dict[str, object]:
    rvc_root = resolve_path(args.rvc_root)
    config_path = resolve_path(args.rvc_config)
    weights_path = resolve_path(args.rvc_weights)
    if str(rvc_root) not in sys.path:
        sys.path.insert(0, str(rvc_root))
    from infer.lib.infer_pack.models import SynthesizerTrnMs256NSFsid

    config_json = json.loads(config_path.read_text(encoding="utf-8"))
    model_cfg = config_json["model"]
    sample_rate = int(config_json["data"]["sampling_rate"])
    hop_length = int(config_json["data"]["hop_length"])
    n_fft = int(config_json["data"]["filter_length"])
    model_args = [
        n_fft // 2 + 1,
        int(config_json["train"]["segment_size"]) // hop_length,
        model_cfg["inter_channels"],
        model_cfg["hidden_channels"],
        model_cfg["filter_channels"],
        model_cfg["n_heads"],
        model_cfg["n_layers"],
        model_cfg["kernel_size"],
        model_cfg["p_dropout"],
        model_cfg["resblock"],
        model_cfg["resblock_kernel_sizes"],
        model_cfg["resblock_dilation_sizes"],
        model_cfg["upsample_rates"],
        model_cfg["upsample_initial_channel"],
        model_cfg["upsample_kernel_sizes"],
        model_cfg["spk_embed_dim"],
        model_cfg["gin_channels"],
        sample_rate,
    ]

    device = choose_device(args.rvc_device)
    net_g = SynthesizerTrnMs256NSFsid(*model_args, is_half=False)
    checkpoint = load_torch_checkpoint(weights_path)
    state_dict = checkpoint["model"] if "model" in checkpoint else checkpoint["weight"]
    net_g.load_state_dict(state_dict, strict=False)
    net_g.eval().to(device)

    mel_basis = librosa.filters.mel(
        sr=sample_rate,
        n_fft=n_fft,
        n_mels=args.n_mels,
        fmin=args.fmin,
        fmax=min(float(args.fmax), sample_rate / 2.0),
    )
    mel_pinv = np.linalg.pinv(mel_basis).astype(np.float32)
    return {
        "device": device,
        "model": net_g,
        "sample_rate": sample_rate,
        "hop_length": hop_length,
        "n_fft": n_fft,
        "mel_pinv": mel_pinv,
    }


def build_wavernn_backend(args: argparse.Namespace) -> dict[str, object]:
    import torchaudio

    device = choose_device(args.wavernn_device)
    vocoder = torchaudio.pipelines.TACOTRON2_WAVERNN_PHONE_LJSPEECH.get_vocoder()
    vocoder = vocoder.to(device).eval()
    return {
        "device": device,
        "model": vocoder,
        "sample_rate": int(vocoder.sample_rate),
        "n_fft": 2048,
        "win_length": 1100,
        "hop_length": 275,
        "n_mels": 80,
        "fmin": 40.0,
        "fmax": 11025.0,
        "power": 1.0,
        "center": True,
    }


def build_bigvgan_backend(args: argparse.Namespace) -> dict[str, object]:
    bigvgan_root = resolve_path(args.bigvgan_root)
    device = choose_device(args.bigvgan_device)
    if str(bigvgan_root) not in sys.path:
        sys.path.insert(0, str(bigvgan_root))
    import bigvgan

    model = bigvgan.BigVGAN.from_pretrained(str(bigvgan_root), use_cuda_kernel=False)
    model.remove_weight_norm()
    model = model.eval().to(device)
    h = model.h
    fmax_value = float(h.fmax) if h.fmax is not None else float(h.sampling_rate) / 2.0
    return {
        "device": device,
        "model": model,
        "sample_rate": int(h.sampling_rate),
        "n_fft": int(h.n_fft),
        "win_length": int(h.win_size),
        "hop_length": int(h.hop_size),
        "n_mels": int(h.num_mels),
        "fmin": float(h.fmin),
        "fmax": fmax_value,
        "power": 1.0,
        "center": False,
    }


def build_vocos_backend(args: argparse.Namespace) -> dict[str, object]:
    from vocos import Vocos

    vocos_root = resolve_path(args.vocos_root)
    device = choose_device(args.vocos_device)
    model = Vocos.from_hparams(str(vocos_root / "config.yaml"))
    state_dict = load_torch_checkpoint(vocos_root / "pytorch_model.bin")
    model.load_state_dict(state_dict)
    model = model.eval().to(device)

    mel_extractor = model.feature_extractor.mel_spec
    sample_rate = int(mel_extractor.sample_rate)
    fmax_value = float(mel_extractor.f_max) if mel_extractor.f_max is not None else float(sample_rate) / 2.0
    return {
        "device": device,
        "model": model,
        "sample_rate": sample_rate,
        "n_fft": int(mel_extractor.n_fft),
        "win_length": int(mel_extractor.win_length),
        "hop_length": int(mel_extractor.hop_length),
        "n_mels": int(mel_extractor.n_mels),
        "fmin": 0.0 if mel_extractor.f_min is None else float(mel_extractor.f_min),
        "fmax": fmax_value,
        "power": float(mel_extractor.power),
        "center": bool(model.feature_extractor.padding == "center"),
    }


def synthesize_rvc_posterior_bridge(
    log_mel: np.ndarray,
    original_audio: np.ndarray,
    original_sample_rate: int,
    *,
    backend: dict[str, object],
    args: argparse.Namespace,
) -> tuple[np.ndarray, int]:
    backend_sample_rate = int(backend["sample_rate"])
    backend_hop_length = int(backend["hop_length"])
    backend_n_fft = int(backend["n_fft"])
    model = backend["model"]
    device = str(backend["device"])
    mel_pinv = np.asarray(backend["mel_pinv"], dtype=np.float32)

    working_audio = np.asarray(original_audio, dtype=np.float32)
    if original_sample_rate != backend_sample_rate:
        working_audio = librosa.resample(working_audio, orig_sr=original_sample_rate, target_sr=backend_sample_rate).astype(np.float32)

    target_frames = max(1, int(round(working_audio.shape[0] / backend_hop_length)))
    aligned_log_mel = align_time_axis(np.asarray(log_mel, dtype=np.float64), target_frames).astype(np.float32)
    mel_power = np.exp(aligned_log_mel)
    mel_amplitude = np.sqrt(np.maximum(mel_power, 1e-9)).astype(np.float32)
    pseudo_spec = np.maximum(mel_pinv @ mel_amplitude, 1e-6).astype(np.float32)

    f0_track = estimate_harvest_f0(
        working_audio,
        backend_sample_rate,
        hop_length=backend_hop_length,
        f0_min=args.rvc_f0_min,
        f0_max=args.rvc_f0_max,
    )
    aligned_f0 = align_vector_length(f0_track, target_frames).astype(np.float32)
    coarse_f0 = f0_to_coarse(aligned_f0, f0_min=args.rvc_f0_min, f0_max=args.rvc_f0_max)

    spec_tensor = torch.from_numpy(pseudo_spec).unsqueeze(0).to(device)
    length_tensor = torch.tensor([target_frames], dtype=torch.long, device=device)
    f0_tensor = torch.from_numpy(aligned_f0).unsqueeze(0).to(device)
    coarse_tensor = torch.from_numpy(coarse_f0).unsqueeze(0).to(device)
    sid_tensor = torch.tensor([args.rvc_sid], dtype=torch.long, device=device)
    with torch.no_grad():
        g = model.emb_g(sid_tensor).unsqueeze(-1)
        z, _, _, x_mask = model.enc_q(spec_tensor, length_tensor, g=g)
        audio = model.dec(z * x_mask, f0_tensor, g=g)[0, 0].detach().cpu().numpy().astype(np.float32)

    if audio.size == 0:
        raise ValueError("Neural carrier returned empty audio.")
    expected_length = target_frames * backend_hop_length
    if audio.shape[0] != expected_length:
        audio = librosa.util.fix_length(audio, size=expected_length)
    return audio, backend_sample_rate


def synthesize_wavernn_bridge(
    log_mel: np.ndarray,
    original_audio: np.ndarray,
    original_sample_rate: int,
    *,
    backend: dict[str, object],
) -> tuple[np.ndarray, int]:
    sample_rate = int(backend["sample_rate"])
    device = str(backend["device"])
    model = backend["model"]

    working_audio = np.asarray(original_audio, dtype=np.float32)
    if original_sample_rate != sample_rate:
        working_audio = librosa.resample(working_audio, orig_sr=original_sample_rate, target_sr=sample_rate).astype(np.float32)

    target_frame_count = max(1, int(round(working_audio.shape[0] / 275.0)))
    aligned_log_mel = align_time_axis(np.asarray(log_mel, dtype=np.float64), target_frame_count).astype(np.float32)
    mel_tensor = torch.from_numpy(aligned_log_mel).unsqueeze(0).to(device)
    length_tensor = torch.tensor([target_frame_count], dtype=torch.long, device=device)
    with torch.no_grad():
        waveform, waveform_lengths = model(mel_tensor, length_tensor)
    audio = waveform[0].detach().cpu().numpy().astype(np.float32)
    valid_length = int(waveform_lengths[0].item()) if waveform_lengths is not None else audio.shape[0]
    return audio[:valid_length], sample_rate


def synthesize_bigvgan_bridge(
    log_mel: np.ndarray,
    original_audio: np.ndarray,
    original_sample_rate: int,
    *,
    backend: dict[str, object],
) -> tuple[np.ndarray, int]:
    sample_rate = int(backend["sample_rate"])
    device = str(backend["device"])
    model = backend["model"]

    working_audio = np.asarray(original_audio, dtype=np.float32)
    if original_sample_rate != sample_rate:
        working_audio = librosa.resample(working_audio, orig_sr=original_sample_rate, target_sr=sample_rate).astype(np.float32)

    target_frame_count = max(1, int(round(working_audio.shape[0] / float(backend["hop_length"]))))
    aligned_log_mel = align_time_axis(np.asarray(log_mel, dtype=np.float64), target_frame_count).astype(np.float32)
    mel_tensor = torch.from_numpy(aligned_log_mel).unsqueeze(0).to(device)
    with torch.no_grad():
        waveform = model(mel_tensor)
    audio = waveform[0, 0].detach().cpu().numpy().astype(np.float32)
    return audio, sample_rate


def synthesize_vocos_bridge(
    log_mel: np.ndarray,
    original_audio: np.ndarray,
    original_sample_rate: int,
    *,
    backend: dict[str, object],
) -> tuple[np.ndarray, int]:
    sample_rate = int(backend["sample_rate"])
    device = str(backend["device"])
    model = backend["model"]

    working_audio = np.asarray(original_audio, dtype=np.float32)
    if original_sample_rate != sample_rate:
        working_audio = librosa.resample(working_audio, orig_sr=original_sample_rate, target_sr=sample_rate).astype(np.float32)

    target_frame_count = max(1, int(round(working_audio.shape[0] / float(backend["hop_length"]))))
    aligned_log_mel = align_time_axis(np.asarray(log_mel, dtype=np.float64), target_frame_count).astype(np.float32)
    mel_tensor = torch.from_numpy(aligned_log_mel).unsqueeze(0).to(device)
    with torch.no_grad():
        waveform = model.decode(mel_tensor)
    audio = waveform[0].detach().cpu().numpy().astype(np.float32)
    return audio, sample_rate


def rebuild_backend_target_log_mel(
    package: dict[str, np.ndarray],
    original_audio: np.ndarray,
    original_sample_rate: int,
    *,
    sample_rate: int,
    n_fft: int,
    win_length: int,
    hop_length: int,
    n_mels: int,
    fmin: float,
    fmax: float,
    power: float,
    center: bool,
    frame_distribution_anchor_alpha: float,
    frame_anchor_l1_threshold: float | None,
    frame_anchor_min_alpha: float,
    target_bin_delta_threshold: float | None,
    target_bin_delta_threshold_masculine: float | None,
    target_bin_delta_threshold_feminine: float | None,
    target_bin_delta_threshold_masculine_low_f0: float | None,
    target_bin_delta_threshold_masculine_mid_f0: float | None,
    target_bin_delta_threshold_masculine_high_f0: float | None,
    target_bin_delta_threshold_feminine_low_f0: float | None,
    target_bin_delta_threshold_feminine_mid_f0: float | None,
    target_bin_delta_threshold_feminine_high_f0: float | None,
    target_bin_shape_topk_count: int,
    target_bin_shape_topk_sum_cutoff: float | None,
    target_bin_delta_threshold_feminine_sharp: float | None,
    target_bin_source_emd_cutoff: float | None,
    target_bin_delta_threshold_masculine_weak: float | None,
    target_bin_delta_threshold_feminine_weak: float | None,
    target_bin_record_override_thresholds: dict[str, float],
    target_bin_record_veto_ids: set[str],
    target_bin_occupancy_threshold: float | None,
) -> tuple[np.ndarray, np.ndarray]:
    working_audio = np.asarray(original_audio, dtype=np.float32)
    if original_sample_rate != sample_rate:
        working_audio = librosa.resample(working_audio, orig_sr=original_sample_rate, target_sr=sample_rate).astype(np.float32)
    source_mel_power = compute_mel_custom(
        working_audio,
        sample_rate,
        n_fft=n_fft,
        hop_length=hop_length,
        win_length=win_length,
        n_mels=n_mels,
        fmin=fmin,
        fmax=fmax,
        power=power,
        center=center,
    )
    frame_count = source_mel_power.shape[1]
    edited_frames = np.asarray(package["edited_frame_distributions"], dtype=np.float64)
    edited_frames = align_time_axis(edited_frames.T, frame_count).T
    edited_frames = align_distribution_bins(edited_frames, source_mel_power.shape[0])
    edited_frames = normalize_frame_distributions(edited_frames)
    source_distribution = align_vector_length(np.asarray(package["source_distribution"], dtype=np.float64), source_mel_power.shape[0])
    target_distribution = align_vector_length(np.asarray(package["target_distribution"], dtype=np.float64), source_mel_power.shape[0])
    target_occupancy = align_vector_length(np.asarray(package["target_occupancy"], dtype=np.float64), source_mel_power.shape[0])
    voiced_mask = align_vector_length(np.asarray(package["voiced_mask"], dtype=np.float64), frame_count) > 0.5
    record_id = scalar_string(package["record_id"]).strip()
    target_direction = scalar_string(package["target_direction"]).strip().lower()
    f0_condition = scalar_string(package["f0_condition"]).strip().lower()
    source_target_emd = one_dim_emd(source_distribution, target_distribution)
    target_delta = np.abs(target_distribution - source_distribution)
    topk = max(1, int(target_bin_shape_topk_count))
    target_delta_topk_sum = float(np.sum(np.sort(target_delta)[-topk:]))

    active_delta_threshold = target_bin_delta_threshold
    if target_direction == "masculine" and target_bin_delta_threshold_masculine is not None:
        active_delta_threshold = target_bin_delta_threshold_masculine
    elif target_direction == "feminine" and target_bin_delta_threshold_feminine is not None:
        active_delta_threshold = target_bin_delta_threshold_feminine
    if target_direction == "masculine":
        if f0_condition == "low_f0" and target_bin_delta_threshold_masculine_low_f0 is not None:
            active_delta_threshold = target_bin_delta_threshold_masculine_low_f0
        elif f0_condition == "mid_f0" and target_bin_delta_threshold_masculine_mid_f0 is not None:
            active_delta_threshold = target_bin_delta_threshold_masculine_mid_f0
        elif f0_condition == "high_f0" and target_bin_delta_threshold_masculine_high_f0 is not None:
            active_delta_threshold = target_bin_delta_threshold_masculine_high_f0
    elif target_direction == "feminine":
        if f0_condition == "low_f0" and target_bin_delta_threshold_feminine_low_f0 is not None:
            active_delta_threshold = target_bin_delta_threshold_feminine_low_f0
        elif f0_condition == "mid_f0" and target_bin_delta_threshold_feminine_mid_f0 is not None:
            active_delta_threshold = target_bin_delta_threshold_feminine_mid_f0
        elif f0_condition == "high_f0" and target_bin_delta_threshold_feminine_high_f0 is not None:
            active_delta_threshold = target_bin_delta_threshold_feminine_high_f0
    if target_bin_source_emd_cutoff is not None and source_target_emd <= float(target_bin_source_emd_cutoff):
        if target_direction == "masculine" and target_bin_delta_threshold_masculine_weak is not None:
            active_delta_threshold = target_bin_delta_threshold_masculine_weak
        elif target_direction == "feminine" and target_bin_delta_threshold_feminine_weak is not None:
            active_delta_threshold = target_bin_delta_threshold_feminine_weak
    if (
        target_direction == "feminine"
        and target_bin_shape_topk_sum_cutoff is not None
        and target_bin_delta_threshold_feminine_sharp is not None
        and target_delta_topk_sum >= float(target_bin_shape_topk_sum_cutoff)
    ):
        active_delta_threshold = target_bin_delta_threshold_feminine_sharp
    if record_id in target_bin_record_override_thresholds:
        active_delta_threshold = float(target_bin_record_override_thresholds[record_id])
    record_force_source_only = record_id in target_bin_record_veto_ids

    target_mel_power = np.array(source_mel_power, dtype=np.float64, copy=True)
    source_frame_energy = np.sum(source_mel_power, axis=0)
    bounded_anchor_alpha = max(0.0, min(1.0, float(frame_distribution_anchor_alpha)))
    bounded_min_alpha = max(0.0, min(bounded_anchor_alpha, float(frame_anchor_min_alpha)))
    for frame_idx in range(frame_count):
        if not bool(voiced_mask[frame_idx]):
            continue
        source_frame_distribution = source_mel_power[:, frame_idx] / max(source_frame_energy[frame_idx], 1e-12)
        candidate_distribution = np.array(edited_frames[frame_idx], dtype=np.float64, copy=True)
        if record_force_source_only:
            candidate_distribution = np.array(source_frame_distribution, dtype=np.float64, copy=True)
        elif active_delta_threshold is not None and target_bin_occupancy_threshold is not None:
            stable_bins = (
                np.abs(target_distribution - source_distribution) >= float(active_delta_threshold)
            ) & (target_occupancy >= float(target_bin_occupancy_threshold))
            candidate_distribution[~stable_bins] = source_frame_distribution[~stable_bins]
            candidate_distribution = np.maximum(candidate_distribution, 1e-12)
            candidate_distribution /= max(float(np.sum(candidate_distribution)), 1e-12)
        frame_anchor_alpha = bounded_anchor_alpha
        if frame_anchor_l1_threshold is not None and math.isfinite(frame_anchor_l1_threshold):
            frame_l1 = float(np.sum(np.abs(candidate_distribution - source_frame_distribution)))
            if frame_l1 > float(frame_anchor_l1_threshold):
                max_l1 = max(2.0 - float(frame_anchor_l1_threshold), 1e-12)
                reduction = min(max((frame_l1 - float(frame_anchor_l1_threshold)) / max_l1, 0.0), 1.0)
                frame_anchor_alpha = bounded_anchor_alpha - reduction * (bounded_anchor_alpha - bounded_min_alpha)
        anchored_distribution = (
            frame_anchor_alpha * candidate_distribution
            + (1.0 - frame_anchor_alpha) * source_frame_distribution
        )
        anchored_distribution = np.maximum(anchored_distribution, 1e-12)
        anchored_distribution /= max(float(np.sum(anchored_distribution)), 1e-12)
        target_mel_power[:, frame_idx] = np.maximum(
            anchored_distribution * max(source_frame_energy[frame_idx], 1e-12),
            1e-12,
        )
    return np.log(source_mel_power).astype(np.float32), np.log(target_mel_power).astype(np.float32)


def blend_voiced_target_log_mel(
    source_log_mel: np.ndarray,
    target_log_mel: np.ndarray,
    frame_voiced_mask: np.ndarray,
    *,
    alpha: float,
) -> np.ndarray:
    if alpha >= 0.999999:
        return np.asarray(target_log_mel, dtype=np.float32)
    bounded_alpha = max(0.0, min(1.0, float(alpha)))
    source = np.asarray(source_log_mel, dtype=np.float64)
    target = np.asarray(target_log_mel, dtype=np.float64)
    voiced = align_vector_length(np.asarray(frame_voiced_mask, dtype=np.float64), target.shape[1]) > 0.5
    blended = np.array(target, dtype=np.float64, copy=True)
    blended[:, voiced] = bounded_alpha * target[:, voiced] + (1.0 - bounded_alpha) * source[:, voiced]
    return blended.astype(np.float32)


def save_audio(path: Path, audio: np.ndarray, sample_rate: int, clip_threshold: float) -> None:
    safe_audio = np.clip(np.asarray(audio, dtype=np.float32), -clip_threshold, clip_threshold)
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(path, safe_audio, sample_rate, subtype="PCM_16")


def queue_lookup(rows: list[dict[str, str]]) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]], dict[str, list[dict[str, str]]]]:
    by_record_id = {row["record_id"]: row for row in rows if row.get("record_id")}
    by_utt_id = {row["utt_id"]: row for row in rows if row.get("utt_id")}
    by_rule_id: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        rule_id = row.get("rule_id", "")
        if rule_id:
            by_rule_id.setdefault(rule_id, []).append(row)
    return by_record_id, by_utt_id, by_rule_id


def target_files(path: Path, limit: int | None, patterns: list[str]) -> list[Path]:
    items = sorted(path.glob("*.npz"))
    if patterns:
        lowered = [pattern.lower() for pattern in patterns if pattern]
        filtered: list[Path] = []
        for item in items:
            key = item.name.lower()
            if any(pattern in key for pattern in lowered):
                filtered.append(item)
        items = filtered
    if limit is not None:
        items = items[:limit]
    return items


def safe_slug(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in value)


def format_metric(value: float, digits: int = 6) -> str:
    if not math.isfinite(value):
        return ""
    return fmt_float(value, digits=digits)


def log_mel_mae(
    audio: np.ndarray,
    reference_log_mel: np.ndarray,
    sample_rate: int,
    *,
    n_fft: int,
    hop_length: int,
    n_mels: int,
    fmin: float,
    fmax: float,
    power: float,
    center: bool,
) -> float:
    mel_power = compute_mel_custom(
        np.asarray(audio, dtype=np.float32),
        sample_rate,
        n_fft=n_fft,
        hop_length=hop_length,
        win_length=n_fft,
        n_mels=n_mels,
        fmin=fmin,
        fmax=fmax,
        power=power,
        center=center,
    )
    audio_log_mel = np.log(mel_power)
    if audio_log_mel.shape[1] <= 0:
        return float("nan")
    aligned_reference = align_time_axis(np.asarray(reference_log_mel, dtype=np.float64), audio_log_mel.shape[1])
    return float(np.mean(np.abs(aligned_reference - audio_log_mel)))


def carrier_target_shift_score(source_emd: float, carrier_emd: float) -> float:
    if source_emd <= 1e-12:
        return 0.0
    improvement = (source_emd - carrier_emd) / source_emd
    return float(max(0.0, min(100.0, 50.0 + 50.0 * improvement)))


def write_summary_md(path: Path, rows: list[dict[str, str]], args: argparse.Namespace) -> None:
    success_rows = [row for row in rows if row["synthesis_status"] == "ok"]
    fail_rows = [row for row in rows if row["synthesis_status"] != "ok"]
    strongest_rows = sorted(
        success_rows,
        key=lambda row: float(row["carrier_target_shift_score"] or "0"),
        reverse=True,
    )[:3]
    weakest_rows = sorted(
        success_rows,
        key=lambda row: float(row["carrier_target_shift_score"] or "0"),
    )[:3]

    def avg(field: str) -> float:
        values = [float(row[field]) for row in success_rows if row.get(field)]
        return float(sum(values) / len(values)) if values else float("nan")

    bigvgan_label = resolve_path(args.bigvgan_root).name if getattr(args, "bigvgan_root", None) else "unknown_bigvgan_root"
    vocos_label = resolve_path(args.vocos_root).name if getattr(args, "vocos_root", None) else "unknown_vocos_root"

    backend_scope_notes = {
        "griffinlim_mel_probe": [
            "- The current backend is a bounded non-neural mel inversion probe.",
            "- It is useful as a machine baseline, not as a route candidate.",
        ],
        "rvc_f0_posterior_bridge_v1": [
            "- The current backend is a posterior-side bridge through local `RVC` weights.",
            "- The local RVC generator stack is not a direct `edited_log_mel -> waveform` vocoder.",
            "- This backend uses a posterior-side bridge through pseudo linear spectrograms plus source F0.",
        ],
        "torchaudio_wavernn_bridge_v1": [
            "- The current backend is the pretrained `torchaudio` WaveRNN vocoder bundle.",
            "- This is the first true mel-native neural vocoder backend on the active route.",
        ],
        "bigvgan_local_v1": [
            f"- The current backend is the local `{bigvgan_label}` generator.",
            "- This is a mel-native GAN vocoder with a backend domain close to the exported target packages.",
        ],
        "vocos_local_v1": [
            f"- The current backend is the local `{vocos_label}` model.",
            "- This is a Fourier-domain mel-native vocoder with a local checkpoint and local config.",
        ],
    }

    lines = [
        "# ATRR Vocoder Carrier Adapter Probe v1",
        "",
        "## Scope",
        "",
        "- This run validates the carrier adapter boundary only.",
        "- It is not a human-review candidate.",
        *backend_scope_notes.get(args.backend, [f"- The current backend is `{args.backend}`."]),
        "",
        "## Parameters",
        "",
        f"- backend: `{args.backend}`",
        f"- griffinlim_iter: `{args.griffinlim_iter}`",
        f"- n_fft: `{args.n_fft}`",
        f"- hop_length: `{args.hop_length}`",
        f"- n_mels: `{args.n_mels}`",
        f"- match_source_rms: `{args.match_source_rms}`",
        f"- pitch_correct_source_median: `{args.pitch_correct_source_median}`",
        f"- pitch_correct_voiced_only: `{args.pitch_correct_voiced_only}`",
        f"- pitch_correct_min_drift_cents: `{args.pitch_correct_min_drift_cents}`",
        f"- pitch_correct_max_cents: `{args.pitch_correct_max_cents}`",
        f"- pitch_correct_crossfade_ms: `{args.pitch_correct_crossfade_ms}`",
        f"- pitch_correct_min_span_ms: `{args.pitch_correct_min_span_ms}`",
        f"- voiced_target_blend_alpha: `{args.voiced_target_blend_alpha}`",
        f"- frame_distribution_anchor_alpha: `{args.frame_distribution_anchor_alpha}`",
        f"- frame_anchor_l1_threshold: `{args.frame_anchor_l1_threshold}`",
        f"- frame_anchor_min_alpha: `{args.frame_anchor_min_alpha}`",
        f"- target_bin_delta_threshold: `{args.target_bin_delta_threshold}`",
        f"- target_bin_delta_threshold_masculine: `{args.target_bin_delta_threshold_masculine}`",
        f"- target_bin_delta_threshold_feminine: `{args.target_bin_delta_threshold_feminine}`",
        f"- target_bin_delta_threshold_masculine_low_f0: `{args.target_bin_delta_threshold_masculine_low_f0}`",
        f"- target_bin_delta_threshold_masculine_mid_f0: `{args.target_bin_delta_threshold_masculine_mid_f0}`",
        f"- target_bin_delta_threshold_masculine_high_f0: `{args.target_bin_delta_threshold_masculine_high_f0}`",
        f"- target_bin_delta_threshold_feminine_low_f0: `{args.target_bin_delta_threshold_feminine_low_f0}`",
        f"- target_bin_delta_threshold_feminine_mid_f0: `{args.target_bin_delta_threshold_feminine_mid_f0}`",
        f"- target_bin_delta_threshold_feminine_high_f0: `{args.target_bin_delta_threshold_feminine_high_f0}`",
        f"- target_bin_shape_topk_count: `{args.target_bin_shape_topk_count}`",
        f"- target_bin_shape_topk_sum_cutoff: `{args.target_bin_shape_topk_sum_cutoff}`",
        f"- target_bin_delta_threshold_feminine_sharp: `{args.target_bin_delta_threshold_feminine_sharp}`",
        f"- target_bin_source_emd_cutoff: `{args.target_bin_source_emd_cutoff}`",
        f"- target_bin_delta_threshold_masculine_weak: `{args.target_bin_delta_threshold_masculine_weak}`",
        f"- target_bin_delta_threshold_feminine_weak: `{args.target_bin_delta_threshold_feminine_weak}`",
        f"- target_bin_record_override: `{args.target_bin_record_override}`",
        f"- target_bin_record_veto: `{args.target_bin_record_veto}`",
        f"- target_bin_occupancy_threshold: `{args.target_bin_occupancy_threshold}`",
        f"- rvc_sid: `{args.rvc_sid}`",
        f"- bigvgan_root: `{resolve_path(args.bigvgan_root)}`" if args.backend == "bigvgan_local_v1" else None,
        f"- vocos_root: `{resolve_path(args.vocos_root)}`" if args.backend == "vocos_local_v1" else None,
        "",
        "## Pack Summary",
        "",
        f"- rows: `{len(rows)}`",
        f"- synthesis ok: `{len(success_rows)}`",
        f"- synthesis failed: `{len(fail_rows)}`",
        f"- avg carrier_target_shift_score: `{avg('carrier_target_shift_score'):.2f}`" if success_rows else "- avg carrier_target_shift_score: `n/a`",
        f"- avg target_log_mel_mae: `{avg('target_log_mel_mae'):.4f}`" if success_rows else "- avg target_log_mel_mae: `n/a`",
        f"- avg source_probe_self_emd: `{avg('source_probe_self_emd'):.6f}`" if success_rows else "- avg source_probe_self_emd: `n/a`",
        f"- avg loudness_drift_db: `{avg('loudness_drift_db'):.2f}`" if success_rows else "- avg loudness_drift_db: `n/a`",
        f"- avg f0_drift_cents: `{avg('f0_drift_cents'):.2f}`" if success_rows and any(row.get('f0_drift_cents') for row in success_rows) else "- avg f0_drift_cents: `n/a`",
        "",
        "## Strongest Rows",
        "",
    ]
    for row in strongest_rows:
        lines.append(
            f"- `{row['rule_id']}` | shift=`{row['carrier_target_shift_score']}` | "
            f"mel_mae=`{row['target_log_mel_mae']}` | target_wav=`{row['target_probe_wav']}`"
        )
    lines.extend(["", "## Weakest Rows", ""])
    for row in weakest_rows:
        lines.append(
            f"- `{row['rule_id']}` | shift=`{row['carrier_target_shift_score']}` | "
            f"mel_mae=`{row['target_log_mel_mae']}` | target_wav=`{row['target_probe_wav']}`"
        )
    if fail_rows:
        lines.extend(["", "## Failures", ""])
        for row in fail_rows[:5]:
            lines.append(f"- `{row['rule_id']}` | error=`{row['error_message']}`")
    final_lines = [line for line in lines if line is not None]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(final_lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    record_override_thresholds = parse_record_threshold_overrides(args.target_bin_record_override)
    record_veto_ids = {item.strip() for item in args.target_bin_record_veto if item and item.strip()}
    target_dir = resolve_path(args.target_dir)
    queue_csv = resolve_path(args.queue_csv)
    output_dir = resolve_path(args.output_dir)
    if args.backend == "rvc_f0_posterior_bridge_v1":
        backend_context = build_rvc_backend(args)
    elif args.backend == "torchaudio_wavernn_bridge_v1":
        backend_context = build_wavernn_backend(args)
    elif args.backend == "bigvgan_local_v1":
        backend_context = build_bigvgan_backend(args)
    elif args.backend == "vocos_local_v1":
        backend_context = build_vocos_backend(args)
    else:
        backend_context = None

    with queue_csv.open("r", encoding="utf-8", newline="") as handle:
        queue_rows = list(csv.DictReader(handle))
    by_record_id, by_utt_id, by_rule_id = queue_lookup(queue_rows)
    targets = target_files(target_dir, args.limit, args.target_pattern)
    if not targets:
        raise ValueError("No target packages found.")

    summary_rows: list[dict[str, str]] = []
    source_probe_dir = output_dir / "source_probe_wav"
    target_probe_dir = output_dir / "target_probe_wav"

    for target_path in targets:
        package = np.load(target_path)
        rule_id = scalar_string(package["rule_id"])
        record_id = scalar_string(package["record_id"])
        utt_id = scalar_string(package["utt_id"])
        queue_row = by_record_id.get(record_id)
        if queue_row is None:
            queue_row = by_utt_id.get(utt_id)
        if queue_row is None:
            rule_matches = by_rule_id.get(rule_id, [])
            if len(rule_matches) == 1:
                queue_row = rule_matches[0]
        if queue_row is None:
            summary_rows.append(
                {
                    "rule_id": rule_id,
                    "record_id": record_id,
                    "utt_id": utt_id,
                    "backend": args.backend,
                    "synthesis_status": "missing_queue_row",
                    "error_message": "record_id and utt_id not found in queue csv",
                    "target_npz": str(target_path),
                    "source_probe_wav": "",
                    "target_probe_wav": "",
                    "duration_delta_ms": "",
                    "loudness_drift_db": "",
                    "clipping_ratio": "",
                    "f0_source_median_hz": "",
                    "f0_probe_median_hz": "",
                    "f0_drift_cents": "",
                    "source_target_emd": "",
                    "carrier_target_emd": "",
                    "carrier_target_shift_score": "",
                    "target_log_mel_mae": "",
                    "source_probe_self_emd": "",
                }
            )
            continue

        original_audio, sample_rate = load_audio(resolve_path(queue_row["original_copy"]))
        target_log_mel = np.asarray(package["target_log_mel"], dtype=np.float64)
        source_log_mel = np.asarray(package["source_log_mel"], dtype=np.float64)
        source_distribution = np.asarray(package["source_distribution"], dtype=np.float64)
        target_distribution = np.asarray(package["target_distribution"], dtype=np.float64)
        source_target_emd = one_dim_emd(source_distribution, target_distribution)

        base_name = f"{safe_slug(record_id)}__{safe_slug(utt_id)}"
        source_probe_wav = source_probe_dir / f"{base_name}.wav"
        target_probe_wav = target_probe_dir / f"{base_name}.wav"

        try:
            mel_metric_params = {
                "n_fft": args.n_fft,
                "hop_length": args.hop_length,
                "n_mels": args.n_mels,
                "fmin": args.fmin,
                "fmax": args.fmax,
                "power": 2.0,
                "center": True,
            }
            if args.backend == "griffinlim_mel_probe":
                probe_sample_rate = int(np.asarray(package["sample_rate"]).reshape(-1)[0])
                if sample_rate != probe_sample_rate:
                    original_audio = librosa.resample(original_audio, orig_sr=sample_rate, target_sr=probe_sample_rate).astype(np.float32)
                    sample_rate = probe_sample_rate
                source_probe_audio = inverse_log_mel(
                    source_log_mel,
                    probe_sample_rate,
                    n_fft=args.n_fft,
                    hop_length=args.hop_length,
                    fmin=args.fmin,
                    fmax=args.fmax,
                    griffinlim_iter=args.griffinlim_iter,
                    target_length=original_audio.shape[0],
                )
                target_probe_audio = inverse_log_mel(
                    target_log_mel,
                    probe_sample_rate,
                    n_fft=args.n_fft,
                    hop_length=args.hop_length,
                    fmin=args.fmin,
                    fmax=args.fmax,
                    griffinlim_iter=args.griffinlim_iter,
                    target_length=original_audio.shape[0],
                )
            elif args.backend == "rvc_f0_posterior_bridge_v1":
                assert backend_context is not None
                source_probe_audio, probe_sample_rate = synthesize_rvc_posterior_bridge(
                    source_log_mel,
                    original_audio,
                    sample_rate,
                    backend=backend_context,
                    args=args,
                )
                target_probe_audio, probe_sample_rate = synthesize_rvc_posterior_bridge(
                    target_log_mel,
                    original_audio,
                    sample_rate,
                    backend=backend_context,
                    args=args,
                )
                if sample_rate != probe_sample_rate:
                    original_audio = librosa.resample(original_audio, orig_sr=sample_rate, target_sr=probe_sample_rate).astype(np.float32)
                    sample_rate = probe_sample_rate
            elif args.backend == "torchaudio_wavernn_bridge_v1":
                assert backend_context is not None
                source_backend_log_mel, target_backend_log_mel = rebuild_backend_target_log_mel(
                    package,
                    original_audio,
                    sample_rate,
                    sample_rate=int(backend_context["sample_rate"]),
                    n_fft=int(backend_context["n_fft"]),
                    win_length=int(backend_context["win_length"]),
                    hop_length=int(backend_context["hop_length"]),
                    n_mels=int(backend_context["n_mels"]),
                    fmin=float(backend_context["fmin"]),
                    fmax=float(backend_context["fmax"]),
                    power=float(backend_context["power"]),
                    center=bool(backend_context["center"]),
                    frame_distribution_anchor_alpha=args.frame_distribution_anchor_alpha,
                    frame_anchor_l1_threshold=args.frame_anchor_l1_threshold,
                    frame_anchor_min_alpha=args.frame_anchor_min_alpha,
                    target_bin_delta_threshold=args.target_bin_delta_threshold,
                    target_bin_delta_threshold_masculine=args.target_bin_delta_threshold_masculine,
                    target_bin_delta_threshold_feminine=args.target_bin_delta_threshold_feminine,
                    target_bin_delta_threshold_masculine_low_f0=args.target_bin_delta_threshold_masculine_low_f0,
                    target_bin_delta_threshold_masculine_mid_f0=args.target_bin_delta_threshold_masculine_mid_f0,
                    target_bin_delta_threshold_masculine_high_f0=args.target_bin_delta_threshold_masculine_high_f0,
                    target_bin_delta_threshold_feminine_low_f0=args.target_bin_delta_threshold_feminine_low_f0,
                    target_bin_delta_threshold_feminine_mid_f0=args.target_bin_delta_threshold_feminine_mid_f0,
                    target_bin_delta_threshold_feminine_high_f0=args.target_bin_delta_threshold_feminine_high_f0,
                    target_bin_shape_topk_count=args.target_bin_shape_topk_count,
                    target_bin_shape_topk_sum_cutoff=args.target_bin_shape_topk_sum_cutoff,
                    target_bin_delta_threshold_feminine_sharp=args.target_bin_delta_threshold_feminine_sharp,
                    target_bin_source_emd_cutoff=args.target_bin_source_emd_cutoff,
                    target_bin_delta_threshold_masculine_weak=args.target_bin_delta_threshold_masculine_weak,
                    target_bin_delta_threshold_feminine_weak=args.target_bin_delta_threshold_feminine_weak,
                    target_bin_record_override_thresholds=record_override_thresholds,
                    target_bin_record_veto_ids=record_veto_ids,
                    target_bin_occupancy_threshold=args.target_bin_occupancy_threshold,
                )
                if args.voiced_target_blend_alpha < 0.999999:
                    target_backend_log_mel = blend_voiced_target_log_mel(
                        source_backend_log_mel,
                        target_backend_log_mel,
                        np.asarray(package["voiced_mask"], dtype=np.float64),
                        alpha=args.voiced_target_blend_alpha,
                    )
                source_probe_audio, probe_sample_rate = synthesize_wavernn_bridge(
                    source_backend_log_mel,
                    original_audio,
                    sample_rate,
                    backend=backend_context,
                )
                target_probe_audio, probe_sample_rate = synthesize_wavernn_bridge(
                    target_backend_log_mel,
                    original_audio,
                    sample_rate,
                    backend=backend_context,
                )
                if sample_rate != probe_sample_rate:
                    original_audio = librosa.resample(original_audio, orig_sr=sample_rate, target_sr=probe_sample_rate).astype(np.float32)
                    sample_rate = probe_sample_rate
                source_log_mel = source_backend_log_mel
                target_log_mel = target_backend_log_mel
                mel_metric_params = {
                    "n_fft": int(backend_context["n_fft"]),
                    "hop_length": int(backend_context["hop_length"]),
                    "n_mels": int(backend_context["n_mels"]),
                    "fmin": float(backend_context["fmin"]),
                    "fmax": float(backend_context["fmax"]),
                    "power": float(backend_context["power"]),
                    "center": bool(backend_context["center"]),
                }
            elif args.backend == "bigvgan_local_v1":
                assert backend_context is not None
                source_backend_log_mel, target_backend_log_mel = rebuild_backend_target_log_mel(
                    package,
                    original_audio,
                    sample_rate,
                    sample_rate=int(backend_context["sample_rate"]),
                    n_fft=int(backend_context["n_fft"]),
                    win_length=int(backend_context["win_length"]),
                    hop_length=int(backend_context["hop_length"]),
                    n_mels=int(backend_context["n_mels"]),
                    fmin=float(backend_context["fmin"]),
                    fmax=float(backend_context["fmax"]),
                    power=float(backend_context["power"]),
                    center=bool(backend_context["center"]),
                    frame_distribution_anchor_alpha=args.frame_distribution_anchor_alpha,
                    frame_anchor_l1_threshold=args.frame_anchor_l1_threshold,
                    frame_anchor_min_alpha=args.frame_anchor_min_alpha,
                    target_bin_delta_threshold=args.target_bin_delta_threshold,
                    target_bin_delta_threshold_masculine=args.target_bin_delta_threshold_masculine,
                    target_bin_delta_threshold_feminine=args.target_bin_delta_threshold_feminine,
                    target_bin_delta_threshold_masculine_low_f0=args.target_bin_delta_threshold_masculine_low_f0,
                    target_bin_delta_threshold_masculine_mid_f0=args.target_bin_delta_threshold_masculine_mid_f0,
                    target_bin_delta_threshold_masculine_high_f0=args.target_bin_delta_threshold_masculine_high_f0,
                    target_bin_delta_threshold_feminine_low_f0=args.target_bin_delta_threshold_feminine_low_f0,
                    target_bin_delta_threshold_feminine_mid_f0=args.target_bin_delta_threshold_feminine_mid_f0,
                    target_bin_delta_threshold_feminine_high_f0=args.target_bin_delta_threshold_feminine_high_f0,
                    target_bin_shape_topk_count=args.target_bin_shape_topk_count,
                    target_bin_shape_topk_sum_cutoff=args.target_bin_shape_topk_sum_cutoff,
                    target_bin_delta_threshold_feminine_sharp=args.target_bin_delta_threshold_feminine_sharp,
                    target_bin_source_emd_cutoff=args.target_bin_source_emd_cutoff,
                    target_bin_delta_threshold_masculine_weak=args.target_bin_delta_threshold_masculine_weak,
                    target_bin_delta_threshold_feminine_weak=args.target_bin_delta_threshold_feminine_weak,
                    target_bin_record_override_thresholds=record_override_thresholds,
                    target_bin_record_veto_ids=record_veto_ids,
                    target_bin_occupancy_threshold=args.target_bin_occupancy_threshold,
                )
                if args.voiced_target_blend_alpha < 0.999999:
                    target_backend_log_mel = blend_voiced_target_log_mel(
                        source_backend_log_mel,
                        target_backend_log_mel,
                        np.asarray(package["voiced_mask"], dtype=np.float64),
                        alpha=args.voiced_target_blend_alpha,
                    )
                source_probe_audio, probe_sample_rate = synthesize_bigvgan_bridge(
                    source_backend_log_mel,
                    original_audio,
                    sample_rate,
                    backend=backend_context,
                )
                target_probe_audio, probe_sample_rate = synthesize_bigvgan_bridge(
                    target_backend_log_mel,
                    original_audio,
                    sample_rate,
                    backend=backend_context,
                )
                if sample_rate != probe_sample_rate:
                    original_audio = librosa.resample(original_audio, orig_sr=sample_rate, target_sr=probe_sample_rate).astype(np.float32)
                    sample_rate = probe_sample_rate
                source_log_mel = source_backend_log_mel
                target_log_mel = target_backend_log_mel
                mel_metric_params = {
                    "n_fft": int(backend_context["n_fft"]),
                    "hop_length": int(backend_context["hop_length"]),
                    "n_mels": int(backend_context["n_mels"]),
                    "fmin": float(backend_context["fmin"]),
                    "fmax": float(backend_context["fmax"]),
                    "power": float(backend_context["power"]),
                    "center": bool(backend_context["center"]),
                }
            elif args.backend == "vocos_local_v1":
                assert backend_context is not None
                source_backend_log_mel, target_backend_log_mel = rebuild_backend_target_log_mel(
                    package,
                    original_audio,
                    sample_rate,
                    sample_rate=int(backend_context["sample_rate"]),
                    n_fft=int(backend_context["n_fft"]),
                    win_length=int(backend_context["win_length"]),
                    hop_length=int(backend_context["hop_length"]),
                    n_mels=int(backend_context["n_mels"]),
                    fmin=float(backend_context["fmin"]),
                    fmax=float(backend_context["fmax"]),
                    power=float(backend_context["power"]),
                    center=bool(backend_context["center"]),
                    frame_distribution_anchor_alpha=args.frame_distribution_anchor_alpha,
                    frame_anchor_l1_threshold=args.frame_anchor_l1_threshold,
                    frame_anchor_min_alpha=args.frame_anchor_min_alpha,
                    target_bin_delta_threshold=args.target_bin_delta_threshold,
                    target_bin_delta_threshold_masculine=args.target_bin_delta_threshold_masculine,
                    target_bin_delta_threshold_feminine=args.target_bin_delta_threshold_feminine,
                    target_bin_delta_threshold_masculine_low_f0=args.target_bin_delta_threshold_masculine_low_f0,
                    target_bin_delta_threshold_masculine_mid_f0=args.target_bin_delta_threshold_masculine_mid_f0,
                    target_bin_delta_threshold_masculine_high_f0=args.target_bin_delta_threshold_masculine_high_f0,
                    target_bin_delta_threshold_feminine_low_f0=args.target_bin_delta_threshold_feminine_low_f0,
                    target_bin_delta_threshold_feminine_mid_f0=args.target_bin_delta_threshold_feminine_mid_f0,
                    target_bin_delta_threshold_feminine_high_f0=args.target_bin_delta_threshold_feminine_high_f0,
                    target_bin_shape_topk_count=args.target_bin_shape_topk_count,
                    target_bin_shape_topk_sum_cutoff=args.target_bin_shape_topk_sum_cutoff,
                    target_bin_delta_threshold_feminine_sharp=args.target_bin_delta_threshold_feminine_sharp,
                    target_bin_source_emd_cutoff=args.target_bin_source_emd_cutoff,
                    target_bin_delta_threshold_masculine_weak=args.target_bin_delta_threshold_masculine_weak,
                    target_bin_delta_threshold_feminine_weak=args.target_bin_delta_threshold_feminine_weak,
                    target_bin_record_override_thresholds=record_override_thresholds,
                    target_bin_record_veto_ids=record_veto_ids,
                    target_bin_occupancy_threshold=args.target_bin_occupancy_threshold,
                )
                if args.voiced_target_blend_alpha < 0.999999:
                    target_backend_log_mel = blend_voiced_target_log_mel(
                        source_backend_log_mel,
                        target_backend_log_mel,
                        np.asarray(package["voiced_mask"], dtype=np.float64),
                        alpha=args.voiced_target_blend_alpha,
                    )
                source_probe_audio, probe_sample_rate = synthesize_vocos_bridge(
                    source_backend_log_mel,
                    original_audio,
                    sample_rate,
                    backend=backend_context,
                )
                target_probe_audio, probe_sample_rate = synthesize_vocos_bridge(
                    target_backend_log_mel,
                    original_audio,
                    sample_rate,
                    backend=backend_context,
                )
                if sample_rate != probe_sample_rate:
                    original_audio = librosa.resample(original_audio, orig_sr=sample_rate, target_sr=probe_sample_rate).astype(np.float32)
                    sample_rate = probe_sample_rate
                source_log_mel = source_backend_log_mel
                target_log_mel = target_backend_log_mel
                mel_metric_params = {
                    "n_fft": int(backend_context["n_fft"]),
                    "hop_length": int(backend_context["hop_length"]),
                    "n_mels": int(backend_context["n_mels"]),
                    "fmin": float(backend_context["fmin"]),
                    "fmax": float(backend_context["fmax"]),
                    "power": float(backend_context["power"]),
                    "center": bool(backend_context["center"]),
                }
            else:
                raise ValueError(f"Unsupported backend: {args.backend}")

            if args.pitch_correct_source_median:
                correction_fn = pitch_correct_to_reference_median
                correction_kwargs = {
                    "n_fft": args.n_fft,
                    "hop_length": args.hop_length,
                    "min_drift_cents": args.pitch_correct_min_drift_cents,
                    "max_correction_cents": args.pitch_correct_max_cents,
                }
                if args.pitch_correct_voiced_only:
                    correction_fn = pitch_correct_to_reference_median_voiced_only
                    correction_kwargs = {
                        "frame_voiced_mask": np.asarray(package["voiced_mask"], dtype=np.float64),
                        "hop_length": args.hop_length,
                        "n_fft": args.n_fft,
                        "min_drift_cents": args.pitch_correct_min_drift_cents,
                        "max_correction_cents": args.pitch_correct_max_cents,
                        "crossfade_ms": args.pitch_correct_crossfade_ms,
                        "min_span_ms": args.pitch_correct_min_span_ms,
                    }
                source_probe_audio = correction_fn(
                    source_probe_audio,
                    original_audio,
                    sample_rate,
                    **correction_kwargs,
                )
                target_probe_audio = correction_fn(
                    target_probe_audio,
                    original_audio,
                    sample_rate,
                    **correction_kwargs,
                )

            if args.match_source_rms:
                source_probe_audio = match_rms(source_probe_audio, original_audio)
                target_probe_audio = match_rms(target_probe_audio, original_audio)

            save_audio(source_probe_wav, source_probe_audio, sample_rate, args.clip_threshold)
            save_audio(target_probe_wav, target_probe_audio, sample_rate, args.clip_threshold)

            source_probe_features = build_distribution_features(
                source_probe_audio,
                sample_rate,
                n_fft=args.n_fft,
                hop_length=args.hop_length,
                n_mels=args.n_mels,
                fmin=args.fmin,
                fmax=args.fmax,
                rms_threshold_db=args.rms_threshold_db,
                frame_core_threshold=args.frame_core_threshold,
            )
            target_probe_features = build_distribution_features(
                target_probe_audio,
                sample_rate,
                n_fft=args.n_fft,
                hop_length=args.hop_length,
                n_mels=args.n_mels,
                fmin=args.fmin,
                fmax=args.fmax,
                rms_threshold_db=args.rms_threshold_db,
                frame_core_threshold=args.frame_core_threshold,
            )

            carrier_emd = one_dim_emd(target_probe_features.utterance_distribution, target_distribution)
            source_probe_self_emd = one_dim_emd(source_probe_features.utterance_distribution, source_distribution)
            mel_mae = log_mel_mae(
                target_probe_audio,
                target_log_mel,
                sample_rate,
                n_fft=mel_metric_params["n_fft"],
                hop_length=mel_metric_params["hop_length"],
                n_mels=mel_metric_params["n_mels"],
                fmin=mel_metric_params["fmin"],
                fmax=mel_metric_params["fmax"],
                power=mel_metric_params["power"],
                center=mel_metric_params["center"],
            )
            source_f0_hz, _ = estimate_f0_median_hz(
                original_audio,
                sample_rate,
                n_fft=args.n_fft,
                hop_length=args.hop_length,
            )
            probe_f0_hz, _ = estimate_f0_median_hz(
                target_probe_audio,
                sample_rate,
                n_fft=args.n_fft,
                hop_length=args.hop_length,
            )

            summary_rows.append(
                {
                    "rule_id": rule_id,
                    "record_id": record_id,
                    "utt_id": utt_id,
                    "backend": args.backend,
                    "synthesis_status": "ok",
                    "error_message": "",
                    "target_npz": str(target_path),
                    "source_probe_wav": str(source_probe_wav),
                    "target_probe_wav": str(target_probe_wav),
                    "duration_delta_ms": format_metric((len(target_probe_audio) - len(original_audio)) / sample_rate * 1000.0, digits=3),
                    "loudness_drift_db": format_metric(safe_rms_db(target_probe_audio) - safe_rms_db(original_audio), digits=3),
                    "clipping_ratio": format_metric(clipping_ratio(target_probe_audio, args.clip_threshold)),
                    "f0_source_median_hz": format_metric(source_f0_hz, digits=3),
                    "f0_probe_median_hz": format_metric(probe_f0_hz, digits=3),
                    "f0_drift_cents": format_metric(cents_difference(source_f0_hz, probe_f0_hz), digits=2),
                    "source_target_emd": format_metric(source_target_emd),
                    "carrier_target_emd": format_metric(carrier_emd),
                    "carrier_target_shift_score": format_metric(carrier_target_shift_score(source_target_emd, carrier_emd), digits=2),
                    "target_log_mel_mae": format_metric(mel_mae, digits=6),
                    "source_probe_self_emd": format_metric(source_probe_self_emd),
                }
            )
        except Exception as exc:
            summary_rows.append(
                {
                    "rule_id": rule_id,
                    "record_id": record_id,
                    "utt_id": utt_id,
                    "backend": args.backend,
                    "synthesis_status": "failed",
                    "error_message": str(exc),
                    "target_npz": str(target_path),
                    "source_probe_wav": "",
                    "target_probe_wav": "",
                    "duration_delta_ms": "",
                    "loudness_drift_db": "",
                    "clipping_ratio": "",
                    "f0_source_median_hz": "",
                    "f0_probe_median_hz": "",
                    "f0_drift_cents": "",
                    "source_target_emd": "",
                    "carrier_target_emd": "",
                    "carrier_target_shift_score": "",
                    "target_log_mel_mae": "",
                    "source_probe_self_emd": "",
                }
            )

    detail_csv = output_dir / "atrr_vocoder_carrier_adapter_summary.csv"
    summary_md = output_dir / "ATRR_VOCODER_CARRIER_ADAPTER_SUMMARY.md"
    write_csv(detail_csv, summary_rows)
    write_summary_md(summary_md, summary_rows, args)
    print(f"Wrote {detail_csv}")
    print(f"Wrote {summary_md}")
    print(f"Rows: {len(summary_rows)}")


if __name__ == "__main__":
    main()
