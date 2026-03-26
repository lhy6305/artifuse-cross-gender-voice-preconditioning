from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "tmp" / "stage1_rvc_cascade_eval" / "v1" / "rvc_cascade_manifest.csv"
DEFAULT_OUTPUT_CSV = ROOT / "tmp" / "stage1_rvc_cascade_eval" / "v1" / "rvc_cascade_review_queue.csv"
DEFAULT_SUMMARY_MD = ROOT / "tmp" / "stage1_rvc_cascade_eval" / "v1" / "rvc_cascade_review_summary.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest-csv", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--output-csv", default=str(DEFAULT_OUTPUT_CSV))
    parser.add_argument("--summary-md", default=str(DEFAULT_SUMMARY_MD))
    return parser.parse_args()


def resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return ROOT / path


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError("No rows to write.")
    fieldnames = list(rows[0].keys())
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_summary(path: Path, rows: list[dict[str, str]]) -> None:
    lines = [
        "# Stage1 RVC Cascade Review Summary",
        "",
        f"- rows: `{len(rows)}`",
        "",
        "## Composition",
        "",
    ]
    counts: dict[str, int] = {}
    for row in rows:
        key = f"{row['target_id']} | {row['target_direction']}"
        counts[key] = counts.get(key, 0) + 1
    for key in sorted(counts):
        lines.append(f"- `{key}`: `{counts[key]}`")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_review_rows(manifest_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    paired: dict[tuple[str, str], dict[str, dict[str, str]]] = {}
    for row in manifest_rows:
        if row.get("status") != "done":
            continue
        key = (row["utt_id"], row["target_id"])
        paired.setdefault(key, {})[row["input_variant"]] = row

    rows: list[dict[str, str]] = []
    for key in sorted(paired):
        pair = paired[key]
        raw_row = pair.get("raw")
        proc_row = pair.get("preconditioned")
        if raw_row is None or proc_row is None:
            continue
        rows.append(
            {
                "rule_id": raw_row["rule_id"],
                "utt_id": raw_row["utt_id"],
                "source_gender": raw_row["source_gender"],
                "target_direction": raw_row["target_direction"],
                "group_value": raw_row["group_value"],
                "f0_condition": "cascade_pair",
                "f0_median_hz": raw_row.get("f0_median_hz", ""),
                "confidence": "stage1_cascade_eval",
                "strength_label": "raw_vs_preconditioned",
                "alpha_default": "",
                "alpha_max": "",
                "action_family": "cascade_compare",
                "rule_notes": (
                    f"cascade_compare | source=input_audio | "
                    f"original_copy=preconditioned_audio | processed_audio=rvc_output_audio | "
                    f"rvc_baseline_audio={raw_row['output_audio']} | "
                    f"target={raw_row['target_id']} model={raw_row['model_name']} | "
                    f"source_f0_hz={raw_row.get('f0_median_hz', '')} | "
                    f"target_f0_hz={raw_row.get('target_f0_reference_hz', '')} | "
                    f"f0_up_key={raw_row.get('f0_up_key', '')} | "
                    f"f0_reason={raw_row.get('f0_up_key_reason', '')}"
                ),
                "summary_signature": f"{raw_row['utt_id']}|{raw_row['target_id']}",
                "input_audio": raw_row["input_audio"],
                "original_copy": proc_row["input_audio"],
                "processed_audio": proc_row["output_audio"],
                "original_mtime_ns": str(Path(proc_row["input_audio"]).stat().st_mtime_ns),
                "processed_mtime_ns": str(Path(proc_row["output_audio"]).stat().st_mtime_ns),
                "original_rms_dbfs": "",
                "processed_rms_dbfs": "",
                "delta_rms_dbfs": "",
                "original_peak_dbfs": "",
                "processed_peak_dbfs": "",
                "delta_peak_dbfs": "",
                "original_clipping_ratio": "",
                "processed_clipping_ratio": "",
                "delta_clipping_ratio": "",
                "original_silence_ratio_40db": "",
                "processed_silence_ratio_40db": "",
                "delta_silence_ratio_40db": "",
                "original_f0_voiced_ratio": "",
                "processed_f0_voiced_ratio": "",
                "delta_f0_voiced_ratio": "",
                "original_f0_median_hz": "",
                "processed_f0_median_hz": "",
                "delta_f0_median_hz": "",
                "delta_f0_median_pct": "",
                "original_spectral_centroid_hz_mean": "",
                "processed_spectral_centroid_hz_mean": "",
                "delta_spectral_centroid_hz_mean": "",
                "original_log_centroid_minus_log_f0": "",
                "processed_log_centroid_minus_log_f0": "",
                "delta_log_centroid_minus_log_f0": "",
                "original_low_mid_0_1500_share_db": "",
                "processed_low_mid_0_1500_share_db": "",
                "delta_low_mid_0_1500_share_db": "",
                "original_presence_1500_3000_share_db": "",
                "processed_presence_1500_3000_share_db": "",
                "delta_presence_1500_3000_share_db": "",
                "original_brilliance_3000_8000_share_db": "",
                "processed_brilliance_3000_8000_share_db": "",
                "delta_brilliance_3000_8000_share_db": "",
                "waveform_mean_abs_diff": "",
                "waveform_max_abs_diff": "",
                "stft_logmag_l1": "",
                "auto_direction_score": "",
                "auto_preservation_score": "",
                "auto_effect_score": "",
                "auto_quant_score": "",
                "auto_direction_flag": "",
                "auto_preservation_flag": "",
                "auto_audibility_flag": "",
                "auto_quant_grade": "",
                "auto_quant_notes": "",
                "target_id": raw_row["target_id"],
                "rvc_baseline_audio": raw_row["output_audio"],
                "review_status": "pending",
                "direction_correct": "",
                "effect_audible": "",
                "artifact_issue": "",
                "strength_fit": "",
                "keep_recommendation": "",
                "reviewer": "",
                "review_notes": "",
            }
        )
    return rows


def main() -> None:
    args = parse_args()
    manifest_rows = read_rows(resolve_path(args.manifest_csv))
    review_rows = build_review_rows(manifest_rows)
    write_csv(resolve_path(args.output_csv), review_rows)
    write_summary(resolve_path(args.summary_md), review_rows)
    print(f"Wrote {resolve_path(args.output_csv)}")
    print(f"Wrote {resolve_path(args.summary_md)}")
    print(f"Rows: {len(review_rows)}")


if __name__ == "__main__":
    main()
