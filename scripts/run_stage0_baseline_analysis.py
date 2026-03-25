from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

from enrich_manifest_features import enrich_row


ROOT = Path(__file__).resolve().parents[1]
META_DIR = ROOT / "data" / "datasets" / "_meta"
FIXED_EVAL_FINAL = ROOT / "experiments" / "fixed_eval" / "v1_2" / "fixed_eval_review_final_v1_2.csv"

DEFAULT_SPEECH_INPUT = META_DIR / "utterance_manifest_clean_speech_v1.csv"
DEFAULT_SINGING_INPUT = META_DIR / "utterance_manifest_clean_singing_v1.csv"
DEFAULT_OUTPUT_DIR = ROOT / "experiments" / "stage0_baseline" / "v1"

FEATURE_FIELDS = [
    "rms_dbfs",
    "peak_dbfs",
    "clipping_ratio",
    "silence_ratio_40db",
    "zcr_mean",
    "spectral_centroid_hz_mean",
    "f0_voiced_ratio",
    "f0_median_hz",
    "f0_p10_hz",
    "f0_p90_hz",
]

SPEECH_PILOT_QUOTA_PER_CELL = 64
SINGING_PILOT_QUOTA_PER_CELL = 16


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--speech-input", default=str(DEFAULT_SPEECH_INPUT))
    parser.add_argument("--singing-input", default=str(DEFAULT_SINGING_INPUT))
    parser.add_argument("--fixed-eval-input", default=str(FIXED_EVAL_FINAL))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--pilot", action="store_true", help="Run on a small deterministic subset first.")
    parser.add_argument("--reuse-existing", action="store_true", help="Reuse enriched CSVs when they already exist.")
    parser.add_argument("--f0-sr", type=int, default=16000)
    parser.add_argument("--frame-period-ms", type=float, default=10.0)
    return parser.parse_args()


def resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return ROOT / path


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"No rows to write for {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def fmt_float(value: float | None, digits: int = 6) -> str:
    if value is None or math.isnan(value):
        return ""
    return f"{value:.{digits}f}"


def parse_float(value: str) -> float | None:
    if value == "":
        return None
    try:
        out = float(value)
    except ValueError:
        return None
    if math.isnan(out):
        return None
    return out


def group_limit(rows: list[dict[str, str]], key_fields: list[str], quota: int) -> list[dict[str, str]]:
    counts: Counter[tuple[str, ...]] = Counter()
    selected: list[dict[str, str]] = []
    for row in rows:
        key = tuple(row[field] for field in key_fields)
        if counts[key] >= quota:
            continue
        selected.append(row)
        counts[key] += 1
    return selected


def build_pilot_inputs(
    speech_rows: list[dict[str, str]],
    singing_rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    speech_selected = group_limit(speech_rows, ["selection_cell"], SPEECH_PILOT_QUOTA_PER_CELL)
    singing_selected = group_limit(singing_rows, ["selection_cell"], SINGING_PILOT_QUOTA_PER_CELL)
    return speech_selected, singing_selected


def enrich_manifest(
    rows: list[dict[str, str]],
    out_csv: Path,
    reuse_existing: bool,
    f0_sr: int,
    frame_period_ms: float,
) -> list[dict[str, str]]:
    if reuse_existing and out_csv.exists():
        return read_rows(out_csv)

    enriched_rows = [enrich_row(row, f0_sr=f0_sr, frame_period_ms=frame_period_ms) for row in rows]
    write_rows(out_csv, enriched_rows)
    return enriched_rows


def build_overview_rows(
    speech_rows: list[dict[str, str]],
    singing_rows: list[dict[str, str]],
    fixed_eval_rows: list[dict[str, str]],
    mode_name: str,
) -> list[dict[str, str]]:
    overview: list[dict[str, str]] = []

    def add_subset_rows(rows: list[dict[str, str]], subset_name: str) -> None:
        gender_counts = Counter(row["gender"] for row in rows)
        feature_ok = sum(1 for row in rows if row.get("feature_status") == "ok")
        overview.append(
            {
                "section": "subset_overview",
                "name": subset_name,
                "mode_name": mode_name,
                "num_rows": str(len(rows)),
                "female_rows": str(gender_counts.get("female", 0)),
                "male_rows": str(gender_counts.get("male", 0)),
                "feature_ok_rows": str(feature_ok),
                "feature_error_rows": str(len(rows) - feature_ok),
                "notes": "",
            }
        )

    add_subset_rows(speech_rows, "clean_speech")
    add_subset_rows(singing_rows, "clean_singing")

    usable_yes = sum(1 for row in fixed_eval_rows if row.get("usable_for_fixed_eval") == "yes")
    reviewed = sum(1 for row in fixed_eval_rows if row.get("review_status") == "reviewed")
    overview.append(
        {
            "section": "fixed_eval_status",
            "name": "fixed_eval_v1_2",
            "mode_name": mode_name,
            "num_rows": str(len(fixed_eval_rows)),
            "female_rows": str(sum(1 for row in fixed_eval_rows if row["gender"] == "female")),
            "male_rows": str(sum(1 for row in fixed_eval_rows if row["gender"] == "male")),
            "feature_ok_rows": str(sum(1 for row in fixed_eval_rows if row.get("feature_status") == "ok")),
            "feature_error_rows": str(sum(1 for row in fixed_eval_rows if row.get("feature_status") != "ok")),
            "notes": f"usable_yes={usable_yes};reviewed={reviewed}",
        }
    )
    return overview


def feature_summary_rows(
    rows: list[dict[str, str]],
    subset_name: str,
    group_axis: str,
) -> list[dict[str, str]]:
    grouped: defaultdict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row[group_axis], row["gender"])].append(row)

    out_rows: list[dict[str, str]] = []
    for group_value in sorted({key[0] for key in grouped}):
        female_rows = grouped.get((group_value, "female"), [])
        male_rows = grouped.get((group_value, "male"), [])
        for feature_name in FEATURE_FIELDS:
            female_values = [parse_float(row.get(feature_name, "")) for row in female_rows]
            male_values = [parse_float(row.get(feature_name, "")) for row in male_rows]
            female_values = [v for v in female_values if v is not None]
            male_values = [v for v in male_values if v is not None]
            female_mean = statistics.fmean(female_values) if female_values else math.nan
            male_mean = statistics.fmean(male_values) if male_values else math.nan
            out_rows.append(
                {
                    "subset_name": subset_name,
                    "group_axis": group_axis,
                    "group_value": group_value,
                    "feature_name": feature_name,
                    "female_count": str(len(female_values)),
                    "male_count": str(len(male_values)),
                    "female_mean": fmt_float(female_mean),
                    "male_mean": fmt_float(male_mean),
                    "female_minus_male": fmt_float(
                        female_mean - male_mean if female_values and male_values else math.nan
                    ),
                }
            )
    return out_rows


def quantile_thresholds(values: list[float], quantiles: list[float]) -> list[float]:
    ordered = sorted(values)
    thresholds: list[float] = []
    for q in quantiles:
        idx = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * q)))
        thresholds.append(ordered[idx])
    return thresholds


def assign_bin(value: float, thresholds: list[float]) -> str:
    if value <= thresholds[0]:
        return "q1_low"
    if value <= thresholds[1]:
        return "q2_midlow"
    if value <= thresholds[2]:
        return "q3_midhigh"
    return "q4_high"


def f0_bucket_rows(rows: list[dict[str, str]], subset_name: str, group_axis: str) -> list[dict[str, str]]:
    voiced_rows = [row for row in rows if row.get("feature_status") == "ok" and parse_float(row.get("f0_median_hz", ""))]
    values = [parse_float(row["f0_median_hz"]) for row in voiced_rows]
    values = [v for v in values if v is not None]
    if len(values) < 4:
        return []

    thresholds = quantile_thresholds(values, [0.25, 0.5, 0.75])
    grouped: defaultdict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in voiced_rows:
        value = parse_float(row["f0_median_hz"])
        if value is None:
            continue
        f0_bin = assign_bin(value, thresholds)
        grouped[(row[group_axis], row["gender"], f0_bin)].append(row)

    out_rows: list[dict[str, str]] = []
    for key in sorted(grouped):
        group_value, gender, f0_bin = key
        cell_rows = grouped[key]
        centroid_values = [parse_float(row["spectral_centroid_hz_mean"]) for row in cell_rows]
        tilt_values = []
        for row in cell_rows:
            centroid = parse_float(row["spectral_centroid_hz_mean"])
            f0_median = parse_float(row["f0_median_hz"])
            if centroid is None or f0_median in (None, 0.0):
                continue
            tilt_values.append(math.log10(max(centroid, 1e-6)) - math.log10(max(f0_median, 1e-6)))

        out_rows.append(
            {
                "subset_name": subset_name,
                "group_axis": group_axis,
                "group_value": group_value,
                "gender": gender,
                "f0_bin": f0_bin,
                "num_rows": str(len(cell_rows)),
                "f0_bin_upper_q1_hz": fmt_float(thresholds[0]),
                "f0_bin_upper_q2_hz": fmt_float(thresholds[1]),
                "f0_bin_upper_q3_hz": fmt_float(thresholds[2]),
                "mean_f0_median_hz": fmt_float(
                    statistics.fmean(v for v in (parse_float(row["f0_median_hz"]) for row in cell_rows) if v is not None)
                ),
                "mean_spectral_centroid_hz": fmt_float(
                    statistics.fmean(v for v in centroid_values if v is not None) if centroid_values else math.nan
                ),
                "mean_log_centroid_minus_log_f0": fmt_float(
                    statistics.fmean(tilt_values) if tilt_values else math.nan
                ),
            }
        )
    return out_rows


def top_shift_rows(summary_rows: list[dict[str, str]], subset_name: str, feature_name: str, limit: int = 5) -> list[dict[str, str]]:
    filtered = [row for row in summary_rows if row["subset_name"] == subset_name and row["feature_name"] == feature_name]
    sortable = []
    for row in filtered:
        delta = parse_float(row["female_minus_male"])
        if delta is None:
            continue
        sortable.append((abs(delta), delta, row))
    sortable.sort(reverse=True, key=lambda item: item[0])
    out_rows: list[dict[str, str]] = []
    for rank, (_, delta, row) in enumerate(sortable[:limit], start=1):
        out_rows.append(
            {
                "subset_name": subset_name,
                "feature_name": feature_name,
                "rank": str(rank),
                "group_axis": row["group_axis"],
                "group_value": row["group_value"],
                "female_minus_male": fmt_float(delta),
            }
        )
    return out_rows


def build_readme(
    output_path: Path,
    mode_name: str,
    speech_rows: list[dict[str, str]],
    singing_rows: list[dict[str, str]],
    overview_rows: list[dict[str, str]],
    summary_rows: list[dict[str, str]],
) -> None:
    overview_by_name = {row["name"]: row for row in overview_rows}
    speech_top_centroid = top_shift_rows(summary_rows, "clean_speech", "spectral_centroid_hz_mean", limit=4)
    singing_top_centroid = top_shift_rows(summary_rows, "clean_singing", "spectral_centroid_hz_mean", limit=4)

    def render_shift_block(rows: list[dict[str, str]]) -> list[str]:
        if not rows:
            return ["- 无足够数据"]
        return [
            f"- {row['group_axis']}={row['group_value']}，female_minus_male={row['female_minus_male']}"
            for row in rows
        ]

    lines = [
        "# Stage 0 Baseline Analysis",
        "",
        f"- 运行模式：`{mode_name}`",
        f"- speech 输入条数：`{len(speech_rows)}`",
        f"- singing 输入条数：`{len(singing_rows)}`",
        f"- 固定评测集终稿：`{overview_by_name['fixed_eval_v1_2']['notes']}`",
        "",
        "## 输出文件",
        "",
        "- `input_snapshot/clean_speech_input.csv`",
        "- `input_snapshot/clean_singing_input.csv`",
        "- `clean_speech_enriched.csv`",
        "- `clean_singing_enriched.csv`",
        "- `analysis_overview.csv`",
        "- `gender_feature_summary.csv`",
        "- `f0_bucket_summary.csv`",
        "",
        "## 观察摘要",
        "",
        f"- clean_speech feature OK：`{overview_by_name['clean_speech']['feature_ok_rows']}/{overview_by_name['clean_speech']['num_rows']}`",
        f"- clean_singing feature OK：`{overview_by_name['clean_singing']['feature_ok_rows']}/{overview_by_name['clean_singing']['num_rows']}`",
        "",
        "### speech 侧 spectral centroid 差异较大的 group",
        "",
        *render_shift_block(speech_top_centroid),
        "",
        "### singing 侧 spectral centroid 差异较大的 group",
        "",
        *render_shift_block(singing_top_centroid),
        "",
        "## 备注",
        "",
        "- 本轮只固定第一版基线入口，不把统计显著性和热图一次做满。",
        "- `f0_bucket_summary.csv` 使用当前样本的 `f0_median_hz` 四分位做分桶。",
        "- 如需全量开跑，可去掉 `--pilot` 并保留同一输出结构。",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    args = parse_args()
    speech_input = resolve_path(args.speech_input)
    singing_input = resolve_path(args.singing_input)
    fixed_eval_input = resolve_path(args.fixed_eval_input)
    output_dir = resolve_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    speech_rows = read_rows(speech_input)
    singing_rows = read_rows(singing_input)
    fixed_eval_rows = read_rows(fixed_eval_input)

    mode_name = "pilot" if args.pilot else "full"
    if args.pilot:
        speech_rows, singing_rows = build_pilot_inputs(speech_rows, singing_rows)

    input_snapshot_dir = output_dir / "input_snapshot"
    input_snapshot_dir.mkdir(parents=True, exist_ok=True)
    write_rows(input_snapshot_dir / "clean_speech_input.csv", speech_rows)
    write_rows(input_snapshot_dir / "clean_singing_input.csv", singing_rows)

    speech_enriched = enrich_manifest(
        speech_rows,
        output_dir / "clean_speech_enriched.csv",
        reuse_existing=args.reuse_existing,
        f0_sr=args.f0_sr,
        frame_period_ms=args.frame_period_ms,
    )
    singing_enriched = enrich_manifest(
        singing_rows,
        output_dir / "clean_singing_enriched.csv",
        reuse_existing=args.reuse_existing,
        f0_sr=args.f0_sr,
        frame_period_ms=args.frame_period_ms,
    )

    overview_rows = build_overview_rows(speech_enriched, singing_enriched, fixed_eval_rows, mode_name)
    write_rows(output_dir / "analysis_overview.csv", overview_rows)

    summary_rows = feature_summary_rows(speech_enriched, "clean_speech", "dataset_name")
    summary_rows.extend(feature_summary_rows(singing_enriched, "clean_singing", "coarse_style"))
    write_rows(output_dir / "gender_feature_summary.csv", summary_rows)

    f0_rows = f0_bucket_rows(speech_enriched, "clean_speech", "dataset_name")
    f0_rows.extend(f0_bucket_rows(singing_enriched, "clean_singing", "coarse_style"))
    write_rows(output_dir / "f0_bucket_summary.csv", f0_rows)

    build_readme(output_dir / "README.md", mode_name, speech_enriched, singing_enriched, overview_rows, summary_rows)

    print(f"Wrote baseline analysis to {output_dir}")
    print(f"Speech rows: {len(speech_enriched)}")
    print(f"Singing rows: {len(singing_enriched)}")


if __name__ == "__main__":
    main()
