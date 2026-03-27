from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

import librosa
import numpy as np
import pyworld

from enrich_manifest_features import load_audio


ROOT = Path(__file__).resolve().parents[1]
FIXED_EVAL_INPUT = ROOT / "experiments" / "fixed_eval" / "v1_2" / "fixed_eval_review_final_v1_2.csv"
CLEAN_SPEECH_INPUT = ROOT / "data" / "datasets" / "_meta" / "utterance_manifest_clean_speech_v1.csv"
DEFAULT_INPUT_CSV = FIXED_EVAL_INPUT
DEFAULT_OUTPUT_DIR = ROOT / "experiments" / "representation_layer" / "v1_fixed_eval_pilot"

REPRESENTATION_NAMES = ["world_mel", "lpc_mel", "mfcc"]
VALID_GENDERS = {"female", "male"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-csv", default=str(DEFAULT_INPUT_CSV))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--samples-per-cell", type=int, default=0)
    parser.add_argument("--max-rows", type=int, default=0)
    parser.add_argument("--world-sr", type=int, default=16000)
    parser.add_argument("--frame-period-ms", type=float, default=10.0)
    parser.add_argument("--frame-length", type=int, default=1024)
    parser.add_argument("--hop-length", type=int, default=256)
    parser.add_argument("--lpc-order", type=int, default=16)
    parser.add_argument("--repr-n-fft", type=int, default=2048)
    parser.add_argument("--mel-bins", type=int, default=24)
    parser.add_argument("--mfcc-order", type=int, default=16)
    return parser.parse_args()


def resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return ROOT / path


def fmt_float(value: float | None, digits: int = 6) -> str:
    if value is None or math.isnan(value):
        return ""
    return f"{value:.{digits}f}"


def vector_json(value: np.ndarray | None) -> str:
    if value is None:
        return ""
    return json.dumps([float(x) for x in value], ensure_ascii=False)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    output: list[dict[str, str]] = []
    for row in rows:
        gender = row.get("gender", "")
        if gender not in VALID_GENDERS:
            continue
        if row.get("domain") and row.get("domain") != "speech":
            continue
        if row.get("usable_for_fixed_eval") and row.get("usable_for_fixed_eval") != "yes":
            continue
        if row.get("review_status") and row.get("review_status") != "reviewed":
            continue
        if not row.get("path_raw"):
            continue
        output.append(row)
    return output


def select_rows(rows: list[dict[str, str]], samples_per_cell: int, max_rows: int) -> list[dict[str, str]]:
    selected = rows
    if samples_per_cell > 0:
        grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
        for row in rows:
            grouped[(row.get("dataset_name", "unknown"), row["gender"])].append(row)
        selected = []
        for key in sorted(grouped):
            group_rows = sorted(grouped[key], key=lambda row: row.get("utt_id", ""))
            selected.extend(group_rows[:samples_per_cell])
    if max_rows > 0:
        selected = selected[:max_rows]
    return selected


def cosine_distance(a: np.ndarray, b: np.ndarray) -> float:
    a_norm = float(np.linalg.norm(a))
    b_norm = float(np.linalg.norm(b))
    if a_norm <= 1e-12 or b_norm <= 1e-12:
        return float("nan")
    cosine = float(np.dot(a, b) / (a_norm * b_norm))
    cosine = max(-1.0, min(1.0, cosine))
    return 1.0 - cosine


def mean_distance_to_centroid(vectors: list[np.ndarray]) -> float:
    if len(vectors) < 2:
        return float("nan")
    centroid = np.mean(np.stack(vectors, axis=0), axis=0)
    distances = [cosine_distance(vector, centroid) for vector in vectors]
    clean = [value for value in distances if not math.isnan(value)]
    return float(statistics.fmean(clean)) if clean else float("nan")


def continuity_l1(frames: np.ndarray) -> float:
    if frames.shape[0] < 2:
        return float("nan")
    deltas = np.abs(np.diff(frames, axis=0))
    return float(np.mean(deltas))


def ensure_audio_length(audio: np.ndarray, frame_length: int) -> np.ndarray:
    if audio.size >= frame_length:
        return audio
    pad = frame_length - int(audio.size)
    return np.pad(audio, (0, pad))


def analyze_world(audio: np.ndarray, sample_rate: int, world_sr: int, frame_period_ms: float) -> tuple[np.ndarray, np.ndarray, np.ndarray, int]:
    if sample_rate != world_sr:
        audio_world = librosa.resample(audio.astype(np.float32), orig_sr=sample_rate, target_sr=world_sr).astype(np.float64)
    else:
        audio_world = audio.astype(np.float64)
    f0, time_axis = pyworld.harvest(audio_world, world_sr, frame_period=frame_period_ms, f0_floor=71.0, f0_ceil=800.0)
    f0 = pyworld.stonemask(audio_world, f0, time_axis, world_sr)
    sp = pyworld.cheaptrick(audio_world, f0, time_axis, world_sr)
    return f0, time_axis, sp, world_sr


def voiced_mask_for_frame_times(frame_times_sec: np.ndarray, world_times_sec: np.ndarray, f0: np.ndarray) -> np.ndarray:
    if f0.size == 0 or world_times_sec.size == 0 or frame_times_sec.size == 0:
        return np.zeros(frame_times_sec.shape[0], dtype=np.float32)
    voiced = (f0 > 0.0).astype(np.float32)
    interpolated = np.interp(frame_times_sec, world_times_sec, voiced, left=voiced[0], right=voiced[-1])
    return np.clip(interpolated, 0.0, 1.0)


def compute_world_representation(
    *,
    sp: np.ndarray,
    f0: np.ndarray,
    world_sr: int,
    mel_bins: int,
) -> dict[str, object]:
    if sp.size == 0 or f0.size == 0:
        return {"status": "no_world_frames", "voiced_frames": 0, "continuity_l1": float("nan"), "vector": None}
    world_n_fft = max((sp.shape[1] - 1) * 2, 512)
    mel_basis = librosa.filters.mel(
        sr=world_sr,
        n_fft=world_n_fft,
        n_mels=mel_bins,
        fmin=80.0,
        fmax=min(7600.0, world_sr / 2.0),
    )
    mel_env = np.log(np.maximum(sp @ mel_basis.T, 1e-7))
    voiced_frames = mel_env[f0 > 0.0]
    if voiced_frames.shape[0] == 0:
        return {"status": "no_voiced_frames", "voiced_frames": 0, "continuity_l1": float("nan"), "vector": None}
    return {
        "status": "ok",
        "voiced_frames": int(voiced_frames.shape[0]),
        "continuity_l1": continuity_l1(voiced_frames),
        "vector": np.mean(voiced_frames, axis=0),
    }


def compute_lpc_representation(
    *,
    audio: np.ndarray,
    sample_rate: int,
    world_times_sec: np.ndarray,
    f0: np.ndarray,
    frame_length: int,
    hop_length: int,
    lpc_order: int,
    repr_n_fft: int,
    mel_bins: int,
) -> dict[str, object]:
    audio = ensure_audio_length(audio, frame_length).astype(np.float32)
    frames = librosa.util.frame(audio, frame_length=frame_length, hop_length=hop_length).T
    if frames.shape[0] == 0:
        return {"status": "no_frames", "voiced_frames": 0, "continuity_l1": float("nan"), "vector": None}
    frame_times_sec = (np.arange(frames.shape[0]) * hop_length + frame_length / 2.0) / sample_rate
    voiced_mask = voiced_mask_for_frame_times(frame_times_sec, world_times_sec, f0)
    mel_basis = librosa.filters.mel(sr=sample_rate, n_fft=repr_n_fft, n_mels=mel_bins, fmin=80.0, fmax=min(7600.0, sample_rate / 2.0))
    window = np.hanning(frame_length).astype(np.float32)
    voiced_vectors: list[np.ndarray] = []
    for frame, voiced_value in zip(frames, voiced_mask, strict=False):
        if voiced_value < 0.5:
            continue
        try:
            lpc = librosa.lpc((frame * window).astype(np.float64), order=lpc_order)
        except Exception:
            continue
        response = np.abs(np.fft.rfft(lpc, n=repr_n_fft))
        envelope = 1.0 / np.maximum(response, 1e-6)
        mel_env = np.log(np.maximum(mel_basis @ envelope, 1e-7))
        voiced_vectors.append(mel_env.astype(np.float32))
    if not voiced_vectors:
        return {"status": "no_voiced_frames", "voiced_frames": 0, "continuity_l1": float("nan"), "vector": None}
    voiced_matrix = np.stack(voiced_vectors, axis=0)
    return {
        "status": "ok",
        "voiced_frames": int(voiced_matrix.shape[0]),
        "continuity_l1": continuity_l1(voiced_matrix),
        "vector": np.mean(voiced_matrix, axis=0),
    }


def compute_mfcc_representation(
    *,
    audio: np.ndarray,
    sample_rate: int,
    world_times_sec: np.ndarray,
    f0: np.ndarray,
    frame_length: int,
    hop_length: int,
    mfcc_order: int,
) -> dict[str, object]:
    audio = ensure_audio_length(audio, frame_length).astype(np.float32)
    mel_power = librosa.feature.melspectrogram(
        y=audio,
        sr=sample_rate,
        n_fft=frame_length,
        hop_length=hop_length,
        win_length=frame_length,
        center=False,
        n_mels=max(40, mfcc_order * 3),
        fmin=80.0,
        fmax=min(7600.0, sample_rate / 2.0),
    )
    mfcc = librosa.feature.mfcc(S=librosa.power_to_db(mel_power), n_mfcc=mfcc_order).T
    if mfcc.shape[0] == 0:
        return {"status": "no_frames", "voiced_frames": 0, "continuity_l1": float("nan"), "vector": None}
    frame_times_sec = (np.arange(mfcc.shape[0]) * hop_length + frame_length / 2.0) / sample_rate
    voiced_mask = voiced_mask_for_frame_times(frame_times_sec, world_times_sec, f0)
    voiced_frames = mfcc[voiced_mask >= 0.5]
    if voiced_frames.shape[0] == 0:
        return {"status": "no_voiced_frames", "voiced_frames": 0, "continuity_l1": float("nan"), "vector": None}
    return {
        "status": "ok",
        "voiced_frames": int(voiced_frames.shape[0]),
        "continuity_l1": continuity_l1(voiced_frames),
        "vector": np.mean(voiced_frames, axis=0),
    }


def extract_row(row: dict[str, str], args: argparse.Namespace) -> dict[str, str]:
    audio_path = resolve_path(row["path_raw"])
    audio, sample_rate = load_audio(audio_path)
    audio = np.asarray(audio, dtype=np.float64)
    duration_sec = float(audio.shape[0] / sample_rate)

    f0, world_times_sec, sp, world_sr = analyze_world(audio, sample_rate, args.world_sr, args.frame_period_ms)
    voiced_ratio = float(np.mean(f0 > 0.0)) if f0.size else float("nan")
    f0_voiced = f0[f0 > 0.0]
    f0_median_hz = float(np.median(f0_voiced)) if f0_voiced.size else float("nan")

    world_repr = compute_world_representation(
        sp=sp,
        f0=f0,
        world_sr=world_sr,
        mel_bins=args.mel_bins,
    )
    lpc_repr = compute_lpc_representation(
        audio=audio,
        sample_rate=sample_rate,
        world_times_sec=world_times_sec,
        f0=f0,
        frame_length=args.frame_length,
        hop_length=args.hop_length,
        lpc_order=args.lpc_order,
        repr_n_fft=args.repr_n_fft,
        mel_bins=args.mel_bins,
    )
    mfcc_repr = compute_mfcc_representation(
        audio=audio,
        sample_rate=sample_rate,
        world_times_sec=world_times_sec,
        f0=f0,
        frame_length=args.frame_length,
        hop_length=args.hop_length,
        mfcc_order=args.mfcc_order,
    )

    out = {
        "utt_id": row.get("utt_id", ""),
        "dataset_name": row.get("dataset_name", "unknown"),
        "gender": row["gender"],
        "path_raw": str(audio_path),
        "duration_sec": fmt_float(duration_sec),
        "world_voiced_ratio": fmt_float(voiced_ratio),
        "world_f0_median_hz": fmt_float(f0_median_hz),
    }
    for name, payload in [("world_mel", world_repr), ("lpc_mel", lpc_repr), ("mfcc", mfcc_repr)]:
        out[f"{name}_status"] = str(payload["status"])
        out[f"{name}_voiced_frames"] = str(payload["voiced_frames"])
        out[f"{name}_continuity_l1"] = fmt_float(float(payload["continuity_l1"]) if not math.isnan(float(payload["continuity_l1"])) else float("nan"))
        out[f"{name}_vector_json"] = vector_json(payload["vector"])
    return out


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"No rows to write for {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def parse_vector(value: str) -> np.ndarray | None:
    if not value:
        return None
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return None
    if not parsed:
        return None
    return np.asarray(parsed, dtype=np.float64)


def build_group_summary(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row["dataset_name"], row["gender"])].append(row)

    output: list[dict[str, str]] = []
    datasets = sorted({row["dataset_name"] for row in rows})
    for dataset_name in datasets:
        female_rows = grouped.get((dataset_name, "female"), [])
        male_rows = grouped.get((dataset_name, "male"), [])
        for representation in REPRESENTATION_NAMES:
            female_vectors = [parse_vector(row[f"{representation}_vector_json"]) for row in female_rows if row.get(f"{representation}_status") == "ok"]
            male_vectors = [parse_vector(row[f"{representation}_vector_json"]) for row in male_rows if row.get(f"{representation}_status") == "ok"]
            female_vectors = [value for value in female_vectors if value is not None]
            male_vectors = [value for value in male_vectors if value is not None]
            female_cont = [float(row[f"{representation}_continuity_l1"]) for row in female_rows if row.get(f"{representation}_continuity_l1")]
            male_cont = [float(row[f"{representation}_continuity_l1"]) for row in male_rows if row.get(f"{representation}_continuity_l1")]

            between = float("nan")
            if female_vectors and male_vectors:
                female_mean = np.mean(np.stack(female_vectors, axis=0), axis=0)
                male_mean = np.mean(np.stack(male_vectors, axis=0), axis=0)
                between = cosine_distance(female_mean, male_mean)

            female_within = mean_distance_to_centroid(female_vectors)
            male_within = mean_distance_to_centroid(male_vectors)
            within_values = [value for value in [female_within, male_within] if not math.isnan(value)]
            within_mean = float(statistics.fmean(within_values)) if within_values else float("nan")
            separation_ratio = between / within_mean if within_values and not math.isnan(between) and abs(within_mean) > 1e-12 else float("nan")

            output.append(
                {
                    "dataset_name": dataset_name,
                    "representation": representation,
                    "female_count": str(len(female_vectors)),
                    "male_count": str(len(male_vectors)),
                    "between_gender_cosine_distance": fmt_float(between),
                    "within_female_cosine_distance_mean": fmt_float(female_within),
                    "within_male_cosine_distance_mean": fmt_float(male_within),
                    "separation_ratio": fmt_float(separation_ratio),
                    "female_continuity_l1_mean": fmt_float(statistics.fmean(female_cont) if female_cont else float("nan")),
                    "male_continuity_l1_mean": fmt_float(statistics.fmean(male_cont) if male_cont else float("nan")),
                }
            )
    return output


def build_readme(path: Path, *, input_csv: Path, rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    top_rows = sorted(
        summary_rows,
        key=lambda row: float(row["separation_ratio"]) if row.get("separation_ratio") else -1.0,
        reverse=True,
    )[:6]
    lines = [
        "# Representation Layer Probe v1",
        "",
        "- purpose: `compare candidate tract/resonance representations before further editing work`",
        f"- input_csv: `{input_csv.relative_to(ROOT).as_posix() if input_csv.is_relative_to(ROOT) else input_csv}`",
        f"- rows: `{len(rows)}`",
        "",
        "## Representations",
        "",
        "- `world_mel`: WORLD cheaptrick 谱包络压到 mel bins 后做 voiced 平均",
        "- `lpc_mel`: LPC 包络频响压到 mel bins 后做 voiced 平均",
        "- `mfcc`: voiced 段 MFCC 平均，作为低阶 cepstral envelope proxy",
        "",
        "## Top Separation Rows",
        "",
    ]
    if not top_rows:
        lines.append("- none")
    else:
        for row in top_rows:
            lines.append(
                f"- `{row['dataset_name']}` / `{row['representation']}` | "
                f"between=`{row['between_gender_cosine_distance'] or 'n/a'}` | "
                f"sep_ratio=`{row['separation_ratio'] or 'n/a'}`"
            )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- 这个 probe 只回答表示是否稳定、是否携带性别相关分离度，不直接回答编辑是否有效。",
            "- 下一步应基于 separation / continuity 结果，选择 1-2 条表示进入真正的编辑与重建阶段。",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    input_csv = resolve_path(args.input_csv)
    output_dir = resolve_path(args.output_dir)
    rows = select_rows(read_rows(input_csv), samples_per_cell=args.samples_per_cell, max_rows=args.max_rows)
    extracted_rows = [extract_row(row, args) for row in rows]
    summary_rows = build_group_summary(extracted_rows)

    write_rows(output_dir / "representation_probe_rows.csv", extracted_rows)
    write_rows(output_dir / "representation_probe_summary.csv", summary_rows)
    build_readme(output_dir / "README.md", input_csv=input_csv, rows=extracted_rows, summary_rows=summary_rows)

    print(f"Wrote {output_dir / 'representation_probe_rows.csv'}")
    print(f"Wrote {output_dir / 'representation_probe_summary.csv'}")
    print(f"Wrote {output_dir / 'README.md'}")
    print(f"Rows: {len(extracted_rows)}")


if __name__ == "__main__":
    main()
