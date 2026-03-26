from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from apply_stage0_rule_preconditioner import load_audio, process_one, resolve_path, save_audio
from select_stage0_candidate_rules import load_config as load_rule_config
from select_stage0_candidate_rules import matches_range, parse_float


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RULE_CONFIG = ROOT / "experiments" / "stage0_baseline" / "v1_full" / "rule_candidate_v1.json"
DEFAULT_PROFILE_CONFIG = ROOT / "experiments" / "stage0_baseline" / "v1_full" / "rule_candidate_band_gain_profiles_v1.json"
DEFAULT_INPUT_CSV = ROOT / "experiments" / "stage0_baseline" / "v1_full" / "clean_singing_enriched.csv"
DEFAULT_OUTPUT_DIR = ROOT / "tmp" / "stage0_rule_listening_pack" / "v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rule-config", default=str(DEFAULT_RULE_CONFIG))
    parser.add_argument("--profile-config", default=str(DEFAULT_PROFILE_CONFIG))
    parser.add_argument("--input-csv", default=str(DEFAULT_INPUT_CSV))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--audio-format", choices=["wav", "flac"], default="wav")
    parser.add_argument("--n-fft", type=int, default=2048)
    parser.add_argument("--hop-length", type=int, default=512)
    parser.add_argument("--peak-limit", type=float, default=0.98)
    return parser.parse_args()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_profile_lookup(profile_config: dict) -> dict[str, dict]:
    return {rule["rule_id"]: rule for rule in profile_config["rules"]}


def desired_source_gender(target_direction: str) -> str:
    return "male" if target_direction == "feminine" else "female"


def row_matches_rule(row: dict[str, str], rule: dict) -> bool:
    if row.get("domain") != rule["match"]["domain"]:
        return False
    if row.get("coarse_style", "") != rule["match"]["group_value"]:
        return False
    if row.get("gender") != desired_source_gender(rule["target_direction"]):
        return False
    f0_median = parse_float(row.get("f0_median_hz"))
    if not matches_range(
        f0_median,
        rule["match"].get("f0_lower_hz"),
        rule["match"].get("f0_upper_hz"),
    ):
        return False
    return True


def select_rows_for_rules(rows: list[dict[str, str]], rules: list[dict]) -> list[tuple[dict, dict]]:
    selected: list[tuple[dict, dict]] = []
    used_utt_ids: set[str] = set()
    for rule in rules:
        candidates = [row for row in rows if row_matches_rule(row, rule) and row["utt_id"] not in used_utt_ids]
        candidates.sort(key=lambda row: row["utt_id"])
        if not candidates:
            continue
        chosen = candidates[0]
        used_utt_ids.add(chosen["utt_id"])
        selected.append((rule, chosen))
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
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    rule_config = load_rule_config(resolve_path(args.rule_config))
    profile_lookup = build_profile_lookup(load_json(resolve_path(args.profile_config)))
    input_csv = resolve_path(args.input_csv)
    output_dir = resolve_path(args.output_dir)
    originals_dir = output_dir / "original"
    processed_dir = output_dir / "processed"

    with input_csv.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    selected_pairs = select_rows_for_rules(rows, rule_config["rules"])
    summary_rows: list[dict[str, str]] = []

    for rule, row in selected_pairs:
        input_audio = resolve_path(row["path_raw"])
        stem = f"{rule['match']['group_value']}__{rule['target_direction']}__{row['utt_id']}"
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
            group_value=row["coarse_style"],
            target_direction=rule["target_direction"],
            f0_median_hz=parse_float(row["f0_median_hz"]),
            n_fft=args.n_fft,
            hop_length=args.hop_length,
            peak_limit=args.peak_limit,
        )

        summary_rows.append(
            {
                "rule_id": rule["rule_id"],
                "utt_id": row["utt_id"],
                "source_gender": row["gender"],
                "target_direction": rule["target_direction"],
                "group_value": row["coarse_style"],
                "f0_condition": rule["match"]["f0_condition"],
                "f0_median_hz": row["f0_median_hz"],
                "input_audio": str(input_audio),
                "original_copy": str(original_copy),
                "processed_audio": result["output_audio"],
                "confidence": rule["confidence"],
                "strength_label": rule["strength"]["label"],
                "alpha_default": f"{rule['strength']['alpha_default']:.3f}",
                "alpha_max": f"{rule['strength']['alpha_max']:.3f}",
            }
        )

    summary_path = output_dir / "listening_pack_summary.csv"
    write_summary(summary_path, summary_rows)
    print(f"Wrote {summary_path}")
    print(f"Selected rules: {len(summary_rows)}")
    print(f"Output dir: {output_dir}")


if __name__ == "__main__":
    main()
