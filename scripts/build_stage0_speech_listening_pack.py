from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

from apply_stage0_rule_preconditioner import load_audio, process_one, resolve_path, save_audio
from select_stage0_candidate_rules import load_config as load_rule_config
from select_stage0_candidate_rules import parse_float


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RULE_CONFIG = ROOT / "experiments" / "stage0_baseline" / "v1_full" / "speech_rule_candidate_v1.json"
DEFAULT_PROFILE_CONFIG = ROOT / "experiments" / "stage0_baseline" / "v1_full" / "speech_rule_band_gain_profiles_v1.json"
DEFAULT_INPUT_CSV = ROOT / "experiments" / "fixed_eval" / "v1_2" / "fixed_eval_review_final_v1_2.csv"
DEFAULT_OUTPUT_DIR = ROOT / "tmp" / "stage0_speech_listening_pack" / "v1"

TARGET_DIRECTION_BY_SOURCE_GENDER = {
    "male": "feminine",
    "female": "masculine",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rule-config", default=str(DEFAULT_RULE_CONFIG))
    parser.add_argument("--profile-config", default=str(DEFAULT_PROFILE_CONFIG))
    parser.add_argument("--input-csv", default=str(DEFAULT_INPUT_CSV))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--samples-per-cell", type=int, default=2)
    parser.add_argument("--audio-format", choices=["wav", "flac"], default="wav")
    parser.add_argument("--n-fft", type=int, default=2048)
    parser.add_argument("--hop-length", type=int, default=512)
    parser.add_argument("--peak-limit", type=float, default=0.98)
    return parser.parse_args()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_profile_lookup(profile_config: dict) -> dict[str, dict]:
    return {rule["rule_id"]: rule for rule in profile_config["rules"]}


def build_rule_lookup(rule_config: dict) -> dict[str, dict]:
    return {rule["rule_id"]: rule for rule in rule_config["rules"]}


def load_source_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    return [
        row
        for row in rows
        if row.get("domain") == "speech"
        and row.get("review_status") == "reviewed"
        and row.get("usable_for_fixed_eval") == "yes"
        and row.get("speaker_or_gender_bucket_ok") == "yes"
        and row.get("gender") in TARGET_DIRECTION_BY_SOURCE_GENDER
    ]


def robust_scale(values: list[float], fallback: float) -> float:
    if not values:
        return fallback
    if len(values) == 1:
        return fallback
    median = statistics.median(values)
    deviations = [abs(value - median) for value in values]
    mad = statistics.median(deviations)
    return max(mad * 1.4826, fallback)


def row_distance_score(
    row: dict[str, str],
    *,
    duration_center: float,
    duration_scale: float,
    f0_center: float,
    f0_scale: float,
    centroid_center: float,
    centroid_scale: float,
) -> float:
    duration = parse_float(row.get("duration_sec")) or 0.0
    f0_median = parse_float(row.get("f0_median_hz")) or 0.0
    centroid = parse_float(row.get("spectral_centroid_hz_mean")) or 0.0
    silence_ratio = parse_float(row.get("silence_ratio_40db")) or 0.0
    triage_score = parse_float(row.get("triage_score")) or 0.0

    score = 0.0
    score += abs(duration - duration_center) / duration_scale
    score += abs(f0_median - f0_center) / f0_scale
    score += abs(centroid - centroid_center) / centroid_scale
    score += silence_ratio * 8.0
    score += triage_score / 20.0
    return score


def select_rows(rows: list[dict[str, str]], samples_per_cell: int) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row["dataset_name"], row["gender"])].append(row)

    selected: list[dict[str, str]] = []
    for key in sorted(grouped):
        group_rows = grouped[key]
        durations = [parse_float(row["duration_sec"]) or 0.0 for row in group_rows]
        f0_values = [parse_float(row["f0_median_hz"]) or 0.0 for row in group_rows]
        centroids = [parse_float(row["spectral_centroid_hz_mean"]) or 0.0 for row in group_rows]
        duration_center = statistics.median(durations)
        f0_center = statistics.median(f0_values)
        centroid_center = statistics.median(centroids)
        duration_scale = robust_scale(durations, fallback=0.8)
        f0_scale = robust_scale(f0_values, fallback=15.0)
        centroid_scale = robust_scale(centroids, fallback=180.0)

        scored_rows: list[tuple[float, dict[str, str]]] = []
        for row in group_rows:
            score = row_distance_score(
                row,
                duration_center=duration_center,
                duration_scale=duration_scale,
                f0_center=f0_center,
                f0_scale=f0_scale,
                centroid_center=centroid_center,
                centroid_scale=centroid_scale,
            )
            row = dict(row)
            row["selection_score"] = f"{score:.6f}"
            scored_rows.append((score, row))

        scored_rows.sort(key=lambda item: (item[0], item[1]["utt_id"]))
        for rank, (_, row) in enumerate(scored_rows[:samples_per_cell], start=1):
            row["selection_rank"] = str(rank)
            selected.append(row)

    selected.sort(key=lambda row: (row["dataset_name"], row["gender"], int(row["selection_rank"])))
    return selected


def write_summary(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "rule_id",
        "utt_id",
        "source_gender",
        "target_direction",
        "group_value",
        "f0_condition",
        "f0_median_hz",
        "input_audio",
        "original_copy",
        "processed_audio",
        "confidence",
        "strength_label",
        "alpha_default",
        "alpha_max",
        "dataset_name",
        "eval_bucket",
        "duration_sec",
        "selection_rank",
        "selection_score",
        "profile_version",
        "rule_notes",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_pack_notes(path: Path, rows: list[dict[str, str]]) -> None:
    lines = [
        "# Stage0 Speech Listening Pack v1",
        "",
        "- purpose: `speech-first audibility diagnostic`",
        "- source: `experiments/fixed_eval/v1_2/fixed_eval_review_final_v1_2.csv`",
        "- selection: `dataset_name x source_gender` 每格取 `2` 条最接近该格中位 duration / f0 / centroid 的样本",
        f"- rows: `{len(rows)}`",
        "",
        "## Composition",
        "",
    ]
    counts: dict[tuple[str, str], int] = defaultdict(int)
    for row in rows:
        counts[(row["dataset_name"], row["source_gender"])] += 1
    for key in sorted(counts):
        dataset_name, source_gender = key
        lines.append(f"- `{dataset_name}` / `{source_gender}`: `{counts[key]}`")
    lines.extend(
        [
            "",
            "## Rebuild",
            "",
            "```powershell",
            ".\\python.exe .\\scripts\\build_stage0_speech_listening_pack.py",
            ".\\python.exe .\\scripts\\build_stage0_rule_review_queue.py `",
            "  --rule-config experiments/stage0_baseline/v1_full/speech_rule_candidate_v1.json `",
            "  --summary-csv tmp/stage0_speech_listening_pack/v1/listening_pack_summary.csv `",
            "  --output-csv tmp/stage0_speech_listening_pack/v1/listening_review_queue.csv `",
            "  --summary-md tmp/stage0_speech_listening_pack/v1/listening_review_quant_summary.md",
            "```",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    rule_config = load_rule_config(resolve_path(args.rule_config))
    rule_lookup = build_rule_lookup(rule_config)
    profile_config = load_json(resolve_path(args.profile_config))
    profile_lookup = build_profile_lookup(profile_config)
    input_csv = resolve_path(args.input_csv)
    output_dir = resolve_path(args.output_dir)
    originals_dir = output_dir / "original"
    processed_dir = output_dir / "processed"

    selected_rows = select_rows(load_source_rows(input_csv), samples_per_cell=args.samples_per_cell)
    summary_rows: list[dict[str, str]] = []

    for row in selected_rows:
        input_audio = resolve_path(row["path_raw"])
        target_direction = TARGET_DIRECTION_BY_SOURCE_GENDER[row["gender"]]
        dataset_slug = "libritts_r" if row["dataset_name"] == "LibriTTS-R" else "vctk"
        stem = f"{dataset_slug}__{row['gender']}__{target_direction}__{row['utt_id']}"
        original_copy = originals_dir / f"{stem}.{args.audio_format}"
        processed_audio = processed_dir / f"{stem}.{args.audio_format}"

        audio, sample_rate = load_audio(input_audio)
        save_audio(original_copy, audio, sample_rate)

        result = process_one(
            rule_config=rule_config,
            profile_lookup=profile_lookup,
            input_audio=input_audio,
            output_audio=processed_audio,
            domain=row["domain"],
            group_value=row["dataset_name"],
            target_direction=target_direction,
            f0_median_hz=parse_float(row.get("f0_median_hz")),
            n_fft=args.n_fft,
            hop_length=args.hop_length,
            peak_limit=args.peak_limit,
        )
        if result["status"] != "ok":
            raise RuntimeError(f"No matching speech rule for utt_id={row['utt_id']} target={target_direction}")

        matched_rule = rule_lookup[result["rule_id"]]
        summary_rows.append(
            {
                "rule_id": matched_rule["rule_id"],
                "utt_id": row["utt_id"],
                "source_gender": row["gender"],
                "target_direction": target_direction,
                "group_value": row["dataset_name"],
                "f0_condition": matched_rule["match"]["f0_condition"],
                "f0_median_hz": row["f0_median_hz"],
                "input_audio": str(input_audio),
                "original_copy": str(original_copy),
                "processed_audio": result["output_audio"],
                "confidence": matched_rule["confidence"],
                "strength_label": matched_rule["strength"]["label"],
                "alpha_default": f"{matched_rule['strength']['alpha_default']:.3f}",
                "alpha_max": f"{matched_rule['strength']['alpha_max']:.3f}",
                "dataset_name": row["dataset_name"],
                "eval_bucket": row["eval_bucket"],
                "duration_sec": row["duration_sec"],
                "selection_rank": row["selection_rank"],
                "selection_score": row["selection_score"],
                "profile_version": profile_config["profile_version"],
                "rule_notes": matched_rule.get("notes", ""),
            }
        )

    summary_path = output_dir / "listening_pack_summary.csv"
    write_summary(summary_path, summary_rows)
    write_pack_notes(output_dir / "README.md", summary_rows)
    print(f"Wrote {summary_path}")
    print(f"Selected rows: {len(summary_rows)}")
    print(f"Output dir: {output_dir}")


if __name__ == "__main__":
    main()
