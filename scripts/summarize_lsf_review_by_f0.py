from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUEUE_CSV = ROOT / "artifacts" / "listening_review" / "stage0_speech_lsf_listening_pack" / "v8" / "listening_review_queue.csv"
DEFAULT_INPUT_CSV = ROOT / "experiments" / "fixed_eval" / "v1_2" / "fixed_eval_review_final_v1_2.csv"
DEFAULT_OUTPUT_DIR = ROOT / "artifacts" / "diagnostics" / "lsf_v8_review_f0_summary"

TARGET_DIRECTION_BY_SOURCE_GENDER = {
    "male": "feminine",
    "female": "masculine",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue-csv", default=str(DEFAULT_QUEUE_CSV))
    parser.add_argument("--input-csv", default=str(DEFAULT_INPUT_CSV))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    return parser.parse_args()


def resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return ROOT / path


def parse_float(value: str | None) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def percentile_value(values: list[float], fraction: float) -> float:
    if not values:
        raise ValueError("percentile_value requires non-empty values.")
    sorted_values = sorted(values)
    if len(sorted_values) == 1:
        return sorted_values[0]
    index = round((len(sorted_values) - 1) * fraction)
    index = max(0, min(index, len(sorted_values) - 1))
    return sorted_values[index]


def build_bucket_reference(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in rows:
        source_gender = row.get("gender", "")
        if source_gender not in TARGET_DIRECTION_BY_SOURCE_GENDER:
            continue
        if row.get("domain") != "speech":
            continue
        if row.get("review_status") != "reviewed":
            continue
        if row.get("usable_for_fixed_eval") != "yes":
            continue
        if row.get("speaker_or_gender_bucket_ok") != "yes":
            continue
        f0_value = parse_float(row.get("f0_median_hz"))
        if f0_value is None:
            continue
        grouped[(row["dataset_name"], TARGET_DIRECTION_BY_SOURCE_GENDER[source_gender])].append(f0_value)

    reference_rows: list[dict[str, str]] = []
    for dataset_name, target_direction in sorted(grouped):
        values = grouped[(dataset_name, target_direction)]
        lower = percentile_value(values, 1.0 / 3.0)
        upper = percentile_value(values, 2.0 / 3.0)
        reference_rows.append(
            {
                "dataset_name": dataset_name,
                "target_direction": target_direction,
                "source_gender": "female" if target_direction == "masculine" else "male",
                "row_count": str(len(values)),
                "f0_bucket_low_upper_hz": f"{lower:.6f}",
                "f0_bucket_mid_upper_hz": f"{upper:.6f}",
                "f0_min_hz": f"{min(values):.6f}",
                "f0_max_hz": f"{max(values):.6f}",
            }
        )
    return reference_rows


def assign_bucket(f0_value: float | None, lower: float, upper: float) -> str:
    if f0_value is None:
        return "unknown_f0"
    if f0_value <= lower:
        return "low_f0"
    if f0_value <= upper:
        return "mid_f0"
    return "high_f0"


def build_bucket_lookup(reference_rows: list[dict[str, str]]) -> dict[tuple[str, str], tuple[float, float]]:
    return {
        (row["dataset_name"], row["target_direction"]): (
            float(row["f0_bucket_low_upper_hz"]),
            float(row["f0_bucket_mid_upper_hz"]),
        )
        for row in reference_rows
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def summarize_bucket(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row["dataset_name"], row["target_direction"], row["f0_bucket"])].append(row)

    summary_rows: list[dict[str, str]] = []
    for dataset_name, target_direction, f0_bucket in sorted(grouped):
        bucket_rows = grouped[(dataset_name, target_direction, f0_bucket)]
        reviewed_rows = [row for row in bucket_rows if row.get("review_status") == "reviewed"]
        too_weak_rows = [row for row in reviewed_rows if row.get("strength_fit") == "too_weak"]
        artifact_rows = [row for row in reviewed_rows if row.get("artifact_issue") not in {"", "no"}]
        direction_yes_rows = [row for row in reviewed_rows if row.get("direction_correct") == "yes"]
        direction_maybe_rows = [row for row in reviewed_rows if row.get("direction_correct") == "maybe"]
        audible_yes_rows = [row for row in reviewed_rows if row.get("effect_audible") == "yes"]
        auto_quant_values = [parse_float(row.get("auto_quant_score")) for row in bucket_rows]
        clean_auto_quant = [value for value in auto_quant_values if value is not None]
        summary_rows.append(
            {
                "dataset_name": dataset_name,
                "target_direction": target_direction,
                "f0_bucket": f0_bucket,
                "rows": str(len(bucket_rows)),
                "reviewed_rows": str(len(reviewed_rows)),
                "direction_yes_rows": str(len(direction_yes_rows)),
                "direction_maybe_rows": str(len(direction_maybe_rows)),
                "audible_yes_rows": str(len(audible_yes_rows)),
                "artifact_flagged_rows": str(len(artifact_rows)),
                "too_weak_rows": str(len(too_weak_rows)),
                "avg_auto_quant_score": f"{(sum(clean_auto_quant) / len(clean_auto_quant)):.2f}" if clean_auto_quant else "",
            }
        )
    return summary_rows


def build_row_summary(queue_rows: list[dict[str, str]], bucket_lookup: dict[tuple[str, str], tuple[float, float]]) -> list[dict[str, str]]:
    row_summaries: list[dict[str, str]] = []
    for row in queue_rows:
        dataset_name = row.get("dataset_name") or row.get("group_value", "")
        key = (dataset_name, row["target_direction"])
        if key not in bucket_lookup:
            continue
        lower, upper = bucket_lookup[key]
        f0_value = parse_float(row.get("f0_median_hz"))
        row_summaries.append(
            {
                "record_id": row.get("record_id", ""),
                "utt_id": row["utt_id"],
                "dataset_name": dataset_name,
                "source_gender": row["source_gender"],
                "target_direction": row["target_direction"],
                "f0_median_hz": row.get("f0_median_hz", ""),
                "f0_bucket": assign_bucket(f0_value, lower, upper),
                "rule_id": row["rule_id"],
                "strength_label": row["strength_label"],
                "auto_quant_score": row.get("auto_quant_score", ""),
                "auto_quant_grade": row.get("auto_quant_grade", ""),
                "review_status": row.get("review_status", ""),
                "direction_correct": row.get("direction_correct", ""),
                "effect_audible": row.get("effect_audible", ""),
                "artifact_issue": row.get("artifact_issue", ""),
                "strength_fit": row.get("strength_fit", ""),
                "keep_recommendation": row.get("keep_recommendation", ""),
                "review_notes": row.get("review_notes", ""),
            }
        )
    row_summaries.sort(key=lambda row: (row["dataset_name"], row["target_direction"], row["f0_bucket"], row["utt_id"]))
    return row_summaries


def build_summary_md(
    *,
    reference_rows: list[dict[str, str]],
    bucket_summary_rows: list[dict[str, str]],
    row_summary_rows: list[dict[str, str]],
) -> str:
    lines = [
        "# LSF Review By F0 Summary",
        "",
        "## Bucket Reference",
        "",
    ]
    for row in reference_rows:
        lines.append(
            f"- `{row['dataset_name']}` / `{row['target_direction']}`: "
            f"low <= `{row['f0_bucket_low_upper_hz']}`, mid <= `{row['f0_bucket_mid_upper_hz']}`, "
            f"high > `{row['f0_bucket_mid_upper_hz']}`"
        )

    lines.extend(["", "## Bucket Summary", ""])
    for row in bucket_summary_rows:
        lines.append(
            f"- `{row['dataset_name']}` / `{row['target_direction']}` / `{row['f0_bucket']}`: "
            f"rows=`{row['rows']}`, reviewed=`{row['reviewed_rows']}`, too_weak=`{row['too_weak_rows']}`, "
            f"artifact=`{row['artifact_flagged_rows']}`, direction yes/maybe=`{row['direction_yes_rows']}`/`{row['direction_maybe_rows']}`, "
            f"audible_yes=`{row['audible_yes_rows']}`, avg_auto_quant=`{row['avg_auto_quant_score'] or 'n/a'}`"
        )

    lines.extend(["", "## Reviewed Rows", ""])
    reviewed_rows = [row for row in row_summary_rows if row["review_status"] == "reviewed"]
    if not reviewed_rows:
        lines.append("- none")
    else:
        for row in reviewed_rows:
            notes = row["review_notes"] or "-"
            lines.append(
                f"- `{row['dataset_name']}` / `{row['target_direction']}` / `{row['f0_bucket']}` / `{row['utt_id']}`: "
                f"dir=`{row['direction_correct'] or '-'}`, audible=`{row['effect_audible'] or '-'}`, "
                f"artifact=`{row['artifact_issue'] or '-'}`, strength=`{row['strength_fit'] or '-'}`, notes=`{notes}`"
            )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    queue_rows = read_csv(resolve_path(args.queue_csv))
    input_rows = read_csv(resolve_path(args.input_csv))
    output_dir = resolve_path(args.output_dir)

    reference_rows = build_bucket_reference(input_rows)
    bucket_lookup = build_bucket_lookup(reference_rows)
    row_summary_rows = build_row_summary(queue_rows, bucket_lookup)
    bucket_summary_rows = summarize_bucket(row_summary_rows)

    write_csv(output_dir / "lsf_review_f0_bucket_reference.csv", reference_rows)
    write_csv(output_dir / "lsf_review_f0_row_summary.csv", row_summary_rows)
    write_csv(output_dir / "lsf_review_f0_bucket_summary.csv", bucket_summary_rows)
    (output_dir / "LSF_REVIEW_BY_F0_SUMMARY.md").write_text(
        build_summary_md(
            reference_rows=reference_rows,
            bucket_summary_rows=bucket_summary_rows,
            row_summary_rows=row_summary_rows,
        ),
        encoding="utf-8",
    )
    print(f"Wrote {output_dir}")
    print(f"Reference rows: {len(reference_rows)}")
    print(f"Queue rows summarized: {len(row_summary_rows)}")


if __name__ == "__main__":
    main()
