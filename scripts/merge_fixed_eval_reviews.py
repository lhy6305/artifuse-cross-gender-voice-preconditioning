from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from row_identity import get_record_id


ROOT = Path(__file__).resolve().parents[1]
BASE_QUEUE = ROOT / "experiments" / "fixed_eval" / "v1" / "review_pack" / "review_queue_v1.csv"
REPLACEMENT_QUEUE = ROOT / "experiments" / "fixed_eval" / "v1_1" / "review_pack" / "replacements_only_queue_v1_1.csv"
OUT_DIR = ROOT / "experiments" / "fixed_eval" / "v1_1"


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_summary(path: Path, rows: list[dict[str, str]]) -> None:
    usable_counter = Counter(row.get("usable_for_fixed_eval", "") for row in rows)
    maybe_rows = [row for row in rows if row.get("usable_for_fixed_eval") == "maybe"]

    lines = [
        "# fixed_eval v1.1 merged review status",
        "",
        "## 说明",
        "",
        "- 这份状态只反映当前仓库里真实写入的听审结果。",
        "- 基础 96 条来自 `v1/review_queue_v1.csv`。",
        "- 被 `v1_1` 替换掉的样本不再进入最终合并视图。",
        "- `v1_1/replacements_only_queue_v1_1.csv` 中的补听结果会覆盖对应替换位。",
        "",
        "## 汇总",
        "",
        f"- 总样本数：`{len(rows)}`",
        f"- `usable=yes`：`{usable_counter.get('yes', 0)}`",
        f"- `usable=maybe`：`{usable_counter.get('maybe', 0)}`",
        f"- 其他：`{len(rows) - usable_counter.get('yes', 0) - usable_counter.get('maybe', 0)}`",
        "",
        "## 当前仍为 maybe 的样本",
        "",
    ]
    for row in maybe_rows:
        note = row.get("review_notes", "")
        lines.append(f"- `{row['utt_id']}` | `{row['eval_bucket']}` | `{note}`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    base_rows = load_csv(BASE_QUEUE)
    replacement_rows = load_csv(REPLACEMENT_QUEUE)

    excluded_utts = {row["replacement_for"] for row in replacement_rows}
    excluded_record_ids = {get_record_id(row) for row in base_rows if row["utt_id"] in excluded_utts}
    merged_rows = [row for row in base_rows if get_record_id(row) not in excluded_record_ids] + replacement_rows
    merged_rows.sort(
        key=lambda row: (
            row.get("eval_bucket", ""),
            row.get("dataset_name", ""),
            row.get("duration_bin", ""),
            int(row.get("selection_order", "0")),
            get_record_id(row),
        )
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    for row in merged_rows:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)
    write_csv(OUT_DIR / "fixed_eval_review_merged_v1_1.csv", fieldnames, merged_rows)
    write_summary(OUT_DIR / "MERGED_REVIEW_STATUS.md", merged_rows)

    print(f"Wrote {OUT_DIR / 'fixed_eval_review_merged_v1_1.csv'}")
    print(f"Rows: {len(merged_rows)}")
    print(f"Maybe: {sum(1 for row in merged_rows if row.get('usable_for_fixed_eval') == 'maybe')}")


if __name__ == "__main__":
    main()
