from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REVIEW_COLUMNS = [
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input enriched manifest path relative to repo root or absolute path.")
    parser.add_argument("--output-dir", required=True, help="Output folder relative to repo root or absolute path.")
    return parser.parse_args()


def resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return ROOT / path


def triage(row: dict[str, str]) -> tuple[str, int, str]:
    reasons: list[str] = []
    score = 0

    if row.get("feature_status") != "ok":
        score += 100
        reasons.append("feature_error")

    rms_dbfs = float(row["rms_dbfs"]) if row.get("rms_dbfs") else None
    silence_ratio = float(row["silence_ratio_40db"]) if row.get("silence_ratio_40db") else None
    voiced_ratio = float(row["f0_voiced_ratio"]) if row.get("f0_voiced_ratio") else None
    clipping_ratio = float(row["clipping_ratio"]) if row.get("clipping_ratio") else None

    if rms_dbfs is not None:
        if rms_dbfs < -40.0:
            score += 40
            reasons.append("very_low_rms")
        elif rms_dbfs < -35.0:
            score += 20
            reasons.append("low_rms")

    if silence_ratio is not None:
        if silence_ratio > 0.30:
            score += 40
            reasons.append("very_high_silence")
        elif silence_ratio > 0.20:
            score += 20
            reasons.append("high_silence")

    if voiced_ratio is not None:
        if voiced_ratio < 0.35:
            score += 40
            reasons.append("very_low_voiced_ratio")
        elif voiced_ratio < 0.55:
            score += 20
            reasons.append("low_voiced_ratio")

    if clipping_ratio is not None and clipping_ratio > 0.001:
        score += 20
        reasons.append("possible_clipping")

    if score >= 40:
        priority = "high"
    elif score >= 20:
        priority = "medium"
    else:
        priority = "low"

    return priority, score, ";".join(reasons)


def load_existing_reviews(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    return {
        row["path_raw"]: {column: row.get(column, "") for column in REVIEW_COLUMNS}
        for row in rows
        if row.get("path_raw")
    }


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_readme(path: Path) -> None:
    content = """# review_pack

## 文件说明

- `review_queue_v1.csv`
  - 推荐直接在 GUI 中打开的主队列，已经按 triage 优先级和风险分数排序。
- `priority_high.csv`
  - 最值得先听的一批样本，通常包含低响度、高静音比、低有声比或特征提取异常。
- `priority_medium.csv`
  - 次优先级样本，建议在 high 听完后处理。
- `priority_low.csv`
  - 没有明显自动特征异常，但仍建议最终过一遍。

## 推荐流程

1. 先运行 `scripts/open_fixed_eval_review_gui.ps1`。
2. GUI 默认读取 `review_queue_v1.csv`，从高优先级未审样本开始。
3. 如只想先做粗筛，也可以直接先听 `priority_high.csv` 里的样本。

## triage 规则

- `high`
  - 特征提取失败，或出现明显低响度 / 高静音比 / 低有声比。
- `medium`
  - 有轻到中度异常迹象，建议排在 `high` 之后。
- `low`
  - 暂无明显异常，只需做常规人工确认。
"""
    path.write_text(content, encoding="utf-8")


def main() -> None:
    args = parse_args()
    in_csv = resolve_path(args.input)
    out_dir = resolve_path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    review_queue_path = out_dir / "review_queue_v1.csv"
    existing_reviews = load_existing_reviews(review_queue_path)

    with in_csv.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    output_rows = []
    for row in rows:
        priority, score, reason = triage(row)
        out_row = dict(row)
        out_row["triage_priority"] = priority
        out_row["triage_score"] = str(score)
        out_row["triage_reason"] = reason
        out_row.update(
            {
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
        if row["path_raw"] in existing_reviews:
            out_row.update(existing_reviews[row["path_raw"]])
        output_rows.append(out_row)

    output_rows.sort(
        key=lambda row: (
            {"high": 0, "medium": 1, "low": 2}.get(row["triage_priority"], 3),
            -int(row["triage_score"]),
            row["eval_bucket"],
            row["dataset_name"],
            row["duration_bin"],
            int(row["selection_order"]),
        )
    )

    fieldnames = list(output_rows[0].keys()) if output_rows else []
    write_csv(review_queue_path, fieldnames, output_rows)
    write_csv(out_dir / "priority_high.csv", fieldnames, [row for row in output_rows if row["triage_priority"] == "high"])
    write_csv(out_dir / "priority_medium.csv", fieldnames, [row for row in output_rows if row["triage_priority"] == "medium"])
    write_csv(out_dir / "priority_low.csv", fieldnames, [row for row in output_rows if row["triage_priority"] == "low"])
    write_readme(out_dir / "README.md")

    print(f"Wrote {review_queue_path}")
    print(f"Rows: {len(output_rows)}")
    print(f"High: {sum(1 for row in output_rows if row['triage_priority'] == 'high')}")
    print(f"Medium: {sum(1 for row in output_rows if row['triage_priority'] == 'medium')}")
    print(f"Low: {sum(1 for row in output_rows if row['triage_priority'] == 'low')}")


if __name__ == "__main__":
    main()
