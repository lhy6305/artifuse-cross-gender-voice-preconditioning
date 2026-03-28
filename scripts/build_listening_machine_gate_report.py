from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LISTENING_REVIEW_ROOT = ROOT / "artifacts" / "listening_review"
DEFAULT_OUTPUT_DIR = ROOT / "artifacts" / "machine_gate" / "v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--input-csv", action="append", default=[], help="Optional listening_review_queue.csv path. Can be passed multiple times.")
    parser.add_argument("--min-avg-quant", type=float, default=65.0)
    parser.add_argument("--min-avg-direction", type=float, default=45.0)
    parser.add_argument("--min-avg-effect", type=float, default=45.0)
    parser.add_argument("--min-top-score", type=float, default=75.0)
    parser.add_argument("--min-strongish-rows", type=int, default=2, help="Minimum rows with grade in {strong_pass,pass,borderline}.")
    return parser.parse_args()


def resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return ROOT / path


def discover_default_inputs() -> list[Path]:
    if not DEFAULT_LISTENING_REVIEW_ROOT.exists():
        return []
    return sorted(DEFAULT_LISTENING_REVIEW_ROOT.rglob("listening_review_queue.csv"))


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def parse_float(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def queue_label(path: Path) -> str:
    return f"{path.parent.parent.name}/{path.parent.name}"


def avg(rows: list[dict[str, str]], field_name: str) -> float:
    values = [parse_float(row.get(field_name, "")) for row in rows]
    filtered = [value for value in values if value is not None]
    if not filtered:
        return 0.0
    return sum(filtered) / len(filtered)


def max_value(rows: list[dict[str, str]], field_name: str) -> float:
    values = [parse_float(row.get(field_name, "")) for row in rows]
    filtered = [value for value in values if value is not None]
    if not filtered:
        return 0.0
    return max(filtered)


def gate_decision(
    *,
    avg_quant: float,
    avg_direction: float,
    avg_effect: float,
    top_score: float,
    strongish_rows: int,
    args: argparse.Namespace,
) -> tuple[str, str]:
    quant_ok = avg_quant >= float(args.min_avg_quant)
    direction_ok = avg_direction >= float(args.min_avg_direction)
    effect_ok = avg_effect >= float(args.min_avg_effect)
    top_ok = top_score >= float(args.min_top_score)
    rows_ok = strongish_rows >= int(args.min_strongish_rows)

    if quant_ok and direction_ok and effect_ok and (top_ok or rows_ok):
        return "allow_human_review", "meets_primary_machine_gate"
    if top_ok and direction_ok and avg_effect >= float(args.min_avg_effect) * 0.8:
        return "borderline_review_optional", "has_high_top_score_but_pack_average_is_weaker"
    return "skip_human_review", "machine_gate_not_met"


def proposed_outcome_from_reviews(rows: list[dict[str, str]]) -> str:
    reviewed_rows = [row for row in rows if row.get("review_status", "").strip() == "reviewed"]
    if not reviewed_rows:
        return "not_reviewed"
    effect_counter = Counter(row.get("effect_audible", "").strip() for row in reviewed_rows)
    if effect_counter.get("yes", 0) == 0 and effect_counter.get("maybe", 0) == 0 and effect_counter.get("no", 0) == len(reviewed_rows):
        return "reviewed_null_result"
    return "reviewed_non_null"


def build_pack_rows(paths: list[Path], args: argparse.Namespace) -> list[dict[str, str]]:
    output_rows: list[dict[str, str]] = []
    for path in paths:
        rows = read_rows(path)
        avg_quant = avg(rows, "auto_quant_score")
        avg_direction = avg(rows, "auto_direction_score")
        avg_effect = avg(rows, "auto_effect_score")
        top_score = max_value(rows, "auto_quant_score")
        grade_counter = Counter(row.get("auto_quant_grade", "").strip() for row in rows)
        strongish_rows = sum(grade_counter.get(label, 0) for label in ("strong_pass", "pass", "borderline"))
        decision, reason = gate_decision(
            avg_quant=avg_quant,
            avg_direction=avg_direction,
            avg_effect=avg_effect,
            top_score=top_score,
            strongish_rows=strongish_rows,
            args=args,
        )
        reviewed_outcome = proposed_outcome_from_reviews(rows)
        output_rows.append(
            {
                "queue_label": queue_label(path),
                "queue_path": str(path),
                "rows": str(len(rows)),
                "avg_auto_quant_score": f"{avg_quant:.2f}",
                "avg_auto_direction_score": f"{avg_direction:.2f}",
                "avg_auto_effect_score": f"{avg_effect:.2f}",
                "top_auto_quant_score": f"{top_score:.2f}",
                "strong_pass_rows": str(grade_counter.get("strong_pass", 0)),
                "pass_rows": str(grade_counter.get("pass", 0)),
                "borderline_rows": str(grade_counter.get("borderline", 0)),
                "fail_rows": str(grade_counter.get("fail", 0)),
                "strongish_rows": str(strongish_rows),
                "machine_gate_decision": decision,
                "machine_gate_reason": reason,
                "reviewed_outcome": reviewed_outcome,
            }
        )
    return sorted(output_rows, key=lambda row: (row["machine_gate_decision"], -float(row["avg_auto_quant_score"]), row["queue_label"]))


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError("No rows to write.")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def build_summary_markdown(rows: list[dict[str, str]], args: argparse.Namespace) -> str:
    allow_rows = [row for row in rows if row["machine_gate_decision"] == "allow_human_review"]
    borderline_rows = [row for row in rows if row["machine_gate_decision"] == "borderline_review_optional"]
    skip_rows = [row for row in rows if row["machine_gate_decision"] == "skip_human_review"]
    lines = [
        "# Listening Machine Gate Report v1",
        "",
        "## Gate Policy",
        "",
        f"- `avg_auto_quant_score >= {args.min_avg_quant:.2f}`",
        f"- `avg_auto_direction_score >= {args.min_avg_direction:.2f}`",
        f"- `avg_auto_effect_score >= {args.min_avg_effect:.2f}`",
        f"- and (`top_auto_quant_score >= {args.min_top_score:.2f}` or `strongish_rows >= {args.min_strongish_rows}`)",
        "",
        "这个 gate 的目标不是证明方法成立，而是先过滤掉明显不值得上人工的包。",
        "",
        "## Decision Counts",
        "",
        f"- allow_human_review: `{len(allow_rows)}`",
        f"- borderline_review_optional: `{len(borderline_rows)}`",
        f"- skip_human_review: `{len(skip_rows)}`",
        "",
        "## Pack Summary",
        "",
    ]
    for row in rows:
        lines.extend(
            [
                f"### `{row['queue_label']}`",
                "",
                f"- decision: `{row['machine_gate_decision']}`",
                f"- reason: `{row['machine_gate_reason']}`",
                f"- avg quant / direction / effect: `{row['avg_auto_quant_score']}` / `{row['avg_auto_direction_score']}` / `{row['avg_auto_effect_score']}`",
                f"- top score: `{row['top_auto_quant_score']}`",
                f"- strong/pass/borderline/fail: `{row['strong_pass_rows']}` / `{row['pass_rows']}` / `{row['borderline_rows']}` / `{row['fail_rows']}`",
                f"- reviewed outcome: `{row['reviewed_outcome']}`",
                "",
            ]
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    output_dir = resolve_path(args.output_dir)
    input_paths = [resolve_path(value) for value in args.input_csv] if args.input_csv else discover_default_inputs()
    existing_paths = [path for path in input_paths if path.exists()]
    if not existing_paths:
        raise FileNotFoundError("No listening review queues found.")

    pack_rows = build_pack_rows(existing_paths, args)
    write_rows(output_dir / "listening_machine_gate_pack_summary.csv", pack_rows)
    (output_dir / "LISTENING_MACHINE_GATE_REPORT.md").write_text(
        build_summary_markdown(pack_rows, args),
        encoding="utf-8",
    )
    print(f"Wrote {output_dir / 'listening_machine_gate_pack_summary.csv'}")
    print(f"Wrote {output_dir / 'LISTENING_MACHINE_GATE_REPORT.md'}")
    print(f"Queues: {len(existing_paths)}")


if __name__ == "__main__":
    main()
