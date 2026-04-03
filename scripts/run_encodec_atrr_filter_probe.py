from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from types import SimpleNamespace

import librosa
import numpy as np
import scipy.fft
import torch
import torchaudio
from encodec import EncodecModel

from simulate_targetward_resonance_residual import build_combined_core_mask


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE_QUEUE = (
    ROOT
    / "artifacts"
    / "listening_review"
    / "stage0_speech_lsf_machine_sweep_v9_fixed8"
    / "split_core_focus_v9a"
    / "listening_review_queue.csv"
)
DEFAULT_TARGET_DIR = (
    ROOT
    / "artifacts"
    / "diagnostics"
    / "atrr_vocoder_bridge_target_export"
    / "v1_fixed8_v9a"
    / "targets"
)
DEFAULT_OUTPUT_DIR = (
    ROOT
    / "artifacts"
    / "diagnostics"
    / "encodec_atrr_filter_probe"
    / "v1_fixed8_env12_s020_d15_g15_bw24"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template-queue", default=str(DEFAULT_TEMPLATE_QUEUE))
    parser.add_argument("--target-dir", default=str(DEFAULT_TARGET_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--repository", default="")
    parser.add_argument("--bandwidth", type=float, default=24.0)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--max-rows", type=int, default=0)
    parser.add_argument("--n-fft", type=int, default=2048)
    parser.add_argument("--hop-length", type=int, default=256)
    parser.add_argument("--n-mels", type=int, default=80)
    parser.add_argument("--fmin", type=float, default=50.0)
    parser.add_argument("--fmax", type=float, default=8000.0)
    parser.add_argument("--delta-scale", type=float, default=0.20)
    parser.add_argument("--delta-cap-db", type=float, default=1.50)
    parser.add_argument("--keep-coeffs", type=int, default=12)
    parser.add_argument("--gain-cap-db", type=float, default=1.50)
    parser.add_argument("--gain-floor-db", type=float, default=-1.50)
    parser.add_argument("--time-smooth-frames", type=int, default=5)
    parser.add_argument("--voiced-only", action="store_true")
    parser.add_argument("--core-mask", action="store_true")
    parser.add_argument("--core-mask-energy-threshold", type=float, default=0.60)
    parser.add_argument("--core-mask-occupancy-threshold", type=float, default=0.35)
    parser.add_argument("--core-mask-offcore-scale", type=float, default=0.00)
    parser.add_argument("--core-mask-frame-threshold", type=float, default=0.60)
    parser.add_argument("--core-mask-frame-occupancy-threshold", type=float, default=0.25)
    return parser.parse_args()


def resolve_path(value: str | Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return ROOT / path


def choose_device(value: str) -> str:
    if value != "auto":
        return value
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def read_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
        return rows, list(rows[0].keys()) if rows else []


def write_rows(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_audio_mono(path: Path, sample_rate: int) -> torch.Tensor:
    audio, src_sr = torchaudio.load(path)
    if audio.shape[0] > 1:
        audio = torch.mean(audio, dim=0, keepdim=True)
    if src_sr != sample_rate:
        audio = torchaudio.functional.resample(audio, src_sr, sample_rate)
    return audio


def align_columns(matrix: np.ndarray, target_frames: int) -> np.ndarray:
    source = np.asarray(matrix, dtype=np.float64)
    if source.shape[1] == target_frames:
        return source
    if source.shape[1] <= 1:
        return np.repeat(source, target_frames, axis=1)
    x_old = np.linspace(0.0, 1.0, num=source.shape[1], endpoint=True)
    x_new = np.linspace(0.0, 1.0, num=target_frames, endpoint=True)
    aligned = np.empty((source.shape[0], target_frames), dtype=np.float64)
    for idx in range(source.shape[0]):
        aligned[idx] = np.interp(x_new, x_old, source[idx])
    return aligned


def align_mask(mask: np.ndarray, target_frames: int) -> np.ndarray:
    source = np.asarray(mask, dtype=np.float64).reshape(-1)
    if source.shape[0] == target_frames:
        return source >= 0.5
    if source.shape[0] <= 1:
        fill = bool(source[0] >= 0.5) if source.shape[0] == 1 else False
        return np.full(target_frames, fill, dtype=bool)
    x_old = np.linspace(0.0, 1.0, num=source.shape[0], endpoint=True)
    x_new = np.linspace(0.0, 1.0, num=target_frames, endpoint=True)
    return np.interp(x_new, x_old, source) >= 0.5


def smooth_time(matrix: np.ndarray, radius: int) -> np.ndarray:
    if radius <= 1:
        return matrix
    kernel = np.ones(radius, dtype=np.float64) / float(radius)
    padded = np.pad(matrix, ((0, 0), (radius // 2, radius - 1 - radius // 2)), mode="edge")
    return np.apply_along_axis(lambda row: np.convolve(row, kernel, mode="valid"), 1, padded)


def build_frame_core_occupancy(
    edited_frame_distributions: np.ndarray,
    *,
    energy_threshold: float,
) -> np.ndarray:
    frames = np.asarray(edited_frame_distributions, dtype=np.float64)
    if frames.ndim != 2 or frames.shape[0] == 0:
        return np.zeros((frames.shape[1] if frames.ndim == 2 else 0,), dtype=np.float64)
    masks = np.zeros_like(frames, dtype=np.float64)
    for frame_idx in range(frames.shape[0]):
        frame = np.asarray(frames[frame_idx], dtype=np.float64)
        total = float(np.sum(frame))
        if total <= 1e-12:
            continue
        normalized = frame / total
        ordered = np.argsort(normalized)[::-1]
        cumulative = 0.0
        for idx in ordered:
            cumulative += float(normalized[idx])
            masks[frame_idx, idx] = 1.0
            if cumulative >= energy_threshold:
                break
    return np.mean(masks, axis=0)


def build_target_index(target_dir: Path) -> dict[str, Path]:
    index: dict[str, Path] = {}
    for npz_path in sorted(target_dir.glob("*.npz")):
        with np.load(npz_path) as payload:
            record_id = str(payload["record_id"])
        index[record_id] = npz_path
    return index


def db_to_log_amplitude(value_db: float) -> float:
    return float(value_db) * math.log(10.0) / 20.0


def log_amplitude_to_db(value_ln: np.ndarray) -> np.ndarray:
    return np.asarray(value_ln, dtype=np.float64) * 20.0 / math.log(10.0)


def build_low_quefrency_envelope(log_mag: np.ndarray, keep_coeffs: int) -> np.ndarray:
    cep = scipy.fft.dct(np.asarray(log_mag, dtype=np.float64), type=2, axis=0, norm="ortho")
    coeff_count = min(int(keep_coeffs), max(int(cep.shape[0] - 1), 0))
    env_cep = np.zeros_like(cep, dtype=np.float64)
    env_cep[0, :] = cep[0, :]
    if coeff_count > 0:
        env_cep[1 : 1 + coeff_count, :] = cep[1 : 1 + coeff_count, :]
    return scipy.fft.idct(env_cep, type=2, axis=0, norm="ortho").astype(np.float64)


def build_readme(args: argparse.Namespace, output_dir: Path, rows: int) -> str:
    rel_template = resolve_path(args.template_queue).relative_to(ROOT).as_posix()
    rel_target = resolve_path(args.target_dir).relative_to(ROOT).as_posix()
    rel_output = output_dir.relative_to(ROOT).as_posix()
    return (
        "# Encodec ATRR Filter Probe v1\n\n"
        "- purpose: `source-preserving Encodec roundtrip anchor with narrow filter-side ATRR injection`\n"
        f"- rows: `{rows}`\n"
        f"- bandwidth_kbps: `{args.bandwidth:.1f}`\n"
        f"- delta_scale: `{args.delta_scale:.2f}`\n"
        f"- delta_cap_db: `{args.delta_cap_db:.2f}`\n"
        f"- keep_coeffs: `{args.keep_coeffs}`\n"
        f"- gain_floor_db: `{args.gain_floor_db:.2f}`\n"
        f"- gain_cap_db: `{args.gain_cap_db:.2f}`\n"
        f"- voiced_only: `{bool(args.voiced_only)}`\n"
        f"- core_mask: `{bool(args.core_mask)}`\n"
        f"- core_mask_offcore_scale: `{args.core_mask_offcore_scale:.2f}`\n\n"
        "## Rebuild\n\n"
        "```powershell\n"
        ".\\python.exe .\\scripts\\run_encodec_atrr_filter_probe.py `\n"
        f"  --template-queue {rel_template} `\n"
        f"  --target-dir {rel_target} `\n"
        f"  --output-dir {rel_output} `\n"
        f"  --bandwidth {args.bandwidth:.1f} `\n"
        f"  --delta-scale {args.delta_scale:.2f} `\n"
        f"  --delta-cap-db {args.delta_cap_db:.2f} `\n"
        f"  --keep-coeffs {args.keep_coeffs} `\n"
        f"  --gain-floor-db {args.gain_floor_db:.2f} `\n"
        f"  --gain-cap-db {args.gain_cap_db:.2f}"
        + (
            f" `\n  --core-mask `\n  --core-mask-energy-threshold {args.core_mask_energy_threshold:.2f} `\n"
            f"  --core-mask-occupancy-threshold {args.core_mask_occupancy_threshold:.2f} `\n"
            f"  --core-mask-offcore-scale {args.core_mask_offcore_scale:.2f} `\n"
            f"  --core-mask-frame-threshold {args.core_mask_frame_threshold:.2f} `\n"
            f"  --core-mask-frame-occupancy-threshold {args.core_mask_frame_occupancy_threshold:.2f}"
            if args.core_mask
            else ""
        )
        + (" `\n  --voiced-only\n" if args.voiced_only else "\n")
        + "```\n"
    )


def build_summary(rows: list[dict[str, str]], args: argparse.Namespace, device: str, sample_rate: int) -> str:
    def avg(field: str) -> float:
        return sum(float(row[field]) for row in rows) / max(len(rows), 1)

    strongest = sorted(rows, key=lambda row: float(row["applied_envelope_gain_abs_mean_db"]), reverse=True)[:3]
    weakest = sorted(rows, key=lambda row: float(row["target_logmel_delta_l1_db"]))[:3]
    lines = [
        "# Encodec ATRR Filter Probe Summary v1",
        "",
        f"- rows: `{len(rows)}`",
        f"- sample_rate: `{sample_rate}`",
        f"- device: `{device}`",
        f"- bandwidth_kbps: `{args.bandwidth:.1f}`",
        f"- avg target_logmel_delta_l1_db: `{avg('target_logmel_delta_l1_db'):.4f}`",
        f"- avg applied_envelope_gain_abs_mean_db: `{avg('applied_envelope_gain_abs_mean_db'):.4f}`",
        f"- avg applied_envelope_gain_abs_max_db: `{avg('applied_envelope_gain_abs_max_db'):.4f}`",
        f"- avg core_mask_ratio: `{avg('core_mask_ratio'):.4f}`",
        "",
        "## Strongest Applied Rows",
        "",
    ]
    for row in strongest:
        lines.append(
            f"- `{row['record_id']}` | env_gain_mean_db=`{row['applied_envelope_gain_abs_mean_db']}` | "
            f"env_gain_max_db=`{row['applied_envelope_gain_abs_max_db']}`"
        )
    lines.extend(["", "## Weakest Target Delta Rows", ""])
    for row in weakest:
        lines.append(
            f"- `{row['record_id']}` | target_delta_l1_db=`{row['target_logmel_delta_l1_db']}` | "
            f"core_mask_ratio=`{row['core_mask_ratio']}`"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    template_queue = resolve_path(args.template_queue)
    target_dir = resolve_path(args.target_dir)
    output_dir = resolve_path(args.output_dir)
    repository = resolve_path(args.repository) if args.repository else None
    device = choose_device(args.device)

    rows, fieldnames = read_rows(template_queue)
    if not rows:
        raise ValueError("Template queue is empty.")
    if args.max_rows > 0:
        rows = rows[: args.max_rows]

    target_index = build_target_index(target_dir)
    if not target_index:
        raise ValueError("Target package directory is empty.")

    model = EncodecModel.encodec_model_24khz(pretrained=True, repository=repository)
    model.set_target_bandwidth(float(args.bandwidth))
    model = model.to(device).eval()

    processed_dir = output_dir / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    summary_rows: list[dict[str, str]] = []
    output_rows: list[dict[str, str]] = []
    for row in rows:
        record_id = row["record_id"]
        target_npz = target_index.get(record_id)
        if target_npz is None:
            raise KeyError(f"Missing target package for record_id={record_id}")

        source_path = resolve_path(row["input_audio"])
        audio = load_audio_mono(source_path, int(model.sample_rate)).to(device)
        with torch.no_grad():
            encoded_frames = model.encode(audio.unsqueeze(0))
            roundtrip = model.decode(encoded_frames).detach().cpu().squeeze().numpy().astype(np.float32)

        with np.load(target_npz) as payload:
            source_log_mel = np.asarray(payload["source_log_mel"], dtype=np.float64)
            target_log_mel = np.asarray(payload["target_log_mel"], dtype=np.float64)
            voiced_mask = np.asarray(payload["voiced_mask"], dtype=np.float64)
            target_sample_rate = int(np.asarray(payload["sample_rate"]).reshape(-1)[0])
            source_distribution = np.asarray(payload["source_distribution"], dtype=np.float64)
            target_distribution = np.asarray(payload["target_distribution"], dtype=np.float64)
            target_occupancy = np.asarray(payload["target_occupancy"], dtype=np.float64)
            edited_frame_distributions = np.asarray(payload["edited_frame_distributions"], dtype=np.float64)

        source_stft = librosa.stft(roundtrip, n_fft=args.n_fft, hop_length=args.hop_length)
        source_mag = np.abs(source_stft).astype(np.float64)
        phase = np.exp(1j * np.angle(source_stft))
        source_log_mag = np.log(np.maximum(source_mag, 1e-8))

        source_log_mel_rt = np.log(
            np.maximum(
                librosa.feature.melspectrogram(
                    y=roundtrip,
                    sr=int(model.sample_rate),
                    n_fft=args.n_fft,
                    hop_length=args.hop_length,
                    power=2.0,
                    n_mels=args.n_mels,
                    fmin=float(args.fmin),
                    fmax=float(args.fmax),
                ).astype(np.float64),
                1e-12,
            )
        )

        frame_count = source_mag.shape[1]
        delta_log_mel = target_log_mel - source_log_mel
        delta_log_mel = align_columns(delta_log_mel, frame_count)
        core_mask_ratio = 1.0
        if args.core_mask:
            source_core_occupancy = build_frame_core_occupancy(
                np.transpose(np.exp(source_log_mel)),
                energy_threshold=float(args.core_mask_frame_threshold),
            )
            combined_core = build_combined_core_mask(
                source=SimpleNamespace(
                    utterance_distribution=source_distribution,
                    occupancy_distribution=np.asarray(source_core_occupancy, dtype=np.float64),
                ),
                target_prototype=target_distribution,
                target_occupancy=target_occupancy,
                core_energy_threshold=float(args.core_mask_energy_threshold),
                occupancy_threshold=float(args.core_mask_occupancy_threshold),
            )
            combined_core_bool = np.asarray(combined_core >= 0.5, dtype=bool)
            edited_core_occupancy = build_frame_core_occupancy(
                edited_frame_distributions,
                energy_threshold=float(args.core_mask_frame_threshold),
            )
            target_support = np.asarray(
                combined_core_bool
                & (
                    (edited_core_occupancy >= float(args.core_mask_frame_occupancy_threshold))
                    | (target_occupancy >= float(args.core_mask_occupancy_threshold))
                ),
                dtype=np.float64,
            )
            if float(np.sum(target_support)) <= 0.0:
                target_support = np.asarray(combined_core_bool, dtype=np.float64)
            offcore_scale = float(np.clip(args.core_mask_offcore_scale, 0.0, 1.0))
            mask_scale = target_support[:, None] + ((1.0 - target_support[:, None]) * offcore_scale)
            delta_log_mel = delta_log_mel * mask_scale
            core_mask_ratio = float(np.mean(target_support))
        if args.voiced_only:
            aligned_mask = align_mask(voiced_mask, frame_count).astype(np.float64)[None, :]
            delta_log_mel = delta_log_mel * aligned_mask

        mel_delta_limit = db_to_log_amplitude(float(args.delta_cap_db))
        delta_log_mel = np.clip(delta_log_mel * float(args.delta_scale), -mel_delta_limit, mel_delta_limit)

        proxy_target_log_mel = source_log_mel_rt + delta_log_mel
        proxy_target_mag = librosa.feature.inverse.mel_to_stft(
            np.exp(proxy_target_log_mel),
            sr=int(model.sample_rate),
            n_fft=args.n_fft,
            power=2.0,
            fmin=float(args.fmin),
            fmax=float(args.fmax),
        ).astype(np.float64)
        proxy_target_mag = align_columns(proxy_target_mag, frame_count)
        proxy_target_log_mag = np.log(np.maximum(proxy_target_mag, 1e-8))

        source_env_log = build_low_quefrency_envelope(source_log_mag, int(args.keep_coeffs))
        proxy_target_env_log = build_low_quefrency_envelope(proxy_target_log_mag, int(args.keep_coeffs))
        envelope_delta_log = proxy_target_env_log - source_env_log

        if args.voiced_only:
            envelope_delta_log = envelope_delta_log * align_mask(voiced_mask, frame_count).astype(np.float64)[None, :]

        gain_floor_ln = db_to_log_amplitude(float(args.gain_floor_db))
        gain_cap_ln = db_to_log_amplitude(float(args.gain_cap_db))
        envelope_delta_log = np.clip(envelope_delta_log, gain_floor_ln, gain_cap_ln)
        envelope_delta_log = smooth_time(envelope_delta_log, int(args.time_smooth_frames))
        applied_gain = np.exp(envelope_delta_log)

        processed_mag = source_mag * applied_gain
        processed_stft = processed_mag * phase
        processed_audio = librosa.istft(processed_stft, hop_length=args.hop_length, length=roundtrip.shape[0]).astype(np.float32)

        output_path = processed_dir / f"{record_id}__encodec_filter_bw{int(args.bandwidth)}.wav"
        torchaudio.save(str(output_path), torch.from_numpy(processed_audio).unsqueeze(0), sample_rate=int(model.sample_rate))

        updated = dict(row)
        updated["processed_audio"] = str(output_path)
        output_rows.append(updated)
        summary_rows.append(
            {
                "record_id": record_id,
                "rule_id": row["rule_id"],
                "target_npz": str(target_npz),
                "target_npz_sample_rate": str(target_sample_rate),
                "target_logmel_delta_l1_db": f"{float(np.mean(np.abs(delta_log_mel))):.6f}",
                "applied_envelope_gain_abs_mean_db": f"{float(np.mean(np.abs(log_amplitude_to_db(envelope_delta_log)))):.6f}",
                "applied_envelope_gain_abs_max_db": f"{float(np.max(np.abs(log_amplitude_to_db(envelope_delta_log)))):.6f}",
                "core_mask_ratio": f"{float(core_mask_ratio):.6f}",
            }
        )

    queue_path = output_dir / "listening_review_queue.csv"
    summary_csv = output_dir / "encodec_atrr_filter_probe_summary.csv"
    summary_md = output_dir / "ENCODEC_ATRR_FILTER_PROBE_SUMMARY.md"
    readme_path = output_dir / "README.md"
    write_rows(queue_path, output_rows, fieldnames)
    write_rows(summary_csv, summary_rows, list(summary_rows[0].keys()))
    summary_md.write_text(build_summary(summary_rows, args, device, int(model.sample_rate)), encoding="utf-8")
    readme_path.write_text(build_readme(args, output_dir, len(output_rows)), encoding="utf-8")
    print(f"Wrote {queue_path}")
    print(f"Wrote {summary_csv}")
    print(f"Wrote {summary_md}")
    print(f"Wrote {readme_path}")
    print(f"Rows: {len(output_rows)}")


if __name__ == "__main__":
    main()
