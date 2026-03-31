from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path

import librosa
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUEUE_CSVS = [
    ROOT
    / "artifacts"
    / "listening_review"
    / "stage0_atrr_vocoder_bigvgan_fixed8"
    / "blend075_pc150_cap200_v1"
    / "listening_review_queue.csv",
    ROOT
    / "artifacts"
    / "listening_review"
    / "stage0_speech_lsf_machine_sweep_v9_fixed8"
    / "split_core_focus_v9a"
    / "listening_review_queue.csv",
]
DEFAULT_OUTPUT_DIR = ROOT / "artifacts" / "diagnostics" / "speech_structure_audit" / "v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue-csv", action="append", default=[])
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--target-sr", type=int, default=24000)
    parser.add_argument("--n-fft", type=int, default=1024)
    parser.add_argument("--hop-length", type=int, default=256)
    parser.add_argument("--n-mels", type=int, default=40)
    parser.add_argument("--n-mfcc", type=int, default=13)
    return parser.parse_args()


def resolve_path(value: str | Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return ROOT / path


def parse_float(value: str | float | int | None) -> float | None:
    if value in (None, ""):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(result):
        return None
    return result


def fmt_float(value: float | None, digits: int = 4) -> str:
    if value is None or not math.isfinite(value):
        return ""
    return f"{value:.{digits}f}"


def load_audio_mono(path: Path, target_sr: int) -> np.ndarray:
    audio, sr = librosa.load(path, sr=target_sr, mono=True)
    return np.asarray(audio, dtype=np.float32)


def align_vector_length(vector: np.ndarray, target_length: int) -> np.ndarray:
    source = np.asarray(vector, dtype=np.float64).reshape(-1)
    if target_length <= 0:
        raise ValueError("target_length must be positive")
    if source.shape[0] == target_length:
        return source
    if source.shape[0] <= 1:
        fill_value = float(source[0]) if source.shape[0] == 1 else 0.0
        return np.full(target_length, fill_value, dtype=np.float64)
    x_old = np.linspace(0.0, 1.0, num=source.shape[0], endpoint=True)
    x_new = np.linspace(0.0, 1.0, num=target_length, endpoint=True)
    return np.interp(x_new, x_old, source).astype(np.float64)


def align_feature_columns(matrix: np.ndarray, target_frames: int) -> np.ndarray:
    source = np.asarray(matrix, dtype=np.float64)
    if source.shape[1] == target_frames:
        return source
    aligned = np.empty((source.shape[0], target_frames), dtype=np.float64)
    x_old = np.linspace(0.0, 1.0, num=source.shape[1], endpoint=True)
    x_new = np.linspace(0.0, 1.0, num=target_frames, endpoint=True)
    for idx in range(source.shape[0]):
        aligned[idx] = np.interp(x_new, x_old, source[idx])
    return aligned


def compute_logmel(audio: np.ndarray, *, sr: int, n_fft: int, hop_length: int, n_mels: int) -> np.ndarray:
    mel = librosa.feature.melspectrogram(
        y=audio,
        sr=sr,
        n_fft=n_fft,
        hop_length=hop_length,
        n_mels=n_mels,
        power=2.0,
    )
    return np.log(np.maximum(mel, 1e-12)).astype(np.float64)


def compute_mfcc(audio: np.ndarray, *, sr: int, n_fft: int, hop_length: int, n_mels: int, n_mfcc: int) -> np.ndarray:
    mel = librosa.feature.melspectrogram(
        y=audio,
        sr=sr,
        n_fft=n_fft,
        hop_length=hop_length,
        n_mels=n_mels,
        power=2.0,
    )
    db = librosa.power_to_db(np.maximum(mel, 1e-12), ref=1.0)
    return librosa.feature.mfcc(S=db, n_mfcc=n_mfcc).astype(np.float64)


def normalized_dtw_cost(x: np.ndarray, y: np.ndarray, metric: str) -> float:
    _, wp = librosa.sequence.dtw(X=x, Y=y, metric=metric)
    wp = np.asarray(wp[::-1], dtype=np.int64)
    if wp.size == 0:
        return float("nan")
    total = 0.0
    for xi, yi in wp:
        if metric == "cosine":
            xv = x[:, xi]
            yv = y[:, yi]
            denom = float(np.linalg.norm(xv) * np.linalg.norm(yv))
            cost = 1.0 if denom <= 1e-12 else 1.0 - float(np.dot(xv, yv) / denom)
        else:
            cost = float(np.mean(np.abs(x[:, xi] - y[:, yi])))
        total += cost
    return float(total / len(wp))


def compute_f0(audio: np.ndarray, *, sr: int, n_fft: int, hop_length: int) -> np.ndarray:
    f0, _, _ = librosa.pyin(
        audio,
        fmin=librosa.note_to_hz("C2"),
        fmax=librosa.note_to_hz("C6"),
        sr=sr,
        frame_length=n_fft,
        hop_length=hop_length,
    )
    return np.asarray(f0, dtype=np.float64)


def harmonic_share(audio: np.ndarray) -> float:
    harmonic, percussive = librosa.effects.hpss(audio)
    harmonic_energy = float(np.sum(np.square(harmonic.astype(np.float64))))
    total_energy = float(np.sum(np.square(audio.astype(np.float64))))
    if total_energy <= 1e-12:
        return 0.0
    return harmonic_energy / total_energy


def mean_log_spectral_flatness(audio: np.ndarray, *, n_fft: int, hop_length: int) -> float:
    flatness = librosa.feature.spectral_flatness(y=audio, n_fft=n_fft, hop_length=hop_length)
    return float(np.mean(np.log10(np.maximum(flatness, 1e-12))))


def evaluate_pair(
    source_audio: np.ndarray,
    processed_audio: np.ndarray,
    *,
    sr: int,
    n_fft: int,
    hop_length: int,
    n_mels: int,
    n_mfcc: int,
) -> dict[str, float]:
    logmel_src = compute_logmel(source_audio, sr=sr, n_fft=n_fft, hop_length=hop_length, n_mels=n_mels)
    logmel_proc = compute_logmel(processed_audio, sr=sr, n_fft=n_fft, hop_length=hop_length, n_mels=n_mels)
    mfcc_src = compute_mfcc(source_audio, sr=sr, n_fft=n_fft, hop_length=hop_length, n_mels=n_mels, n_mfcc=n_mfcc)
    mfcc_proc = compute_mfcc(processed_audio, sr=sr, n_fft=n_fft, hop_length=hop_length, n_mels=n_mels, n_mfcc=n_mfcc)

    target_frames = max(logmel_src.shape[1], logmel_proc.shape[1])
    f0_src = align_vector_length(compute_f0(source_audio, sr=sr, n_fft=n_fft, hop_length=hop_length), target_frames)
    f0_proc = align_vector_length(compute_f0(processed_audio, sr=sr, n_fft=n_fft, hop_length=hop_length), target_frames)

    src_voiced = np.isfinite(f0_src)
    proc_voiced = np.isfinite(f0_proc)
    voiced_union = src_voiced | proc_voiced
    voiced_both = src_voiced & proc_voiced

    if np.any(voiced_both):
        cents = np.abs(1200.0 * np.log2(np.maximum(f0_proc[voiced_both], 1e-6) / np.maximum(f0_src[voiced_both], 1e-6)))
        f0_overlap_mae_cents = float(np.mean(cents))
        x = np.log2(np.maximum(f0_src[voiced_both], 1e-6))
        y = np.log2(np.maximum(f0_proc[voiced_both], 1e-6))
        if x.size >= 2 and float(np.std(x)) > 1e-8 and float(np.std(y)) > 1e-8:
            f0_overlap_corr = float(np.corrcoef(x, y)[0, 1])
        else:
            f0_overlap_corr = float("nan")
    else:
        f0_overlap_mae_cents = float("nan")
        f0_overlap_corr = float("nan")

    return {
        "duration_drift_ms": (len(processed_audio) - len(source_audio)) / sr * 1000.0,
        "logmel_dtw_l1": normalized_dtw_cost(logmel_src, logmel_proc, metric="euclidean"),
        "mfcc_dtw_cosine": normalized_dtw_cost(mfcc_src, mfcc_proc, metric="cosine"),
        "voiced_overlap_iou": float(np.sum(voiced_both) / max(np.sum(voiced_union), 1)),
        "f0_overlap_mae_cents": f0_overlap_mae_cents,
        "f0_overlap_corr": f0_overlap_corr,
        "harmonic_share_src": harmonic_share(source_audio),
        "harmonic_share_proc": harmonic_share(processed_audio),
        "harmonic_share_delta": harmonic_share(processed_audio) - harmonic_share(source_audio),
        "mean_log_flatness_src": mean_log_spectral_flatness(source_audio, n_fft=n_fft, hop_length=hop_length),
        "mean_log_flatness_proc": mean_log_spectral_flatness(processed_audio, n_fft=n_fft, hop_length=hop_length),
        "mean_log_flatness_delta": mean_log_spectral_flatness(processed_audio, n_fft=n_fft, hop_length=hop_length)
        - mean_log_spectral_flatness(source_audio, n_fft=n_fft, hop_length=hop_length),
        "zcr_src": float(np.mean(librosa.feature.zero_crossing_rate(source_audio, frame_length=n_fft, hop_length=hop_length))),
        "zcr_proc": float(np.mean(librosa.feature.zero_crossing_rate(processed_audio, frame_length=n_fft, hop_length=hop_length))),
        "zcr_delta": float(
            np.mean(librosa.feature.zero_crossing_rate(processed_audio, frame_length=n_fft, hop_length=hop_length))
            - np.mean(librosa.feature.zero_crossing_rate(source_audio, frame_length=n_fft, hop_length=hop_length))
        ),
    }


def structure_risk_score(metrics: dict[str, float]) -> float:
    score = 0.0
    score += min(max(metrics["logmel_dtw_l1"] / 1.2, 0.0), 1.0) * 30.0
    score += min(max(metrics["mfcc_dtw_cosine"] / 0.20, 0.0), 1.0) * 20.0
    score += min(max((1.0 - metrics["voiced_overlap_iou"]) / 0.60, 0.0), 1.0) * 15.0
    f0_mae = metrics["f0_overlap_mae_cents"]
    if math.isfinite(f0_mae):
        score += min(max(f0_mae / 220.0, 0.0), 1.0) * 20.0
    flat_delta = metrics["mean_log_flatness_delta"]
    score += min(max(flat_delta / 0.25, 0.0), 1.0) * 10.0
    zcr_delta = metrics["zcr_delta"]
    score += min(max(zcr_delta / 0.04, 0.0), 1.0) * 5.0
    return float(score)


def queue_label_from_path(path: Path) -> str:
    try:
        return path.parent.relative_to(ROOT / "artifacts" / "listening_review").as_posix()
    except ValueError:
        return path.parent.name


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    queue_csvs = [resolve_path(path) for path in (args.queue_csv or [])] or [resolve_path(path) for path in DEFAULT_QUEUE_CSVS]
    output_dir = resolve_path(args.output_dir)

    row_output: list[dict[str, str]] = []
    pack_output: list[dict[str, str]] = []

    for queue_csv in queue_csvs:
        with queue_csv.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        queue_label = queue_label_from_path(queue_csv)
        per_pack: list[dict[str, float | str]] = []
        for row in rows:
            source_path = resolve_path(row["input_audio"])
            processed_path = resolve_path(row["processed_audio"])
            source_audio = load_audio_mono(source_path, args.target_sr)
            processed_audio = load_audio_mono(processed_path, args.target_sr)
            metrics = evaluate_pair(
                source_audio,
                processed_audio,
                sr=args.target_sr,
                n_fft=args.n_fft,
                hop_length=args.hop_length,
                n_mels=args.n_mels,
                n_mfcc=args.n_mfcc,
            )
            risk_score = structure_risk_score(metrics)
            reviewed_artifact = row.get("artifact_issue", "")
            reviewed_audible = row.get("effect_audible", "")
            output_row = {
                "queue_label": queue_label,
                "record_id": row["record_id"],
                "rule_id": row["rule_id"],
                "reviewed_artifact_issue": reviewed_artifact,
                "reviewed_effect_audible": reviewed_audible,
                **{key: fmt_float(value) for key, value in metrics.items()},
                "structure_risk_score": fmt_float(risk_score, digits=2),
            }
            row_output.append(output_row)
            per_pack.append({"record_id": row["record_id"], **metrics, "structure_risk_score": risk_score})

        def avg(field: str) -> float:
            values = [float(item[field]) for item in per_pack if math.isfinite(float(item[field]))]
            return float(sum(values) / len(values)) if values else float("nan")

        top_risk = sorted(per_pack, key=lambda item: float(item["structure_risk_score"]), reverse=True)[:3]
        pack_output.append(
            {
                "queue_label": queue_label,
                "rows": str(len(per_pack)),
                "avg_logmel_dtw_l1": fmt_float(avg("logmel_dtw_l1")),
                "avg_mfcc_dtw_cosine": fmt_float(avg("mfcc_dtw_cosine")),
                "avg_voiced_overlap_iou": fmt_float(avg("voiced_overlap_iou")),
                "avg_f0_overlap_mae_cents": fmt_float(avg("f0_overlap_mae_cents")),
                "avg_harmonic_share_delta": fmt_float(avg("harmonic_share_delta")),
                "avg_mean_log_flatness_delta": fmt_float(avg("mean_log_flatness_delta")),
                "avg_zcr_delta": fmt_float(avg("zcr_delta")),
                "avg_structure_risk_score": fmt_float(avg("structure_risk_score"), digits=2),
                "top_risk_records": ";".join(item["record_id"] for item in top_risk),
            }
        )

    row_csv = output_dir / "speech_structure_row_audit.csv"
    pack_csv = output_dir / "speech_structure_pack_audit.csv"
    md_path = output_dir / "SPEECH_STRUCTURE_AUDIT.md"
    row_fields = list(row_output[0].keys()) if row_output else []
    pack_fields = list(pack_output[0].keys()) if pack_output else []
    write_csv(row_csv, row_fields, row_output)
    write_csv(pack_csv, pack_fields, pack_output)

    lines = [
        "# Speech Structure Audit v1",
        "",
        "## Scope",
        "",
        "- This audit measures source-to-processed structural distortion directly.",
        "- It is designed for packs where target-resonance judgment is blocked by audible synthesis artifacts.",
        "",
        "## Pack Summary",
        "",
    ]
    for row in pack_output:
        lines.extend(
            [
                f"### `{row['queue_label']}`",
                "",
                f"- rows: `{row['rows']}`",
                f"- avg logmel_dtw_l1: `{row['avg_logmel_dtw_l1']}`",
                f"- avg mfcc_dtw_cosine: `{row['avg_mfcc_dtw_cosine']}`",
                f"- avg voiced_overlap_iou: `{row['avg_voiced_overlap_iou']}`",
                f"- avg f0_overlap_mae_cents: `{row['avg_f0_overlap_mae_cents']}`",
                f"- avg harmonic_share_delta: `{row['avg_harmonic_share_delta']}`",
                f"- avg mean_log_flatness_delta: `{row['avg_mean_log_flatness_delta']}`",
                f"- avg zcr_delta: `{row['avg_zcr_delta']}`",
                f"- avg structure_risk_score: `{row['avg_structure_risk_score']}`",
                f"- top risk records: `{row['top_risk_records']}`",
                "",
            ]
        )
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {row_csv}")
    print(f"Wrote {pack_csv}")
    print(f"Wrote {md_path}")
    print(f"Queues: {len(queue_csvs)}")


if __name__ == "__main__":
    main()
