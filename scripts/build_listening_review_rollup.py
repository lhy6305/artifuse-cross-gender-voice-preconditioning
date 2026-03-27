from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "artifacts" / "listening_review_rollup" / "v1"
DEFAULT_LISTENING_REVIEW_ROOT = ROOT / "artifacts" / "listening_review"
DEFAULT_STAGE1_ROOT = ROOT / "artifacts" / "stage1_rvc_cascade_eval"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--input-csv", action="append", default=[], help="Optional review queue path. Can be passed multiple times.")
    return parser.parse_args()


def resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return ROOT / path


def discover_default_inputs() -> list[Path]:
    paths: list[Path] = []
    if DEFAULT_LISTENING_REVIEW_ROOT.exists():
        paths.extend(sorted(DEFAULT_LISTENING_REVIEW_ROOT.rglob("listening_review_queue.csv")))
    if DEFAULT_STAGE1_ROOT.exists():
        paths.extend(sorted(DEFAULT_STAGE1_ROOT.rglob("rvc_cascade_review_queue.csv")))
    return paths


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError("No rows to write.")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def queue_label(path: Path) -> str:
    parent = path.parent.name
    grandparent = path.parent.parent.name if len(path.parents) >= 2 else ""
    stem = path.stem
    if stem == "rvc_cascade_review_queue":
        return f"{grandparent}/{parent}/stage1_cascade"
    if grandparent:
        return f"{grandparent}/{parent}"
    return parent


def normalize_secondary(effect_value: str, field_name: str, raw_value: str) -> tuple[str, str]:
    raw_value = raw_value.strip()
    effect_value = effect_value.strip()
    if raw_value:
        return raw_value, "explicit"
    if effect_value == "yes":
        inferred = {
            "direction_correct": "yes",
            "artifact_issue": "no",
            "strength_fit": "ok",
            "keep_recommendation": "yes",
        }[field_name]
        return inferred, "implicit_from_audible_yes"
    if effect_value in {"no", "maybe"}:
        return "n/a", "not_required_for_subtle_or_unclear_change"
    return "", "missing_primary_effect"


def normalize_keep(effect_value: str, row: dict[str, str]) -> tuple[str, str]:
    raw_keep = row.get("keep_recommendation", "").strip()
    if raw_keep:
        return raw_keep, "explicit"
    if effect_value != "yes":
        if effect_value in {"no", "maybe"}:
            return "n/a", "not_required_for_subtle_or_unclear_change"
        return "", "missing_primary_effect"

    direction_raw = row.get("direction_correct", "").strip()
    artifact_raw = row.get("artifact_issue", "").strip()
    strength_raw = row.get("strength_fit", "").strip()
    if direction_raw == "no" or artifact_raw in {"yes", "slight"}:
        return "n/a", "blocked_by_explicit_negative_signal"
    if strength_raw == "too_strong":
        return "n/a", "blocked_by_explicit_negative_signal"
    return "yes", "implicit_from_audible_yes"


def proposed_disposition(
    *,
    audible_yes: int,
    audible_maybe: int,
    audible_no: int,
    direction_no: int,
    artifact_yes: int,
    artifact_slight: int,
) -> str:
    if direction_no > 0 or artifact_yes > 0:
        return "reject"
    if audible_yes == 0 and audible_maybe <= 1 and audible_no > 0 and artifact_slight == 0:
        return "null_result"
    if audible_yes > 0 or audible_maybe > 0:
        if artifact_slight > 0:
            return "watch_with_risk"
        return "watch"
    return "needs_more_data"


def build_row_rollup(path: Path, rows: list[dict[str, str]]) -> list[dict[str, str]]:
    output_rows: list[dict[str, str]] = []
    label = queue_label(path)
    for row in rows:
        effect_value = row.get("effect_audible", "").strip()
        direction_value, direction_source = normalize_secondary(effect_value, "direction_correct", row.get("direction_correct", ""))
        artifact_value, artifact_source = normalize_secondary(effect_value, "artifact_issue", row.get("artifact_issue", ""))
        strength_value, strength_source = normalize_secondary(effect_value, "strength_fit", row.get("strength_fit", ""))
        keep_value, keep_source = normalize_keep(effect_value, row)
        output_rows.append(
            {
                "queue_label": label,
                "queue_path": str(path),
                "utt_id": row.get("utt_id", ""),
                "target_direction": row.get("target_direction", ""),
                "action_family": row.get("action_family", ""),
                "review_status": row.get("review_status", ""),
                "effect_audible_raw": effect_value,
                "direction_correct_raw": row.get("direction_correct", "").strip(),
                "artifact_issue_raw": row.get("artifact_issue", "").strip(),
                "strength_fit_raw": row.get("strength_fit", "").strip(),
                "keep_recommendation_raw": row.get("keep_recommendation", "").strip(),
                "effect_audible_norm": effect_value or "",
                "direction_correct_norm": direction_value,
                "artifact_issue_norm": artifact_value,
                "strength_fit_norm": strength_value,
                "keep_recommendation_norm": keep_value,
                "direction_source": direction_source,
                "artifact_source": artifact_source,
                "strength_source": strength_source,
                "keep_source": keep_source,
                "review_notes": row.get("review_notes", "").strip(),
            }
        )
    return output_rows


def count_value(rows: list[dict[str, str]], field_name: str, target: str) -> int:
    return sum(1 for row in rows if row.get(field_name, "") == target)


def build_pack_rollup(row_rollup: list[dict[str, str]]) -> list[dict[str, str]]:
    groups: dict[str, list[dict[str, str]]] = {}
    for row in row_rollup:
        groups.setdefault(row["queue_label"], []).append(row)

    output_rows: list[dict[str, str]] = []
    for label in sorted(groups):
        rows = groups[label]
        reviewed_rows = [row for row in rows if row["review_status"] == "reviewed"]
        effect_counter = Counter(row["effect_audible_norm"] for row in reviewed_rows)
        direction_counter = Counter(row["direction_correct_norm"] for row in reviewed_rows)
        artifact_counter = Counter(row["artifact_issue_norm"] for row in reviewed_rows)
        keep_counter = Counter(row["keep_recommendation_norm"] for row in reviewed_rows)
        strength_counter = Counter(row["strength_fit_norm"] for row in reviewed_rows)
        output_rows.append(
            {
                "queue_label": label,
                "queue_path": rows[0]["queue_path"],
                "total_rows": str(len(rows)),
                "reviewed_rows": str(len(reviewed_rows)),
                "pending_rows": str(sum(1 for row in rows if row["review_status"] == "pending")),
                "audible_yes": str(effect_counter.get("yes", 0)),
                "audible_maybe": str(effect_counter.get("maybe", 0)),
                "audible_no": str(effect_counter.get("no", 0)),
                "direction_yes": str(direction_counter.get("yes", 0)),
                "direction_maybe": str(direction_counter.get("maybe", 0)),
                "direction_no": str(direction_counter.get("no", 0)),
                "direction_na": str(direction_counter.get("n/a", 0)),
                "artifact_yes": str(artifact_counter.get("yes", 0)),
                "artifact_slight": str(artifact_counter.get("slight", 0)),
                "artifact_no": str(artifact_counter.get("no", 0)),
                "artifact_na": str(artifact_counter.get("n/a", 0)),
                "keep_yes": str(keep_counter.get("yes", 0)),
                "keep_maybe": str(keep_counter.get("maybe", 0)),
                "keep_no": str(keep_counter.get("no", 0)),
                "keep_na": str(keep_counter.get("n/a", 0)),
                "strength_ok": str(strength_counter.get("ok", 0)),
                "strength_too_weak": str(strength_counter.get("too_weak", 0)),
                "strength_too_strong": str(strength_counter.get("too_strong", 0)),
                "strength_na": str(strength_counter.get("n/a", 0)),
                "proposed_disposition": proposed_disposition(
                    audible_yes=effect_counter.get("yes", 0),
                    audible_maybe=effect_counter.get("maybe", 0),
                    audible_no=effect_counter.get("no", 0),
                    direction_no=direction_counter.get("no", 0),
                    artifact_yes=artifact_counter.get("yes", 0),
                    artifact_slight=artifact_counter.get("slight", 0),
                ),
                "implicit_direction_yes": str(
                    count_value(reviewed_rows, "direction_source", "implicit_from_audible_yes")
                ),
                "implicit_artifact_no": str(
                    count_value(reviewed_rows, "artifact_source", "implicit_from_audible_yes")
                ),
                "implicit_strength_ok": str(
                    count_value(reviewed_rows, "strength_source", "implicit_from_audible_yes")
                ),
                "implicit_keep_yes": str(
                    count_value(reviewed_rows, "keep_source", "implicit_from_audible_yes")
                ),
            }
        )
    return output_rows


def build_summary_markdown(pack_rows: list[dict[str, str]]) -> str:
    lines = [
        "# Listening Review Rollup v1",
        "",
        "## Sparse Review Semantics",
        "",
        "- `effect_audible` 是主开关。",
        "- 当 `effect_audible` 为 `no` 或 `maybe` 时，其它空字段视为 `n/a`，不是漏填。",
        "- 当 `effect_audible` 为 `yes` 且其它字段留空时，按用户约定解释为“该字段没有明显问题”。",
        "- 因此本汇总会对 `direction_correct / artifact_issue / strength_fit / keep_recommendation` 生成 `norm` 字段，但不会改写原始 CSV。",
        "",
        "## Pack Summary",
        "",
    ]
    for row in pack_rows:
        lines.extend(
            [
                f"### `{row['queue_label']}`",
                "",
                f"- reviewed: `{row['reviewed_rows']}/{row['total_rows']}`",
                f"- audible: `yes={row['audible_yes']}` `maybe={row['audible_maybe']}` `no={row['audible_no']}`",
                f"- direction: `yes={row['direction_yes']}` `maybe={row['direction_maybe']}` `no={row['direction_no']}` `n/a={row['direction_na']}`",
                f"- artifact: `yes={row['artifact_yes']}` `slight={row['artifact_slight']}` `no={row['artifact_no']}` `n/a={row['artifact_na']}`",
                f"- keep: `yes={row['keep_yes']}` `maybe={row['keep_maybe']}` `no={row['keep_no']}` `n/a={row['keep_na']}`",
                f"- strength: `ok={row['strength_ok']}` `too_weak={row['strength_too_weak']}` `too_strong={row['strength_too_strong']}` `n/a={row['strength_na']}`",
                f"- proposed disposition: `{row['proposed_disposition']}`",
                f"- implicit fills from audible=yes: `direction_yes={row['implicit_direction_yes']}` `artifact_no={row['implicit_artifact_no']}` `strength_ok={row['implicit_strength_ok']}` `keep_yes={row['implicit_keep_yes']}`",
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
        raise FileNotFoundError("No review queues found.")

    row_rollup: list[dict[str, str]] = []
    for path in existing_paths:
        row_rollup.extend(build_row_rollup(path, read_rows(path)))

    pack_rollup = build_pack_rollup(row_rollup)
    write_rows(output_dir / "listening_review_row_rollup.csv", row_rollup)
    write_rows(output_dir / "listening_review_pack_rollup.csv", pack_rollup)
    (output_dir / "LISTENING_REVIEW_ROLLUP.md").write_text(
        build_summary_markdown(pack_rollup),
        encoding="utf-8",
    )
    print(f"Wrote {output_dir / 'listening_review_row_rollup.csv'}")
    print(f"Wrote {output_dir / 'listening_review_pack_rollup.csv'}")
    print(f"Wrote {output_dir / 'LISTENING_REVIEW_ROLLUP.md'}")
    print(f"Queues: {len(existing_paths)}")
    print(f"Rows: {len(row_rollup)}")


if __name__ == "__main__":
    main()
