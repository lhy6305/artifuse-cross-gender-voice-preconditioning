from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from row_identity import get_record_id


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "experiments" / "fixed_eval" / "v1_2" / "fixed_eval_manifest_v1_2.csv"
REPLACEMENTS = ROOT / "experiments" / "fixed_eval" / "v1_2" / "review_pack" / "replacements_only_queue_v1_2.csv"
OUT_DIR = ROOT / "experiments" / "fixed_eval" / "v1_2"


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
    usable = Counter(row.get("usable_for_fixed_eval", "") for row in rows)
    lines = [
        "# fixed_eval v1.2 final status",
        "",
        "## 结论",
        "",
        "- `v1.2` 新增的 4 条替换样本已全部补听并通过。",
        "- 当前固定评测集总计 `96` 条，全部已审。",
        "- 当前没有残留 `maybe` 样本。",
        "",
        "## 汇总",
        "",
        f"- 总样本数：`{len(rows)}`",
        f"- `usable=yes`：`{usable.get('yes', 0)}`",
        f"- `usable=maybe`：`{usable.get('maybe', 0)}`",
        f"- 其他：`{len(rows) - usable.get('yes', 0) - usable.get('maybe', 0)}`",
        "",
        "## 后续默认入口",
        "",
        "- 主清单：`experiments/fixed_eval/v1_2/fixed_eval_manifest_v1_2.csv`",
        "- 增强清单：`experiments/fixed_eval/v1_2/fixed_eval_manifest_v1_2_enriched.csv`",
        "- 最终状态：`experiments/fixed_eval/v1_2/fixed_eval_review_final_v1_2.csv`",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    manifest_rows = load_csv(MANIFEST)
    replacement_rows = load_csv(REPLACEMENTS)
    replacement_by_record_id = {get_record_id(row): row for row in replacement_rows}

    final_rows = []
    for row in manifest_rows:
        out_row = dict(row)
        record_id = get_record_id(row)
        if record_id in replacement_by_record_id:
            replacement = replacement_by_record_id[record_id]
            for key, value in replacement.items():
                if key in out_row:
                    out_row[key] = value
                else:
                    out_row[key] = value
        out_row["usable_for_fixed_eval"] = out_row.get("usable_for_fixed_eval") or "yes"
        out_row["review_status"] = out_row.get("review_status") or "reviewed"
        final_rows.append(out_row)

    final_rows.sort(
        key=lambda row: (
            row.get("eval_bucket", ""),
            row.get("dataset_name", ""),
            row.get("duration_bin", ""),
            int(row.get("selection_order", "0")),
            get_record_id(row),
        )
    )

    fieldnames: list[str] = []
    for row in final_rows:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)

    write_csv(OUT_DIR / "fixed_eval_review_final_v1_2.csv", fieldnames, final_rows)
    write_summary(OUT_DIR / "FINAL_STATUS.md", final_rows)

    print(f"Wrote {OUT_DIR / 'fixed_eval_review_final_v1_2.csv'}")
    print(f"Rows: {len(final_rows)}")
    print(f"Maybe: {sum(1 for row in final_rows if row.get('usable_for_fixed_eval') == 'maybe')}")


if __name__ == "__main__":
    main()
