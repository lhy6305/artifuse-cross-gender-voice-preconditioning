from __future__ import annotations

import argparse
from pathlib import Path

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
    build_target_index,
    choose_device,
    decode_wave,
    load_audio_mono,
    read_rows,
    resolve_path,
    set_seed,
    write_rows,
)


DEFAULT_OUTPUT_DIR = (
    ROOT
    / "artifacts"
    / "diagnostics"
    / "encodec_atrr_latent_distribution_probe"
    / "v1_fixed8_rank4_ds035_fu100_uu050_ea050_w100_bw24"
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
    parser.add_argument("--distribution-scale", type=float, default=0.35)
    parser.add_argument("--rank", type=int, default=4)
    parser.add_argument("--steps", type=int, default=30)
    parser.add_argument("--lr", type=float, default=0.01)
    parser.add_argument("--init-scale", type=float, default=0.01)
    parser.add_argument("--latent-cap", type=float, default=0.20)
    parser.add_argument("--lambda-frame-kl", type=float, default=1.00)
    parser.add_argument("--lambda-utt-kl", type=float, default=0.50)
    parser.add_argument("--lambda-energy-anchor", type=float, default=0.50)
    parser.add_argument("--lambda-latent-l2", type=float, default=0.20)
    parser.add_argument("--lambda-latent-time", type=float, default=0.10)
    parser.add_argument("--lambda-wave-l1", type=float, default=1.00)
    parser.add_argument("--voiced-only", action="store_true")
    return parser.parse_args()


def normalize_columns_np(matrix: np.ndarray) -> np.ndarray:
    source = np.asarray(matrix, dtype=np.float64)
    denom = np.sum(source, axis=0, keepdims=True)
    denom = np.maximum(denom, 1e-12)
    return np.asarray(source / denom, dtype=np.float64)


def build_distribution_targets(
    payload: dict[str, np.ndarray],
    *,
    mel_frame_count: int,
    latent_frame_count: int,
    distribution_scale: float,
    voiced_only: bool,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    source_log_mel = np.asarray(payload["source_log_mel"], dtype=np.float64)
    source_distribution = np.asarray(payload["source_distribution"], dtype=np.float64)
    target_distribution = np.asarray(payload["target_distribution"], dtype=np.float64)
    edited_frame_distributions = np.asarray(payload["edited_frame_distributions"], dtype=np.float64)
    voiced_mask = np.asarray(payload["voiced_mask"], dtype=np.float64)

    source_power = np.exp(source_log_mel)
    source_frame_distribution = normalize_columns_np(align_columns(source_power, mel_frame_count))
    target_frame_distribution = normalize_columns_np(align_columns(np.transpose(edited_frame_distributions), mel_frame_count))

    scale = float(np.clip(distribution_scale, 0.0, 1.0))
    blended_frame_distribution = np.clip(
        source_frame_distribution + (scale * (target_frame_distribution - source_frame_distribution)),
        1e-12,
        None,
    )
    blended_frame_distribution = normalize_columns_np(blended_frame_distribution)

    blended_utterance_distribution = np.clip(
        np.asarray(source_distribution, dtype=np.float64)
        + (scale * (np.asarray(target_distribution, dtype=np.float64) - np.asarray(source_distribution, dtype=np.float64))),
        1e-12,
        None,
    )
    blended_utterance_distribution = blended_utterance_distribution / np.sum(blended_utterance_distribution)

    source_frame_energy = np.sum(align_columns(source_power, mel_frame_count), axis=0)
    source_log_energy = np.log(np.maximum(source_frame_energy, 1e-12))

    if voiced_only:
        frame_weight = align_mask(voiced_mask, mel_frame_count).astype(np.float64)
        latent_time_gate = align_mask(voiced_mask, latent_frame_count).astype(np.float32)
    else:
        frame_weight = np.ones((mel_frame_count,), dtype=np.float64)
        latent_time_gate = np.ones((latent_frame_count,), dtype=np.float32)
    if float(np.sum(frame_weight)) <= 0.0:
        frame_weight = np.ones((mel_frame_count,), dtype=np.float64)
        latent_time_gate = np.ones((latent_frame_count,), dtype=np.float32)
    frame_weight = frame_weight / np.sum(frame_weight)

    return (
        blended_frame_distribution,
        blended_utterance_distribution,
        source_log_energy,
        frame_weight,
        latent_time_gate,
    )


def build_readme(args: argparse.Namespace, output_dir: Path, rows: int) -> str:
    rel_template = resolve_path(args.template_queue).relative_to(ROOT).as_posix()
    rel_target = resolve_path(args.target_dir).relative_to(ROOT).as_posix()
    rel_output = output_dir.relative_to(ROOT).as_posix()
    return (
        "# Encodec ATRR Latent Distribution Probe v1\n\n"
        "- purpose: `source-preserving Encodec latent edit with frame-distribution and utterance-distribution objectives`\n"
        f"- rows: `{rows}`\n"
        f"- bandwidth_kbps: `{args.bandwidth:.1f}`\n"
        f"- distribution_scale: `{args.distribution_scale:.2f}`\n"
        f"- rank: `{args.rank}`\n"
        f"- steps: `{args.steps}`\n"
        f"- lambda_frame_kl: `{args.lambda_frame_kl:.3f}`\n"
        f"- lambda_utt_kl: `{args.lambda_utt_kl:.3f}`\n"
        f"- lambda_energy_anchor: `{args.lambda_energy_anchor:.3f}`\n"
        f"- lambda_wave_l1: `{args.lambda_wave_l1:.3f}`\n\n"
        "## Rebuild\n\n"
        "```powershell\n"
        ".\\python.exe .\\scripts\\run_encodec_atrr_latent_distribution_probe.py `\n"
        f"  --template-queue {rel_template} `\n"
        f"  --target-dir {rel_target} `\n"
        f"  --output-dir {rel_output} `\n"
        f"  --bandwidth {args.bandwidth:.1f} `\n"
        f"  --distribution-scale {args.distribution_scale:.2f} `\n"
        f"  --rank {args.rank} `\n"
        f"  --steps {args.steps} `\n"
        f"  --lr {args.lr:.4f} `\n"
        f"  --init-scale {args.init_scale:.4f} `\n"
        f"  --latent-cap {args.latent_cap:.3f} `\n"
        f"  --lambda-frame-kl {args.lambda_frame_kl:.3f} `\n"
        f"  --lambda-utt-kl {args.lambda_utt_kl:.3f} `\n"
        f"  --lambda-energy-anchor {args.lambda_energy_anchor:.3f} `\n"
        f"  --lambda-latent-l2 {args.lambda_latent_l2:.3f} `\n"
        f"  --lambda-latent-time {args.lambda_latent_time:.3f} `\n"
        f"  --lambda-wave-l1 {args.lambda_wave_l1:.3f}"
        + (" `\n  --voiced-only\n" if args.voiced_only else "\n")
        + "```\n"
    )


def build_summary(rows: list[dict[str, str]], args: argparse.Namespace, device: str, sample_rate: int) -> str:
    def avg(field: str) -> float:
        return sum(float(row[field]) for row in rows) / max(len(rows), 1)

    strongest = sorted(rows, key=lambda row: float(row["latent_delta_rms"]), reverse=True)[:3]
    closest = sorted(rows, key=lambda row: float(row["final_frame_kl"]))[:3]
    lines = [
        "# Encodec ATRR Latent Distribution Probe Summary v1",
        "",
        f"- rows: `{len(rows)}`",
        f"- sample_rate: `{sample_rate}`",
        f"- device: `{device}`",
        f"- bandwidth_kbps: `{args.bandwidth:.1f}`",
        f"- distribution_scale: `{args.distribution_scale:.2f}`",
        f"- avg latent_delta_rms: `{avg('latent_delta_rms'):.4f}`",
        f"- avg latent_delta_abs_mean: `{avg('latent_delta_abs_mean'):.4f}`",
        f"- avg final_frame_kl: `{avg('final_frame_kl'):.6f}`",
        f"- avg final_utt_kl: `{avg('final_utt_kl'):.6f}`",
        f"- avg final_energy_l1: `{avg('final_energy_l1'):.6f}`",
        f"- avg final_wave_l1: `{avg('final_wave_l1'):.6f}`",
        "",
        "## Strongest Latent Rows",
        "",
    ]
    for row in strongest:
        lines.append(
            f"- `{row['record_id']}` | latent_rms=`{row['latent_delta_rms']}` | "
            f"frame_kl=`{row['final_frame_kl']}`"
        )
    lines.extend(["", "## Closest Frame-Distribution Rows", ""])
    for row in closest:
        lines.append(
            f"- `{row['record_id']}` | frame_kl=`{row['final_frame_kl']}` | "
            f"utt_kl=`{row['final_utt_kl']}`"
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

        with np.load(target_npz) as loaded:
            payload = {key: np.asarray(loaded[key]) for key in loaded.files}
        target_sample_rate = int(np.asarray(payload["sample_rate"]).reshape(-1)[0])

        (
            target_frame_distribution,
            target_utterance_distribution,
            source_log_energy,
            frame_weight,
            latent_time_gate_np,
        ) = build_distribution_targets(
            payload,
            mel_frame_count=int(base_mel.shape[-1]),
            latent_frame_count=int(base_latent.shape[-1]),
            distribution_scale=float(args.distribution_scale),
            voiced_only=bool(args.voiced_only),
        )

        target_frame_dist_t = torch.from_numpy(target_frame_distribution.astype(np.float32)).to(device)[None, :, :]
        target_utt_dist_t = torch.from_numpy(target_utterance_distribution.astype(np.float32)).to(device)[None, :]
        source_log_energy_t = torch.from_numpy(source_log_energy.astype(np.float32)).to(device)[None, :]
        frame_weight_t = torch.from_numpy(frame_weight.astype(np.float32)).to(device)[None, :]
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
            edited_frame_dist = edited_mel / torch.clamp(edited_mel.sum(dim=1, keepdim=True), min=1e-12)
            edited_log_frame_dist = torch.log(torch.clamp(edited_frame_dist, min=1e-12))

            frame_kl_per_frame = torch.sum(
                target_frame_dist_t * (torch.log(torch.clamp(target_frame_dist_t, min=1e-12)) - edited_log_frame_dist),
                dim=1,
            )
            frame_kl = torch.sum(frame_kl_per_frame * frame_weight_t) / torch.clamp(frame_weight_t.sum(), min=1e-6)

            weighted_frame_dist = edited_frame_dist * frame_weight_t[:, None, :]
            edited_utt_dist = weighted_frame_dist.sum(dim=2)
            edited_utt_dist = edited_utt_dist / torch.clamp(edited_utt_dist.sum(dim=1, keepdim=True), min=1e-12)
            utt_kl = torch.sum(
                target_utt_dist_t * (torch.log(torch.clamp(target_utt_dist_t, min=1e-12)) - torch.log(torch.clamp(edited_utt_dist, min=1e-12))),
                dim=1,
            ).mean()

            edited_log_energy = torch.log(torch.clamp(edited_mel.sum(dim=1), min=1e-12))
            energy_l1 = torch.sum(torch.abs(edited_log_energy - source_log_energy_t) * frame_weight_t) / torch.clamp(frame_weight_t.sum(), min=1e-6)

            latent_l2 = torch.mean(delta_latent.square())
            latent_time = (
                torch.mean((delta_latent[:, :, 1:] - delta_latent[:, :, :-1]).square())
                if delta_latent.shape[-1] > 1
                else torch.tensor(0.0, device=device, dtype=delta_latent.dtype)
            )
            wave_l1 = torch.mean(torch.abs(edited_wave - base_wave))
            loss = (
                (float(args.lambda_frame_kl) * frame_kl)
                + (float(args.lambda_utt_kl) * utt_kl)
                + (float(args.lambda_energy_anchor) * energy_l1)
                + (float(args.lambda_latent_l2) * latent_l2)
                + (float(args.lambda_latent_time) * latent_time)
                + (float(args.lambda_wave_l1) * wave_l1)
            )
            loss.backward()
            optimizer.step()
            final_frame_kl = float(frame_kl.detach().cpu())
            final_utt_kl = float(utt_kl.detach().cpu())
            final_energy_l1 = float(energy_l1.detach().cpu())
            final_wave_l1 = float(wave_l1.detach().cpu())

        with torch.no_grad():
            low_rank_delta = torch.matmul(channel_factors, time_factors)
            delta_latent = (torch.tanh(low_rank_delta) * float(args.latent_cap) * latent_time_gate).detach()
            edited_latent = base_latent + delta_latent
            edited_wave = decode_wave(model, edited_latent, scale, audio_length).detach()

        output_path = processed_dir / f"{record_id}__encodec_latent_distribution_bw{int(args.bandwidth)}.wav"
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
                "final_frame_kl": f"{float(final_frame_kl):.6f}",
                "final_utt_kl": f"{float(final_utt_kl):.6f}",
                "final_energy_l1": f"{float(final_energy_l1):.6f}",
                "final_wave_l1": f"{float(final_wave_l1):.6f}",
            }
        )

    queue_path = output_dir / "listening_review_queue.csv"
    summary_csv = output_dir / "encodec_atrr_latent_distribution_probe_summary.csv"
    summary_md = output_dir / "ENCODEC_ATRR_LATENT_DISTRIBUTION_PROBE_SUMMARY.md"
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
