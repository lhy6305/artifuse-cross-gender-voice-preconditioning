from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import librosa
import numpy as np

from enrich_manifest_features import compute_features, load_audio


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RULE_CONFIG = ROOT / "experiments" / "stage0_baseline" / "v1_full" / "rule_candidate_v1.json"
DEFAULT_SUMMARY_CSV = ROOT / "tmp" / "stage0_rule_listening_pack" / "v1" / "listening_pack_summary.csv"
DEFAULT_OUTPUT_CSV = ROOT / "tmp" / "stage0_rule_listening_pack" / "v1" / "listening_review_queue.csv"
DEFAULT_SUMMARY_MD = ROOT / "tmp" / "stage0_rule_listening_pack" / "v1" / "listening_review_quant_summary.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rule-config", default=str(DEFAULT_RULE_CONFIG))
    parser.add_argument("--summary-csv", default=str(DEFAULT_SUMMARY_CSV))
    parser.add_argument("--output-csv", default=str(DEFAULT_OUTPUT_CSV))
    parser.add_argument("--summary-md", default=str(DEFAULT_SUMMARY_MD))
    parser.add_argument("--f0-sr", type=int, default=16000)
    parser.add_argument("--frame-period-ms", type=float, default=10.0)
    parser.add_argument("--n-fft", type=int, default=2048)
    parser.add_argument("--hop-length", type=int, default=512)
    return parser.parse_args()


def resolve_path(value: str) -> Path:
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


def fmt_float(value: float | None, digits: int = 6) -> str:
    if value is None or math.isnan(value):
        return ""
    return f"{value:.{digits}f}"


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def load_rule_lookup(path: Path) -> dict[str, dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {row["rule_id"]: row for row in payload["rules"]}


def feature_map(audio: np.ndarray, sample_rate: int, f0_sr: int, frame_period_ms: float) -> dict[str, float | None]:
    raw = compute_features(audio, sample_rate, f0_sr=f0_sr, frame_period_ms=frame_period_ms)
    return {key: parse_float(value) for key, value in raw.items() if key not in {"feature_status", "feature_error"}}


def log_centroid_minus_log_f0(features: dict[str, float | None]) -> float | None:
    centroid = features.get("spectral_centroid_hz_mean")
    f0_median = features.get("f0_median_hz")
    if centroid in (None, 0.0) or f0_median in (None, 0.0):
        return None
    return math.log10(max(centroid, 1e-6)) - math.log10(max(f0_median, 1e-6))


def band_share_db(
    audio: np.ndarray,
    sample_rate: int,
    n_fft: int,
    hop_length: int,
) -> dict[str, float]:
    stft = librosa.stft(audio.astype(np.float32), n_fft=n_fft, hop_length=hop_length)
    power = np.mean(np.abs(stft) ** 2, axis=1)
    freqs = librosa.fft_frequencies(sr=sample_rate, n_fft=n_fft)
    total = max(float(np.sum(power)), 1e-12)

    def share(low_hz: float, high_hz: float) -> float:
        mask = (freqs >= low_hz) & (freqs < high_hz)
        value = float(np.sum(power[mask]))
        return 10.0 * math.log10(max(value, 1e-12) / total)

    return {
        "low_mid_0_1500_share_db": share(0.0, 1500.0),
        "presence_1500_3000_share_db": share(1500.0, 3000.0),
        "brilliance_3000_8000_share_db": share(3000.0, min(8000.0, sample_rate / 2.0)),
    }


def waveform_diff(original: np.ndarray, processed: np.ndarray) -> dict[str, float]:
    length = min(len(original), len(processed))
    if length == 0:
        return {"waveform_mean_abs_diff": 0.0, "waveform_max_abs_diff": 0.0}
    diff = np.abs(processed[:length] - original[:length])
    return {
        "waveform_mean_abs_diff": float(np.mean(diff)),
        "waveform_max_abs_diff": float(np.max(diff)),
    }


def stft_logmag_l1(
    original: np.ndarray,
    processed: np.ndarray,
    n_fft: int,
    hop_length: int,
) -> float:
    length = min(len(original), len(processed))
    if length == 0:
        return 0.0
    orig_stft = librosa.stft(original[:length].astype(np.float32), n_fft=n_fft, hop_length=hop_length)
    proc_stft = librosa.stft(processed[:length].astype(np.float32), n_fft=n_fft, hop_length=hop_length)
    log_orig = np.log1p(np.abs(orig_stft))
    log_proc = np.log1p(np.abs(proc_stft))
    return float(np.mean(np.abs(log_proc - log_orig)))


def delta(new_value: float | None, old_value: float | None) -> float | None:
    if new_value is None or old_value is None:
        return None
    return new_value - old_value


def pct_delta(new_value: float | None, old_value: float | None) -> float | None:
    if new_value is None or old_value in (None, 0.0):
        return None
    return (new_value - old_value) / old_value * 100.0


def action_expected_sign(action_family: str) -> float:
    return 1.0 if action_family == "brightness_up" else -1.0


def direction_control_delta(action_family: str, delta_low_mid_share_db: float | None, delta_brilliance_share_db: float | None) -> float | None:
    if action_family == "brightness_up":
        return delta_brilliance_share_db
    if delta_low_mid_share_db is None:
        return None
    return -delta_low_mid_share_db


def build_auto_notes(
    *,
    signed_primary_delta: float | None,
    effect_score: float,
    preservation_score: float,
    delta_f0_median_pct: float | None,
    delta_rms_dbfs: float | None,
    delta_f0_voiced_ratio: float | None,
    delta_clipping_ratio: float | None,
) -> str:
    notes: list[str] = []
    if signed_primary_delta is None:
        notes.append("missing_primary_metric")
    elif signed_primary_delta < -0.005:
        notes.append("wrong_direction")
    elif signed_primary_delta < 0.015:
        notes.append("direction_weak")
    if effect_score < 30:
        notes.append("effect_subtle")
    if preservation_score < 60:
        notes.append("preservation_risky")
    if delta_f0_median_pct is not None and abs(delta_f0_median_pct) > 3.0:
        notes.append("f0_drift_gt_3pct")
    if delta_rms_dbfs is not None and abs(delta_rms_dbfs) > 1.5:
        notes.append("rms_drift_gt_1p5db")
    if delta_f0_voiced_ratio is not None and abs(delta_f0_voiced_ratio) > 0.08:
        notes.append("voiced_ratio_shift_gt_0p08")
    if delta_clipping_ratio is not None and delta_clipping_ratio > 0.001:
        notes.append("clipping_increase")
    return ";".join(notes)


def score_row(
    *,
    action_family: str,
    delta_log_centroid_minus_log_f0: float | None,
    delta_low_mid_share_db: float | None,
    delta_brilliance_share_db: float | None,
    delta_spectral_centroid_hz_mean: float | None,
    delta_f0_median_pct: float | None,
    delta_rms_dbfs: float | None,
    delta_f0_voiced_ratio: float | None,
    delta_clipping_ratio: float | None,
    spectral_distance_l1: float,
) -> dict[str, str]:
    expected_sign = action_expected_sign(action_family)
    signed_primary = None if delta_log_centroid_minus_log_f0 is None else expected_sign * delta_log_centroid_minus_log_f0
    control_delta = direction_control_delta(action_family, delta_low_mid_share_db, delta_brilliance_share_db)

    primary_score = 0.0 if signed_primary is None else clamp(100.0 * signed_primary / 0.040, 0.0, 100.0)
    control_score = 0.0 if control_delta is None else clamp(100.0 * control_delta / 1.000, 0.0, 100.0)
    direction_score = 0.7 * primary_score + 0.3 * control_score

    centroid_effect = 0.0 if delta_spectral_centroid_hz_mean is None else clamp(abs(delta_spectral_centroid_hz_mean) / 150.0 * 100.0, 0.0, 100.0)
    primary_effect = 0.0 if delta_log_centroid_minus_log_f0 is None else clamp(abs(delta_log_centroid_minus_log_f0) / 0.040 * 100.0, 0.0, 100.0)
    control_effect = 0.0 if control_delta is None else clamp(abs(control_delta) / 1.000 * 100.0, 0.0, 100.0)
    effect_score = 0.5 * primary_effect + 0.3 * control_effect + 0.2 * centroid_effect

    preservation_score = 100.0
    if delta_f0_median_pct is not None:
        preservation_score -= clamp(max(abs(delta_f0_median_pct) - 1.5, 0.0) * 8.0, 0.0, 35.0)
    if delta_rms_dbfs is not None:
        preservation_score -= clamp(max(abs(delta_rms_dbfs) - 0.75, 0.0) * 14.0, 0.0, 20.0)
    if delta_f0_voiced_ratio is not None:
        preservation_score -= clamp(max(abs(delta_f0_voiced_ratio) - 0.05, 0.0) * 160.0, 0.0, 20.0)
    if delta_clipping_ratio is not None:
        preservation_score -= clamp(max(delta_clipping_ratio, 0.0) * 4000.0, 0.0, 15.0)
    preservation_score -= clamp(max(spectral_distance_l1 - 0.12, 0.0) * 80.0, 0.0, 15.0)
    preservation_score = clamp(preservation_score, 0.0, 100.0)

    quant_score = 0.45 * direction_score + 0.30 * preservation_score + 0.25 * effect_score

    if direction_score >= 70.0:
        direction_flag = "pass"
    elif direction_score >= 40.0:
        direction_flag = "borderline"
    else:
        direction_flag = "fail"

    if effect_score >= 60.0:
        audibility_flag = "likely"
    elif effect_score >= 30.0:
        audibility_flag = "borderline"
    else:
        audibility_flag = "weak"

    if preservation_score >= 80.0:
        preservation_flag = "safe"
    elif preservation_score >= 60.0:
        preservation_flag = "borderline"
    else:
        preservation_flag = "risky"

    if direction_flag == "pass" and preservation_flag == "safe" and effect_score >= 60.0:
        quant_grade = "strong_pass"
    elif direction_flag == "pass" and preservation_flag != "risky":
        quant_grade = "pass"
    elif direction_flag == "fail" or preservation_flag == "risky":
        quant_grade = "fail"
    else:
        quant_grade = "borderline"

    notes = build_auto_notes(
        signed_primary_delta=signed_primary,
        effect_score=effect_score,
        preservation_score=preservation_score,
        delta_f0_median_pct=delta_f0_median_pct,
        delta_rms_dbfs=delta_rms_dbfs,
        delta_f0_voiced_ratio=delta_f0_voiced_ratio,
        delta_clipping_ratio=delta_clipping_ratio,
    )
    return {
        "auto_direction_score": fmt_float(direction_score, digits=2),
        "auto_preservation_score": fmt_float(preservation_score, digits=2),
        "auto_effect_score": fmt_float(effect_score, digits=2),
        "auto_quant_score": fmt_float(quant_score, digits=2),
        "auto_direction_flag": direction_flag,
        "auto_preservation_flag": preservation_flag,
        "auto_audibility_flag": audibility_flag,
        "auto_quant_grade": quant_grade,
        "auto_quant_notes": notes,
    }


def build_output_row(
    *,
    row: dict[str, str],
    rule: dict,
    original_features: dict[str, float | None],
    processed_features: dict[str, float | None],
    original_band: dict[str, float],
    processed_band: dict[str, float],
    diff_metrics: dict[str, float],
    spectral_distance_l1: float,
) -> dict[str, str]:
    original_log = log_centroid_minus_log_f0(original_features)
    processed_log = log_centroid_minus_log_f0(processed_features)

    delta_rms_dbfs = delta(processed_features.get("rms_dbfs"), original_features.get("rms_dbfs"))
    delta_peak_dbfs = delta(processed_features.get("peak_dbfs"), original_features.get("peak_dbfs"))
    delta_clipping_ratio = delta(processed_features.get("clipping_ratio"), original_features.get("clipping_ratio"))
    delta_silence_ratio = delta(processed_features.get("silence_ratio_40db"), original_features.get("silence_ratio_40db"))
    delta_centroid = delta(processed_features.get("spectral_centroid_hz_mean"), original_features.get("spectral_centroid_hz_mean"))
    delta_voiced_ratio = delta(processed_features.get("f0_voiced_ratio"), original_features.get("f0_voiced_ratio"))
    delta_f0_median = delta(processed_features.get("f0_median_hz"), original_features.get("f0_median_hz"))
    delta_f0_pct = pct_delta(processed_features.get("f0_median_hz"), original_features.get("f0_median_hz"))
    delta_log_metric = delta(processed_log, original_log)
    delta_low_mid = delta(processed_band["low_mid_0_1500_share_db"], original_band["low_mid_0_1500_share_db"])
    delta_presence = delta(processed_band["presence_1500_3000_share_db"], original_band["presence_1500_3000_share_db"])
    delta_brilliance = delta(processed_band["brilliance_3000_8000_share_db"], original_band["brilliance_3000_8000_share_db"])

    auto_metrics = score_row(
        action_family=rule["action_family"],
        delta_log_centroid_minus_log_f0=delta_log_metric,
        delta_low_mid_share_db=delta_low_mid,
        delta_brilliance_share_db=delta_brilliance,
        delta_spectral_centroid_hz_mean=delta_centroid,
        delta_f0_median_pct=delta_f0_pct,
        delta_rms_dbfs=delta_rms_dbfs,
        delta_f0_voiced_ratio=delta_voiced_ratio,
        delta_clipping_ratio=delta_clipping_ratio,
        spectral_distance_l1=spectral_distance_l1,
    )

    return {
        "rule_id": row["rule_id"],
        "utt_id": row["utt_id"],
        "source_gender": row["source_gender"],
        "target_direction": row["target_direction"],
        "group_value": row["group_value"],
        "f0_condition": row["f0_condition"],
        "f0_median_hz": row["f0_median_hz"],
        "confidence": row["confidence"],
        "strength_label": row["strength_label"],
        "alpha_default": row["alpha_default"],
        "alpha_max": row["alpha_max"],
        "action_family": rule["action_family"],
        "rule_notes": rule.get("notes", ""),
        "input_audio": row["input_audio"],
        "original_copy": row["original_copy"],
        "processed_audio": row["processed_audio"],
        "original_rms_dbfs": fmt_float(original_features.get("rms_dbfs")),
        "processed_rms_dbfs": fmt_float(processed_features.get("rms_dbfs")),
        "delta_rms_dbfs": fmt_float(delta_rms_dbfs),
        "original_peak_dbfs": fmt_float(original_features.get("peak_dbfs")),
        "processed_peak_dbfs": fmt_float(processed_features.get("peak_dbfs")),
        "delta_peak_dbfs": fmt_float(delta_peak_dbfs),
        "original_clipping_ratio": fmt_float(original_features.get("clipping_ratio")),
        "processed_clipping_ratio": fmt_float(processed_features.get("clipping_ratio")),
        "delta_clipping_ratio": fmt_float(delta_clipping_ratio),
        "original_silence_ratio_40db": fmt_float(original_features.get("silence_ratio_40db")),
        "processed_silence_ratio_40db": fmt_float(processed_features.get("silence_ratio_40db")),
        "delta_silence_ratio_40db": fmt_float(delta_silence_ratio),
        "original_f0_voiced_ratio": fmt_float(original_features.get("f0_voiced_ratio")),
        "processed_f0_voiced_ratio": fmt_float(processed_features.get("f0_voiced_ratio")),
        "delta_f0_voiced_ratio": fmt_float(delta_voiced_ratio),
        "original_f0_median_hz": fmt_float(original_features.get("f0_median_hz")),
        "processed_f0_median_hz": fmt_float(processed_features.get("f0_median_hz")),
        "delta_f0_median_hz": fmt_float(delta_f0_median),
        "delta_f0_median_pct": fmt_float(delta_f0_pct, digits=3),
        "original_spectral_centroid_hz_mean": fmt_float(original_features.get("spectral_centroid_hz_mean")),
        "processed_spectral_centroid_hz_mean": fmt_float(processed_features.get("spectral_centroid_hz_mean")),
        "delta_spectral_centroid_hz_mean": fmt_float(delta_centroid),
        "original_log_centroid_minus_log_f0": fmt_float(original_log),
        "processed_log_centroid_minus_log_f0": fmt_float(processed_log),
        "delta_log_centroid_minus_log_f0": fmt_float(delta_log_metric),
        "original_low_mid_0_1500_share_db": fmt_float(original_band["low_mid_0_1500_share_db"]),
        "processed_low_mid_0_1500_share_db": fmt_float(processed_band["low_mid_0_1500_share_db"]),
        "delta_low_mid_0_1500_share_db": fmt_float(delta_low_mid),
        "original_presence_1500_3000_share_db": fmt_float(original_band["presence_1500_3000_share_db"]),
        "processed_presence_1500_3000_share_db": fmt_float(processed_band["presence_1500_3000_share_db"]),
        "delta_presence_1500_3000_share_db": fmt_float(delta_presence),
        "original_brilliance_3000_8000_share_db": fmt_float(original_band["brilliance_3000_8000_share_db"]),
        "processed_brilliance_3000_8000_share_db": fmt_float(processed_band["brilliance_3000_8000_share_db"]),
        "delta_brilliance_3000_8000_share_db": fmt_float(delta_brilliance),
        "waveform_mean_abs_diff": fmt_float(diff_metrics["waveform_mean_abs_diff"]),
        "waveform_max_abs_diff": fmt_float(diff_metrics["waveform_max_abs_diff"]),
        "stft_logmag_l1": fmt_float(spectral_distance_l1),
        **auto_metrics,
        "review_status": "pending",
        "direction_correct": "",
        "effect_audible": "",
        "artifact_issue": "",
        "strength_fit": "",
        "keep_recommendation": "",
        "reviewer": "",
        "review_notes": "",
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError("No rows to write.")
    fieldnames = list(rows[0].keys())
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_summary_md(path: Path, rows: list[dict[str, str]]) -> None:
    grade_counts: dict[str, int] = {}
    for row in rows:
        grade = row["auto_quant_grade"]
        grade_counts[grade] = grade_counts.get(grade, 0) + 1

    def avg(field: str) -> float:
        values = [parse_float(row[field]) for row in rows]
        clean = [value for value in values if value is not None]
        return float(sum(clean) / len(clean)) if clean else 0.0

    high_risk = [row for row in rows if row["auto_quant_grade"] == "fail"]
    strongest = sorted(rows, key=lambda row: parse_float(row["auto_quant_score"]) or 0.0, reverse=True)[:3]

    lines = [
        "# Stage0 Rule Listening Quant Summary",
        "",
        f"- rows: `{len(rows)}`",
        f"- avg auto_quant_score: `{avg('auto_quant_score'):.2f}`",
        f"- avg auto_direction_score: `{avg('auto_direction_score'):.2f}`",
        f"- avg auto_preservation_score: `{avg('auto_preservation_score'):.2f}`",
        f"- avg auto_effect_score: `{avg('auto_effect_score'):.2f}`",
        "",
        "## Grade Counts",
        "",
    ]
    for grade in ["strong_pass", "pass", "borderline", "fail"]:
        lines.append(f"- `{grade}`: `{grade_counts.get(grade, 0)}`")

    lines.extend(["", "## Top Rows", ""])
    for row in strongest:
        lines.append(
            f"- `{row['rule_id']}` | score=`{row['auto_quant_score']}` | "
            f"grade=`{row['auto_quant_grade']}` | notes=`{row['auto_quant_notes'] or 'ok'}`"
        )

    lines.extend(["", "## Risk Rows", ""])
    if not high_risk:
        lines.append("- none")
    else:
        for row in high_risk:
            lines.append(
                f"- `{row['rule_id']}` | score=`{row['auto_quant_score']}` | "
                f"direction=`{row['auto_direction_flag']}` | preserve=`{row['auto_preservation_flag']}` | "
                f"notes=`{row['auto_quant_notes']}`"
            )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    rule_lookup = load_rule_lookup(resolve_path(args.rule_config))
    summary_csv = resolve_path(args.summary_csv)
    output_csv = resolve_path(args.output_csv)
    summary_md = resolve_path(args.summary_md)

    with summary_csv.open("r", encoding="utf-8", newline="") as f:
        summary_rows = list(csv.DictReader(f))

    output_rows: list[dict[str, str]] = []
    for row in summary_rows:
        rule = rule_lookup[row["rule_id"]]
        original_audio, original_sr = load_audio(Path(row["original_copy"]))
        processed_audio, processed_sr = load_audio(Path(row["processed_audio"]))
        if original_sr != processed_sr:
            processed_audio = librosa.resample(processed_audio.astype(np.float32), orig_sr=processed_sr, target_sr=original_sr)
            processed_sr = original_sr

        original_features = feature_map(original_audio, original_sr, f0_sr=args.f0_sr, frame_period_ms=args.frame_period_ms)
        processed_features = feature_map(processed_audio, processed_sr, f0_sr=args.f0_sr, frame_period_ms=args.frame_period_ms)
        original_band = band_share_db(original_audio, original_sr, n_fft=args.n_fft, hop_length=args.hop_length)
        processed_band = band_share_db(processed_audio, processed_sr, n_fft=args.n_fft, hop_length=args.hop_length)
        diff_metrics = waveform_diff(original_audio, processed_audio)
        spectral_distance = stft_logmag_l1(original_audio, processed_audio, n_fft=args.n_fft, hop_length=args.hop_length)

        output_rows.append(
            build_output_row(
                row=row,
                rule=rule,
                original_features=original_features,
                processed_features=processed_features,
                original_band=original_band,
                processed_band=processed_band,
                diff_metrics=diff_metrics,
                spectral_distance_l1=spectral_distance,
            )
        )

    write_csv(output_csv, output_rows)
    write_summary_md(summary_md, output_rows)
    print(f"Wrote {output_csv}")
    print(f"Wrote {summary_md}")
    print(f"Rows: {len(output_rows)}")


if __name__ == "__main__":
    main()
