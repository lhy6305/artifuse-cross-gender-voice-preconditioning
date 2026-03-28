from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import librosa
import numpy as np
import scipy.fft
import torch
import torch.nn as nn
import torch.optim as optim

from row_identity import get_record_id


ROOT = Path(__file__).resolve().parents[1]

ENVELOPE_SUMMARY_FIELDS = [
    "rule_id",
    "record_id",
    "utt_id",
    "source_gender",
    "target_direction",
    "group_value",
    "f0_condition",
    "f0_median_hz",
    "input_audio",
    "original_copy",
    "processed_audio",
    "confidence",
    "strength_label",
    "alpha_default",
    "alpha_max",
    "dataset_name",
    "eval_bucket",
    "duration_sec",
    "selection_rank",
    "selection_score",
    "method_family",
    "method_params",
    "rule_notes",
]


class EnvelopeAutoencoder(nn.Module):
    def __init__(self, input_dim: int, hidden_dims: list[int], latent_dim: int) -> None:
        super().__init__()
        if latent_dim <= 0:
            raise ValueError("latent_dim must be positive")
        clean_hidden_dims = [int(value) for value in hidden_dims if int(value) > 0]
        encoder_layers: list[nn.Module] = []
        last_dim = int(input_dim)
        for hidden_dim in clean_hidden_dims:
            encoder_layers.append(nn.Linear(last_dim, hidden_dim))
            encoder_layers.append(nn.GELU())
            last_dim = hidden_dim
        encoder_layers.append(nn.Linear(last_dim, int(latent_dim)))
        self.encoder = nn.Sequential(*encoder_layers)

        decoder_layers: list[nn.Module] = []
        last_dim = int(latent_dim)
        for hidden_dim in reversed(clean_hidden_dims):
            decoder_layers.append(nn.Linear(last_dim, hidden_dim))
            decoder_layers.append(nn.GELU())
            last_dim = hidden_dim
        decoder_layers.append(nn.Linear(last_dim, int(input_dim)))
        self.decoder = nn.Sequential(*decoder_layers)

    def encode(self, inputs: torch.Tensor) -> torch.Tensor:
        return self.encoder(inputs)

    def decode(self, latents: torch.Tensor) -> torch.Tensor:
        return self.decoder(latents)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return self.decode(self.encode(inputs))


class LatentTranslator(nn.Module):
    def __init__(self, latent_dim: int, hidden_dims: list[int]) -> None:
        super().__init__()
        clean_hidden_dims = [int(value) for value in hidden_dims if int(value) > 0]
        layers: list[nn.Module] = []
        last_dim = int(latent_dim)
        for hidden_dim in clean_hidden_dims:
            layers.append(nn.Linear(last_dim, hidden_dim))
            layers.append(nn.GELU())
            last_dim = hidden_dim
        layers.append(nn.Linear(last_dim, int(latent_dim)))
        self.net = nn.Sequential(*layers)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return self.net(inputs)


class GenderProbe(nn.Module):
    def __init__(self, input_dim: int, hidden_dims: list[int]) -> None:
        super().__init__()
        clean_hidden_dims = [int(value) for value in hidden_dims if int(value) > 0]
        layers: list[nn.Module] = []
        last_dim = int(input_dim)
        for hidden_dim in clean_hidden_dims:
            layers.append(nn.Linear(last_dim, hidden_dim))
            layers.append(nn.GELU())
            last_dim = hidden_dim
        layers.append(nn.Linear(last_dim, 1))
        self.net = nn.Sequential(*layers)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return self.net(inputs).squeeze(-1)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_enabled_directional_rule_lookup(rule_config: dict) -> dict[tuple[str, str], dict]:
    return {
        (rule["match"]["group_value"], rule["target_direction"]): rule
        for rule in rule_config["rules"]
        if rule.get("enabled", False)
    }


def safe_rms(audio: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(audio.astype(np.float64))))) if audio.size else 0.0


def analyze_f0(audio: np.ndarray, sample_rate: int, world_sr: int, frame_period_ms: float) -> tuple[np.ndarray, np.ndarray]:
    if sample_rate != world_sr:
        audio_world = librosa.resample(audio.astype(np.float32), orig_sr=sample_rate, target_sr=world_sr).astype(np.float64)
    else:
        audio_world = audio.astype(np.float64)
    import pyworld

    f0, time_axis = pyworld.harvest(audio_world, world_sr, frame_period=frame_period_ms, f0_floor=71.0, f0_ceil=800.0)
    f0 = pyworld.stonemask(audio_world, f0, time_axis, world_sr)
    return f0, time_axis


def stft_frame_centers_sec(frame_count: int, n_fft: int, hop_length: int, sample_rate: int) -> np.ndarray:
    return (np.arange(frame_count, dtype=np.float64) * hop_length + n_fft / 2.0) / sample_rate


def interpolate_voiced_mask(frame_times_sec: np.ndarray, world_times_sec: np.ndarray, f0: np.ndarray) -> np.ndarray:
    if frame_times_sec.size == 0 or world_times_sec.size == 0 or f0.size == 0:
        return np.zeros(frame_times_sec.shape[0], dtype=np.float32)
    voiced = (f0 > 0.0).astype(np.float32)
    interpolated = np.interp(frame_times_sec, world_times_sec, voiced, left=voiced[0], right=voiced[-1])
    if interpolated.size > 2:
        interpolated = np.convolve(interpolated, np.array([0.2, 0.6, 0.2], dtype=np.float32), mode="same")
    return np.clip(interpolated.astype(np.float32), 0.0, 1.0)


def read_reference_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    output: list[dict[str, str]] = []
    for row in rows:
        if row.get("domain") != "speech":
            continue
        if row.get("gender") not in {"female", "male"}:
            continue
        if not row.get("path_raw"):
            continue
        output.append(row)
    return output


def select_reference_rows(rows: list[dict[str, str]], samples_per_cell: int) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row["dataset_name"], row["gender"])].append(row)
    selected: list[dict[str, str]] = []
    for key in sorted(grouped):
        group_rows = sorted(grouped[key], key=lambda row: row.get("utt_id", ""))
        if samples_per_cell > 0:
            selected.extend(group_rows[:samples_per_cell])
        else:
            selected.extend(group_rows)
    return selected


def build_smoothing_kernel(size: int) -> np.ndarray:
    if size <= 1:
        return np.ones(1, dtype=np.float32)
    kernel = np.hanning(size).astype(np.float32)
    if float(np.sum(kernel)) <= 0.0:
        kernel = np.ones(size, dtype=np.float32)
    return kernel / np.sum(kernel)


def smooth_along_time(values: np.ndarray, voiced_mask: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    if values.size == 0 or kernel.size <= 1:
        return values
    output = np.empty_like(values)
    denominator = np.convolve(voiced_mask.astype(np.float32), kernel, mode="same") + 1e-6
    for coeff_idx in range(values.shape[0]):
        weighted = np.convolve(values[coeff_idx] * voiced_mask, kernel, mode="same")
        output[coeff_idx] = weighted / denominator
    return output


def extract_voiced_cepstral_frames(
    audio: np.ndarray,
    *,
    sample_rate: int,
    n_fft: int,
    hop_length: int,
    keep_coeffs: int,
    world_sr: int,
    frame_period_ms: float,
    frame_stride: int,
) -> np.ndarray | None:
    stft = librosa.stft(audio.astype(np.float32), n_fft=n_fft, hop_length=hop_length)
    magnitude = np.abs(stft).astype(np.float32)
    if magnitude.size == 0:
        return None
    log_mag = np.log(np.maximum(magnitude, 1e-7))
    cep = scipy.fft.dct(log_mag, type=2, axis=0, norm="ortho").astype(np.float32)
    coeff_count = min(int(keep_coeffs), int(cep.shape[0] - 1))
    if coeff_count <= 0:
        return None
    f0, world_times_sec = analyze_f0(audio, sample_rate, world_sr, frame_period_ms)
    frame_times_sec = stft_frame_centers_sec(cep.shape[1], n_fft, hop_length, sample_rate)
    voiced_mask = interpolate_voiced_mask(frame_times_sec, world_times_sec, f0)
    voiced_frames = cep[1 : 1 + coeff_count, voiced_mask >= 0.5].T
    if voiced_frames.size == 0:
        return None
    stride = max(int(frame_stride), 1)
    return voiced_frames[::stride].astype(np.float32, copy=True)


def clip_ratio(values: np.ndarray, low: float, high: float) -> np.ndarray:
    return np.clip(values, low, high).astype(np.float32)


def parse_hidden_dims(values: object) -> list[int]:
    if isinstance(values, list):
        return [int(value) for value in values]
    if isinstance(values, str):
        return [int(part.strip()) for part in values.split(",") if part.strip()]
    raise ValueError(f"Unsupported hidden_dims value: {values!r}")


def resolve_torch_device(device_name: str) -> torch.device:
    requested = str(device_name).strip().lower()
    if requested == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if requested == "cuda" and not torch.cuda.is_available():
        return torch.device("cpu")
    return torch.device(requested)


def stable_name_seed(value: str) -> int:
    total = 0
    for index, char in enumerate(value.encode("utf-8"), start=1):
        total += index * int(char)
    return total


def train_autoencoder(
    frames: np.ndarray,
    *,
    hidden_dims: list[int],
    latent_dim: int,
    train_epochs: int,
    train_batch_size: int,
    learning_rate: float,
    weight_decay: float,
    device: torch.device,
    seed: int,
) -> tuple[EnvelopeAutoencoder, np.ndarray, np.ndarray]:
    if frames.ndim != 2 or frames.shape[0] < 4:
        raise ValueError("Need at least 4 training frames for autoencoder training")

    torch.manual_seed(int(seed))
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(int(seed))

    mean_vector = np.mean(frames, axis=0).astype(np.float32)
    std_vector = np.maximum(np.std(frames, axis=0), 1e-3).astype(np.float32)
    normalized = ((frames - mean_vector[None, :]) / std_vector[None, :]).astype(np.float32)

    model = EnvelopeAutoencoder(input_dim=int(frames.shape[1]), hidden_dims=hidden_dims, latent_dim=int(latent_dim)).to(device)
    optimizer = optim.AdamW(model.parameters(), lr=float(learning_rate), weight_decay=float(weight_decay))
    loss_fn = nn.MSELoss()
    data_tensor = torch.from_numpy(normalized).to(device)
    batch_size = max(1, min(int(train_batch_size), int(data_tensor.shape[0])))

    model.train()
    for epoch_idx in range(max(1, int(train_epochs))):
        generator = torch.Generator(device=device.type if device.type != "cpu" else "cpu")
        generator.manual_seed(int(seed) + epoch_idx)
        permutation = torch.randperm(int(data_tensor.shape[0]), generator=generator, device=device)
        for start_idx in range(0, int(data_tensor.shape[0]), batch_size):
            batch_indices = permutation[start_idx : start_idx + batch_size]
            batch = data_tensor[batch_indices]
            optimizer.zero_grad(set_to_none=True)
            recon = model(batch)
            loss = loss_fn(recon, batch)
            loss.backward()
            optimizer.step()

    model.eval()
    return model, mean_vector, std_vector


def encode_frames(
    model: EnvelopeAutoencoder,
    normalized_frames: np.ndarray,
    *,
    device: torch.device,
) -> np.ndarray:
    with torch.no_grad():
        inputs = torch.from_numpy(normalized_frames.astype(np.float32)).to(device)
        latents = model.encode(inputs).detach().cpu().numpy().astype(np.float32)
    return latents


def dataset_slug(dataset_name: str) -> str:
    return "libritts_r" if dataset_name == "LibriTTS-R" else "vctk"


def build_output_stem(row: dict[str, str], *, target_direction: str, method_token: str) -> str:
    return f"{dataset_slug(row['dataset_name'])}__{row['gender']}__{target_direction}__{method_token}__{row['utt_id']}"


def build_summary_row(
    row: dict[str, str],
    *,
    rule: dict,
    target_direction: str,
    input_audio: Path,
    original_copy: Path,
    processed_audio: Path,
) -> dict[str, str]:
    return {
        "rule_id": rule["rule_id"],
        "record_id": get_record_id(row),
        "utt_id": row["utt_id"],
        "source_gender": row["gender"],
        "target_direction": target_direction,
        "group_value": row["dataset_name"],
        "f0_condition": rule["match"]["f0_condition"],
        "f0_median_hz": row["f0_median_hz"],
        "input_audio": str(input_audio),
        "original_copy": str(original_copy),
        "processed_audio": str(processed_audio),
        "confidence": rule["confidence"],
        "strength_label": rule["strength"]["label"],
        "alpha_default": f"{rule['strength']['alpha_default']:.3f}",
        "alpha_max": f"{rule['strength']['alpha_max']:.3f}",
        "dataset_name": row["dataset_name"],
        "eval_bucket": row["eval_bucket"],
        "duration_sec": row["duration_sec"],
        "selection_rank": row["selection_rank"],
        "selection_score": row["selection_score"],
        "method_family": rule["method_family"],
        "method_params": json.dumps(rule["method_params"], ensure_ascii=False, sort_keys=True),
        "rule_notes": rule.get("notes", ""),
    }


def write_summary(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=ENVELOPE_SUMMARY_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_pack_readme(
    path: Path,
    *,
    rows: list[dict[str, str]],
    pack_title: str,
    purpose: str,
    script_name: str,
    rule_config_path: Path,
) -> None:
    pack_dir = path.parent
    pack_version = pack_dir.name
    try:
        rule_config_rel = rule_config_path.relative_to(ROOT).as_posix()
    except ValueError:
        rule_config_rel = str(rule_config_path)
    summary_rel = (pack_dir / "listening_pack_summary.csv").relative_to(ROOT).as_posix()
    queue_rel = (pack_dir / "listening_review_queue.csv").relative_to(ROOT).as_posix()
    summary_md_rel = (pack_dir / "listening_review_quant_summary.md").relative_to(ROOT).as_posix()
    lines = [
        f"# {pack_title} {pack_version}",
        "",
        f"- purpose: `{purpose}`",
        f"- rows: `{len(rows)}`",
        "",
        "## Rebuild",
        "",
        "```powershell",
        f".\\python.exe .\\scripts\\{script_name}",
        ".\\python.exe .\\scripts\\build_stage0_rule_review_queue.py `",
        f"  --rule-config {rule_config_rel} `",
        f"  --summary-csv {summary_rel} `",
        f"  --output-csv {queue_rel} `",
        f"  --summary-md {summary_md_rel}",
        "```",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
