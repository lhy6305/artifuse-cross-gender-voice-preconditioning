from __future__ import annotations

import argparse
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch
import torchaudio
from encodec import EncodecModel

from run_encodec_atrr_latent_probe import (
    DEFAULT_TARGET_DIR,
    DEFAULT_TEMPLATE_QUEUE,
    ROOT,
    align_columns,
    align_mask,
    build_frame_core_occupancy,
    build_target_index,
    choose_device,
    db_to_log_amplitude,
    decode_wave,
    load_audio_mono,
    read_rows,
    resolve_path,
    set_seed,
    write_rows,
)
from simulate_targetward_resonance_residual import build_combined_core_mask


DEFAULT_OUTPUT_DIR = (
    ROOT
    / "artifacts"
    / "diagnostics"
    / "encodec_atrr_latent_support_probe"
    / "v1_fixed8_rank4_s020_d15_fb065_oa050_sf015_sp075_nf020_bw24"
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
    parser.add_argument("--seed", type=int, default=20260402)
    parser.add_argument("--n-fft", type=int, default=2048)
    parser.add_argument("--hop-length", type=int, default=256)
    parser.add_argument("--n-mels", type=int, default=80)
    parser.add_argument("--fmin", type=float, default=50.0)
    parser.add_argument("--fmax", type=float, default=8000.0)
    parser.add_argument("--delta-scale", type=float, default=0.20)
    parser.add_argument("--delta-cap-db", type=float, default=1.50)
    parser.add_argument("--rank", type=int, default=4)
    parser.add_argument("--steps", type=int, default=30)
    parser.add_argument("--lr", type=float, default=0.01)
    parser.add_argument("--init-scale", type=float, default=0.01)
    parser.add_argument("--latent-cap", type=float, default=0.20)
    parser.add_argument("--lambda-latent-l2", type=float, default=0.20)
    parser.add_argument("--lambda-latent-time", type=float, default=0.10)
    parser.add_argument("--lambda-wave-l1", type=float, default=1.00)
    parser.add_argument("--lambda-null", type=float, default=0.20)
    parser.add_argument("--frame-blend", type=float, default=0.65)
    parser.add_argument("--occupancy-anchor", type=float, default=0.50)
    parser.add_argument("--support-floor", type=float, default=0.15)
    parser.add_argument("--support-power", type=float, default=0.75)
    parser.add_argument("--null-floor", type=float, default=0.20)
    parser.add_argument("--offcore-fit-scale", type=float, default=0.00)
    parser.add_argument("--voiced-only", action="store_true")
    parser.add_argument("--core-mask", action="store_true")
    parser.add_argument("--core-mask-energy-threshold", type=float, default=0.60)
    parser.add_argument("--core-mask-occupancy-threshold", type=float, default=0.35)
    parser.add_argument("--core-mask-frame-threshold", type=float, default=0.60)
    parser.add_argument("--core-mask-frame-occupancy-threshold", type=float, default=0.25)
    return parser.parse_args()


def safe_weighted_mean(values: torch.Tensor, weights: torch.Tensor) -> torch.Tensor:
    return (values * weights).sum() / torch.clamp(weights.sum(), min=1e-6)


def normalize_columns(matrix: np.ndarray) -> np.ndarray:
    source = np.asarray(matrix, dtype=np.float64)
    if source.ndim != 2:
        raise ValueError("Expected a 2D matrix.")
    denom = np.max(source, axis=0, keepdims=True)
    denom = np.maximum(denom, 1e-12)
    return np.asarray(source / denom, dtype=np.float64)


def build_soft_masks(
    args: argparse.Namespace,
    payload: dict[str, np.ndarray],
    *,
    mel_frame_count: int,
    latent_frame_count: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float, float, np.ndarray]:
    source_log_mel = np.asarray(payload["source_log_mel"], dtype=np.float64)
    target_log_mel = np.asarray(payload["target_log_mel"], dtype=np.float64)
    voiced_mask = np.asarray(payload["voiced_mask"], dtype=np.float64)
    source_distribution = np.asarray(payload["source_distribution"], dtype=np.float64)
    target_distribution = np.asarray(payload["target_distribution"], dtype=np.float64)
    target_occupancy = np.asarray(payload["target_occupancy"], dtype=np.float64)
    edited_frame_distributions = np.asarray(payload["edited_frame_distributions"], dtype=np.float64)

    delta_log_mel = align_columns(target_log_mel - source_log_mel, mel_frame_count)

    fit_active = np.ones((delta_log_mel.shape[0],), dtype=np.float64)
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
        fit_active = np.asarray(
            combined_core_bool
            & (
                (edited_core_occupancy >= float(args.core_mask_frame_occupancy_threshold))
                | (target_occupancy >= float(args.core_mask_occupancy_threshold))
            ),
            dtype=np.float64,
        )
        if float(np.sum(fit_active)) <= 0.0:
            fit_active = np.asarray(combined_core_bool, dtype=np.float64)
        core_mask_ratio = float(np.mean(fit_active))

    aligned_frame_dist = align_columns(np.transpose(edited_frame_distributions), mel_frame_count)
    aligned_frame_dist = np.clip(aligned_frame_dist, 0.0, None)
    frame_support = normalize_columns(aligned_frame_dist)

    delta_support = normalize_columns(np.abs(delta_log_mel))
    blend = float(np.clip(args.frame_blend, 0.0, 1.0))
    support_map = (blend * frame_support) + ((1.0 - blend) * delta_support)

    occupancy_anchor = np.maximum(
        build_frame_core_occupancy(
            edited_frame_distributions,
            energy_threshold=float(args.core_mask_frame_threshold),
        ),
        np.asarray(target_occupancy, dtype=np.float64),
    )
    occupancy_anchor = np.clip(occupancy_anchor, 0.0, 1.0)[:, None]
    support_map = np.maximum(
        support_map,
        occupancy_anchor * float(np.clip(args.occupancy_anchor, 0.0, 1.0)),
    )
    support_map = np.clip(support_map, 0.0, 1.0)
    support_map = np.power(support_map, max(float(args.support_power), 1e-6))

    support_floor = float(np.clip(args.support_floor, 0.0, 1.0))
    offcore_fit_scale = float(np.clip(args.offcore_fit_scale, 0.0, 1.0))
    fit_weight = (
        fit_active[:, None] * (support_floor + ((1.0 - support_floor) * support_map))
        + ((1.0 - fit_active[:, None]) * offcore_fit_scale)
    )

    if args.voiced_only:
        voiced_weight = align_mask(voiced_mask, mel_frame_count).astype(np.float64)[None, :]
        fit_weight = fit_weight * voiced_weight
        latent_time_gate = align_mask(voiced_mask, latent_frame_count).astype(np.float32)
        total_weight = np.broadcast_to(voiced_weight, fit_weight.shape)
    else:
        latent_time_gate = np.ones((latent_frame_count,), dtype=np.float32)
        total_weight = np.ones_like(fit_weight, dtype=np.float64)

    null_floor = float(np.clip(args.null_floor, 0.0, 1.0))
    null_weight = np.clip(total_weight - fit_weight, 0.0, None)
    if null_floor > 0.0:
        null_weight = np.maximum(null_weight, null_floor * total_weight)
        null_weight = np.clip(null_weight - fit_weight, 0.0, None)
    fit_weight_mean = float(np.sum(fit_weight) / max(np.sum(total_weight), 1e-12))

    delta_limit = db_to_log_amplitude(float(args.delta_cap_db))
    delta_log_mel = np.clip(delta_log_mel * float(args.delta_scale), -delta_limit, delta_limit)
    return delta_log_mel, fit_weight, null_weight, core_mask_ratio, fit_weight_mean, latent_time_gate


def build_readme(args: argparse.Namespace, output_dir: Path, rows: int) -> str:
    rel_template = resolve_path(args.template_queue).relative_to(ROOT).as_posix()
    rel_target = resolve_path(args.target_dir).relative_to(ROOT).as_posix()
    rel_output = output_dir.relative_to(ROOT).as_posix()
    return (
        "# Encodec ATRR Latent Support Probe v1\n\n"
        "- purpose: `single-stage latent edit with soft time-frequency support and off-support null regularization`\n"
        f"- rows: `{rows}`\n"
        f"- bandwidth_kbps: `{args.bandwidth:.1f}`\n"
        f"- delta_scale: `{args.delta_scale:.2f}`\n"
        f"- delta_cap_db: `{args.delta_cap_db:.2f}`\n"
        f"- rank: `{args.rank}`\n"
        f"- steps: `{args.steps}`\n"
        f"- frame_blend: `{args.frame_blend:.2f}`\n"
        f"- occupancy_anchor: `{args.occupancy_anchor:.2f}`\n"
        f"- support_floor: `{args.support_floor:.2f}`\n"
        f"- support_power: `{args.support_power:.2f}`\n"
        f"- null_floor: `{args.null_floor:.2f}`\n"
        f"- lambda_null: `{args.lambda_null:.3f}`\n\n"
        "## Rebuild\n\n"
        "```powershell\n"
        ".\\python.exe .\\scripts\\run_encodec_atrr_latent_support_probe.py `\n"
        f"  --template-queue {rel_template} `\n"
        f"  --target-dir {rel_target} `\n"
        f"  --output-dir {rel_output} `\n"
        f"  --bandwidth {args.bandwidth:.1f} `\n"
        f"  --delta-scale {args.delta_scale:.2f} `\n"
        f"  --delta-cap-db {args.delta_cap_db:.2f} `\n"
        f"  --rank {args.rank} `\n"
        f"  --steps {args.steps} `\n"
        f"  --lr {args.lr:.4f} `\n"
        f"  --init-scale {args.init_scale:.4f} `\n"
        f"  --latent-cap {args.latent_cap:.3f} `\n"
        f"  --lambda-latent-l2 {args.lambda_latent_l2:.3f} `\n"
        f"  --lambda-latent-time {args.lambda_latent_time:.3f} `\n"
        f"  --lambda-wave-l1 {args.lambda_wave_l1:.3f} `\n"
        f"  --lambda-null {args.lambda_null:.3f} `\n"
        f"  --frame-blend {args.frame_blend:.2f} `\n"
        f"  --occupancy-anchor {args.occupancy_anchor:.2f} `\n"
        f"  --support-floor {args.support_floor:.2f} `\n"
        f"  --support-power {args.support_power:.2f} `\n"
        f"  --null-floor {args.null_floor:.2f}"
        + (" `\n  --voiced-only" if args.voiced_only else "")
        + (" `\n  --core-mask" if args.core_mask else "")
        + "\n```\n"
    )


def build_summary(rows: list[dict[str, str]], args: argparse.Namespace, device: str, sample_rate: int) -> str:
    def avg(field: str) -> float:
        return sum(float(row[field]) for row in rows) / max(len(rows), 1)

    strongest = sorted(rows, key=lambda row: float(row["latent_delta_rms"]), reverse=True)[:3]
    widest_support = sorted(rows, key=lambda row: float(row["fit_weight_mean"]), reverse=True)[:3]
    lines = [
        "# Encodec ATRR Latent Support Probe Summary v1",
        "",
        f"- rows: `{len(rows)}`",
        f"- sample_rate: `{sample_rate}`",
        f"- device: `{device}`",
        f"- bandwidth_kbps: `{args.bandwidth:.1f}`",
        f"- avg target_logmel_delta_l1_db: `{avg('target_logmel_delta_l1_db'):.4f}`",
        f"- avg latent_delta_rms: `{avg('latent_delta_rms'):.4f}`",
        f"- avg latent_delta_abs_mean: `{avg('latent_delta_abs_mean'):.4f}`",
        f"- avg final_fit_loss: `{avg('final_fit_loss'):.6f}`",
        f"- avg final_null_loss: `{avg('final_null_loss'):.6f}`",
        f"- avg final_wave_l1: `{avg('final_wave_l1'):.6f}`",
        f"- avg core_mask_ratio: `{avg('core_mask_ratio'):.4f}`",
        f"- avg fit_weight_mean: `{avg('fit_weight_mean'):.4f}`",
        f"- avg null_weight_mean: `{avg('null_weight_mean'):.4f}`",
        "",
        "## Strongest Latent Rows",
        "",
    ]
    for row in strongest:
        lines.append(
            f"- `{row['record_id']}` | latent_rms=`{row['latent_delta_rms']}` | "
            f"fit_loss=`{row['final_fit_loss']}`"
        )
    lines.extend(["", "## Widest Support Rows", ""])
    for row in widest_support:
        lines.append(
            f"- `{row['record_id']}` | fit_weight_mean=`{row['fit_weight_mean']}` | "
            f"null_weight_mean=`{row['null_weight_mean']}`"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    template_queue = resolve_path(args.template_queue)
    target_dir = resolve_path(args.target_dir)
    output_dir = resolve_path(args.output_dir)
    repository = resolve_path(args.repository) if args.repository else None
    device = choose_device(args.device)
    set_seed(args.seed)

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

    mel_transform = torchaudio.transforms.MelSpectrogram(
        sample_rate=int(model.sample_rate),
        n_fft=args.n_fft,
        hop_length=args.hop_length,
        n_mels=args.n_mels,
        f_min=float(args.fmin),
        f_max=float(args.fmax),
        power=2.0,
    ).to(device)

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
        audio_length = int(audio.shape[-1])

        with torch.no_grad():
            encoded_frames = model.encode(audio.unsqueeze(0))
        if len(encoded_frames) != 1:
            raise ValueError("This probe expects a single Encodec frame per row.")
        codes, scale = encoded_frames[0]
        with torch.no_grad():
            base_latent = model.quantizer.decode(codes.transpose(0, 1)).detach()
            base_wave = decode_wave(model, base_latent, scale, audio_length).detach()
            base_log_mel = torch.log(torch.clamp(mel_transform(base_wave.squeeze(1)), min=1e-12)).detach()

        with np.load(target_npz) as loaded:
            payload = {key: np.asarray(loaded[key]) for key in loaded.files}
        target_sample_rate = int(np.asarray(payload["sample_rate"]).reshape(-1)[0])

        delta_log_mel, fit_weight, null_weight, core_mask_ratio, fit_weight_mean, latent_time_gate_np = build_soft_masks(
            args=args,
            payload=payload,
            mel_frame_count=int(base_log_mel.shape[-1]),
            latent_frame_count=int(base_latent.shape[-1]),
        )

        target_delta_t = torch.from_numpy(delta_log_mel.astype(np.float32)).to(device)[None, :, :]
        fit_weight_t = torch.from_numpy(fit_weight.astype(np.float32)).to(device)[None, :, :]
        null_weight_t = torch.from_numpy(null_weight.astype(np.float32)).to(device)[None, :, :]
        latent_time_gate = torch.from_numpy(latent_time_gate_np).to(device)[None, None, :]

        channel_factors = torch.nn.Parameter(
            torch.randn((1, int(base_latent.shape[1]), int(args.rank)), dtype=base_latent.dtype, device=device)
            * float(args.init_scale)
        )
        time_factors = torch.nn.Parameter(
            torch.randn((1, int(args.rank), int(base_latent.shape[2])), dtype=base_latent.dtype, device=device)
            * float(args.init_scale)
        )
        optimizer = torch.optim.Adam([channel_factors, time_factors], lr=float(args.lr))

        final_fit_loss = 0.0
        final_null_loss = 0.0
        final_wave_l1 = 0.0
        delta_latent = torch.zeros_like(base_latent)
        edited_wave = base_wave
        for _ in range(max(1, int(args.steps))):
            optimizer.zero_grad(set_to_none=True)
            low_rank_delta = torch.matmul(channel_factors, time_factors)
            delta_latent = torch.tanh(low_rank_delta) * float(args.latent_cap)
            delta_latent = delta_latent * latent_time_gate
            edited_latent = base_latent + delta_latent
            edited_wave = decode_wave(model, edited_latent, scale, audio_length)
            edited_log_mel = torch.log(torch.clamp(mel_transform(edited_wave.squeeze(1)), min=1e-12))
            edited_delta_mel = edited_log_mel - base_log_mel

            fit_error = (edited_delta_mel - target_delta_t).square()
            fit_loss = safe_weighted_mean(fit_error, fit_weight_t)
            null_loss = safe_weighted_mean(edited_delta_mel.square(), null_weight_t)
            latent_l2 = torch.mean(delta_latent.square())
            latent_time = (
                torch.mean((delta_latent[:, :, 1:] - delta_latent[:, :, :-1]).square())
                if delta_latent.shape[-1] > 1
                else torch.tensor(0.0, device=device, dtype=delta_latent.dtype)
            )
            wave_l1 = torch.mean(torch.abs(edited_wave - base_wave))
            loss = (
                fit_loss
                + (float(args.lambda_null) * null_loss)
                + (float(args.lambda_latent_l2) * latent_l2)
                + (float(args.lambda_latent_time) * latent_time)
                + (float(args.lambda_wave_l1) * wave_l1)
            )
            loss.backward()
            optimizer.step()
            final_fit_loss = float(fit_loss.detach().cpu())
            final_null_loss = float(null_loss.detach().cpu())
            final_wave_l1 = float(wave_l1.detach().cpu())

        with torch.no_grad():
            low_rank_delta = torch.matmul(channel_factors, time_factors)
            delta_latent = (torch.tanh(low_rank_delta) * float(args.latent_cap) * latent_time_gate).detach()
            edited_latent = base_latent + delta_latent
            edited_wave = decode_wave(model, edited_latent, scale, audio_length).detach()

        output_path = processed_dir / f"{record_id}__encodec_latent_support_bw{int(args.bandwidth)}.wav"
        torchaudio.save(str(output_path), edited_wave.squeeze(0).cpu(), sample_rate=int(model.sample_rate))

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
                "latent_delta_rms": f"{float(torch.sqrt(torch.mean(delta_latent.square())).cpu()):.6f}",
                "latent_delta_abs_mean": f"{float(torch.mean(torch.abs(delta_latent)).cpu()):.6f}",
                "final_fit_loss": f"{float(final_fit_loss):.6f}",
                "final_null_loss": f"{float(final_null_loss):.6f}",
                "final_wave_l1": f"{float(final_wave_l1):.6f}",
                "core_mask_ratio": f"{float(core_mask_ratio):.6f}",
                "fit_weight_mean": f"{float(fit_weight_mean):.6f}",
                "null_weight_mean": f"{float(np.mean(null_weight)):.6f}",
            }
        )

    queue_path = output_dir / "listening_review_queue.csv"
    summary_csv = output_dir / "encodec_atrr_latent_support_probe_summary.csv"
    summary_md = output_dir / "ENCODEC_ATRR_LATENT_SUPPORT_PROBE_SUMMARY.md"
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
