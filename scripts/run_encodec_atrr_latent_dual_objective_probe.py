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
    / "encodec_atrr_latent_dual_objective_probe"
    / "v1_fixed8_rank4_s020_d15_fk040_uk015_ea025_ds020_gf010_bw24"
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
    parser.add_argument("--distribution-scale", type=float, default=0.20)
    parser.add_argument("--rank", type=int, default=4)
    parser.add_argument("--steps", type=int, default=30)
    parser.add_argument("--lr", type=float, default=0.01)
    parser.add_argument("--init-scale", type=float, default=0.01)
    parser.add_argument("--latent-cap", type=float, default=0.20)
    parser.add_argument("--lambda-latent-l2", type=float, default=0.20)
    parser.add_argument("--lambda-latent-time", type=float, default=0.10)
    parser.add_argument("--lambda-wave-l1", type=float, default=1.00)
    parser.add_argument("--lambda-frame-kl", type=float, default=0.40)
    parser.add_argument("--lambda-utt-kl", type=float, default=0.15)
    parser.add_argument("--lambda-energy-anchor", type=float, default=0.25)
    parser.add_argument("--gap-floor", type=float, default=0.10)
    parser.add_argument("--gap-power", type=float, default=1.00)
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


def normalize_columns_np(matrix: np.ndarray) -> np.ndarray:
    source = np.asarray(matrix, dtype=np.float64)
    if source.ndim != 2:
        raise ValueError("Expected a 2D matrix.")
    denom = np.sum(source, axis=0, keepdims=True)
    denom = np.maximum(denom, 1e-12)
    return np.asarray(source / denom, dtype=np.float64)


def build_dual_targets(
    args: argparse.Namespace,
    payload: dict[str, np.ndarray],
    *,
    mel_frame_count: int,
    latent_frame_count: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, float, float]:
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

    delta_limit = db_to_log_amplitude(float(args.delta_cap_db))
    delta_log_mel = np.clip(delta_log_mel * float(args.delta_scale), -delta_limit, delta_limit)
    delta_weight = fit_active[:, None] + ((1.0 - fit_active[:, None]) * float(args.core_mask_offcore_scale))

    source_power = np.exp(source_log_mel)
    source_frame_distribution = normalize_columns_np(align_columns(source_power, mel_frame_count))
    target_frame_distribution = normalize_columns_np(align_columns(np.transpose(edited_frame_distributions), mel_frame_count))

    distribution_scale = float(np.clip(args.distribution_scale, 0.0, 1.0))
    target_frame_distribution = np.clip(
        source_frame_distribution + (distribution_scale * (target_frame_distribution - source_frame_distribution)),
        1e-12,
        None,
    )
    target_frame_distribution = normalize_columns_np(target_frame_distribution)

    target_utterance_distribution = np.clip(
        source_distribution + (distribution_scale * (target_distribution - source_distribution)),
        1e-12,
        None,
    )
    target_utterance_distribution = target_utterance_distribution / np.sum(target_utterance_distribution)

    frame_gap = 0.5 * np.sum(np.abs(target_frame_distribution - source_frame_distribution), axis=0)
    frame_gap = np.clip(frame_gap, 0.0, 1.0)
    frame_gap = np.power(frame_gap, max(float(args.gap_power), 1e-6))
    frame_gap = float(np.clip(args.gap_floor, 0.0, 1.0)) + ((1.0 - float(np.clip(args.gap_floor, 0.0, 1.0))) * frame_gap)
    # The masked delta-fit lives in mel-bin space, while the distribution
    # objectives are frame-level. Only the gap term should weight frames here.
    distribution_frame_weight = frame_gap

    source_log_energy = np.log(np.maximum(np.sum(align_columns(source_power, mel_frame_count), axis=0), 1e-12))
    if args.voiced_only:
        voiced_frame = align_mask(voiced_mask, mel_frame_count).astype(np.float64)
        delta_weight = delta_weight * voiced_frame[None, :]
        distribution_frame_weight = distribution_frame_weight * voiced_frame
        latent_time_gate = align_mask(voiced_mask, latent_frame_count).astype(np.float32)
    else:
        latent_time_gate = np.ones((latent_frame_count,), dtype=np.float32)

    if float(np.sum(distribution_frame_weight)) <= 0.0:
        distribution_frame_weight = np.ones((mel_frame_count,), dtype=np.float64)

    distribution_weight_mean = float(np.mean(distribution_frame_weight))
    return (
        delta_log_mel,
        delta_weight,
        target_frame_distribution,
        target_utterance_distribution,
        source_log_energy,
        distribution_frame_weight,
        latent_time_gate,
        core_mask_ratio,
        distribution_weight_mean,
    )


def build_readme(args: argparse.Namespace, output_dir: Path, rows: int) -> str:
    rel_template = resolve_path(args.template_queue).relative_to(ROOT).as_posix()
    rel_target = resolve_path(args.target_dir).relative_to(ROOT).as_posix()
    rel_output = output_dir.relative_to(ROOT).as_posix()
    return (
        "# Encodec ATRR Latent Dual Objective Probe v1\n\n"
        "- purpose: `single latent edit with masked delta-fit primary loss plus gap-adaptive distribution objectives`\n"
        f"- rows: `{rows}`\n"
        f"- bandwidth_kbps: `{args.bandwidth:.1f}`\n"
        f"- delta_scale: `{args.delta_scale:.2f}`\n"
        f"- delta_cap_db: `{args.delta_cap_db:.2f}`\n"
        f"- distribution_scale: `{args.distribution_scale:.2f}`\n"
        f"- rank: `{args.rank}`\n"
        f"- steps: `{args.steps}`\n"
        f"- lambda_frame_kl: `{args.lambda_frame_kl:.3f}`\n"
        f"- lambda_utt_kl: `{args.lambda_utt_kl:.3f}`\n"
        f"- lambda_energy_anchor: `{args.lambda_energy_anchor:.3f}`\n"
        f"- gap_floor: `{args.gap_floor:.2f}`\n"
        f"- gap_power: `{args.gap_power:.2f}`\n\n"
        "## Rebuild\n\n"
        "```powershell\n"
        ".\\python.exe .\\scripts\\run_encodec_atrr_latent_dual_objective_probe.py `\n"
        f"  --template-queue {rel_template} `\n"
        f"  --target-dir {rel_target} `\n"
        f"  --output-dir {rel_output} `\n"
        f"  --bandwidth {args.bandwidth:.1f} `\n"
        f"  --delta-scale {args.delta_scale:.2f} `\n"
        f"  --delta-cap-db {args.delta_cap_db:.2f} `\n"
        f"  --distribution-scale {args.distribution_scale:.2f} `\n"
        f"  --rank {args.rank} `\n"
        f"  --steps {args.steps} `\n"
        f"  --lr {args.lr:.4f} `\n"
        f"  --init-scale {args.init_scale:.4f} `\n"
        f"  --latent-cap {args.latent_cap:.3f} `\n"
        f"  --lambda-latent-l2 {args.lambda_latent_l2:.3f} `\n"
        f"  --lambda-latent-time {args.lambda_latent_time:.3f} `\n"
        f"  --lambda-wave-l1 {args.lambda_wave_l1:.3f} `\n"
        f"  --lambda-frame-kl {args.lambda_frame_kl:.3f} `\n"
        f"  --lambda-utt-kl {args.lambda_utt_kl:.3f} `\n"
        f"  --lambda-energy-anchor {args.lambda_energy_anchor:.3f} `\n"
        f"  --gap-floor {args.gap_floor:.2f} `\n"
        f"  --gap-power {args.gap_power:.2f}"
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

    strongest = sorted(rows, key=lambda row: float(row["latent_delta_rms"]), reverse=True)[:3]
    best_delta = sorted(rows, key=lambda row: float(row["final_delta_loss"]))[:3]
    lines = [
        "# Encodec ATRR Latent Dual Objective Probe Summary v1",
        "",
        f"- rows: `{len(rows)}`",
        f"- sample_rate: `{sample_rate}`",
        f"- device: `{device}`",
        f"- bandwidth_kbps: `{args.bandwidth:.1f}`",
        f"- avg latent_delta_rms: `{avg('latent_delta_rms'):.4f}`",
        f"- avg latent_delta_abs_mean: `{avg('latent_delta_abs_mean'):.4f}`",
        f"- avg final_delta_loss: `{avg('final_delta_loss'):.6f}`",
        f"- avg final_frame_kl: `{avg('final_frame_kl'):.6f}`",
        f"- avg final_utt_kl: `{avg('final_utt_kl'):.6f}`",
        f"- avg final_energy_l1: `{avg('final_energy_l1'):.6f}`",
        f"- avg final_wave_l1: `{avg('final_wave_l1'):.6f}`",
        f"- avg core_mask_ratio: `{avg('core_mask_ratio'):.4f}`",
        f"- avg distribution_weight_mean: `{avg('distribution_weight_mean'):.4f}`",
        "",
        "## Strongest Latent Rows",
        "",
    ]
    for row in strongest:
        lines.append(
            f"- `{row['record_id']}` | latent_rms=`{row['latent_delta_rms']}` | "
            f"delta_loss=`{row['final_delta_loss']}`"
        )
    lines.extend(["", "## Lowest Delta Loss Rows", ""])
    for row in best_delta:
        lines.append(
            f"- `{row['record_id']}` | delta_loss=`{row['final_delta_loss']}` | "
            f"frame_kl=`{row['final_frame_kl']}`"
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
            base_mel = torch.clamp(mel_transform(base_wave.squeeze(1)), min=1e-12).detach()
            base_log_mel = torch.log(base_mel).detach()

        with np.load(target_npz) as loaded:
            payload = {key: np.asarray(loaded[key]) for key in loaded.files}
        target_sample_rate = int(np.asarray(payload["sample_rate"]).reshape(-1)[0])

        (
            target_delta_mel,
            delta_weight,
            target_frame_distribution,
            target_utterance_distribution,
            source_log_energy,
            distribution_frame_weight,
            latent_time_gate_np,
            core_mask_ratio,
            distribution_weight_mean,
        ) = build_dual_targets(
            args,
            payload,
            mel_frame_count=int(base_mel.shape[-1]),
            latent_frame_count=int(base_latent.shape[-1]),
        )

        target_delta_t = torch.from_numpy(target_delta_mel.astype(np.float32)).to(device)[None, :, :]
        delta_weight_t = torch.from_numpy(delta_weight.astype(np.float32)).to(device)[None, :, :]
        target_frame_dist_t = torch.from_numpy(target_frame_distribution.astype(np.float32)).to(device)[None, :, :]
        target_utt_dist_t = torch.from_numpy(target_utterance_distribution.astype(np.float32)).to(device)[None, :]
        source_log_energy_t = torch.from_numpy(source_log_energy.astype(np.float32)).to(device)[None, :]
        distribution_frame_weight_t = torch.from_numpy(distribution_frame_weight.astype(np.float32)).to(device)[None, :]
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

        final_delta_loss = 0.0
        final_frame_kl = 0.0
        final_utt_kl = 0.0
        final_energy_l1 = 0.0
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
            edited_mel = torch.clamp(mel_transform(edited_wave.squeeze(1)), min=1e-12)
            edited_log_mel = torch.log(edited_mel)
            edited_delta_mel = edited_log_mel - base_log_mel

            delta_error = (edited_delta_mel - target_delta_t).square()
            delta_loss = safe_weighted_mean(delta_error, delta_weight_t)

            edited_frame_dist = edited_mel / torch.clamp(edited_mel.sum(dim=1, keepdim=True), min=1e-12)
            edited_log_frame_dist = torch.log(torch.clamp(edited_frame_dist, min=1e-12))
            frame_kl_per_frame = torch.sum(
                target_frame_dist_t * (torch.log(torch.clamp(target_frame_dist_t, min=1e-12)) - edited_log_frame_dist),
                dim=1,
            )
            frame_kl = torch.sum(frame_kl_per_frame * distribution_frame_weight_t) / torch.clamp(
                distribution_frame_weight_t.sum(),
                min=1e-6,
            )

            weighted_frame_dist = edited_frame_dist * distribution_frame_weight_t[:, None, :]
            edited_utt_dist = weighted_frame_dist.sum(dim=2)
            edited_utt_dist = edited_utt_dist / torch.clamp(edited_utt_dist.sum(dim=1, keepdim=True), min=1e-12)
            utt_kl = torch.sum(
                target_utt_dist_t
                * (
                    torch.log(torch.clamp(target_utt_dist_t, min=1e-12))
                    - torch.log(torch.clamp(edited_utt_dist, min=1e-12))
                ),
                dim=1,
            ).mean()

            edited_log_energy = torch.log(torch.clamp(edited_mel.sum(dim=1), min=1e-12))
            energy_l1 = torch.sum(
                torch.abs(edited_log_energy - source_log_energy_t) * distribution_frame_weight_t
            ) / torch.clamp(distribution_frame_weight_t.sum(), min=1e-6)

            latent_l2 = torch.mean(delta_latent.square())
            latent_time = (
                torch.mean((delta_latent[:, :, 1:] - delta_latent[:, :, :-1]).square())
                if delta_latent.shape[-1] > 1
                else torch.tensor(0.0, device=device, dtype=delta_latent.dtype)
            )
            wave_l1 = torch.mean(torch.abs(edited_wave - base_wave))
            loss = (
                delta_loss
                + (float(args.lambda_frame_kl) * frame_kl)
                + (float(args.lambda_utt_kl) * utt_kl)
                + (float(args.lambda_energy_anchor) * energy_l1)
                + (float(args.lambda_latent_l2) * latent_l2)
                + (float(args.lambda_latent_time) * latent_time)
                + (float(args.lambda_wave_l1) * wave_l1)
            )
            loss.backward()
            optimizer.step()
            final_delta_loss = float(delta_loss.detach().cpu())
            final_frame_kl = float(frame_kl.detach().cpu())
            final_utt_kl = float(utt_kl.detach().cpu())
            final_energy_l1 = float(energy_l1.detach().cpu())
            final_wave_l1 = float(wave_l1.detach().cpu())

        with torch.no_grad():
            low_rank_delta = torch.matmul(channel_factors, time_factors)
            delta_latent = (torch.tanh(low_rank_delta) * float(args.latent_cap) * latent_time_gate).detach()
            edited_latent = base_latent + delta_latent
            edited_wave = decode_wave(model, edited_latent, scale, audio_length).detach()

        output_path = processed_dir / f"{record_id}__encodec_latent_dual_bw{int(args.bandwidth)}.wav"
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
                "latent_delta_rms": f"{float(torch.sqrt(torch.mean(delta_latent.square())).cpu()):.6f}",
                "latent_delta_abs_mean": f"{float(torch.mean(torch.abs(delta_latent)).cpu()):.6f}",
                "final_delta_loss": f"{float(final_delta_loss):.6f}",
                "final_frame_kl": f"{float(final_frame_kl):.6f}",
                "final_utt_kl": f"{float(final_utt_kl):.6f}",
                "final_energy_l1": f"{float(final_energy_l1):.6f}",
                "final_wave_l1": f"{float(final_wave_l1):.6f}",
                "core_mask_ratio": f"{float(core_mask_ratio):.6f}",
                "distribution_weight_mean": f"{float(distribution_weight_mean):.6f}",
            }
        )

    queue_path = output_dir / "listening_review_queue.csv"
    summary_csv = output_dir / "encodec_atrr_latent_dual_objective_probe_summary.csv"
    summary_md = output_dir / "ENCODEC_ATRR_LATENT_DUAL_OBJECTIVE_PROBE_SUMMARY.md"
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
