from __future__ import annotations

import argparse
import csv
import math
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE_QUEUE = (
    ROOT
    / "artifacts"
    / "listening_review"
    / "stage0_speech_lsf_machine_sweep_v9_fixed8"
    / "split_core_focus_v9a"
    / "listening_review_queue.csv"
)
DEFAULT_ADAPTER_SUMMARY = (
    ROOT
    / "artifacts"
    / "diagnostics"
    / "atrr_vocoder_carrier_adapter"
    / "v1_fixed8_v9a_bigvgan_11025_blend075_pc150_cap200_full8"
    / "atrr_vocoder_carrier_adapter_summary.csv"
)
DEFAULT_OUTPUT_DIR = (
    ROOT
    / "artifacts"
    / "listening_review"
    / "stage0_atrr_vocoder_bigvgan_fixed8"
    / "blend075_pc150_cap200_v1"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template-queue", default=str(DEFAULT_TEMPLATE_QUEUE))
    parser.add_argument("--adapter-summary", default=str(DEFAULT_ADAPTER_SUMMARY))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--pack-label", default="bigvgan_blend075_pc150_cap200_v1")
    parser.add_argument(
        "--pack-purpose",
        default="first fixed8 human pack for voiced-blend BigVGAN carrier stack",
    )
    parser.add_argument(
        "--pack-note",
        action="append",
        default=[],
        help="Extra README note line for this pack.",
    )
    parser.add_argument(
        "--control-record-id",
        action="append",
        default=[],
        help="Record ids that should be annotated as control rows in the queue.",
    )
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


def fmt_float(value: float | None, digits: int = 2) -> str:
    if value is None or not math.isfinite(value):
        return ""
    return f"{value:.{digits}f}"


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def preservation_score(f0_drift_cents: float | None, mel_mae: float | None) -> float:
    if f0_drift_cents is None and mel_mae is None:
        return 0.0
    drift_penalty = 0.0 if f0_drift_cents is None else 0.12 * f0_drift_cents
    mel_penalty = 0.0 if mel_mae is None else max(mel_mae - 0.35, 0.0) * 45.0
    return clamp(100.0 - drift_penalty - mel_penalty, 0.0, 100.0)


def auto_direction_flag(direction_score: float) -> str:
    if direction_score >= 45.0:
        return "pass"
    if direction_score >= 25.0:
        return "borderline"
    return "fail"


def auto_preservation_flag(score: float) -> str:
    return "safe" if score >= 65.0 else "risky"


def auto_audibility_flag(effect_score: float) -> str:
    return "likely" if effect_score >= 35.0 else "weak"


def auto_quant_grade(quant_score: float, direction_score: float, preservation: float) -> str:
    if quant_score >= 65.0 and direction_score >= 45.0 and preservation >= 70.0:
        return "strong_pass"
    if quant_score >= 55.0 and direction_score >= 35.0:
        return "pass"
    if quant_score >= 40.0:
        return "borderline"
    return "fail"


def auto_quant_notes(
    *,
    shift_score: float,
    f0_drift_cents: float | None,
    mel_mae: float | None,
) -> str:
    notes: list[str] = []
    if shift_score < 30.0:
        notes.append("effect_subtle")
    if f0_drift_cents is not None and f0_drift_cents > 180.0:
        notes.append("f0_drift_gt_180c")
    if mel_mae is not None and mel_mae > 0.90:
        notes.append("mel_mae_gt_0p90")
    return ";".join(notes)


def load_csv_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
        return rows, list(rows[0].keys()) if rows else []


def ensure_copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def build_quant_summary(rows: list[dict[str, str]]) -> str:
    def avg(field: str) -> float:
        values = [parse_float(row.get(field)) for row in rows]
        clean = [value for value in values if value is not None]
        return sum(clean) / len(clean) if clean else float("nan")

    grade_counts: dict[str, int] = {}
    for row in rows:
        grade = row.get("auto_quant_grade", "")
        grade_counts[grade] = grade_counts.get(grade, 0) + 1

    top_rows = sorted(
        rows,
        key=lambda row: parse_float(row.get("auto_quant_score")) or 0.0,
        reverse=True,
    )[:3]
    risk_rows = sorted(
        rows,
        key=lambda row: (
            row.get("auto_direction_flag") == "fail",
            -(parse_float(row.get("f0_drift_cents")) or 0.0),
            -(parse_float(row.get("target_log_mel_mae")) or 0.0),
        ),
        reverse=True,
    )[:3]

    lines = [
        "# ATRR Vocoder Listening Quant Summary",
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
    for row in top_rows:
        lines.append(
            f"- `{row['record_id']}` | score=`{row['auto_quant_score']}` | "
            f"grade=`{row['auto_quant_grade']}` | notes=`{row.get('auto_quant_notes', '') or 'ok'}`"
        )
    lines.extend(["", "## Risk Rows", ""])
    for row in risk_rows:
        lines.append(
            f"- `{row['record_id']}` | score=`{row['auto_quant_score']}` | "
            f"direction=`{row['auto_direction_flag']}` | preserve=`{row['auto_preservation_flag']}` | "
            f"notes=`{row.get('auto_quant_notes', '') or 'ok'}`"
        )
    return "\n".join(lines) + "\n"


def build_readme(pack_label: str, output_dir: Path, args: argparse.Namespace, row_count: int) -> str:
    rel_output = output_dir.relative_to(ROOT).as_posix()
    rel_template = resolve_path(args.template_queue).relative_to(ROOT).as_posix()
    rel_adapter = resolve_path(args.adapter_summary).relative_to(ROOT).as_posix()
    note_lines = "".join(f"- note: `{note}`\n" for note in args.pack_note)
    return (
        f"# ATRR Vocoder Human Review Pack {pack_label}\n\n"
        f"- purpose: `{args.pack_purpose}`\n"
        f"- rows: `{row_count}`\n\n"
        f"{note_lines}\n"
        "## Rebuild\n\n"
        "```powershell\n"
        ".\\python.exe .\\scripts\\build_atrr_vocoder_human_review_pack.py `\n"
        f"  --template-queue {rel_template} `\n"
        f"  --adapter-summary {rel_adapter} `\n"
        f"  --output-dir {rel_output} `\n"
        f"  --pack-label {pack_label}"
        + (
            "".join(f" `\n  --control-record-id {record_id}" for record_id in args.control_record_id)
            if args.control_record_id
            else ""
        )
        + (
            "".join(f" `\n  --pack-note {note}" for note in args.pack_note)
            if args.pack_note
            else ""
        )
        + f" `\n  --pack-purpose \"{args.pack_purpose}\"\n"
        "```\n"
    )


def main() -> None:
    args = parse_args()
    template_queue = resolve_path(args.template_queue)
    adapter_summary = resolve_path(args.adapter_summary)
    output_dir = resolve_path(args.output_dir)

    template_rows, fieldnames = load_csv_rows(template_queue)
    adapter_rows, _ = load_csv_rows(adapter_summary)
    adapter_by_record = {row["record_id"]: row for row in adapter_rows if row.get("record_id")}

    if not template_rows:
        raise ValueError("Template queue is empty.")
    if not adapter_by_record:
        raise ValueError("Adapter summary is empty.")

    original_dir = output_dir / "original"
    processed_dir = output_dir / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)
    control_record_ids = set(args.control_record_id)

    output_rows: list[dict[str, str]] = []
    for template_row in template_rows:
        record_id = template_row["record_id"]
        adapter_row = adapter_by_record.get(record_id)
        if adapter_row is None:
            raise KeyError(f"Missing adapter summary row for record_id={record_id}")

        raw_src = resolve_path(template_row["original_copy"] or template_row["input_audio"])
        processed_src = resolve_path(adapter_row["target_probe_wav"])

        original_dst = original_dir / raw_src.name
        processed_dst = processed_dir / processed_src.name
        ensure_copy(raw_src, original_dst)
        ensure_copy(processed_src, processed_dst)

        shift_score = parse_float(adapter_row.get("carrier_target_shift_score")) or 0.0
        f0_drift = parse_float(adapter_row.get("f0_drift_cents"))
        mel_mae = parse_float(adapter_row.get("target_log_mel_mae"))
        preserve_score = preservation_score(f0_drift, mel_mae)
        direction_score = shift_score
        effect_score = shift_score
        quant_score = 0.7 * shift_score + 0.3 * preserve_score

        row = dict(template_row)
        row["original_copy"] = str(original_dst)
        row["processed_audio"] = str(processed_dst)
        row["review_status"] = "pending"
        row["direction_correct"] = ""
        row["effect_audible"] = ""
        row["artifact_issue"] = ""
        row["strength_fit"] = ""
        row["keep_recommendation"] = ""
        row["review_notes"] = ""
        row["auto_direction_score"] = fmt_float(direction_score, digits=2)
        row["auto_preservation_score"] = fmt_float(preserve_score, digits=2)
        row["auto_effect_score"] = fmt_float(effect_score, digits=2)
        row["auto_quant_score"] = fmt_float(quant_score, digits=2)
        row["auto_direction_flag"] = auto_direction_flag(direction_score)
        row["auto_preservation_flag"] = auto_preservation_flag(preserve_score)
        row["auto_audibility_flag"] = auto_audibility_flag(effect_score)
        row["auto_quant_grade"] = auto_quant_grade(quant_score, direction_score, preserve_score)
        row["auto_quant_notes"] = auto_quant_notes(
            shift_score=shift_score,
            f0_drift_cents=f0_drift,
            mel_mae=mel_mae,
        )
        if record_id in control_record_ids:
            existing_notes = row["auto_quant_notes"]
            row["auto_quant_notes"] = (
                f"{existing_notes};control_row_source_anchor"
                if existing_notes
                else "control_row_source_anchor"
            )
        row["processed_f0_median_hz"] = adapter_row.get("f0_probe_median_hz", row.get("processed_f0_median_hz", ""))
        row["delta_f0_median_pct"] = ""
        row["waveform_mean_abs_diff"] = adapter_row.get("source_probe_self_emd", row.get("waveform_mean_abs_diff", ""))
        row["stft_logmag_l1"] = adapter_row.get("target_log_mel_mae", row.get("stft_logmag_l1", ""))
        output_rows.append(row)

    summary_csv = output_dir / "listening_pack_summary.csv"
    queue_csv = output_dir / "listening_review_queue.csv"
    summary_md = output_dir / "listening_review_quant_summary.md"
    readme_path = output_dir / "README.md"

    for path in [summary_csv, queue_csv]:
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(output_rows)

    summary_md.write_text(build_quant_summary(output_rows), encoding="utf-8")
    readme_path.write_text(build_readme(args.pack_label, output_dir, args, len(output_rows)), encoding="utf-8")

    print(f"Wrote {summary_csv}")
    print(f"Wrote {queue_csv}")
    print(f"Wrote {summary_md}")
    print(f"Wrote {readme_path}")
    print(f"Rows: {len(output_rows)}")


if __name__ == "__main__":
    main()
