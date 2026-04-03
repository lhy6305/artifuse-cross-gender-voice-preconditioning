from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import torch
import torchaudio
from encodec import EncodecModel

from run_encodec_atrr_code_refit_probe import (
    DEFAULT_TARGET_DIR,
    DEFAULT_TEMPLATE_QUEUE,
    ROOT,
    build_target_index,
    build_weight_masks,
    choose_device,
    decode_wave,
    load_audio_mono,
    optimize_teacher_latent,
    read_rows,
    resolve_path,
    set_seed,
    write_rows,
)


DEFAULT_OUTPUT_DIR = (
    ROOT
    / "artifacts"
    / "diagnostics"
    / "encodec_atrr_code_hybrid_probe"
    / "v1_fixed8_q24_n8_tr4_ts30_rr4_rs30_rc080_rl020_rt010_tg050_w100_bw24"
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
    parser.add_argument("--seed", type=int, default=20260401)
    parser.add_argument("--n-fft", type=int, default=2048)
    parser.add_argument("--hop-length", type=int, default=256)
    parser.add_argument("--n-mels", type=int, default=80)
    parser.add_argument("--fmin", type=float, default=50.0)
    parser.add_argument("--fmax", type=float, default=8000.0)
    parser.add_argument("--delta-scale", type=float, default=0.20)
    parser.add_argument("--delta-cap-db", type=float, default=1.50)
    parser.add_argument("--quantizer-start", type=int, default=24)
    parser.add_argument("--quantizer-count", type=int, default=8)
    parser.add_argument("--teacher-rank", type=int, default=4)
    parser.add_argument("--teacher-steps", type=int, default=30)
    parser.add_argument("--teacher-lr", type=float, default=0.01)
    parser.add_argument("--teacher-init-scale", type=float, default=0.01)
    parser.add_argument("--teacher-latent-cap", type=float, default=0.20)
    parser.add_argument("--residual-rank", type=int, default=4)
    parser.add_argument("--residual-steps", type=int, default=30)
    parser.add_argument("--residual-lr", type=float, default=0.01)
    parser.add_argument("--residual-init-scale", type=float, default=0.01)
    parser.add_argument("--residual-cap", type=float, default=0.08)
    parser.add_argument("--lambda-latent-l2", type=float, default=0.20)
    parser.add_argument("--lambda-latent-time", type=float, default=0.10)
    parser.add_argument("--lambda-residual-l2", type=float, default=0.20)
    parser.add_argument("--lambda-residual-time", type=float, default=0.10)
    parser.add_argument("--lambda-teacher-gap", type=float, default=0.50)
    parser.add_argument("--lambda-wave-l1", type=float, default=1.00)
    parser.add_argument("--voiced-only", action="store_true")
    parser.add_argument("--core-mask", action="store_true")
    parser.add_argument("--core-mask-energy-threshold", type=float, default=0.60)
    parser.add_argument("--core-mask-occupancy-threshold", type=float, default=0.35)
    parser.add_argument("--core-mask-offcore-scale", type=float, default=0.00)
    parser.add_argument("--core-mask-frame-threshold", type=float, default=0.60)
    parser.add_argument("--core-mask-frame-occupancy-threshold", type=float, default=0.25)
    return parser.parse_args()


def build_readme(args: argparse.Namespace, output_dir: Path, rows: int, total_quantizers: int) -> str:
    rel_template = resolve_path(args.template_queue).relative_to(ROOT).as_posix()
    rel_target = resolve_path(args.target_dir).relative_to(ROOT).as_posix()
    rel_output = output_dir.relative_to(ROOT).as_posix()
    active_stop = min(int(args.quantizer_start) + int(args.quantizer_count), int(total_quantizers))
    return (
        "# Encodec ATRR Code Hybrid Probe v1\n\n"
        "- purpose: `hard native code scaffold plus bounded continuous residual correction`\n"
        f"- rows: `{rows}`\n"
        f"- bandwidth_kbps: `{args.bandwidth:.1f}`\n"
        f"- delta_scale: `{args.delta_scale:.2f}`\n"
        f"- delta_cap_db: `{args.delta_cap_db:.2f}`\n"
        f"- quantizer_range: `[{int(args.quantizer_start)}, {active_stop})`\n"
        f"- teacher_rank: `{int(args.teacher_rank)}`\n"
        f"- teacher_steps: `{int(args.teacher_steps)}`\n"
        f"- residual_rank: `{int(args.residual_rank)}`\n"
        f"- residual_steps: `{int(args.residual_steps)}`\n"
        f"- residual_cap: `{args.residual_cap:.3f}`\n"
        f"- lambda_residual_l2: `{args.lambda_residual_l2:.3f}`\n"
        f"- lambda_residual_time: `{args.lambda_residual_time:.3f}`\n"
        f"- lambda_teacher_gap: `{args.lambda_teacher_gap:.3f}`\n"
        f"- lambda_wave_l1: `{args.lambda_wave_l1:.3f}`\n"
        f"- voiced_only: `{bool(args.voiced_only)}`\n"
        f"- core_mask: `{bool(args.core_mask)}`\n"
        f"- core_mask_offcore_scale: `{args.core_mask_offcore_scale:.2f}`\n\n"
        "## Rebuild\n\n"
        "```powershell\n"
        ".\\python.exe .\\scripts\\run_encodec_atrr_code_hybrid_probe.py `\n"
        f"  --template-queue {rel_template} `\n"
        f"  --target-dir {rel_target} `\n"
        f"  --output-dir {rel_output} `\n"
        f"  --bandwidth {args.bandwidth:.1f} `\n"
        f"  --delta-scale {args.delta_scale:.2f} `\n"
        f"  --delta-cap-db {args.delta_cap_db:.2f} `\n"
        f"  --quantizer-start {int(args.quantizer_start)} `\n"
        f"  --quantizer-count {int(args.quantizer_count)} `\n"
        f"  --teacher-rank {int(args.teacher_rank)} `\n"
        f"  --teacher-steps {int(args.teacher_steps)} `\n"
        f"  --teacher-lr {args.teacher_lr:.4f} `\n"
        f"  --teacher-init-scale {args.teacher_init_scale:.4f} `\n"
        f"  --teacher-latent-cap {args.teacher_latent_cap:.3f} `\n"
        f"  --residual-rank {int(args.residual_rank)} `\n"
        f"  --residual-steps {int(args.residual_steps)} `\n"
        f"  --residual-lr {args.residual_lr:.4f} `\n"
        f"  --residual-init-scale {args.residual_init_scale:.4f} `\n"
        f"  --residual-cap {args.residual_cap:.3f} `\n"
        f"  --lambda-residual-l2 {args.lambda_residual_l2:.3f} `\n"
        f"  --lambda-residual-time {args.lambda_residual_time:.3f} `\n"
        f"  --lambda-teacher-gap {args.lambda_teacher_gap:.3f} `\n"
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


def build_summary(
    rows: list[dict[str, str]],
    args: argparse.Namespace,
    device: str,
    sample_rate: int,
    total_quantizers: int,
) -> str:
    def avg(field: str) -> float:
        return sum(float(row[field]) for row in rows) / max(len(rows), 1)

    active_stop = min(int(args.quantizer_start) + int(args.quantizer_count), int(total_quantizers))
    strongest = sorted(rows, key=lambda row: float(row["residual_correction_rms"]), reverse=True)[:3]
    closest = sorted(rows, key=lambda row: float(row["final_teacher_gap_rms"]))[:3]
    lines = [
        "# Encodec ATRR Code Hybrid Probe Summary v1",
        "",
        f"- rows: `{len(rows)}`",
        f"- sample_rate: `{sample_rate}`",
        f"- device: `{device}`",
        f"- bandwidth_kbps: `{args.bandwidth:.1f}`",
        f"- quantizer_range: `[{int(args.quantizer_start)}, {active_stop})`",
        f"- avg target_logmel_delta_l1_db: `{avg('target_logmel_delta_l1_db'):.4f}`",
        f"- avg scaffold_teacher_gap_rms: `{avg('scaffold_teacher_gap_rms'):.4f}`",
        f"- avg residual_correction_rms: `{avg('residual_correction_rms'):.4f}`",
        f"- avg final_teacher_gap_rms: `{avg('final_teacher_gap_rms'):.4f}`",
        f"- avg changed_code_ratio: `{avg('changed_code_ratio'):.4f}`",
        f"- avg teacher_final_mel_loss: `{avg('teacher_final_mel_loss'):.6f}`",
        f"- avg teacher_final_wave_l1: `{avg('teacher_final_wave_l1'):.6f}`",
        f"- avg final_mel_loss: `{avg('final_mel_loss'):.6f}`",
        f"- avg final_wave_l1: `{avg('final_wave_l1'):.6f}`",
        f"- avg core_mask_ratio: `{avg('core_mask_ratio'):.4f}`",
        "",
        "## Strongest Residual Rows",
        "",
    ]
    for row in strongest:
        lines.append(
            f"- `{row['record_id']}` | residual_rms=`{row['residual_correction_rms']}` | "
            f"final_gap_rms=`{row['final_teacher_gap_rms']}`"
        )
    lines.extend(["", "## Closest To Teacher After Correction", ""])
    for row in closest:
        lines.append(
            f"- `{row['record_id']}` | final_gap_rms=`{row['final_teacher_gap_rms']}` | "
            f"changed_code_ratio=`{row['changed_code_ratio']}`"
        )
    lines.append("")
    return "\n".join(lines)


def build_refit_scaffold(
    args: argparse.Namespace,
    model: EncodecModel,
    q_indices: torch.Tensor,
    base_layer_latents: list[torch.Tensor],
    inactive_latent: torch.Tensor,
    teacher_latent: torch.Tensor,
    active_quantizers: list[int],
    latent_time_gate: torch.Tensor,
) -> tuple[torch.Tensor, float]:
    gate_bool = latent_time_gate >= 0.5
    active_latent = torch.zeros_like(inactive_latent)
    residual_target = teacher_latent - inactive_latent
    changed_positions = 0.0
    total_positions = 0.0
    with torch.no_grad():
        for layer_idx in active_quantizers:
            layer = model.quantizer.vq.layers[layer_idx]
            proposed_indices = layer.encode(residual_target)
            base_indices = q_indices[layer_idx]
            base_layer = base_layer_latents[layer_idx]
            if args.voiced_only:
                effective_indices = torch.where(gate_bool.squeeze(1), proposed_indices, base_indices)
            else:
                effective_indices = proposed_indices
            effective_latent = layer.decode(effective_indices)
            active_latent = active_latent + effective_latent
            residual_target = residual_target - effective_latent
            changed_mask = effective_indices != base_indices
            if args.voiced_only:
                voiced_positions = gate_bool.squeeze(1)
                changed_positions += float((changed_mask & voiced_positions).sum().cpu())
                total_positions += float(voiced_positions.sum().cpu())
            else:
                changed_positions += float(changed_mask.sum().cpu())
                total_positions += float(changed_mask.numel())
    changed_code_ratio = changed_positions / max(total_positions, 1.0)
    return inactive_latent + active_latent, float(changed_code_ratio)


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
    total_quantizers = int(model.quantizer.n_q)
    quantizer_start = max(0, min(int(args.quantizer_start), total_quantizers - 1))
    quantizer_stop = max(quantizer_start + 1, min(quantizer_start + int(args.quantizer_count), total_quantizers))
    active_quantizers = list(range(quantizer_start, quantizer_stop))

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
        q_indices = codes.transpose(0, 1).detach()

        base_layer_latents: list[torch.Tensor] = []
        with torch.no_grad():
            for layer_idx, layer in enumerate(model.quantizer.vq.layers):
                layer_codes = q_indices[layer_idx]
                layer_latent = layer.decode(layer_codes).detach()
                base_layer_latents.append(layer_latent)
            base_latent = torch.zeros_like(base_layer_latents[0])
            inactive_latent = torch.zeros_like(base_layer_latents[0])
            for layer_idx, layer_latent in enumerate(base_layer_latents):
                base_latent = base_latent + layer_latent
                if layer_idx not in active_quantizers:
                    inactive_latent = inactive_latent + layer_latent
            base_wave = decode_wave(model, base_latent, scale, audio_length).detach()
            base_log_mel = torch.log(torch.clamp(mel_transform(base_wave.squeeze(1)), min=1e-12)).detach()

        with np.load(target_npz) as loaded:
            payload = {key: np.asarray(loaded[key]) for key in loaded.files}
        target_sample_rate = int(np.asarray(payload["sample_rate"]).reshape(-1)[0])

        delta_log_mel, weight_mask, core_mask_ratio, latent_time_gate_np = build_weight_masks(
            args=args,
            payload=payload,
            base_latent_frames=int(base_latent.shape[-1]),
            mel_frame_count=int(base_log_mel.shape[-1]),
        )
        target_delta_t = torch.from_numpy(delta_log_mel.astype(np.float32)).to(device)[None, :, :]
        weight_mask_t = torch.from_numpy(weight_mask.astype(np.float32)).to(device)[None, :, :]
        latent_time_gate = torch.from_numpy(latent_time_gate_np).to(device)[None, None, :]

        teacher_latent, teacher_final_mel_loss, teacher_final_wave_l1 = optimize_teacher_latent(
            args=args,
            model=model,
            mel_transform=mel_transform,
            base_latent=base_latent,
            base_wave=base_wave,
            base_log_mel=base_log_mel,
            scale=scale,
            audio_length=audio_length,
            target_delta_t=target_delta_t,
            weight_mask_t=weight_mask_t,
            latent_time_gate=latent_time_gate,
        )

        refit_latent, changed_code_ratio = build_refit_scaffold(
            args=args,
            model=model,
            q_indices=q_indices,
            base_layer_latents=base_layer_latents,
            inactive_latent=inactive_latent,
            teacher_latent=teacher_latent,
            active_quantizers=active_quantizers,
            latent_time_gate=latent_time_gate,
        )
        scaffold_teacher_gap = (refit_latent - teacher_latent).detach()

        channel_factors = torch.nn.Parameter(
            torch.randn((1, int(refit_latent.shape[1]), int(args.residual_rank)), dtype=refit_latent.dtype, device=device)
            * float(args.residual_init_scale)
        )
        time_factors = torch.nn.Parameter(
            torch.randn((1, int(args.residual_rank), int(refit_latent.shape[2])), dtype=refit_latent.dtype, device=device)
            * float(args.residual_init_scale)
        )
        optimizer = torch.optim.Adam([channel_factors, time_factors], lr=float(args.residual_lr))

        final_mel_loss = 0.0
        final_wave_l1 = 0.0
        residual_correction = torch.zeros_like(refit_latent)
        final_teacher_gap = scaffold_teacher_gap
        for _ in range(max(1, int(args.residual_steps))):
            optimizer.zero_grad(set_to_none=True)
            low_rank_delta = torch.matmul(channel_factors, time_factors)
            residual_correction = torch.tanh(low_rank_delta) * float(args.residual_cap)
            residual_correction = residual_correction * latent_time_gate
            edited_latent = refit_latent + residual_correction
            edited_wave = decode_wave(model, edited_latent, scale, audio_length)
            edited_log_mel = torch.log(torch.clamp(mel_transform(edited_wave.squeeze(1)), min=1e-12))
            edited_delta_mel = edited_log_mel - base_log_mel
            mel_error = edited_delta_mel - target_delta_t
            weighted_mel = (mel_error.square() * weight_mask_t).sum() / torch.clamp(weight_mask_t.sum(), min=1e-6)
            residual_l2 = torch.mean(residual_correction.square())
            residual_time = (
                torch.mean((residual_correction[:, :, 1:] - residual_correction[:, :, :-1]).square())
                if residual_correction.shape[-1] > 1
                else torch.tensor(0.0, device=device, dtype=residual_correction.dtype)
            )
            final_teacher_gap = edited_latent - teacher_latent
            teacher_gap_l2 = torch.mean(final_teacher_gap.square())
            wave_l1 = torch.mean(torch.abs(edited_wave - base_wave))
            loss = (
                weighted_mel
                + float(args.lambda_residual_l2) * residual_l2
                + float(args.lambda_residual_time) * residual_time
                + float(args.lambda_teacher_gap) * teacher_gap_l2
                + float(args.lambda_wave_l1) * wave_l1
            )
            loss.backward()
            optimizer.step()
            final_mel_loss = float(weighted_mel.detach().cpu())
            final_wave_l1 = float(wave_l1.detach().cpu())

        with torch.no_grad():
            low_rank_delta = torch.matmul(channel_factors, time_factors)
            residual_correction = (torch.tanh(low_rank_delta) * float(args.residual_cap) * latent_time_gate).detach()
            edited_latent = refit_latent + residual_correction
            final_teacher_gap = (edited_latent - teacher_latent).detach()
            edited_wave = decode_wave(model, edited_latent, scale, audio_length).detach()

        output_path = processed_dir / f"{record_id}__encodec_code_hybrid_bw{int(args.bandwidth)}.wav"
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
                "scaffold_teacher_gap_rms": f"{float(torch.sqrt(torch.mean(scaffold_teacher_gap.square())).cpu()):.6f}",
                "scaffold_teacher_gap_l1": f"{float(torch.mean(torch.abs(scaffold_teacher_gap)).cpu()):.6f}",
                "residual_correction_rms": f"{float(torch.sqrt(torch.mean(residual_correction.square())).cpu()):.6f}",
                "residual_correction_l1": f"{float(torch.mean(torch.abs(residual_correction)).cpu()):.6f}",
                "final_teacher_gap_rms": f"{float(torch.sqrt(torch.mean(final_teacher_gap.square())).cpu()):.6f}",
                "final_teacher_gap_l1": f"{float(torch.mean(torch.abs(final_teacher_gap)).cpu()):.6f}",
                "changed_code_ratio": f"{float(changed_code_ratio):.6f}",
                "teacher_final_mel_loss": f"{float(teacher_final_mel_loss):.6f}",
                "teacher_final_wave_l1": f"{float(teacher_final_wave_l1):.6f}",
                "final_mel_loss": f"{float(final_mel_loss):.6f}",
                "final_wave_l1": f"{float(final_wave_l1):.6f}",
                "core_mask_ratio": f"{float(core_mask_ratio):.6f}",
                "quantizer_start": str(quantizer_start),
                "quantizer_stop": str(quantizer_stop),
            }
        )

    queue_path = output_dir / "listening_review_queue.csv"
    summary_csv = output_dir / "encodec_atrr_code_hybrid_probe_summary.csv"
    summary_md = output_dir / "ENCODEC_ATRR_CODE_HYBRID_PROBE_SUMMARY.md"
    readme_path = output_dir / "README.md"
    write_rows(queue_path, output_rows, fieldnames)
    write_rows(summary_csv, summary_rows, list(summary_rows[0].keys()))
    summary_md.write_text(
        build_summary(summary_rows, args, device, int(model.sample_rate), total_quantizers),
        encoding="utf-8",
    )
    readme_path.write_text(
        build_readme(args, output_dir, len(output_rows), total_quantizers),
        encoding="utf-8",
    )
    print(f"Wrote {queue_path}")
    print(f"Wrote {summary_csv}")
    print(f"Wrote {summary_md}")
    print(f"Wrote {readme_path}")
    print(f"Rows: {len(output_rows)}")


if __name__ == "__main__":
    main()
