from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from sample_fixed_eval_set import CELL_SPECS, DURATION_BINS, select_for_bin


ROOT = Path(__file__).resolve().parents[1]
REVIEW_QUEUE = ROOT / "experiments" / "fixed_eval" / "v1" / "review_pack" / "review_queue_v1.csv"
UTT_MANIFEST = ROOT / "data" / "datasets" / "_meta" / "utterance_manifest.csv"
OUT_DIR = ROOT / "experiments" / "fixed_eval" / "v1_1"

EXCLUSION_REASONS = {
    "m1_long_inhaled_u": "special phonation: inhaled long tone; not a neutral singing benchmark",
    "m11_scales_vocal_fry_i": "special phonation: vocal fry; not a neutral singing benchmark",
    "m4_long_trillo_e": "special phonation: trillo; unstable / discontinuous singing texture",
    "m1_scales_lip_trill_a": "special phonation: lip trill; not a neutral singing benchmark",
    "f1_scales_lip_trill_a": "special phonation: lip trill; not a neutral singing benchmark",
    "f5_arpeggios_lip_trill_o": "special phonation: lip trill; not a neutral singing benchmark",
    "f3_scales_lip_trill_u": "special phonation: lip trill; not a neutral singing benchmark",
    "f6_scales_vocal_fry_e": "special phonation: vocal fry; not a neutral singing benchmark",
    "p252_391_mic1": "speech sample contains end-of-utterance cough / throat-clearing artifact",
    "1284_1180_000007_000001": "auditory gender salience unclear; exclude from fixed benchmark bucket",
    "2078_142845_000085_000003": "auditory gender salience unclear; exclude from fixed benchmark bucket",
}

KEEP_MAYBE = {
    "f2_arpeggios_f_slow_piano_a": "keep for now; only slight issue noted and still representative",
    "p230_107_mic1": "keep for now; sentence remains usable and bucket assignment is clear",
}
DISALLOWED_SINGING_TECHNIQUE_MARKERS = (
    "/trillo/",
    "/lip_trill/",
    "/vocal_fry/",
    "/inhaled/",
)


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def is_allowed_candidate(row: dict[str, str]) -> bool:
    if row["domain"] != "singing":
        return True
    path_raw = row["path_raw"]
    return not any(marker in path_raw for marker in DISALLOWED_SINGING_TECHNIQUE_MARKERS)


def cell_bin_center(duration_bin: str) -> float:
    for bin_name, _lower, _upper, center in DURATION_BINS:
        if bin_name == duration_bin:
            return center
    raise KeyError(duration_bin)


def cell_bin_bounds(duration_bin: str) -> tuple[float, float]:
    for bin_name, lower, upper, _center in DURATION_BINS:
        if bin_name == duration_bin:
            return lower, upper
    raise KeyError(duration_bin)


def build_replacement_manifest() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    reviewed_rows = load_csv(REVIEW_QUEUE)
    utt_rows = load_csv(UTT_MANIFEST)

    excluded_utts = set(EXCLUSION_REASONS)
    reviewed_by_utt = {row["utt_id"]: row for row in reviewed_rows}

    keep_rows = [row for row in reviewed_rows if row["utt_id"] not in excluded_utts]
    existing_utts = {row["utt_id"] for row in keep_rows}
    all_v1_utts = {row["utt_id"] for row in reviewed_rows}

    replacements: list[dict[str, str]] = []

    for spec in CELL_SPECS:
        cell_rows = [
            row
            for row in keep_rows
            if row["eval_bucket"] == spec.eval_bucket and row["dataset_name"] == spec.dataset_name
        ]
        for duration_bin, _lower, _upper, _center in DURATION_BINS:
            kept_bin_rows = [row for row in cell_rows if row["duration_bin"] == duration_bin]
            quota = spec.per_bin
            if len(kept_bin_rows) >= quota:
                continue

            lower, upper = cell_bin_bounds(duration_bin)
            center = cell_bin_center(duration_bin)
            speaker_counts: Counter[str] = Counter(row["speaker_id"] for row in kept_bin_rows)

            candidates = [
                row
                for row in utt_rows
                if row["dataset_name"] == spec.dataset_name
                and row["domain"] == spec.domain
                and row["gender"] == spec.gender
                and row["quality_flag"] == "ok"
                and lower <= float(row["duration_sec"]) < upper
                and row["utt_id"] not in all_v1_utts
                and row["utt_id"] not in existing_utts
                and row["utt_id"] not in excluded_utts
                and is_allowed_candidate(row)
            ]

            picked = select_for_bin(
                candidates=candidates,
                center=center,
                quota=quota - len(kept_bin_rows),
                max_per_speaker=spec.max_per_speaker,
                speaker_counts=speaker_counts,
            )

            for index, row in enumerate(picked, start=1):
                out_row = dict(row)
                out_row["eval_set_id"] = "fixed_eval_v1_1"
                out_row["eval_bucket"] = spec.eval_bucket
                out_row["duration_bin"] = duration_bin
                out_row["selection_order"] = str(len(kept_bin_rows) + index)
                out_row["selection_rule"] = "replacement_after_review_keep_original_cell_and_duration_quota"
                out_row["replacement_for"] = ""
                replacements.append(out_row)
                existing_utts.add(row["utt_id"])

    replacements_by_cell: dict[tuple[str, str, str], list[dict[str, str]]] = {}
    for row in replacements:
        key = (row["eval_bucket"], row["dataset_name"], row["duration_bin"])
        replacements_by_cell.setdefault(key, []).append(row)

    final_rows: list[dict[str, str]] = []
    replacement_log: list[dict[str, str]] = []

    for row in reviewed_rows:
        utt_id = row["utt_id"]
        if utt_id in excluded_utts:
            key = (row["eval_bucket"], row["dataset_name"], row["duration_bin"])
            candidate_list = replacements_by_cell.get(key, [])
            if not candidate_list:
                raise RuntimeError(f"No replacement found for excluded row {utt_id}")
            replacement = candidate_list.pop(0)
            replacement["replacement_for"] = utt_id
            final_rows.append(replacement)
            replacement_log.append(
                {
                    "excluded_utt_id": utt_id,
                    "excluded_path_raw": row["path_raw"],
                    "excluded_reason": EXCLUSION_REASONS[utt_id],
                    "replacement_utt_id": replacement["utt_id"],
                    "replacement_path_raw": replacement["path_raw"],
                    "eval_bucket": row["eval_bucket"],
                    "dataset_name": row["dataset_name"],
                    "duration_bin": row["duration_bin"],
                }
            )
        else:
            out_row = dict(row)
            out_row["eval_set_id"] = "fixed_eval_v1_1"
            out_row["replacement_for"] = ""
            final_rows.append(out_row)

    excluded_rows = []
    for utt_id, reason in EXCLUSION_REASONS.items():
        row = reviewed_by_utt[utt_id]
        excluded_rows.append(
            {
                "utt_id": utt_id,
                "eval_bucket": row["eval_bucket"],
                "dataset_name": row["dataset_name"],
                "speaker_id": row["speaker_id"],
                "duration_bin": row["duration_bin"],
                "path_raw": row["path_raw"],
                "exclusion_reason": reason,
            }
        )

    final_rows.sort(
        key=lambda row: (
            row["eval_bucket"],
            row["dataset_name"],
            row["duration_bin"],
            int(row["selection_order"]),
            row["utt_id"],
        )
    )
    return final_rows, excluded_rows, replacement_log


def write_summary(path: Path, excluded_rows: list[dict[str, str]], replacement_log: list[dict[str, str]]) -> None:
    lines = [
        "# fixed_eval v1.1 review resolution",
        "",
        "## 决策",
        "",
        "- 移除所有已标记且确属特殊发声技巧的 singing 样本：`trillo`、`lip_trill`、`vocal_fry`、`inhaled`。",
        "- 移除带明显咳嗽 / 清嗓尾音的 speech 样本。",
        "- 移除两条听感性别指向不清的 speech 样本，保持固定评测桶的清晰度。",
        "- 保留其余样本，尽量不打乱已经完成的人工听审结果。",
        "",
        "## 已移除样本",
        "",
    ]
    for row in excluded_rows:
        lines.append(
            f"- `{row['utt_id']}` | `{row['eval_bucket']}` | `{row['dataset_name']}` | {row['exclusion_reason']}"
        )
    lines.extend(["", "## 替换关系", ""])
    for row in replacement_log:
        lines.append(
            f"- `{row['excluded_utt_id']}` -> `{row['replacement_utt_id']}` | "
            f"`{row['eval_bucket']}` | `{row['dataset_name']}` | `{row['duration_bin']}`"
        )
    lines.extend(
        [
            "",
            "## 保留的原存疑样本",
            "",
            *[f"- `{utt_id}` | {reason}" for utt_id, reason in KEEP_MAYBE.items()],
            "",
            "## 后续建议",
            "",
            "- 仅对新增替换进来的样本做补充听审，不需要全量重听。",
            "- 如果后续还要进一步提纯 singing 基准集，可以考虑把 `VocalSet` 中更多技巧性标签整体排除出固定评测集。",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    final_rows, excluded_rows, replacement_log = build_replacement_manifest()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    fieldnames = list(final_rows[0].keys()) if final_rows else []
    write_csv(OUT_DIR / "fixed_eval_manifest_v1_1.csv", fieldnames, final_rows)
    write_csv(
        OUT_DIR / "excluded_samples_v1_1.csv",
        ["utt_id", "eval_bucket", "dataset_name", "speaker_id", "duration_bin", "path_raw", "exclusion_reason"],
        excluded_rows,
    )
    write_csv(
        OUT_DIR / "replacement_log_v1_1.csv",
        [
            "excluded_utt_id",
            "excluded_path_raw",
            "excluded_reason",
            "replacement_utt_id",
            "replacement_path_raw",
            "eval_bucket",
            "dataset_name",
            "duration_bin",
        ],
        replacement_log,
    )
    write_summary(OUT_DIR / "README.md", excluded_rows, replacement_log)

    print(f"Wrote {OUT_DIR / 'fixed_eval_manifest_v1_1.csv'}")
    print(f"Excluded: {len(excluded_rows)}")
    print(f"Replacements: {len(replacement_log)}")


if __name__ == "__main__":
    main()
