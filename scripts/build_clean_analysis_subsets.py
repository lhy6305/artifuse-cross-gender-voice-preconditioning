from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
META_DIR = ROOT / "data" / "datasets" / "_meta"
IN_MANIFEST = META_DIR / "utterance_manifest.csv"
OUT_SPEECH = META_DIR / "utterance_manifest_clean_speech_v1.csv"
OUT_SINGING = META_DIR / "utterance_manifest_clean_singing_v1.csv"
OUT_SUMMARY = META_DIR / "clean_subset_summary_v1.csv"

SPEECH_DATASETS = {"VCTK Corpus 0.92", "LibriTTS-R"}
SINGING_DATASET = "VocalSet 1.2"
SINGING_ALLOWLIST = {
    "fast_forte",
    "fast_piano",
    "forte",
    "pp",
    "slow_forte",
    "slow_piano",
    "straight",
    "vibrato",
}


def load_rows() -> list[dict[str, str]]:
    with IN_MANIFEST.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def extract_technique(path_raw: str) -> str:
    parts = Path(path_raw).parts
    return parts[-2] if len(parts) >= 2 else ""


def stable_row_sort_key(row: dict[str, str]) -> tuple[float, str, str]:
    return (float(row["duration_sec"]), row["speaker_id"], row["utt_id"])


def round_robin_select(rows: list[dict[str, str]], quota: int) -> list[dict[str, str]]:
    by_speaker: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_speaker[row["speaker_id"]].append(row)

    for speaker_rows in by_speaker.values():
        speaker_rows.sort(key=stable_row_sort_key)

    speaker_order = sorted(by_speaker)
    selected: list[dict[str, str]] = []

    while len(selected) < quota:
        progressed = False
        for speaker_id in speaker_order:
            speaker_rows = by_speaker[speaker_id]
            if not speaker_rows:
                continue
            selected.append(speaker_rows.pop(0))
            progressed = True
            if len(selected) >= quota:
                break
        if not progressed:
            raise RuntimeError(f"Unable to fill quota={quota}, only selected {len(selected)} rows.")

    return selected


def build_clean_speech(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    filtered = [
        row
        for row in rows
        if row["dataset_name"] in SPEECH_DATASETS
        and row["domain"] == "speech"
        and row["quality_flag"] == "ok"
        and row["gender"] in {"male", "female"}
        and row["language"] == "English"
        and 2.0 <= float(row["duration_sec"]) <= 20.0
    ]

    cells: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in filtered:
        cells[(row["dataset_name"], row["gender"])].append(row)

    target_per_cell = min(len(cell_rows) for cell_rows in cells.values())
    selected: list[dict[str, str]] = []
    for cell_key in sorted(cells):
        cell_rows = round_robin_select(cells[cell_key], target_per_cell)
        for row in cell_rows:
            out_row = dict(row)
            out_row["clean_subset_name"] = "clean_speech_v1"
            out_row["clean_rule_version"] = "v1"
            out_row["selection_cell"] = f"{cell_key[0]}|{cell_key[1]}"
            out_row["coarse_style"] = "neutral_speech"
            out_row["selection_note"] = (
                "quality_ok;duration_2_20;English;balanced_by_dataset_and_gender;round_robin_by_speaker"
            )
            selected.append(out_row)

    return sorted(selected, key=lambda row: (row["dataset_name"], row["gender"], row["speaker_id"], row["utt_id"]))


def build_clean_singing(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    filtered = []
    for row in rows:
        if row["dataset_name"] != SINGING_DATASET:
            continue
        if row["domain"] != "singing":
            continue
        if row["quality_flag"] != "ok":
            continue
        if row["gender"] not in {"male", "female"}:
            continue
        if not (2.0 <= float(row["duration_sec"]) <= 20.0):
            continue
        technique = extract_technique(row["path_raw"])
        if technique not in SINGING_ALLOWLIST:
            continue
        out_row = dict(row)
        out_row["coarse_style"] = technique
        filtered.append(out_row)

    by_gender_tech: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in filtered:
        by_gender_tech[(row["gender"], row["coarse_style"])].append(row)

    selected: list[dict[str, str]] = []
    for technique in sorted(SINGING_ALLOWLIST):
        female_rows = by_gender_tech.get(("female", technique), [])
        male_rows = by_gender_tech.get(("male", technique), [])
        if not female_rows or not male_rows:
            continue
        target = min(len(female_rows), len(male_rows))
        for gender, cell_rows in (("female", female_rows), ("male", male_rows)):
            chosen = round_robin_select(cell_rows, target)
            for row in chosen:
                out_row = dict(row)
                out_row["clean_subset_name"] = "clean_singing_v1"
                out_row["clean_rule_version"] = "v1"
                out_row["selection_cell"] = f"{gender}|{technique}"
                out_row["selection_note"] = (
                    "quality_ok;duration_2_20;VocalSet_canonical;neutral_technique_allowlist;"
                    "balanced_by_gender_within_technique;round_robin_by_speaker"
                )
                selected.append(out_row)

    return sorted(selected, key=lambda row: (row["gender"], row["coarse_style"], row["speaker_id"], row["utt_id"]))


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_summary_rows(speech_rows: list[dict[str, str]], singing_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    summary_rows: list[dict[str, str]] = []

    def add_rows(rows: list[dict[str, str]], subset_name: str, extra_group: str) -> None:
        counts = Counter()
        speakers: defaultdict[tuple[str, str, str], set[str]] = defaultdict(set)
        for row in rows:
            if extra_group == "dataset":
                group_value = row["dataset_name"]
            elif extra_group == "technique":
                group_value = row["coarse_style"]
            else:
                group_value = ""
            key = (subset_name, row["gender"], group_value)
            counts[key] += 1
            speakers[key].add(row["speaker_id"])
        for key in sorted(counts):
            subset_name_v, gender, group_value = key
            summary_rows.append(
                {
                    "subset_name": subset_name_v,
                    "gender": gender,
                    "group_axis": extra_group,
                    "group_value": group_value,
                    "num_utterances": str(counts[key]),
                    "num_speakers": str(len(speakers[key])),
                }
            )

    add_rows(speech_rows, "clean_speech_v1", "dataset")
    add_rows(singing_rows, "clean_singing_v1", "technique")
    return summary_rows


def write_summary(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = ["subset_name", "gender", "group_axis", "group_value", "num_utterances", "num_speakers"]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    META_DIR.mkdir(parents=True, exist_ok=True)
    rows = load_rows()
    speech_rows = build_clean_speech(rows)
    singing_rows = build_clean_singing(rows)

    write_rows(OUT_SPEECH, speech_rows)
    write_rows(OUT_SINGING, singing_rows)
    write_summary(OUT_SUMMARY, build_summary_rows(speech_rows, singing_rows))

    print(f"Wrote {OUT_SPEECH} ({len(speech_rows)} rows)")
    print(f"Wrote {OUT_SINGING} ({len(singing_rows)} rows)")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
