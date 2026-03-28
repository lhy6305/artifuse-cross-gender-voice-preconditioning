from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input manifest path relative to repo root or absolute path.")
    parser.add_argument("--output", required=True, help="Output review sheet path relative to repo root or absolute path.")
    return parser.parse_args()


def resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return ROOT / path


def main() -> None:
    args = parse_args()
    in_csv = resolve_path(args.input)
    out_csv = resolve_path(args.output)

    with in_csv.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    fieldnames = [
        "eval_set_id",
        "eval_bucket",
        "duration_bin",
        "selection_order",
        "record_id",
        "utt_id",
        "dataset_name",
        "split_name",
        "speaker_id",
        "gender",
        "domain",
        "duration_sec",
        "sample_rate",
        "path_raw",
        "feature_status",
        "rms_dbfs",
        "peak_dbfs",
        "clipping_ratio",
        "silence_ratio_40db",
        "f0_voiced_ratio",
        "f0_median_hz",
        "review_status",
        "content_ok",
        "noise_issue",
        "reverb_issue",
        "clipping_audible",
        "accompaniment_issue",
        "pronunciation_or_lyric_issue",
        "speaker_or_gender_bucket_ok",
        "usable_for_fixed_eval",
        "reviewer",
        "review_notes",
    ]

    output_rows = []
    for row in rows:
        output_rows.append(
            {
                "eval_set_id": row.get("eval_set_id", ""),
                "eval_bucket": row.get("eval_bucket", ""),
                "duration_bin": row.get("duration_bin", ""),
                "selection_order": row.get("selection_order", ""),
                "record_id": row.get("record_id", ""),
                "utt_id": row.get("utt_id", ""),
                "dataset_name": row.get("dataset_name", ""),
                "split_name": row.get("split_name", ""),
                "speaker_id": row.get("speaker_id", ""),
                "gender": row.get("gender", ""),
                "domain": row.get("domain", ""),
                "duration_sec": row.get("duration_sec", ""),
                "sample_rate": row.get("sample_rate", ""),
                "path_raw": row.get("path_raw", ""),
                "feature_status": row.get("feature_status", ""),
                "rms_dbfs": row.get("rms_dbfs", ""),
                "peak_dbfs": row.get("peak_dbfs", ""),
                "clipping_ratio": row.get("clipping_ratio", ""),
                "silence_ratio_40db": row.get("silence_ratio_40db", ""),
                "f0_voiced_ratio": row.get("f0_voiced_ratio", ""),
                "f0_median_hz": row.get("f0_median_hz", ""),
                "review_status": "pending",
                "content_ok": "",
                "noise_issue": "",
                "reverb_issue": "",
                "clipping_audible": "",
                "accompaniment_issue": "",
                "pronunciation_or_lyric_issue": "",
                "speaker_or_gender_bucket_ok": "",
                "usable_for_fixed_eval": "",
                "reviewer": "",
                "review_notes": "",
            }
        )

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Wrote {out_csv}")
    print(f"Rows: {len(output_rows)}")


if __name__ == "__main__":
    main()
