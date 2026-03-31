from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

from audit_speech_structure_from_queue import (
    ROOT,
    evaluate_pair,
    fmt_float,
    load_audio_mono,
    resolve_path,
    structure_risk_score,
)


DEFAULT_SUMMARY_CSVS = [
    ROOT
    / "artifacts"
    / "diagnostics"
    / "atrr_vocoder_carrier_adapter"
    / "v1_fixed8_v9a_bigvgan_11025_blend075_pc150_cap200_full8"
    / "atrr_vocoder_carrier_adapter_summary.csv",
]
DEFAULT_QUEUE_CSV = (
    ROOT
    / "artifacts"
    / "listening_review"
    / "stage0_speech_lsf_machine_sweep_v9_fixed8"
    / "split_core_focus_v9a"
    / "listening_review_queue.csv"
)
DEFAULT_OUTPUT_DIR = ROOT / "artifacts" / "diagnostics" / "atrr_carrier_structure_audit" / "v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-csv", action="append", default=[])
    parser.add_argument("--queue-csv", default=str(DEFAULT_QUEUE_CSV))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--target-sr", type=int, default=24000)
    parser.add_argument("--n-fft", type=int, default=1024)
    parser.add_argument("--hop-length", type=int, default=256)
    parser.add_argument("--n-mels", type=int, default=40)
    parser.add_argument("--n-mfcc", type=int, default=13)
    return parser.parse_args()


def summary_label_from_path(path: Path) -> str:
    try:
        return path.parent.relative_to(ROOT / "artifacts" / "diagnostics" / "atrr_vocoder_carrier_adapter").as_posix()
    except ValueError:
        return path.parent.name


def load_queue_lookup(path: Path) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    by_record_id = {row["record_id"]: row for row in rows if row.get("record_id")}
    by_utt_id = {row["utt_id"]: row for row in rows if row.get("utt_id")}
    return by_record_id, by_utt_id


def average(values: list[float]) -> float:
    clean = [value for value in values if math.isfinite(value)]
    return float(sum(clean) / len(clean)) if clean else float("nan")


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def probe_metrics(
    source_audio,
    probe_path: Path,
    *,
    sr: int,
    n_fft: int,
    hop_length: int,
    n_mels: int,
    n_mfcc: int,
) -> tuple[dict[str, float], float]:
    probe_audio = load_audio_mono(probe_path, sr)
    metrics = evaluate_pair(
        source_audio,
        probe_audio,
        sr=sr,
        n_fft=n_fft,
        hop_length=hop_length,
        n_mels=n_mels,
        n_mfcc=n_mfcc,
    )
    return metrics, structure_risk_score(metrics)


def main() -> None:
    args = parse_args()
    summary_csvs = [resolve_path(path) for path in (args.summary_csv or [])] or [resolve_path(path) for path in DEFAULT_SUMMARY_CSVS]
    queue_by_record_id, queue_by_utt_id = load_queue_lookup(resolve_path(args.queue_csv))
    output_dir = resolve_path(args.output_dir)

    row_output: list[dict[str, str]] = []
    pack_output: list[dict[str, str]] = []

    for summary_csv in summary_csvs:
        with summary_csv.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        label = summary_label_from_path(summary_csv)
        pack_rows: list[dict[str, float]] = []

        for row in rows:
            if row.get("synthesis_status") != "ok":
                continue
            queue_row = queue_by_record_id.get(row.get("record_id", "")) or queue_by_utt_id.get(row.get("utt_id", ""))
            if queue_row is None:
                continue
            source_audio = load_audio_mono(resolve_path(queue_row["original_copy"]), args.target_sr)
            source_metrics, source_risk = probe_metrics(
                source_audio,
                resolve_path(row["source_probe_wav"]),
                sr=args.target_sr,
                n_fft=args.n_fft,
                hop_length=args.hop_length,
                n_mels=args.n_mels,
                n_mfcc=args.n_mfcc,
            )
            target_metrics, target_risk = probe_metrics(
                source_audio,
                resolve_path(row["target_probe_wav"]),
                sr=args.target_sr,
                n_fft=args.n_fft,
                hop_length=args.hop_length,
                n_mels=args.n_mels,
                n_mfcc=args.n_mfcc,
            )
            row_output.append(
                {
                    "summary_label": label,
                    "record_id": row["record_id"],
                    "rule_id": row["rule_id"],
                    "carrier_target_shift_score": row.get("carrier_target_shift_score", ""),
                    "target_log_mel_mae": row.get("target_log_mel_mae", ""),
                    "source_probe_logmel_dtw_l1": fmt_float(source_metrics["logmel_dtw_l1"]),
                    "source_probe_voiced_overlap_iou": fmt_float(source_metrics["voiced_overlap_iou"]),
                    "source_probe_f0_overlap_mae_cents": fmt_float(source_metrics["f0_overlap_mae_cents"]),
                    "source_probe_structure_risk_score": fmt_float(source_risk, digits=2),
                    "target_probe_logmel_dtw_l1": fmt_float(target_metrics["logmel_dtw_l1"]),
                    "target_probe_voiced_overlap_iou": fmt_float(target_metrics["voiced_overlap_iou"]),
                    "target_probe_f0_overlap_mae_cents": fmt_float(target_metrics["f0_overlap_mae_cents"]),
                    "target_probe_structure_risk_score": fmt_float(target_risk, digits=2),
                    "edit_added_structure_risk": fmt_float(target_risk - source_risk, digits=2),
                }
            )
            pack_rows.append(
                {
                    "carrier_target_shift_score": float(row.get("carrier_target_shift_score") or "nan"),
                    "target_log_mel_mae": float(row.get("target_log_mel_mae") or "nan"),
                    "source_probe_structure_risk_score": source_risk,
                    "target_probe_structure_risk_score": target_risk,
                    "edit_added_structure_risk": target_risk - source_risk,
                }
            )

        label_rows = [item for item in row_output if item["summary_label"] == label]
        top_target_risk = sorted(
            label_rows,
            key=lambda item: float(item["target_probe_structure_risk_score"] or "nan"),
            reverse=True,
        )[:3]
        pack_output.append(
            {
                "summary_label": label,
                "rows": str(len(pack_rows)),
                "avg_carrier_target_shift_score": fmt_float(average([item["carrier_target_shift_score"] for item in pack_rows]), digits=2),
                "avg_target_log_mel_mae": fmt_float(average([item["target_log_mel_mae"] for item in pack_rows]), digits=4),
                "avg_source_probe_structure_risk_score": fmt_float(average([item["source_probe_structure_risk_score"] for item in pack_rows]), digits=2),
                "avg_target_probe_structure_risk_score": fmt_float(average([item["target_probe_structure_risk_score"] for item in pack_rows]), digits=2),
                "avg_edit_added_structure_risk": fmt_float(average([item["edit_added_structure_risk"] for item in pack_rows]), digits=2),
                "top_target_risk_records": ";".join(item["record_id"] for item in top_target_risk),
            }
        )

    row_csv = output_dir / "atrr_carrier_structure_row_audit.csv"
    pack_csv = output_dir / "atrr_carrier_structure_pack_audit.csv"
    md_path = output_dir / "ATRR_CARRIER_STRUCTURE_AUDIT.md"
    write_csv(row_csv, list(row_output[0].keys()) if row_output else [], row_output)
    write_csv(pack_csv, list(pack_output[0].keys()) if pack_output else [], pack_output)

    lines = [
        "# ATRR Carrier Structure Audit v1",
        "",
        "## Scope",
        "",
        "- This audit reads machine-probe summary csv files directly.",
        "- It separates carrier-only distortion from target-edit-added distortion.",
        "",
        "## Pack Summary",
        "",
    ]
    for row in pack_output:
        lines.extend(
            [
                f"### `{row['summary_label']}`",
                "",
                f"- rows: `{row['rows']}`",
                f"- avg carrier_target_shift_score: `{row['avg_carrier_target_shift_score']}`",
                f"- avg target_log_mel_mae: `{row['avg_target_log_mel_mae']}`",
                f"- avg source_probe_structure_risk_score: `{row['avg_source_probe_structure_risk_score']}`",
                f"- avg target_probe_structure_risk_score: `{row['avg_target_probe_structure_risk_score']}`",
                f"- avg edit_added_structure_risk: `{row['avg_edit_added_structure_risk']}`",
                f"- top target risk records: `{row['top_target_risk_records']}`",
                "",
            ]
        )
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {row_csv}")
    print(f"Wrote {pack_csv}")
    print(f"Wrote {md_path}")
    print(f"Summaries: {len(summary_csvs)}")


if __name__ == "__main__":
    main()
