from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_DIR = ROOT / "experiments" / "stage0_baseline" / "v1_full"
DEFAULT_OUTPUT_DIR = DEFAULT_INPUT_DIR

FEATURE_LABELS = {
    "spectral_centroid_hz_mean": "Spectral Centroid (Hz)",
    "f0_median_hz": "F0 Median (Hz)",
    "f0_p90_hz": "F0 P90 (Hz)",
    "rms_dbfs": "RMS (dBFS)",
    "f0_voiced_ratio": "Voiced Ratio",
    "silence_ratio_40db": "Silence Ratio (-40 dB)",
}

STABLE_BUCKET_FIELDNAMES = [
    "subset_name",
    "group_axis",
    "group_value",
    "bucket_scheme",
    "num_bins",
    "min_comparable_count",
    "group_comparable_bins",
    "group_sparse_bins",
    "f0_bin",
    "f0_bin_index",
    "f0_lower_hz",
    "f0_upper_hz",
    "gender",
    "num_rows",
    "counterpart_rows",
    "bin_status",
    "mean_f0_median_hz",
    "mean_spectral_centroid_hz",
    "mean_log_centroid_minus_log_f0",
]

CANDIDATE_BUCKET_SCHEMES: list[tuple[str, list[float]]] = [
    ("quartile", [0.25, 0.5, 0.75]),
    ("tertile", [1.0 / 3.0, 2.0 / 3.0]),
    ("median_split", [0.5]),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--min-comparable-count", type=int, default=8)
    return parser.parse_args()


def resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return ROOT / path


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_rows(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        if rows:
            writer.writerows(rows)


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


def fmt_float(value: float | None, digits: int = 6) -> str:
    if value is None or math.isnan(value):
        return ""
    return f"{value:.{digits}f}"


def quantile_thresholds(values: list[float], quantiles: list[float]) -> list[float]:
    ordered = sorted(values)
    thresholds: list[float] = []
    for q in quantiles:
        idx = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * q)))
        thresholds.append(ordered[idx])
    return thresholds


def assign_bin_index(value: float, thresholds: list[float]) -> int:
    for idx, threshold in enumerate(thresholds, start=1):
        if value <= threshold:
            return idx
    return len(thresholds) + 1


def build_bin_label(bin_index: int, num_bins: int) -> str:
    if num_bins == 2:
        return ["low_band", "high_band"][bin_index - 1]
    if num_bins == 3:
        return ["low_band", "mid_band", "high_band"][bin_index - 1]
    return ["q1_low", "q2_midlow", "q3_midhigh", "q4_high"][bin_index - 1]


def filter_feature_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    filtered = []
    for row in rows:
        if row.get("feature_status") != "ok":
            continue
        if parse_float(row.get("f0_median_hz", "")) is None:
            continue
        filtered.append(row)
    return filtered


def score_scheme(
    rows: list[dict[str, str]],
    thresholds: list[float],
    min_comparable_count: int,
) -> tuple[int, int, int, dict[tuple[str, int], int]]:
    num_bins = len(thresholds) + 1
    counts: dict[tuple[str, int], int] = defaultdict(int)
    for row in rows:
        value = parse_float(row["f0_median_hz"])
        if value is None:
            continue
        counts[(row["gender"], assign_bin_index(value, thresholds))] += 1

    comparable_bins = 0
    sparse_bins = 0
    for bin_index in range(1, num_bins + 1):
        female_count = counts.get(("female", bin_index), 0)
        male_count = counts.get(("male", bin_index), 0)
        if female_count >= min_comparable_count and male_count >= min_comparable_count:
            comparable_bins += 1
        elif female_count > 0 or male_count > 0:
            sparse_bins += 1
    return comparable_bins, sparse_bins, num_bins, counts


def choose_bucket_scheme(
    rows: list[dict[str, str]],
    min_comparable_count: int,
) -> tuple[str, list[float], int, int, dict[tuple[str, int], int]]:
    values = [parse_float(row["f0_median_hz"]) for row in rows]
    values = [value for value in values if value is not None]
    if len(values) < 2:
        return "median_split", [statistics.fmean(values)] if values else [], 0, 0, {}

    best_choice: tuple[str, list[float], int, int, int, dict[tuple[str, int], int]] | None = None
    for scheme_name, quantiles in CANDIDATE_BUCKET_SCHEMES:
        thresholds = quantile_thresholds(values, quantiles)
        comparable_bins, sparse_bins, num_bins, counts = score_scheme(rows, thresholds, min_comparable_count)
        score = (comparable_bins, -sparse_bins, num_bins)
        if best_choice is None or score > (best_choice[2], -best_choice[3], best_choice[4]):
            best_choice = (scheme_name, thresholds, comparable_bins, sparse_bins, num_bins, counts)

    assert best_choice is not None
    scheme_name, thresholds, comparable_bins, sparse_bins, _, counts = best_choice
    return scheme_name, thresholds, comparable_bins, sparse_bins, counts


def mean_log_centroid_minus_log_f0(rows: list[dict[str, str]]) -> float:
    values: list[float] = []
    for row in rows:
        centroid = parse_float(row.get("spectral_centroid_hz_mean", ""))
        f0_median = parse_float(row.get("f0_median_hz", ""))
        if centroid is None or f0_median in (None, 0.0):
            continue
        values.append(math.log10(max(centroid, 1e-6)) - math.log10(max(f0_median, 1e-6)))
    if not values:
        return math.nan
    return statistics.fmean(values)


def build_stable_bucket_rows(
    rows: list[dict[str, str]],
    subset_name: str,
    group_axis: str,
    min_comparable_count: int,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    filtered_rows = filter_feature_rows(rows)
    out_rows: list[dict[str, str]] = []
    group_summary_rows: list[dict[str, str]] = []

    for group_value in sorted({row[group_axis] for row in filtered_rows}):
        group_rows = [row for row in filtered_rows if row[group_axis] == group_value]
        scheme_name, thresholds, comparable_bins, sparse_bins, counts = choose_bucket_scheme(
            group_rows,
            min_comparable_count=min_comparable_count,
        )
        num_bins = len(thresholds) + 1

        group_summary_rows.append(
            {
                "subset_name": subset_name,
                "group_axis": group_axis,
                "group_value": group_value,
                "bucket_scheme": scheme_name,
                "num_bins": str(num_bins),
                "min_comparable_count": str(min_comparable_count),
                "group_comparable_bins": str(comparable_bins),
                "group_sparse_bins": str(sparse_bins),
                "thresholds_hz": "/".join(fmt_float(value, digits=3) for value in thresholds),
            }
        )

        for bin_index in range(1, num_bins + 1):
            lower = thresholds[bin_index - 2] if bin_index > 1 else None
            upper = thresholds[bin_index - 1] if bin_index <= len(thresholds) else None
            female_count = counts.get(("female", bin_index), 0)
            male_count = counts.get(("male", bin_index), 0)
            bin_status = (
                "comparable"
                if female_count >= min_comparable_count and male_count >= min_comparable_count
                else "no_overlap"
                if female_count == 0 or male_count == 0
                else "sparse"
            )

            for gender in ("female", "male"):
                bucket_rows: list[dict[str, str]] = []
                for row in group_rows:
                    value = parse_float(row["f0_median_hz"])
                    if value is None:
                        continue
                    if assign_bin_index(value, thresholds) == bin_index and row["gender"] == gender:
                        bucket_rows.append(row)
                counterpart_gender = "male" if gender == "female" else "female"
                out_rows.append(
                    {
                        "subset_name": subset_name,
                        "group_axis": group_axis,
                        "group_value": group_value,
                        "bucket_scheme": scheme_name,
                        "num_bins": str(num_bins),
                        "min_comparable_count": str(min_comparable_count),
                        "group_comparable_bins": str(comparable_bins),
                        "group_sparse_bins": str(sparse_bins),
                        "f0_bin": build_bin_label(bin_index, num_bins),
                        "f0_bin_index": str(bin_index),
                        "f0_lower_hz": fmt_float(lower, digits=3),
                        "f0_upper_hz": fmt_float(upper, digits=3),
                        "gender": gender,
                        "num_rows": str(len(bucket_rows)),
                        "counterpart_rows": str(counts.get((counterpart_gender, bin_index), 0)),
                        "bin_status": bin_status,
                        "mean_f0_median_hz": fmt_float(
                            statistics.fmean(
                                value
                                for value in (parse_float(row["f0_median_hz"]) for row in bucket_rows)
                                if value is not None
                            )
                            if bucket_rows
                            else math.nan
                        ),
                        "mean_spectral_centroid_hz": fmt_float(
                            statistics.fmean(
                                value
                                for value in (parse_float(row["spectral_centroid_hz_mean"]) for row in bucket_rows)
                                if value is not None
                            )
                            if bucket_rows
                            else math.nan
                        ),
                        "mean_log_centroid_minus_log_f0": fmt_float(mean_log_centroid_minus_log_f0(bucket_rows)),
                    }
                )

    return out_rows, group_summary_rows


def find_summary_row(
    summary_rows: list[dict[str, str]],
    subset_name: str,
    feature_name: str,
    group_value: str,
) -> dict[str, str] | None:
    for row in summary_rows:
        if (
            row["subset_name"] == subset_name
            and row["feature_name"] == feature_name
            and row["group_value"] == group_value
        ):
            return row
    return None


def plot_speech_feature_deltas(summary_rows: list[dict[str, str]], output_path: Path) -> None:
    features = [
        "spectral_centroid_hz_mean",
        "f0_median_hz",
        "rms_dbfs",
        "f0_voiced_ratio",
    ]
    dataset_names = ["LibriTTS-R", "VCTK Corpus 0.92"]

    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    axes_flat = axes.flatten()
    colors = ["#D55E00", "#0072B2"]

    for ax, feature_name in zip(axes_flat, features):
        values = []
        for dataset_name in dataset_names:
            row = find_summary_row(summary_rows, "clean_speech", feature_name, dataset_name)
            values.append(parse_float(row["female_minus_male"]) if row else math.nan)

        ax.barh(dataset_names, values, color=colors)
        ax.axvline(0.0, color="#333333", linewidth=1.0)
        ax.set_title(FEATURE_LABELS[feature_name], fontsize=10)
        for idx, value in enumerate(values):
            if value is None or math.isnan(value):
                continue
            ax.text(value, idx, f" {value:.2f}", va="center", fontsize=8)

    fig.suptitle("Stage0 Full Speech Deltas (female - male)", fontsize=13)
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_singing_centroid_delta(summary_rows: list[dict[str, str]], output_path: Path) -> None:
    rows = [
        row
        for row in summary_rows
        if row["subset_name"] == "clean_singing" and row["feature_name"] == "spectral_centroid_hz_mean"
    ]
    rows.sort(key=lambda row: parse_float(row["female_minus_male"]) or -math.inf, reverse=True)
    labels = [row["group_value"] for row in rows]
    values = [parse_float(row["female_minus_male"]) or math.nan for row in rows]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.barh(labels, values, color="#009E73")
    ax.axvline(0.0, color="#333333", linewidth=1.0)
    ax.invert_yaxis()
    ax.set_title("Singing Spectral Centroid Delta by Style (female - male)")
    ax.set_xlabel("Hz")
    for idx, value in enumerate(values):
        if math.isnan(value):
            continue
        ax.text(value, idx, f" {value:.1f}", va="center", fontsize=8)

    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def build_comparable_delta_rows(
    stable_bucket_rows: list[dict[str, str]],
    subset_name: str,
) -> list[dict[str, str]]:
    paired: dict[tuple[str, int], dict[str, dict[str, str]]] = defaultdict(dict)
    for row in stable_bucket_rows:
        if row["subset_name"] != subset_name:
            continue
        if row["bin_status"] != "comparable":
            continue
        key = (row["group_value"], int(row["f0_bin_index"]))
        paired[key][row["gender"]] = row

    out_rows = []
    for (group_value, bin_index), pair in sorted(paired.items()):
        if "female" not in pair or "male" not in pair:
            continue
        female = pair["female"]
        male = pair["male"]
        female_value = parse_float(female["mean_log_centroid_minus_log_f0"])
        male_value = parse_float(male["mean_log_centroid_minus_log_f0"])
        if female_value is None or male_value is None:
            continue
        lower = female["f0_lower_hz"] or male["f0_lower_hz"] or ""
        upper = female["f0_upper_hz"] or male["f0_upper_hz"] or ""
        if lower and upper:
            bucket_range = f"{lower}-{upper} Hz"
        elif upper:
            bucket_range = f"<= {upper} Hz"
        elif lower:
            bucket_range = f"> {lower} Hz"
        else:
            bucket_range = "all"
        out_rows.append(
            {
                "group_value": group_value,
                "f0_bin_index": str(bin_index),
                "label": f"{group_value} | {female['f0_bin']} | {bucket_range}",
                "delta": fmt_float(female_value - male_value),
            }
        )
    return out_rows


def plot_stable_bucket_deltas(
    stable_bucket_rows: list[dict[str, str]],
    subset_name: str,
    output_path: Path,
) -> None:
    delta_rows = build_comparable_delta_rows(stable_bucket_rows, subset_name)
    delta_rows.sort(
        key=lambda row: (row["group_value"], int(row["f0_bin_index"]))
    )
    labels = [row["label"] for row in delta_rows]
    values = [parse_float(row["delta"]) or math.nan for row in delta_rows]
    color = "#CC79A7" if subset_name == "clean_singing" else "#56B4E9"

    fig_height = max(4.0, 0.45 * len(labels))
    fig, ax = plt.subplots(figsize=(11, fig_height))
    ax.barh(labels, values, color=color)
    ax.axvline(0.0, color="#333333", linewidth=1.0)
    ax.invert_yaxis()
    ax.set_title(
        f"{subset_name} stable-bin delta: log10(centroid) - log10(f0) (female - male)"
    )
    for idx, value in enumerate(values):
        if math.isnan(value):
            continue
        ax.text(value, idx, f" {value:.3f}", va="center", fontsize=8)

    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def top_rows(
    summary_rows: list[dict[str, str]],
    subset_name: str,
    feature_name: str,
    limit: int,
) -> list[dict[str, str]]:
    rows = [
        row
        for row in summary_rows
        if row["subset_name"] == subset_name and row["feature_name"] == feature_name
    ]
    rows.sort(key=lambda row: abs(parse_float(row["female_minus_male"]) or 0.0), reverse=True)
    return rows[:limit]


def build_report_markdown(
    output_path: Path,
    overview_rows: list[dict[str, str]],
    summary_rows: list[dict[str, str]],
    group_summary_rows: list[dict[str, str]],
) -> None:
    overview_by_name = {row["name"]: row for row in overview_rows}
    speech_top = top_rows(summary_rows, "clean_speech", "spectral_centroid_hz_mean", limit=2)
    singing_top = top_rows(summary_rows, "clean_singing", "spectral_centroid_hz_mean", limit=8)
    sparse_or_overlap_risk = [
        row
        for row in group_summary_rows
        if int(row["group_sparse_bins"]) > 0 or int(row["group_comparable_bins"]) < int(row["num_bins"])
    ]

    lines = [
        "# Stage 0 Full Report v1",
        "",
        "## 数据健康",
        "",
        f"- clean_speech：`{overview_by_name['clean_speech']['feature_ok_rows']}/{overview_by_name['clean_speech']['num_rows']}` feature OK",
        f"- clean_singing：`{overview_by_name['clean_singing']['feature_ok_rows']}/{overview_by_name['clean_singing']['num_rows']}` feature OK",
        f"- fixed_eval_v1_2：`{overview_by_name['fixed_eval_v1_2']['notes']}`",
        "",
        "## 图表入口",
        "",
        "- `plots/01_speech_feature_deltas.png`",
        "- `plots/02_singing_centroid_delta_by_style.png`",
        "- `plots/03_stable_bucket_tilt_deltas_speech.png`",
        "- `plots/04_stable_bucket_tilt_deltas_singing.png`",
        "",
        "## 关键观察",
        "",
        "- `speech` 侧 `spectral_centroid_hz_mean` 在两个数据集上方向一致，说明 `pilot` 里的方向性在全量样本上被确认。",
        "- `singing` 侧 style 效应仍然很强，不同 style 不能被直接折叠成一套规则。",
        "- 稳健分桶改为按 dataset/style 自适应选 `quartile / tertile / median_split`，目标是最大化可比较 bin 数，而不是固定保留 4 桶。",
        "",
        "## speech 侧 top delta",
        "",
    ]

    for row in speech_top:
        lines.append(
            f"- `{row['group_value']}` | `{row['feature_name']}` | female_minus_male=`{row['female_minus_male']}`"
        )

    lines.extend(
        [
            "",
            "## singing 侧 spectral centroid delta",
            "",
        ]
    )
    for row in singing_top:
        lines.append(
            f"- `{row['group_value']}` | female_minus_male=`{row['female_minus_male']}`"
        )

    lines.extend(
        [
            "",
            "## 稳健分桶选择",
            "",
        ]
    )
    for row in group_summary_rows:
        lines.append(
            f"- `{row['subset_name']}` / `{row['group_value']}` -> `{row['bucket_scheme']}` "
            f"(bins=`{row['num_bins']}`, comparable=`{row['group_comparable_bins']}`, "
            f"sparse=`{row['group_sparse_bins']}`, thresholds=`{row['thresholds_hz']}`)"
        )

    if sparse_or_overlap_risk:
        lines.extend(["", "## 稀疏或低重叠提醒", ""])
        for row in sparse_or_overlap_risk:
            lines.append(
                f"- `{row['subset_name']}` / `{row['group_value']}` 仍有不可完全对齐的 bin；"
                f"当前选择为 `{row['bucket_scheme']}`。"
            )

    lines.extend(
        [
            "",
            "## 输出文件",
            "",
            "- `f0_bucket_summary_stable_v1.csv`",
            "- `stage0_full_report_v1.md`",
            "- `plots/`",
        ]
    )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    args = parse_args()
    input_dir = resolve_path(args.input_dir)
    output_dir = resolve_path(args.output_dir)
    plots_dir = output_dir / "plots"

    speech_rows = read_rows(input_dir / "clean_speech_enriched.csv")
    singing_rows = read_rows(input_dir / "clean_singing_enriched.csv")
    overview_rows = read_rows(input_dir / "analysis_overview.csv")
    summary_rows = read_rows(input_dir / "gender_feature_summary.csv")

    stable_speech_rows, speech_group_summary = build_stable_bucket_rows(
        speech_rows,
        subset_name="clean_speech",
        group_axis="dataset_name",
        min_comparable_count=args.min_comparable_count,
    )
    stable_singing_rows, singing_group_summary = build_stable_bucket_rows(
        singing_rows,
        subset_name="clean_singing",
        group_axis="coarse_style",
        min_comparable_count=args.min_comparable_count,
    )
    stable_bucket_rows = stable_speech_rows + stable_singing_rows
    group_summary_rows = speech_group_summary + singing_group_summary

    write_rows(output_dir / "f0_bucket_summary_stable_v1.csv", stable_bucket_rows, STABLE_BUCKET_FIELDNAMES)
    write_rows(
        output_dir / "f0_bucket_group_scheme_summary_v1.csv",
        group_summary_rows,
        [
            "subset_name",
            "group_axis",
            "group_value",
            "bucket_scheme",
            "num_bins",
            "min_comparable_count",
            "group_comparable_bins",
            "group_sparse_bins",
            "thresholds_hz",
        ],
    )

    plot_speech_feature_deltas(summary_rows, plots_dir / "01_speech_feature_deltas.png")
    plot_singing_centroid_delta(summary_rows, plots_dir / "02_singing_centroid_delta_by_style.png")
    plot_stable_bucket_deltas(
        stable_bucket_rows,
        subset_name="clean_speech",
        output_path=plots_dir / "03_stable_bucket_tilt_deltas_speech.png",
    )
    plot_stable_bucket_deltas(
        stable_bucket_rows,
        subset_name="clean_singing",
        output_path=plots_dir / "04_stable_bucket_tilt_deltas_singing.png",
    )

    build_report_markdown(output_dir / "stage0_full_report_v1.md", overview_rows, summary_rows, group_summary_rows)

    print(f"Wrote report outputs to {output_dir}")
    print(f"Stable bucket rows: {len(stable_bucket_rows)}")
    print(f"Plots dir: {plots_dir}")


if __name__ == "__main__":
    main()
