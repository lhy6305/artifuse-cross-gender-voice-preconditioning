from __future__ import annotations

import argparse
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch
import torchaudio

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
from encodec import EncodecModel


DEFAULT_OUTPUT_DIR = (
    ROOT
    / "artifacts"
    / "diagnostics"
    / "encodec_atrr_latent_structured_probe"
    / "v1_fixed8_tr4_ts30_tc020_tl020_tt010_cr2_cs20_cc008_cl025_ct012_cn040_w100_bw24"
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
    parser.add_argument("--target-rank", type=int, default=4)
    parser.add_argument("--target-steps", type=int, default=30)
    parser.add_argument("--target-lr", type=float, default=0.01)
    parser.add_argument("--target-init-scale", type=float, default=0.01)
    parser.add_argument("--target-cap", type=float, default=0.20)
    parser.add_argument("--lambda-target-l2", type=float, default=0.20)
    parser.add_argument("--lambda-target-time", type=float, default=0.10)
    parser.add_argument("--context-rank", type=int, default=2)
    parser.add_argument("--context-steps", type=int, default=20)
    parser.add_argument("--context-lr", type=float, default=0.01)
    parser.add_argument("--context-init-scale", type=float, default=0.01)
    parser.add_argument("--context-cap", type=float, default=0.08)
    parser.add_argument("--lambda-context-l2", type=float, default=0.25)
    parser.add_argument("--lambda-context-time", type=float, default=0.12)
    parser.add_argument("--lambda-context-null", type=float, default=0.40)
    parser.add_argument("--lambda-wave-l1", type=float, default=1.00)
    parser.add_argument("--voiced-only", action="store_true")
    parser.add_argument("--core-mask", action="store_true")
    parser.add_argument("--core-mask-energy-threshold", type=float, default=0.60)
    parser.add_argument("--core-mask-occupancy-threshold", type=float, default=0.35)
    parser.add_argument("--core-mask-offcore-scale", type=float, default=0.00)
    parser.add_argument("--core-mask-frame-threshold", type=float, default=0.60)
    parser.add_argument("--core-mask-frame-occupancy-threshold", type=float, default=0.25)
    return parser.parse_args()


def safe_weighted_mean(values: torch.Tensor, weights: torch.Tensor) -> torch.Tensor:
    return (values * weights).sum() / torch.clamp(weights.sum(), min=1e-6)


def build_weight_masks(
    args: argparse.Namespace,
    payload: dict[str, np.ndarray],
    *,
    mel_frame_count: int,
    latent_frame_count: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    source_log_mel = np.asarray(payload["source_log_mel"], dtype=np.float64)
    target_log_mel = np.asarray(payload["target_log_mel"], dtype=np.float64)
    voiced_mask = np.asarray(payload["voiced_mask"], dtype=np.float64)
    source_distribution = np.asarray(payload["source_distribution"], dtype=np.float64)
    target_distribution = np.asarray(payload["target_distribution"], dtype=np.float64)
    target_occupancy = np.asarray(payload["target_occupancy"], dtype=np.float64)
    edited_frame_distributions = np.asarray(payload["edited_frame_distributions"], dtype=np.float64)

    delta_log_mel = target_log_mel - source_log_mel
    delta_log_mel = align_columns(delta_log_mel, mel_frame_count)

    target_support = np.ones((delta_log_mel.shape[0],), dtype=np.float64)
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
        core_mask_ratio = float(np.mean(target_support))

    target_weight_mask = target_support[:, None]
    context_weight_mask = 1.0 - target_support[:, None]
    if args.voiced_only:
        voiced_weight = align_mask(voiced_mask, mel_frame_count).astype(np.float64)[None, :]
        target_weight_mask = target_weight_mask * voiced_weight
        context_weight_mask = context_weight_mask * voiced_weight
        latent_time_gate = align_mask(voiced_mask, latent_frame_count).astype(np.float32)
    else:
        latent_time_gate = np.ones((latent_frame_count,), dtype=np.float32)

    delta_limit = db_to_log_amplitude(float(args.delta_cap_db))
    delta_log_mel = np.clip(delta_log_mel * float(args.delta_scale), -delta_limit, delta_limit)
    return delta_log_mel, target_weight_mask, context_weight_mask, core_mask_ratio, latent_time_gate


def optimize_delta(
    *,
    rank: int,
    steps: int,
    lr: float,
    init_scale: float,
    cap: float,
    latent_time_gate: torch.Tensor,
    base_latent: torch.Tensor,
    base_wave: torch.Tensor,
    base_log_mel: torch.Tensor,
    scale: torch.Tensor | None,
    audio_length: int,
    mel_transform: torchaudio.transforms.MelSpectrogram,
    model: EncodecModel,
    primary_target: torch.Tensor,
    primary_weight: torch.Tensor,
    lambda_l2: float,
    lambda_time: float,
    lambda_wave_l1: float,
    secondary_target: torch.Tensor | None = None,
    secondary_weight: torch.Tensor | None = None,
    lambda_secondary: float = 0.0,
) -> tuple[torch.Tensor, float, float, float]:
    channel_factors = torch.nn.Parameter(
        torch.randn((1, int(base_latent.shape[1]), int(rank)), dtype=base_latent.dtype, device=base_latent.device)
        * float(init_scale)
    )
    time_factors = torch.nn.Parameter(
        torch.randn((1, int(rank), int(base_latent.shape[2])), dtype=base_latent.dtype, device=base_latent.device)
        * float(init_scale)
    )
    optimizer = torch.optim.Adam([channel_factors, time_factors], lr=float(lr))

    final_primary = 0.0
    final_secondary = 0.0
    final_wave_l1 = 0.0
    delta_latent = torch.zeros_like(base_latent)
    for _ in range(max(1, int(steps))):
        optimizer.zero_grad(set_to_none=True)
        low_rank_delta = torch.matmul(channel_factors, time_factors)
        delta_latent = torch.tanh(low_rank_delta) * float(cap)
        delta_latent = delta_latent * latent_time_gate
        edited_latent = base_latent + delta_latent
        edited_wave = decode_wave(model, edited_latent, scale, audio_length)
        edited_log_mel = torch.log(torch.clamp(mel_transform(edited_wave.squeeze(1)), min=1e-12))
        edited_delta_mel = edited_log_mel - base_log_mel

        primary_error = (edited_delta_mel - primary_target).square()
        primary_loss = safe_weighted_mean(primary_error, primary_weight)
        secondary_loss = torch.tensor(0.0, device=base_latent.device, dtype=base_latent.dtype)
        if secondary_target is not None and secondary_weight is not None and float(lambda_secondary) > 0.0:
            secondary_error = (edited_delta_mel - secondary_target).square()
            secondary_loss = safe_weighted_mean(secondary_error, secondary_weight)

        latent_l2 = torch.mean(delta_latent.square())
        latent_time = (
            torch.mean((delta_latent[:, :, 1:] - delta_latent[:, :, :-1]).square())
            if delta_latent.shape[-1] > 1
            else torch.tensor(0.0, device=base_latent.device, dtype=base_latent.dtype)
        )
        wave_l1 = torch.mean(torch.abs(edited_wave - base_wave))
        loss = (
            primary_loss
            + float(lambda_secondary) * secondary_loss
            + float(lambda_l2) * latent_l2
            + float(lambda_time) * latent_time
            + float(lambda_wave_l1) * wave_l1
        )
        loss.backward()
        optimizer.step()
        final_primary = float(primary_loss.detach().cpu())
        final_secondary = float(secondary_loss.detach().cpu())
        final_wave_l1 = float(wave_l1.detach().cpu())

    with torch.no_grad():
        low_rank_delta = torch.matmul(channel_factors, time_factors)
        delta_latent = (torch.tanh(low_rank_delta) * float(cap) * latent_time_gate).detach()
    return delta_latent, final_primary, final_secondary, final_wave_l1


def build_readme(args: argparse.Namespace, output_dir: Path, rows: int) -> str:
    rel_template = resolve_path(args.template_queue).relative_to(ROOT).as_posix()
    rel_target = resolve_path(args.target_dir).relative_to(ROOT).as_posix()
    rel_output = output_dir.relative_to(ROOT).as_posix()
    return (
        "# Encodec ATRR Latent Structured Probe v1\n\n"
        "- purpose: `two-stage latent-side edit with target mover plus context compensator`\n"
        f"- rows: `{rows}`\n"
        f"- bandwidth_kbps: `{args.bandwidth:.1f}`\n"
        f"- delta_scale: `{args.delta_scale:.2f}`\n"
        f"- delta_cap_db: `{args.delta_cap_db:.2f}`\n"
        f"- target_rank: `{args.target_rank}`\n"
        f"- target_steps: `{args.target_steps}`\n"
        f"- target_cap: `{args.target_cap:.3f}`\n"
        f"- context_rank: `{args.context_rank}`\n"
        f"- context_steps: `{args.context_steps}`\n"
        f"- context_cap: `{args.context_cap:.3f}`\n"
        f"- lambda_context_null: `{args.lambda_context_null:.3f}`\n"
        f"- lambda_wave_l1: `{args.lambda_wave_l1:.3f}`\n"
        f"- voiced_only: `{bool(args.voiced_only)}`\n"
        f"- core_mask: `{bool(args.core_mask)}`\n\n"
        "## Rebuild\n\n"
        "```powershell\n"
        ".\\python.exe .\\scripts\\run_encodec_atrr_latent_structured_probe.py `\n"
        f"  --template-queue {rel_template} `\n"
        f"  --target-dir {rel_target} `\n"
        f"  --output-dir {rel_output} `\n"
        f"  --bandwidth {args.bandwidth:.1f} `\n"
        f"  --delta-scale {args.delta_scale:.2f} `\n"
        f"  --delta-cap-db {args.delta_cap_db:.2f} `\n"
        f"  --target-rank {args.target_rank} `\n"
        f"  --target-steps {args.target_steps} `\n"
        f"  --target-lr {args.target_lr:.4f} `\n"
        f"  --target-init-scale {args.target_init_scale:.4f} `\n"
        f"  --target-cap {args.target_cap:.3f} `\n"
        f"  --lambda-target-l2 {args.lambda_target_l2:.3f} `\n"
        f"  --lambda-target-time {args.lambda_target_time:.3f} `\n"
        f"  --context-rank {args.context_rank} `\n"
        f"  --context-steps {args.context_steps} `\n"
        f"  --context-lr {args.context_lr:.4f} `\n"
        f"  --context-init-scale {args.context_init_scale:.4f} `\n"
        f"  --context-cap {args.context_cap:.3f} `\n"
        f"  --lambda-context-l2 {args.lambda_context_l2:.3f} `\n"
        f"  --lambda-context-time {args.lambda_context_time:.3f} `\n"
        f"  --lambda-context-null {args.lambda_context_null:.3f} `\n"
        f"  --lambda-wave-l1 {args.lambda_wave_l1:.3f}"
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

    strongest_target = sorted(rows, key=lambda row: float(row["target_delta_rms"]), reverse=True)[:3]
    strongest_context = sorted(rows, key=lambda row: float(row["context_delta_rms"]), reverse=True)[:3]
    lines = [
        "# Encodec ATRR Latent Structured Probe Summary v1",
        "",
        f"- rows: `{len(rows)}`",
        f"- sample_rate: `{sample_rate}`",
        f"- device: `{device}`",
        f"- bandwidth_kbps: `{args.bandwidth:.1f}`",
        f"- avg target_logmel_delta_l1_db: `{avg('target_logmel_delta_l1_db'):.4f}`",
        f"- avg target_delta_rms: `{avg('target_delta_rms'):.4f}`",
        f"- avg context_delta_rms: `{avg('context_delta_rms'):.4f}`",
        f"- avg total_delta_rms: `{avg('total_delta_rms'):.4f}`",
        f"- avg target_core_mel_loss: `{avg('target_core_mel_loss'):.6f}`",
        f"- avg target_offcore_energy: `{avg('target_offcore_energy'):.6f}`",
        f"- avg final_core_mel_loss: `{avg('final_core_mel_loss'):.6f}`",
        f"- avg final_offcore_energy: `{avg('final_offcore_energy'):.6f}`",
        f"- avg final_wave_l1: `{avg('final_wave_l1'):.6f}`",
        f"- avg core_mask_ratio: `{avg('core_mask_ratio'):.4f}`",
        "",
        "## Strongest Target Movers",
        "",
    ]
    for row in strongest_target:
        lines.append(
            f"- `{row['record_id']}` | target_rms=`{row['target_delta_rms']}` | "
            f"core_loss=`{row['final_core_mel_loss']}`"
        )
    lines.extend(["", "## Strongest Context Compensators", ""])
    for row in strongest_context:
        lines.append(
            f"- `{row['record_id']}` | context_rms=`{row['context_delta_rms']}` | "
            f"offcore_energy=`{row['final_offcore_energy']}`"
        )
    lines.append("")
    return "\n".join(lines)


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

        delta_log_mel, target_weight_mask, context_weight_mask, core_mask_ratio, latent_time_gate_np = build_weight_masks(
            args=args,
            payload=payload,
            mel_frame_count=int(base_log_mel.shape[-1]),
            latent_frame_count=int(base_latent.shape[-1]),
        )
        target_delta_t = torch.from_numpy(delta_log_mel.astype(np.float32)).to(device)[None, :, :]
        target_weight_t = torch.from_numpy(target_weight_mask.astype(np.float32)).to(device)[None, :, :]
        context_weight_t = torch.from_numpy(context_weight_mask.astype(np.float32)).to(device)[None, :, :]
        latent_time_gate = torch.from_numpy(latent_time_gate_np).to(device)[None, None, :]
        zero_delta_t = torch.zeros_like(target_delta_t)

        target_delta, target_core_mel_loss, target_offcore_energy, target_wave_l1 = optimize_delta(
            rank=int(args.target_rank),
            steps=int(args.target_steps),
            lr=float(args.target_lr),
            init_scale=float(args.target_init_scale),
            cap=float(args.target_cap),
            latent_time_gate=latent_time_gate,
            base_latent=base_latent,
            base_wave=base_wave,
            base_log_mel=base_log_mel,
            scale=scale,
            audio_length=audio_length,
            mel_transform=mel_transform,
            model=model,
            primary_target=target_delta_t,
            primary_weight=target_weight_t,
            lambda_l2=float(args.lambda_target_l2),
            lambda_time=float(args.lambda_target_time),
            lambda_wave_l1=float(args.lambda_wave_l1),
            secondary_target=zero_delta_t,
            secondary_weight=context_weight_t,
            lambda_secondary=float(args.lambda_context_null),
        )

        target_latent = (base_latent + target_delta).detach()
        context_delta, final_core_mel_loss, final_offcore_energy, final_wave_l1 = optimize_delta(
            rank=int(args.context_rank),
            steps=int(args.context_steps),
            lr=float(args.context_lr),
            init_scale=float(args.context_init_scale),
            cap=float(args.context_cap),
            latent_time_gate=latent_time_gate,
            base_latent=target_latent,
            base_wave=base_wave,
            base_log_mel=base_log_mel,
            scale=scale,
            audio_length=audio_length,
            mel_transform=mel_transform,
            model=model,
            primary_target=target_delta_t,
            primary_weight=target_weight_t,
            lambda_l2=float(args.lambda_context_l2),
            lambda_time=float(args.lambda_context_time),
            lambda_wave_l1=float(args.lambda_wave_l1),
            secondary_target=zero_delta_t,
            secondary_weight=context_weight_t,
            lambda_secondary=float(args.lambda_context_null),
        )

        with torch.no_grad():
            edited_latent = target_latent + context_delta
            edited_wave = decode_wave(model, edited_latent, scale, audio_length).detach()

        output_path = processed_dir / f"{record_id}__encodec_latent_structured_bw{int(args.bandwidth)}.wav"
        torchaudio.save(str(output_path), edited_wave.squeeze(0).cpu(), sample_rate=int(model.sample_rate))

        total_delta = target_delta + context_delta
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
                "target_delta_rms": f"{float(torch.sqrt(torch.mean(target_delta.square())).cpu()):.6f}",
                "target_delta_abs_mean": f"{float(torch.mean(torch.abs(target_delta)).cpu()):.6f}",
                "context_delta_rms": f"{float(torch.sqrt(torch.mean(context_delta.square())).cpu()):.6f}",
                "context_delta_abs_mean": f"{float(torch.mean(torch.abs(context_delta)).cpu()):.6f}",
                "total_delta_rms": f"{float(torch.sqrt(torch.mean(total_delta.square())).cpu()):.6f}",
                "total_delta_abs_mean": f"{float(torch.mean(torch.abs(total_delta)).cpu()):.6f}",
                "target_core_mel_loss": f"{float(target_core_mel_loss):.6f}",
                "target_offcore_energy": f"{float(target_offcore_energy):.6f}",
                "target_wave_l1": f"{float(target_wave_l1):.6f}",
                "final_core_mel_loss": f"{float(final_core_mel_loss):.6f}",
                "final_offcore_energy": f"{float(final_offcore_energy):.6f}",
                "final_wave_l1": f"{float(final_wave_l1):.6f}",
                "core_mask_ratio": f"{float(core_mask_ratio):.6f}",
            }
        )

    queue_path = output_dir / "listening_review_queue.csv"
    summary_csv = output_dir / "encodec_atrr_latent_structured_probe_summary.csv"
    summary_md = output_dir / "ENCODEC_ATRR_LATENT_STRUCTURED_PROBE_SUMMARY.md"
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
