from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from types import SimpleNamespace

import numpy as np
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
    / "encodec_atrr_code_probe"
    / "v1_fixed8_q24_n8_k4_r4_s020_d15_cb020_ct010_nb005_w100_bw24"
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
    parser.add_argument("--neighbor-count", type=int, default=4)
    parser.add_argument("--rank", type=int, default=4)
    parser.add_argument("--steps", type=int, default=30)
    parser.add_argument("--lr", type=float, default=0.01)
    parser.add_argument("--init-scale", type=float, default=0.01)
    parser.add_argument("--identity-bias", type=float, default=5.0)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--lambda-code-l2", type=float, default=0.20)
    parser.add_argument("--lambda-code-time", type=float, default=0.10)
    parser.add_argument("--lambda-nonbase", type=float, default=0.05)
    parser.add_argument("--lambda-wave-l1", type=float, default=1.00)
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


def set_seed(seed: int) -> None:
    torch.manual_seed(int(seed))
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(int(seed))


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


def build_readme(args: argparse.Namespace, output_dir: Path, rows: int, total_quantizers: int) -> str:
    rel_template = resolve_path(args.template_queue).relative_to(ROOT).as_posix()
    rel_target = resolve_path(args.target_dir).relative_to(ROOT).as_posix()
    rel_output = output_dir.relative_to(ROOT).as_posix()
    active_stop = min(int(args.quantizer_start) + int(args.quantizer_count), int(total_quantizers))
    return (
        "# Encodec ATRR Code Probe v1\n\n"
        "- purpose: `source-preserving Encodec roundtrip anchor with local code-side ATRR injection`\n"
        f"- rows: `{rows}`\n"
        f"- bandwidth_kbps: `{args.bandwidth:.1f}`\n"
        f"- delta_scale: `{args.delta_scale:.2f}`\n"
        f"- delta_cap_db: `{args.delta_cap_db:.2f}`\n"
        f"- quantizer_range: `[{int(args.quantizer_start)}, {active_stop})`\n"
        f"- neighbor_count: `{int(args.neighbor_count)}`\n"
        f"- rank: `{int(args.rank)}`\n"
        f"- steps: `{int(args.steps)}`\n"
        f"- lr: `{args.lr:.4f}`\n"
        f"- init_scale: `{args.init_scale:.4f}`\n"
        f"- identity_bias: `{args.identity_bias:.2f}`\n"
        f"- temperature: `{args.temperature:.2f}`\n"
        f"- lambda_code_l2: `{args.lambda_code_l2:.3f}`\n"
        f"- lambda_code_time: `{args.lambda_code_time:.3f}`\n"
        f"- lambda_nonbase: `{args.lambda_nonbase:.3f}`\n"
        f"- lambda_wave_l1: `{args.lambda_wave_l1:.3f}`\n"
        f"- voiced_only: `{bool(args.voiced_only)}`\n"
        f"- core_mask: `{bool(args.core_mask)}`\n"
        f"- core_mask_offcore_scale: `{args.core_mask_offcore_scale:.2f}`\n\n"
        "## Rebuild\n\n"
        "```powershell\n"
        ".\\python.exe .\\scripts\\run_encodec_atrr_code_probe.py `\n"
        f"  --template-queue {rel_template} `\n"
        f"  --target-dir {rel_target} `\n"
        f"  --output-dir {rel_output} `\n"
        f"  --bandwidth {args.bandwidth:.1f} `\n"
        f"  --delta-scale {args.delta_scale:.2f} `\n"
        f"  --delta-cap-db {args.delta_cap_db:.2f} `\n"
        f"  --quantizer-start {int(args.quantizer_start)} `\n"
        f"  --quantizer-count {int(args.quantizer_count)} `\n"
        f"  --neighbor-count {int(args.neighbor_count)} `\n"
        f"  --rank {int(args.rank)} `\n"
        f"  --steps {int(args.steps)} `\n"
        f"  --lr {args.lr:.4f} `\n"
        f"  --init-scale {args.init_scale:.4f} `\n"
        f"  --identity-bias {args.identity_bias:.2f} `\n"
        f"  --temperature {args.temperature:.2f} `\n"
        f"  --lambda-code-l2 {args.lambda_code_l2:.3f} `\n"
        f"  --lambda-code-time {args.lambda_code_time:.3f} `\n"
        f"  --lambda-nonbase {args.lambda_nonbase:.3f} `\n"
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

    strongest = sorted(rows, key=lambda row: float(row["code_delta_rms"]), reverse=True)[:3]
    most_conservative = sorted(rows, key=lambda row: float(row["nonbase_mass"]))[:3]
    active_stop = min(int(args.quantizer_start) + int(args.quantizer_count), int(total_quantizers))
    lines = [
        "# Encodec ATRR Code Probe Summary v1",
        "",
        f"- rows: `{len(rows)}`",
        f"- sample_rate: `{sample_rate}`",
        f"- device: `{device}`",
        f"- bandwidth_kbps: `{args.bandwidth:.1f}`",
        f"- quantizer_range: `[{int(args.quantizer_start)}, {active_stop})`",
        f"- neighbor_count: `{int(args.neighbor_count)}`",
        f"- avg target_logmel_delta_l1_db: `{avg('target_logmel_delta_l1_db'):.4f}`",
        f"- avg code_delta_rms: `{avg('code_delta_rms'):.4f}`",
        f"- avg nonbase_mass: `{avg('nonbase_mass'):.4f}`",
        f"- avg base_choice_prob: `{avg('base_choice_prob'):.4f}`",
        f"- avg final_mel_loss: `{avg('final_mel_loss'):.6f}`",
        f"- avg final_wave_l1: `{avg('final_wave_l1'):.6f}`",
        f"- avg core_mask_ratio: `{avg('core_mask_ratio'):.4f}`",
        "",
        "## Strongest Code Rows",
        "",
    ]
    for row in strongest:
        lines.append(
            f"- `{row['record_id']}` | code_rms=`{row['code_delta_rms']}` | "
            f"nonbase=`{row['nonbase_mass']}`"
        )
    lines.extend(["", "## Most Conservative Rows", ""])
    for row in most_conservative:
        lines.append(
            f"- `{row['record_id']}` | nonbase=`{row['nonbase_mass']}` | "
            f"base_prob=`{row['base_choice_prob']}`"
        )
    return "\n".join(lines) + "\n"


def decode_wave(
    model: EncodecModel,
    latent: torch.Tensor,
    scale: torch.Tensor | None,
    audio_length: int,
) -> torch.Tensor:
    with torch.backends.cudnn.flags(enabled=False):
        wave = model.decoder(latent)
    if scale is not None:
        wave = wave * scale.view(-1, 1, 1)
    return wave[:, :, :audio_length]


def gather_neighbor_codes(codebook: torch.Tensor, base_indices: torch.Tensor, neighbor_count: int) -> torch.Tensor:
    if neighbor_count <= 1:
        return base_indices.unsqueeze(-1)
    flat_indices = base_indices.reshape(-1)
    base_vectors = codebook.index_select(0, flat_indices)
    codebook_norm = torch.sum(codebook.square(), dim=1)
    base_norm = torch.sum(base_vectors.square(), dim=1, keepdim=True)
    distances = base_norm + codebook_norm.unsqueeze(0) - (2.0 * torch.matmul(base_vectors, codebook.transpose(0, 1)))
    distances.scatter_(1, flat_indices.unsqueeze(1), float("inf"))
    neighbor_count = min(int(neighbor_count) - 1, int(codebook.shape[0]) - 1)
    nearest = torch.topk(distances, k=neighbor_count, dim=1, largest=False).indices
    candidates = torch.cat([flat_indices.unsqueeze(1), nearest], dim=1)
    return candidates.view(*base_indices.shape, candidates.shape[-1])


def decode_soft_code_layer(
    layer: torch.nn.Module,
    candidate_indices: torch.Tensor,
    candidate_probs: torch.Tensor,
) -> torch.Tensor:
    codebook = layer.codebook.to(device=candidate_probs.device, dtype=candidate_probs.dtype)
    batch_size, time_steps, _, = candidate_indices.shape
    embedding_dim = int(codebook.shape[1])
    candidate_embeddings = codebook.index_select(0, candidate_indices.reshape(-1)).view(
        batch_size,
        time_steps,
        candidate_indices.shape[-1],
        embedding_dim,
    )
    mixed = torch.sum(candidate_probs.unsqueeze(-1) * candidate_embeddings, dim=2)
    mixed = layer.project_out(mixed)
    return mixed.permute(0, 2, 1)


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

        with np.load(target_npz) as payload:
            source_log_mel = np.asarray(payload["source_log_mel"], dtype=np.float64)
            target_log_mel = np.asarray(payload["target_log_mel"], dtype=np.float64)
            voiced_mask = np.asarray(payload["voiced_mask"], dtype=np.float64)
            target_sample_rate = int(np.asarray(payload["sample_rate"]).reshape(-1)[0])
            source_distribution = np.asarray(payload["source_distribution"], dtype=np.float64)
            target_distribution = np.asarray(payload["target_distribution"], dtype=np.float64)
            target_occupancy = np.asarray(payload["target_occupancy"], dtype=np.float64)
            edited_frame_distributions = np.asarray(payload["edited_frame_distributions"], dtype=np.float64)

        mel_frame_count = int(base_log_mel.shape[-1])
        delta_log_mel = target_log_mel - source_log_mel
        delta_log_mel = align_columns(delta_log_mel, mel_frame_count)
        core_mask_ratio = 1.0
        weight_mask = np.ones_like(delta_log_mel, dtype=np.float64)
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
            weight_mask = target_support[:, None] + ((1.0 - target_support[:, None]) * offcore_scale)
            core_mask_ratio = float(np.mean(target_support))
        if args.voiced_only:
            voiced_weight = align_mask(voiced_mask, mel_frame_count).astype(np.float64)[None, :]
            weight_mask = weight_mask * voiced_weight
            code_time_gate_np = align_mask(voiced_mask, int(base_latent.shape[-1])).astype(np.float32)
        else:
            code_time_gate_np = np.ones((int(base_latent.shape[-1]),), dtype=np.float32)

        delta_limit = db_to_log_amplitude(float(args.delta_cap_db))
        delta_log_mel = np.clip(delta_log_mel * float(args.delta_scale), -delta_limit, delta_limit)

        target_delta_t = torch.from_numpy(delta_log_mel.astype(np.float32)).to(device)[None, :, :]
        weight_mask_t = torch.from_numpy(weight_mask.astype(np.float32)).to(device)[None, :, :]
        code_time_gate = torch.from_numpy(code_time_gate_np).to(device)[None, None, :]

        candidate_index_map: dict[int, torch.Tensor] = {}
        for layer_idx in active_quantizers:
            layer = model.quantizer.vq.layers[layer_idx]
            base_indices = q_indices[layer_idx]
            candidate_index_map[layer_idx] = gather_neighbor_codes(
                layer.codebook.to(device=q_indices.device),
                base_indices,
                int(args.neighbor_count),
            )

        active_count = len(active_quantizers)
        candidate_count = int(candidate_index_map[active_quantizers[0]].shape[-1])
        layer_candidate_factors = torch.nn.Parameter(
            torch.randn((1, active_count * candidate_count, int(args.rank)), dtype=base_latent.dtype, device=device)
            * float(args.init_scale)
        )
        time_factors = torch.nn.Parameter(
            torch.randn((1, int(args.rank), int(base_latent.shape[-1])), dtype=base_latent.dtype, device=device)
            * float(args.init_scale)
        )
        optimizer = torch.optim.Adam([layer_candidate_factors, time_factors], lr=float(args.lr))

        base_choice_bias = torch.zeros((1, active_count, candidate_count, 1), dtype=base_latent.dtype, device=device)
        base_choice_bias[:, :, 0, :] = float(args.identity_bias)

        final_mel_loss = 0.0
        final_wave_l1 = 0.0
        final_nonbase_mass = 0.0
        final_base_choice_prob = 1.0
        edited_wave = base_wave
        code_delta_tensor = torch.zeros((1,), dtype=base_latent.dtype, device=device)
        for _ in range(max(1, int(args.steps))):
            optimizer.zero_grad(set_to_none=True)
            logits = torch.matmul(layer_candidate_factors, time_factors).view(1, active_count, candidate_count, -1)
            logits = (logits + base_choice_bias) / max(float(args.temperature), 1e-4)
            probs = torch.softmax(logits, dim=2)

            edited_latent = inactive_latent
            code_deltas: list[torch.Tensor] = []
            for active_pos, layer_idx in enumerate(active_quantizers):
                layer = model.quantizer.vq.layers[layer_idx]
                layer_probs = probs[:, active_pos].permute(0, 2, 1)
                candidate_indices = candidate_index_map[layer_idx]
                mixed_layer = decode_soft_code_layer(layer, candidate_indices, layer_probs)
                base_layer = base_layer_latents[layer_idx]
                if args.voiced_only:
                    mixed_layer = base_layer + ((mixed_layer - base_layer) * code_time_gate)
                edited_latent = edited_latent + mixed_layer
                code_deltas.append(mixed_layer - base_layer)

            edited_wave = decode_wave(model, edited_latent, scale, audio_length)
            edited_log_mel = torch.log(torch.clamp(mel_transform(edited_wave.squeeze(1)), min=1e-12))
            edited_delta_mel = edited_log_mel - base_log_mel
            mel_error = edited_delta_mel - target_delta_t
            weighted_mel = (mel_error.square() * weight_mask_t).sum() / torch.clamp(weight_mask_t.sum(), min=1e-6)

            code_delta_tensor = torch.cat(code_deltas, dim=1)
            code_l2 = torch.mean(code_delta_tensor.square())
            code_time = (
                torch.mean((code_delta_tensor[:, :, 1:] - code_delta_tensor[:, :, :-1]).square())
                if code_delta_tensor.shape[-1] > 1
                else torch.tensor(0.0, device=device, dtype=code_delta_tensor.dtype)
            )
            wave_l1 = torch.mean(torch.abs(edited_wave - base_wave))

            nonbase = 1.0 - probs[:, :, 0, :]
            base_prob = probs[:, :, 0, :]
            if args.voiced_only:
                gate = code_time_gate.squeeze(1).unsqueeze(1)
                denom = torch.clamp(gate.sum() * float(active_count), min=1e-6)
                nonbase_mass = (nonbase * gate).sum() / denom
                base_choice_prob = (base_prob * gate).sum() / denom
            else:
                nonbase_mass = torch.mean(nonbase)
                base_choice_prob = torch.mean(base_prob)

            loss = (
                weighted_mel
                + float(args.lambda_code_l2) * code_l2
                + float(args.lambda_code_time) * code_time
                + float(args.lambda_nonbase) * nonbase_mass
                + float(args.lambda_wave_l1) * wave_l1
            )
            loss.backward()
            optimizer.step()
            final_mel_loss = float(weighted_mel.detach().cpu())
            final_wave_l1 = float(wave_l1.detach().cpu())
            final_nonbase_mass = float(nonbase_mass.detach().cpu())
            final_base_choice_prob = float(base_choice_prob.detach().cpu())

        with torch.no_grad():
            logits = torch.matmul(layer_candidate_factors, time_factors).view(1, active_count, candidate_count, -1)
            logits = (logits + base_choice_bias) / max(float(args.temperature), 1e-4)
            probs = torch.softmax(logits, dim=2)
            edited_latent = inactive_latent
            code_deltas = []
            for active_pos, layer_idx in enumerate(active_quantizers):
                layer = model.quantizer.vq.layers[layer_idx]
                layer_probs = probs[:, active_pos].permute(0, 2, 1)
                candidate_indices = candidate_index_map[layer_idx]
                mixed_layer = decode_soft_code_layer(layer, candidate_indices, layer_probs)
                base_layer = base_layer_latents[layer_idx]
                if args.voiced_only:
                    mixed_layer = base_layer + ((mixed_layer - base_layer) * code_time_gate)
                edited_latent = edited_latent + mixed_layer
                code_deltas.append(mixed_layer - base_layer)
            code_delta_tensor = torch.cat(code_deltas, dim=1).detach()
            edited_wave = decode_wave(model, edited_latent, scale, audio_length).detach()

        output_path = processed_dir / f"{record_id}__encodec_code_bw{int(args.bandwidth)}.wav"
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
                "code_delta_rms": f"{float(torch.sqrt(torch.mean(code_delta_tensor.square())).cpu()):.6f}",
                "code_delta_abs_mean": f"{float(torch.mean(torch.abs(code_delta_tensor)).cpu()):.6f}",
                "nonbase_mass": f"{float(final_nonbase_mass):.6f}",
                "base_choice_prob": f"{float(final_base_choice_prob):.6f}",
                "final_mel_loss": f"{float(final_mel_loss):.6f}",
                "final_wave_l1": f"{float(final_wave_l1):.6f}",
                "core_mask_ratio": f"{float(core_mask_ratio):.6f}",
                "quantizer_start": str(quantizer_start),
                "quantizer_stop": str(quantizer_stop),
                "neighbor_count": str(candidate_count),
            }
        )

    queue_path = output_dir / "listening_review_queue.csv"
    summary_csv = output_dir / "encodec_atrr_code_probe_summary.csv"
    summary_md = output_dir / "ENCODEC_ATRR_CODE_PROBE_SUMMARY.md"
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
