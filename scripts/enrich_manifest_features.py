from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import librosa
import numpy as np
import pyworld
import soundfile as sf


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input CSV manifest path relative to repo root or absolute path.")
    parser.add_argument("--output", required=True, help="Output CSV path relative to repo root or absolute path.")
    parser.add_argument("--f0-sr", type=int, default=16000, help="Sample rate used for F0 extraction.")
    parser.add_argument("--frame-period-ms", type=float, default=10.0, help="Frame period for WORLD harvest.")
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


def load_audio(path: Path) -> tuple[np.ndarray, int]:
    audio, sample_rate = sf.read(path, always_2d=False)
    audio = np.asarray(audio, dtype=np.float64)
    if audio.ndim == 2:
        audio = audio.mean(axis=1)
    if audio.size == 0:
        raise ValueError("empty audio")
    return audio, sample_rate


def dbfs(value: float) -> float:
    return 20.0 * math.log10(max(value, 1e-12))


def compute_features(audio: np.ndarray, sample_rate: int, f0_sr: int, frame_period_ms: float) -> dict[str, str]:
    peak_abs = float(np.max(np.abs(audio)))
    rms = float(np.sqrt(np.mean(np.square(audio))))
    clipping_ratio = float(np.mean(np.abs(audio) >= 0.999))

    frame_length = min(2048, max(256, audio.shape[0]))
    hop_length = max(128, frame_length // 4)

    rms_frames = librosa.feature.rms(y=audio.astype(np.float32), frame_length=frame_length, hop_length=hop_length)[0]
    rms_db = np.array([dbfs(float(x)) for x in rms_frames], dtype=np.float64)
    max_rms_db = float(np.max(rms_db))
    silence_ratio_40db = float(np.mean(rms_db <= (max_rms_db - 40.0)))

    zcr_mean = float(
        np.mean(
            librosa.feature.zero_crossing_rate(
                y=audio.astype(np.float32),
                frame_length=frame_length,
                hop_length=hop_length,
            )[0]
        )
    )
    spectral_centroid_hz = float(
        np.mean(
            librosa.feature.spectral_centroid(
                y=audio.astype(np.float32),
                sr=sample_rate,
                n_fft=frame_length,
                hop_length=hop_length,
            )[0]
        )
    )

    if sample_rate != f0_sr:
        audio_f0 = librosa.resample(audio.astype(np.float32), orig_sr=sample_rate, target_sr=f0_sr).astype(np.float64)
    else:
        audio_f0 = audio

    f0, _ = pyworld.harvest(audio_f0, f0_sr, frame_period=frame_period_ms)
    voiced = f0[f0 > 0]
    f0_voiced_ratio = float(len(voiced) / len(f0)) if len(f0) else 0.0
    f0_median = float(np.median(voiced)) if len(voiced) else float("nan")
    f0_p10 = float(np.percentile(voiced, 10)) if len(voiced) else float("nan")
    f0_p90 = float(np.percentile(voiced, 90)) if len(voiced) else float("nan")

    return {
        "feature_status": "ok",
        "feature_error": "",
        "rms_dbfs": fmt_float(dbfs(rms)),
        "peak_dbfs": fmt_float(dbfs(peak_abs)),
        "clipping_ratio": fmt_float(clipping_ratio),
        "silence_ratio_40db": fmt_float(silence_ratio_40db),
        "zcr_mean": fmt_float(zcr_mean),
        "spectral_centroid_hz_mean": fmt_float(spectral_centroid_hz),
        "f0_voiced_ratio": fmt_float(f0_voiced_ratio),
        "f0_median_hz": fmt_float(f0_median),
        "f0_p10_hz": fmt_float(f0_p10),
        "f0_p90_hz": fmt_float(f0_p90),
    }


def enrich_row(row: dict[str, str], f0_sr: int, frame_period_ms: float) -> dict[str, str]:
    path_raw = row["path_raw"]
    audio_path = resolve_path(path_raw)
    out_row = dict(row)
    try:
        audio, sample_rate = load_audio(audio_path)
        out_row.update(compute_features(audio, sample_rate, f0_sr=f0_sr, frame_period_ms=frame_period_ms))
    except Exception as exc:
        out_row.update(
            {
                "feature_status": "error",
                "feature_error": f"{type(exc).__name__}: {exc}",
                "rms_dbfs": "",
                "peak_dbfs": "",
                "clipping_ratio": "",
                "silence_ratio_40db": "",
                "zcr_mean": "",
                "spectral_centroid_hz_mean": "",
                "f0_voiced_ratio": "",
                "f0_median_hz": "",
                "f0_p10_hz": "",
                "f0_p90_hz": "",
            }
        )
    return out_row


def main() -> None:
    args = parse_args()
    in_csv = resolve_path(args.input)
    out_csv = resolve_path(args.output)

    with in_csv.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    enriched_rows = [enrich_row(row, f0_sr=args.f0_sr, frame_period_ms=args.frame_period_ms) for row in rows]

    base_fieldnames = list(rows[0].keys()) if rows else []
    extra_fieldnames = [
        "feature_status",
        "feature_error",
        "rms_dbfs",
        "peak_dbfs",
        "clipping_ratio",
        "silence_ratio_40db",
        "zcr_mean",
        "spectral_centroid_hz_mean",
        "f0_voiced_ratio",
        "f0_median_hz",
        "f0_p10_hz",
        "f0_p90_hz",
    ]

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=base_fieldnames + extra_fieldnames)
        writer.writeheader()
        writer.writerows(enriched_rows)

    ok_count = sum(1 for row in enriched_rows if row["feature_status"] == "ok")
    print(f"Wrote {out_csv}")
    print(f"Rows: {len(enriched_rows)}")
    print(f"Feature OK: {ok_count}")
    print(f"Feature errors: {len(enriched_rows) - ok_count}")


if __name__ == "__main__":
    main()
