from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "experiments" / "stage0_baseline" / "v1_full" / "rule_candidate_v1.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--domain")
    parser.add_argument("--group-value")
    parser.add_argument("--target-direction", choices=["feminine", "masculine"])
    parser.add_argument("--f0-median-hz", type=float)
    parser.add_argument("--input-csv", help="Optional CSV for batch preview mode.")
    parser.add_argument("--output-csv", help="Required when --input-csv is set.")
    parser.add_argument("--domain-field", default="domain")
    parser.add_argument("--group-field", default="coarse_style")
    parser.add_argument("--f0-field", default="f0_median_hz")
    return parser.parse_args()


def resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return ROOT / path


def load_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_float(value: str | float | None) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def matches_range(value: float | None, lower: float | None, upper: float | None) -> bool:
    if value is None:
        return False
    if lower is not None and value <= lower:
        return False
    if upper is not None and value > upper:
        return False
    return True


def select_rules(
    config: dict,
    *,
    domain: str,
    group_value: str,
    target_direction: str,
    f0_median_hz: float | None,
) -> list[dict]:
    matched = []
    for rule in config["rules"]:
        if not rule.get("enabled", False):
            continue
        match = rule["match"]
        if match["domain"] != domain:
            continue
        if match["group_value"] != group_value:
            continue
        if rule["target_direction"] != target_direction:
            continue
        if not matches_range(
            f0_median_hz,
            match.get("f0_lower_hz"),
            match.get("f0_upper_hz"),
        ):
            continue
        matched.append(rule)
    matched.sort(key=lambda rule: rule["priority"], reverse=True)
    return matched


def write_preview(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "utt_id",
        "domain",
        "group_value",
        "target_direction",
        "f0_median_hz",
        "matched_rule_id",
        "action_family",
        "strength_label",
        "alpha_default",
        "alpha_max",
        "confidence",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def batch_preview(
    config: dict,
    *,
    input_csv: Path,
    output_csv: Path,
    domain_field: str,
    group_field: str,
    f0_field: str,
    target_direction: str,
) -> None:
    preview_rows: list[dict[str, str]] = []
    with input_csv.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            domain = row.get(domain_field, "")
            group_value = row.get(group_field, "")
            f0_median_hz = parse_float(row.get(f0_field))
            matched = select_rules(
                config,
                domain=domain,
                group_value=group_value,
                target_direction=target_direction,
                f0_median_hz=f0_median_hz,
            )
            selected = matched[0] if matched else None
            preview_rows.append(
                {
                    "utt_id": row.get("utt_id", ""),
                    "domain": domain,
                    "group_value": group_value,
                    "target_direction": target_direction,
                    "f0_median_hz": row.get(f0_field, ""),
                    "matched_rule_id": selected["rule_id"] if selected else "",
                    "action_family": selected["action_family"] if selected else "",
                    "strength_label": selected["strength"]["label"] if selected else "",
                    "alpha_default": f"{selected['strength']['alpha_default']:.3f}" if selected else "",
                    "alpha_max": f"{selected['strength']['alpha_max']:.3f}" if selected else "",
                    "confidence": selected["confidence"] if selected else "",
                }
            )
    write_preview(output_csv, preview_rows)
    matched_count = sum(1 for row in preview_rows if row["matched_rule_id"])
    print(f"Wrote {output_csv}")
    print(f"Preview rows: {len(preview_rows)}")
    print(f"Matched rows: {matched_count}")


def main() -> None:
    args = parse_args()
    config = load_config(resolve_path(args.config))

    if args.input_csv:
        if not args.output_csv:
            raise ValueError("--output-csv is required when --input-csv is set.")
        if not args.target_direction:
            raise ValueError("--target-direction is required in batch mode.")
        batch_preview(
            config,
            input_csv=resolve_path(args.input_csv),
            output_csv=resolve_path(args.output_csv),
            domain_field=args.domain_field,
            group_field=args.group_field,
            f0_field=args.f0_field,
            target_direction=args.target_direction,
        )
        return

    if not all([args.domain, args.group_value, args.target_direction, args.f0_median_hz is not None]):
        raise ValueError(
            "Single mode requires --domain, --group-value, --target-direction, and --f0-median-hz."
        )

    matched = select_rules(
        config,
        domain=args.domain,
        group_value=args.group_value,
        target_direction=args.target_direction,
        f0_median_hz=args.f0_median_hz,
    )
    print(json.dumps(matched, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
