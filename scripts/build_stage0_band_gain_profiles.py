from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RULE_CONFIG = ROOT / "experiments" / "stage0_baseline" / "v1_full" / "rule_candidate_v1.json"
DEFAULT_OUTPUT_DIR = ROOT / "experiments" / "stage0_baseline" / "v1_full"

BANDS_HZ = [
    [0, 300],
    [300, 800],
    [800, 1500],
    [1500, 3000],
    [3000, 5000],
    [5000, 8000],
]

# Prototype-only normalized weights. Final DSP should re-validate these with actual listening tests.
PROFILE_TEMPLATES = {
    ("brightness_up", "high_band"): [0.00, 0.00, 0.35, 0.80, 1.00, 0.55],
    ("brightness_down", "low_band"): [-0.40, -0.70, -1.00, -0.45, -0.10, 0.00],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rule-config", default=str(DEFAULT_RULE_CONFIG))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    return parser.parse_args()


def resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return ROOT / path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_rows(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        if rows:
            writer.writerows(rows)


def build_profile_rows(rule_config: dict) -> tuple[list[dict[str, str]], dict]:
    csv_rows: list[dict[str, str]] = []
    json_rules: list[dict] = []

    for rule in rule_config["rules"]:
        action_family = rule["action_family"]
        f0_condition = rule["match"]["f0_condition"]
        weights = PROFILE_TEMPLATES.get((action_family, f0_condition))
        if weights is None:
            continue

        alpha_default = rule["strength"]["alpha_default"]
        alpha_max = rule["strength"]["alpha_max"]
        gain_db_default = [round(weight * alpha_default, 4) for weight in weights]
        gain_db_max = [round(weight * alpha_max, 4) for weight in weights]

        json_rules.append(
            {
                "rule_id": rule["rule_id"],
                "enabled": rule["enabled"],
                "match": rule["match"],
                "target_direction": rule["target_direction"],
                "action_family": action_family,
                "signal_name": rule["signal_name"],
                "prototype_profile": {
                    "profile_version": "stage0_band_gain_profile_v1",
                    "band_edges_hz": BANDS_HZ,
                    "normalized_weights": weights,
                    "gain_db_default": gain_db_default,
                    "gain_db_max": gain_db_max,
                },
                "confidence": rule["confidence"],
                "priority": rule["priority"],
                "notes": rule["notes"],
            }
        )

        for idx, ((low_hz, high_hz), weight, gain_default, gain_max) in enumerate(
            zip(BANDS_HZ, weights, gain_db_default, gain_db_max),
            start=1,
        ):
            csv_rows.append(
                {
                    "rule_id": rule["rule_id"],
                    "band_index": str(idx),
                    "band_low_hz": str(low_hz),
                    "band_high_hz": str(high_hz),
                    "normalized_weight": f"{weight:.4f}",
                    "gain_db_default": f"{gain_default:.4f}",
                    "gain_db_max": f"{gain_max:.4f}",
                    "action_family": action_family,
                    "target_direction": rule["target_direction"],
                    "group_value": rule["match"]["group_value"],
                    "f0_condition": f0_condition,
                }
            )

    json_payload = {
        "profile_version": "stage0_band_gain_profile_v1",
        "source_rule_config": rule_config["config_version"],
        "bands_hz": BANDS_HZ,
        "rules": json_rules,
    }
    return csv_rows, json_payload


def main() -> None:
    args = parse_args()
    rule_config = load_json(resolve_path(args.rule_config))
    output_dir = resolve_path(args.output_dir)

    csv_rows, json_payload = build_profile_rows(rule_config)
    csv_path = output_dir / "rule_candidate_band_gain_profiles_v1.csv"
    json_path = output_dir / "rule_candidate_band_gain_profiles_v1.json"

    write_rows(
        csv_path,
        csv_rows,
        [
            "rule_id",
            "band_index",
            "band_low_hz",
            "band_high_hz",
            "normalized_weight",
            "gain_db_default",
            "gain_db_max",
            "action_family",
            "target_direction",
            "group_value",
            "f0_condition",
        ],
    )
    json_path.write_text(
        json.dumps(json_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    print(f"Wrote {csv_path}")
    print(f"Wrote {json_path}")
    print(f"Profile rules: {len(json_payload['rules'])}")


if __name__ == "__main__":
    main()
