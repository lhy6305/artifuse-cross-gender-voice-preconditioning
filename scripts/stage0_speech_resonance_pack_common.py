from __future__ import annotations

import csv
import json
from pathlib import Path

import librosa
import numpy as np

from row_identity import get_record_id


ROOT = Path(__file__).resolve().parents[1]

RESONANCE_SUMMARY_FIELDS = [
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


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_enabled_directional_rule_lookup(rule_config: dict) -> dict[tuple[str, str], dict]:
    return {
        (rule["match"]["group_value"], rule["target_direction"]): rule
        for rule in rule_config["rules"]
        if rule.get("enabled", False)
    }


def analyze_f0(audio: np.ndarray, sample_rate: int, world_sr: int, frame_period_ms: float) -> tuple[np.ndarray, np.ndarray]:
    if sample_rate != world_sr:
        audio_world = librosa.resample(audio.astype(np.float32), orig_sr=sample_rate, target_sr=world_sr).astype(np.float64)
    else:
        audio_world = audio.astype(np.float64)
    import pyworld

    f0, time_axis = pyworld.harvest(audio_world, world_sr, frame_period=frame_period_ms, f0_floor=71.0, f0_ceil=800.0)
    f0 = pyworld.stonemask(audio_world, f0, time_axis, world_sr)
    return f0, time_axis


def frame_centers_sec(frame_count: int, frame_length: int, hop_length: int, sample_rate: int) -> np.ndarray:
    return (np.arange(frame_count, dtype=np.float64) * hop_length + frame_length / 2.0) / sample_rate


def interpolate_voiced_mask(frame_times_sec: np.ndarray, world_times_sec: np.ndarray, f0: np.ndarray) -> np.ndarray:
    if frame_times_sec.size == 0 or world_times_sec.size == 0 or f0.size == 0:
        return np.zeros(frame_times_sec.shape[0], dtype=np.float32)
    voiced = (f0 > 0.0).astype(np.float32)
    interpolated = np.interp(frame_times_sec, world_times_sec, voiced, left=voiced[0], right=voiced[-1])
    if interpolated.size > 2:
        interpolated = np.convolve(interpolated, np.array([0.2, 0.6, 0.2], dtype=np.float32), mode="same")
    return np.clip(interpolated.astype(np.float32), 0.0, 1.0)


def safe_rms(audio: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(audio.astype(np.float64))))) if audio.size else 0.0


def stable_lpc(frame: np.ndarray, order: int) -> np.ndarray | None:
    try:
        coeffs = librosa.lpc(frame.astype(np.float64), order=order)
    except Exception:
        return None
    coeffs = np.asarray(coeffs, dtype=np.float64)
    if not np.all(np.isfinite(coeffs)):
        return None
    roots = np.roots(coeffs)
    if roots.size == 0:
        return None
    clipped_roots = []
    for root in roots:
        radius = abs(root)
        angle = np.angle(root)
        if radius >= 0.995:
            radius = 0.995
        clipped_roots.append(radius * np.exp(1j * angle))
    stabilized = np.poly(np.array(clipped_roots, dtype=np.complex128)).real.astype(np.float64)
    if abs(stabilized[0]) <= 1e-8:
        return None
    return stabilized / stabilized[0]


def overlap_add(frames: list[np.ndarray], frame_length: int, hop_length: int, output_length: int) -> np.ndarray:
    if not frames:
        return np.zeros(output_length, dtype=np.float32)
    total_length = max(output_length, (len(frames) - 1) * hop_length + frame_length)
    output = np.zeros(total_length, dtype=np.float64)
    weight = np.zeros(total_length, dtype=np.float64)
    # These are full-amplitude time-domain frames, so synthesis needs a
    # window-normalized overlap-add instead of STFT-style direct summation.
    window = np.hanning(frame_length).astype(np.float64)
    for frame_idx, frame in enumerate(frames):
        start = frame_idx * hop_length
        output[start : start + frame_length] += frame.astype(np.float64) * window
        weight[start : start + frame_length] += window
    output = output / np.maximum(weight, 1e-8)
    return output[:output_length].astype(np.float32)


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
        writer = csv.DictWriter(f, fieldnames=RESONANCE_SUMMARY_FIELDS)
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
    pack_dir_rel = pack_dir.relative_to(ROOT).as_posix()
    lines = [
        f"# {pack_title} {pack_version}",
        "",
        f"- purpose: `{purpose}`",
        f"- rows: `{len(rows)}`",
        "",
        "## Rebuild",
        "",
        "```powershell",
        f".\\python.exe .\\scripts\\{script_name} `",
        f"  --rule-config {rule_config_rel} `",
        f"  --output-dir {pack_dir_rel}",
        ".\\python.exe .\\scripts\\build_stage0_rule_review_queue.py `",
        f"  --rule-config {rule_config_rel} `",
        f"  --summary-csv {summary_rel} `",
        f"  --output-csv {queue_rel} `",
        f"  --summary-md {summary_md_rel}",
        "```",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
