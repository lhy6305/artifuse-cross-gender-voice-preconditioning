from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from sample_fixed_eval_set import DURATION_BINS, select_for_bin  # noqa: E402


MERGED_REVIEW = ROOT / "experiments" / "fixed_eval" / "v1_1" / "fixed_eval_review_merged_v1_1.csv"
UTT_MANIFEST = ROOT / "data" / "datasets" / "_meta" / "utterance_manifest.csv"
OUT_DIR = ROOT / "experiments" / "fixed_eval" / "v1_2"

FINAL_DECISIONS = {
    "f1_arpeggios_lip_trill_a": {
        "decision": "remove",
        "reason": "lip_trill dominates the timbre; not representative of neutral singing input",
    },
    "f3_scales_lip_trill_o": {
        "decision": "remove",
        "reason": "lip_trill dominates the timbre; not representative of neutral singing input",
    },
    "m1_scales_lip_trill_o": {
        "decision": "remove",
        "reason": "lip_trill dominates the timbre; not representative of neutral singing input",
    },
    "m10_scales_vocal_fry_a": {
        "decision": "remove",
        "reason": "vocal_fry dominates the timbre; not representative of neutral singing input",
    },
    "f2_arpeggios_f_slow_piano_a": {
        "decision": "keep",
        "reason": "minor transient level jump only; still representative and otherwise clean",
    },
    "p230_107_mic1": {
        "decision": "keep",
        "reason": "minor transient level jump only; speech content and bucket remain usable",
    },
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


def duration_bounds(duration_bin: str) -> tuple[float, float, float]:
    for name, lower, upper, center in DURATION_BINS:
        if name == duration_bin:
            return lower, upper, center
    raise KeyError(duration_bin)


def is_allowed_candidate(row: dict[str, str]) -> bool:
    if row["domain"] != "singing":
        return True
    return not any(marker in row["path_raw"] for marker in DISALLOWED_SINGING_TECHNIQUE_MARKERS)


def build_v1_2() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    review_rows = load_csv(MERGED_REVIEW)
    utt_rows = load_csv(UTT_MANIFEST)

    removed_utts = {utt_id for utt_id, meta in FINAL_DECISIONS.items() if meta["decision"] == "remove"}
    keep_overrides = {utt_id for utt_id, meta in FINAL_DECISIONS.items() if meta["decision"] == "keep"}

    base_rows = []
    for row in review_rows:
        out_row = dict(row)
        if row["utt_id"] in keep_overrides:
            out_row["usable_for_fixed_eval"] = "yes"
            out_row["review_status"] = "reviewed"
            note = FINAL_DECISIONS[row["utt_id"]]["reason"]
            out_row["review_notes"] = note
        if row["utt_id"] not in removed_utts:
            out_row["eval_set_id"] = "fixed_eval_v1_2"
            base_rows.append(out_row)

    existing_utts = {row["utt_id"] for row in base_rows}
    prior_utts = {row["utt_id"] for row in review_rows}

    replacements: list[dict[str, str]] = []
    replacement_log: list[dict[str, str]] = []

    rows_by_bucket_dataset_bin: dict[tuple[str, str, str], list[dict[str, str]]] = {}
    removed_rows: dict[str, dict[str, str]] = {}
    for row in review_rows:
        key = (row["eval_bucket"], row["dataset_name"], row["duration_bin"])
        rows_by_bucket_dataset_bin.setdefault(key, []).append(row)
        if row["utt_id"] in removed_utts:
            removed_rows[row["utt_id"]] = row

    for removed_utt in removed_utts:
        removed_row = removed_rows[removed_utt]
        eval_bucket = removed_row["eval_bucket"]
        dataset_name = removed_row["dataset_name"]
        duration_bin = removed_row["duration_bin"]
        domain = removed_row["domain"]
        gender = removed_row["gender"]

        lower, upper, center = duration_bounds(duration_bin)
        kept_same_cell = [
            row
            for row in base_rows
            if row["eval_bucket"] == eval_bucket
            and row["dataset_name"] == dataset_name
            and row["duration_bin"] == duration_bin
        ]
        speaker_counts: Counter[str] = Counter(row["speaker_id"] for row in kept_same_cell)

        max_per_speaker = 3 if domain == "singing" else 1
        candidates = [
            row
            for row in utt_rows
            if row["dataset_name"] == dataset_name
            and row["domain"] == domain
            and row["gender"] == gender
            and row["quality_flag"] == "ok"
            and lower <= float(row["duration_sec"]) < upper
            and row["utt_id"] not in prior_utts
            and row["utt_id"] not in existing_utts
            and is_allowed_candidate(row)
        ]
        chosen = select_for_bin(
            candidates=candidates,
            center=center,
            quota=1,
            max_per_speaker=max_per_speaker,
            speaker_counts=speaker_counts,
        )[0]

        replacement = dict(chosen)
        replacement["eval_set_id"] = "fixed_eval_v1_2"
        replacement["eval_bucket"] = eval_bucket
        replacement["duration_bin"] = duration_bin
        replacement["selection_order"] = removed_row["selection_order"]
        replacement["selection_rule"] = "replacement_after_final_maybe_resolution_v1_2"
        replacement["replacement_for"] = removed_utt
        replacement["review_status"] = "pending"
        replacement["content_ok"] = "yes"
        replacement["noise_issue"] = "no"
        replacement["reverb_issue"] = "no"
        replacement["clipping_audible"] = "no"
        replacement["accompaniment_issue"] = "no"
        replacement["pronunciation_or_lyric_issue"] = "no"
        replacement["speaker_or_gender_bucket_ok"] = "yes"
        replacement["usable_for_fixed_eval"] = ""
        replacement["reviewer"] = ""
        replacement["review_notes"] = ""
        replacement["final_resolution"] = "replacement_for_removed_maybe"
        replacement["final_resolution_reason"] = FINAL_DECISIONS[removed_utt]["reason"]
        replacements.append(replacement)
        existing_utts.add(replacement["utt_id"])

        replacement_log.append(
            {
                "removed_utt_id": removed_utt,
                "removed_path_raw": removed_row["path_raw"],
                "removed_reason": FINAL_DECISIONS[removed_utt]["reason"],
                "replacement_utt_id": replacement["utt_id"],
                "replacement_path_raw": replacement["path_raw"],
                "eval_bucket": eval_bucket,
                "dataset_name": dataset_name,
                "duration_bin": duration_bin,
            }
        )

    final_rows = []
    for row in base_rows:
        row.setdefault("replacement_for", "")
        row["final_resolution"] = "keep"
        row["final_resolution_reason"] = FINAL_DECISIONS.get(row["utt_id"], {}).get("reason", "")
        final_rows.append(row)
    final_rows.extend(replacements)
    final_rows.sort(
        key=lambda row: (
            row.get("eval_bucket", ""),
            row.get("dataset_name", ""),
            row.get("duration_bin", ""),
            int(row.get("selection_order", "0")),
            row.get("utt_id", ""),
        )
    )

    removed_summary = []
    for utt_id in removed_utts:
        row = removed_rows[utt_id]
        removed_summary.append(
            {
                "utt_id": utt_id,
                "eval_bucket": row["eval_bucket"],
                "dataset_name": row["dataset_name"],
                "speaker_id": row["speaker_id"],
                "duration_bin": row["duration_bin"],
                "path_raw": row["path_raw"],
                "reason": FINAL_DECISIONS[utt_id]["reason"],
            }
        )

    return final_rows, removed_summary, replacement_log


def write_readme(path: Path, removed_summary: list[dict[str, str]], replacement_log: list[dict[str, str]]) -> None:
    lines = [
        "# fixed_eval v1.2 final maybe resolution",
        "",
        "## 决策",
        "",
        "- 保留两条仅有轻微瞬态电平扰动、但仍具代表性的样本。",
        "- 移除四条技巧性 singing 样本：三条 `lip_trill`，一条 `vocal_fry`。",
        "- 只对新增替换进来的 4 条样本做补充听审，不需要再回听全部 96 条。",
        "",
        "## 保留的原 maybe 样本",
        "",
        f"- `f2_arpeggios_f_slow_piano_a` | {FINAL_DECISIONS['f2_arpeggios_f_slow_piano_a']['reason']}",
        f"- `p230_107_mic1` | {FINAL_DECISIONS['p230_107_mic1']['reason']}",
        "",
        "## 移除样本",
        "",
    ]
    for row in sorted(removed_summary, key=lambda x: x["utt_id"]):
        lines.append(f"- `{row['utt_id']}` | `{row['eval_bucket']}` | {row['reason']}")
    lines.extend(["", "## 替换关系", ""])
    for row in replacement_log:
        lines.append(
            f"- `{row['removed_utt_id']}` -> `{row['replacement_utt_id']}` | "
            f"`{row['eval_bucket']}` | `{row['dataset_name']}` | `{row['duration_bin']}`"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    final_rows, removed_summary, replacement_log = build_v1_2()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    fieldnames: list[str] = []
    for row in final_rows:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)

    write_csv(OUT_DIR / "fixed_eval_manifest_v1_2.csv", fieldnames, final_rows)
    write_csv(
        OUT_DIR / "removed_samples_v1_2.csv",
        ["utt_id", "eval_bucket", "dataset_name", "speaker_id", "duration_bin", "path_raw", "reason"],
        removed_summary,
    )
    write_csv(
        OUT_DIR / "replacement_log_v1_2.csv",
        [
            "removed_utt_id",
            "removed_path_raw",
            "removed_reason",
            "replacement_utt_id",
            "replacement_path_raw",
            "eval_bucket",
            "dataset_name",
            "duration_bin",
        ],
        replacement_log,
    )
    write_readme(OUT_DIR / "README.md", removed_summary, replacement_log)

    print(f"Wrote {OUT_DIR / 'fixed_eval_manifest_v1_2.csv'}")
    print(f"Removed: {len(removed_summary)}")
    print(f"Replacements: {len(replacement_log)}")


if __name__ == "__main__":
    main()
