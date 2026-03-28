from __future__ import annotations

import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from row_identity import get_record_id


ROOT = Path(__file__).resolve().parents[1]
IN_CSV = ROOT / "data" / "datasets" / "_meta" / "utterance_manifest.csv"
OUT_CSV = ROOT / "experiments" / "fixed_eval" / "v1" / "fixed_eval_manifest_v1.csv"

DURATION_BINS = (
    ("3-5s", 3.0, 5.0, 4.0),
    ("5-7s", 5.0, 7.0, 6.0),
    ("7-10s", 7.0, 10.000001, 8.5),
)


@dataclass(frozen=True)
class CellSpec:
    eval_bucket: str
    dataset_name: str
    domain: str
    gender: str
    per_bin: int
    max_per_speaker: int


CELL_SPECS = (
    CellSpec("speech_female", "VCTK Corpus 0.92", "speech", "female", 4, 1),
    CellSpec("speech_female", "LibriTTS-R", "speech", "female", 4, 1),
    CellSpec("speech_male", "VCTK Corpus 0.92", "speech", "male", 4, 1),
    CellSpec("speech_male", "LibriTTS-R", "speech", "male", 4, 1),
    CellSpec("singing_female", "VocalSet 1.2", "singing", "female", 8, 3),
    CellSpec("singing_male", "VocalSet 1.2", "singing", "male", 8, 3),
)


def load_rows() -> list[dict[str, str]]:
    with IN_CSV.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def in_duration_bin(duration_sec: float, lower: float, upper: float) -> bool:
    return lower <= duration_sec < upper


def stable_candidate_sort_key(row: dict[str, str], center: float) -> tuple[float, str, str]:
    duration_sec = float(row["duration_sec"])
    return (abs(duration_sec - center), get_record_id(row), row["path_raw"])


def select_for_bin(
    candidates: list[dict[str, str]],
    center: float,
    quota: int,
    max_per_speaker: int,
    speaker_counts: Counter[str],
) -> list[dict[str, str]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in candidates:
        grouped[row["speaker_id"]].append(row)

    for rows in grouped.values():
        rows.sort(key=lambda row: stable_candidate_sort_key(row, center))

    speaker_order = sorted(grouped)
    chosen: list[dict[str, str]] = []
    used_paths: set[str] = set()

    while len(chosen) < quota:
        progressed = False
        for speaker_id in speaker_order:
            if speaker_counts[speaker_id] >= max_per_speaker:
                continue

            rows = grouped[speaker_id]
            while rows and rows[0]["path_raw"] in used_paths:
                rows.pop(0)

            if not rows:
                continue

            row = rows.pop(0)
            chosen.append(row)
            used_paths.add(row["path_raw"])
            speaker_counts[speaker_id] += 1
            progressed = True

            if len(chosen) >= quota:
                break

        if not progressed:
            raise RuntimeError(
                f"Unable to fill quota={quota} with max_per_speaker={max_per_speaker}. "
                f"Only selected {len(chosen)} items."
            )

    return chosen


def select_fixed_eval(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []

    for spec in CELL_SPECS:
        speaker_counts: Counter[str] = Counter()
        bucket_rows = [
            row
            for row in rows
            if row["dataset_name"] == spec.dataset_name
            and row["domain"] == spec.domain
            and row["gender"] == spec.gender
            and row["quality_flag"] == "ok"
            and 3.0 <= float(row["duration_sec"]) <= 10.0
        ]

        for bin_name, lower, upper, center in DURATION_BINS:
            bin_rows = [
                row
                for row in bucket_rows
                if in_duration_bin(float(row["duration_sec"]), lower, upper)
            ]
            chosen = select_for_bin(
                candidates=bin_rows,
                center=center,
                quota=spec.per_bin,
                max_per_speaker=spec.max_per_speaker,
                speaker_counts=speaker_counts,
            )

            for index, row in enumerate(chosen, start=1):
                out_row = dict(row)
                out_row["eval_set_id"] = "fixed_eval_v1"
                out_row["eval_bucket"] = spec.eval_bucket
                out_row["duration_bin"] = bin_name
                out_row["selection_order"] = str(index)
                out_row["selection_rule"] = (
                    "quality_ok_and_3_10s_then_round_robin_by_speaker_"
                    "with_duration_center_priority"
                )
                selected.append(out_row)

    selected.sort(
        key=lambda row: (
            row["eval_bucket"],
            row["dataset_name"],
            row["duration_bin"],
            int(row["selection_order"]),
            get_record_id(row),
        )
    )
    return selected


def write_rows(rows: list[dict[str, str]]) -> None:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "eval_set_id",
        "eval_bucket",
        "duration_bin",
        "selection_order",
        "selection_rule",
        "record_id",
        "utt_id",
        "dataset_name",
        "split_name",
        "speaker_id",
        "gender",
        "domain",
        "language",
        "path_raw",
        "path_proc",
        "duration_sec",
        "sample_rate",
        "quality_flag",
        "notes",
    ]

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def print_summary(rows: list[dict[str, str]]) -> None:
    summary: Counter[tuple[str, str, str]] = Counter()
    speaker_summary: defaultdict[str, set[str]] = defaultdict(set)
    for row in rows:
        summary[(row["eval_bucket"], row["dataset_name"], row["duration_bin"])] += 1
        speaker_summary[row["eval_bucket"]].add(row["speaker_id"])

    print(f"Wrote {OUT_CSV}")
    print(f"Rows: {len(rows)}")
    for key in sorted(summary):
        print(f"{key[0]} | {key[1]} | {key[2]} -> {summary[key]}")
    for bucket in sorted(speaker_summary):
        print(f"{bucket} speakers: {len(speaker_summary[bucket])}")


def main() -> None:
    rows = load_rows()
    selected = select_fixed_eval(rows)
    write_rows(selected)
    print_summary(selected)


if __name__ == "__main__":
    main()
