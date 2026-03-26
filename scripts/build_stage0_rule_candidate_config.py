from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "experiments" / "stage0_baseline" / "v1_full" / "directional_rule_draft_v1.csv"
DEFAULT_OUTPUT_DIR = ROOT / "experiments" / "stage0_baseline" / "v1_full"
DEFAULT_STABLE_BUCKET_INPUT = DEFAULT_OUTPUT_DIR / "f0_bucket_summary_stable_v1.csv"

STRENGTH_PRESETS = {
    "weak": {"alpha_default": 0.12, "alpha_max": 0.18},
    "medium": {"alpha_default": 0.18, "alpha_max": 0.28},
    "medium_high": {"alpha_default": 0.24, "alpha_max": 0.34},
    "high": {"alpha_default": 0.30, "alpha_max": 0.42},
}

CANDIDATE_FIELDNAMES = [
    "rule_id",
    "enabled",
    "domain",
    "group_axis",
    "group_value",
    "f0_condition",
    "f0_lower_hz",
    "f0_upper_hz",
    "bucket_scheme",
    "signal_name",
    "target_direction",
    "action_family",
    "strength_label",
    "alpha_default",
    "alpha_max",
    "confidence",
    "priority",
    "source_status",
    "notes",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--stable-bucket-input", default=str(DEFAULT_STABLE_BUCKET_INPUT))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
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


def build_bucket_lookup(rows: list[dict[str, str]]) -> dict[tuple[str, str, str], dict[str, str]]:
    lookup: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in rows:
        key = (row["domain"], row["group_value"], row["f0_condition"])
        lookup[key] = row
    return lookup


def normalize_stable_bucket_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for row in rows:
        if row.get("bin_status") != "comparable":
            continue
        if row.get("gender") != "female":
            continue
        subset_name = row.get("subset_name", "")
        if subset_name == "clean_singing":
            domain = "singing"
        elif subset_name == "clean_speech":
            domain = "speech"
        else:
            continue
        normalized.append(
            {
                "domain": domain,
                "group_value": row["group_value"],
                "f0_condition": row["f0_bin"],
                "f0_lower_hz": row.get("f0_lower_hz", ""),
                "f0_upper_hz": row.get("f0_upper_hz", ""),
            }
        )
    return normalized


def sanitize_token(value: str) -> str:
    return value.replace(" ", "_").replace("-", "_")


def derive_target_direction(recommended_action: str) -> str:
    if "feminine" in recommended_action:
        return "feminine"
    if "masculine" in recommended_action:
        return "masculine"
    return "neutral"


def derive_action_family(recommended_action: str) -> str:
    if recommended_action.startswith("brightness_up"):
        return "brightness_up"
    if recommended_action.startswith("brightness_down"):
        return "brightness_down"
    return recommended_action


def priority_rank(row: dict[str, str]) -> int:
    confidence_score = {"high": 3, "medium": 2, "low": 1}.get(row["confidence"], 0)
    strength_score = {"high": 4, "medium_high": 3, "medium": 2, "weak": 1}.get(row["recommended_strength"], 0)
    return confidence_score * 10 + strength_score


def select_candidate_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    for row in rows:
        if row["domain"] != "singing":
            continue
        if row["status"] != "active_candidate":
            continue
        if row["group_value"] in {"forte", "pp"}:
            continue
        target_direction = derive_target_direction(row["recommended_action"])
        if row["f0_condition"] == "high_band" and target_direction != "feminine":
            continue
        if row["f0_condition"] == "low_band" and target_direction != "masculine":
            continue
        selected.append(row)
    return selected


def build_candidate_rows(
    rows: list[dict[str, str]],
    bucket_lookup: dict[tuple[str, str, str], dict[str, str]],
) -> list[dict[str, str]]:
    out_rows: list[dict[str, str]] = []
    for row in rows:
        strength = STRENGTH_PRESETS[row["recommended_strength"]]
        target_direction = derive_target_direction(row["recommended_action"])
        action_family = derive_action_family(row["recommended_action"])
        bucket_row = bucket_lookup.get((row["domain"], row["group_value"], row["f0_condition"]), {})
        rule_id = "_".join(
            [
                "stage0",
                sanitize_token(row["domain"]),
                sanitize_token(row["group_value"]),
                sanitize_token(row["f0_condition"]),
                sanitize_token(target_direction),
                sanitize_token(action_family),
                "v1",
            ]
        )
        out_rows.append(
            {
                "rule_id": rule_id,
                "enabled": "yes",
                "domain": row["domain"],
                "group_axis": row["group_axis"],
                "group_value": row["group_value"],
                "f0_condition": row["f0_condition"],
                "f0_lower_hz": bucket_row.get("f0_lower_hz", ""),
                "f0_upper_hz": bucket_row.get("f0_upper_hz", ""),
                "bucket_scheme": row["bucket_scheme"],
                "signal_name": row["signal_name"],
                "target_direction": target_direction,
                "action_family": action_family,
                "strength_label": row["recommended_strength"],
                "alpha_default": f"{strength['alpha_default']:.3f}",
                "alpha_max": f"{strength['alpha_max']:.3f}",
                "confidence": row["confidence"],
                "priority": str(priority_rank(row)),
                "source_status": row["status"],
                "notes": row["notes"],
            }
        )

    out_rows.sort(key=lambda row: int(row["priority"]), reverse=True)
    return out_rows


def build_json_payload(candidate_rows: list[dict[str, str]]) -> dict:
    return {
        "config_version": "stage0_rule_candidate_v1",
        "source": "directional_rule_draft_v1.csv",
        "selection_policy": {
            "domain": "singing_only",
            "excluded_groups": ["forte", "pp"],
            "high_band_target": "feminine_only",
            "low_band_target": "masculine_only",
        },
        "strength_presets": STRENGTH_PRESETS,
        "rules": [
            {
                "rule_id": row["rule_id"],
                "enabled": row["enabled"] == "yes",
                "match": {
                    "domain": row["domain"],
                        "group_axis": row["group_axis"],
                        "group_value": row["group_value"],
                        "f0_condition": row["f0_condition"],
                        "f0_lower_hz": float(row["f0_lower_hz"]) if row["f0_lower_hz"] else None,
                        "f0_upper_hz": float(row["f0_upper_hz"]) if row["f0_upper_hz"] else None,
                        "bucket_scheme": row["bucket_scheme"],
                    },
                "signal_name": row["signal_name"],
                "target_direction": row["target_direction"],
                "action_family": row["action_family"],
                "strength": {
                    "label": row["strength_label"],
                    "alpha_default": float(row["alpha_default"]),
                    "alpha_max": float(row["alpha_max"]),
                },
                "confidence": row["confidence"],
                "priority": int(row["priority"]),
                "notes": row["notes"],
            }
            for row in candidate_rows
        ],
    }


def main() -> None:
    args = parse_args()
    input_path = resolve_path(args.input)
    stable_bucket_input = resolve_path(args.stable_bucket_input)
    output_dir = resolve_path(args.output_dir)

    rows = read_rows(input_path)
    stable_bucket_rows = read_rows(stable_bucket_input)
    bucket_lookup = build_bucket_lookup(normalize_stable_bucket_rows(stable_bucket_rows))
    candidate_rows = build_candidate_rows(select_candidate_rows(rows), bucket_lookup)

    csv_path = output_dir / "rule_candidate_v1.csv"
    json_path = output_dir / "rule_candidate_v1.json"
    write_rows(csv_path, candidate_rows, CANDIDATE_FIELDNAMES)
    json_path.write_text(
        json.dumps(build_json_payload(candidate_rows), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    print(f"Wrote {csv_path}")
    print(f"Wrote {json_path}")
    print(f"Candidate rules: {len(candidate_rows)}")


if __name__ == "__main__":
    main()
