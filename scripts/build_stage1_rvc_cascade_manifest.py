from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np
import pyworld

from apply_stage0_rule_preconditioner import load_audio, save_audio
from build_stage0_speech_world_stft_delta_listening_pack import (
    apply_world_guided_stft_delta,
    build_rule_lookup,
    load_json as load_rule_json,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUMMARY_CSV = ROOT / "tmp" / "stage0_speech_world_stft_delta_listening_pack" / "v1" / "listening_pack_summary.csv"
DEFAULT_TARGET_REGISTRY = ROOT / "experiments" / "stage1_rvc_eval" / "v1" / "rvc_target_registry_v1.json"
DEFAULT_RULE_CONFIG = ROOT / "experiments" / "stage0_baseline" / "v1_full" / "speech_world_stft_delta_candidate_v1.json"
DEFAULT_OUTPUT_DIR = ROOT / "tmp" / "stage1_rvc_cascade_eval" / "v1"
DEFAULT_DATA_ROOT = ROOT / "data"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-csv", default=str(DEFAULT_SUMMARY_CSV))
    parser.add_argument("--target-registry", default=str(DEFAULT_TARGET_REGISTRY))
    parser.add_argument("--rule-config", default=str(DEFAULT_RULE_CONFIG))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--data-root", default=str(DEFAULT_DATA_ROOT))
    parser.add_argument("--include-raw", action="store_true", default=True)
    parser.add_argument("--include-processed", action="store_true", default=True)
    return parser.parse_args()


def resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return ROOT / path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def slugify(value: str) -> str:
    keep = []
    for ch in value:
        if ch.isalnum():
            keep.append(ch.lower())
        elif ch in {" ", "-", "_"}:
            keep.append("_")
    out = "".join(keep).strip("_")
    while "__" in out:
        out = out.replace("__", "_")
    return out or "item"


def detect_custom_audio_files(data_root: Path) -> list[Path]:
    audio_exts = {".wav", ".flac", ".mp3", ".m4a", ".ogg", ".opus", ".aac"}
    paths: list[Path] = []
    for path in sorted(data_root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in audio_exts:
            continue
        if "datasets" in path.parts:
            continue
        paths.append(path)
    return paths


def compute_f0_median_hz(audio: np.ndarray, sample_rate: int) -> str:
    audio64 = audio.astype(np.float64)
    f0, _ = pyworld.harvest(audio64, sample_rate, frame_period=10.0, f0_floor=71.0, f0_ceil=800.0)
    voiced = f0[f0 > 0.0]
    if voiced.size == 0:
        return ""
    return f"{float(np.median(voiced)):.6f}"


def build_source_entries_from_summary(summary_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {
            "utt_id": row["utt_id"],
            "rule_id": row["rule_id"],
            "source_gender": row["source_gender"],
            "target_direction": row["target_direction"],
            "dataset_name": row["dataset_name"],
            "group_value": row["group_value"],
            "raw_audio": row["original_copy"],
            "preconditioned_audio": row["processed_audio"],
            "f0_median_hz": row.get("f0_median_hz", ""),
            "source_kind": "fixed_eval",
        }
        for row in summary_rows
    ]


def build_custom_source_entries(
    *,
    custom_audio_files: list[Path],
    targets: list[dict],
    rule_lookup: dict[tuple[str, str], dict],
    output_dir: Path,
) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    custom_output_dir = output_dir / "custom_preconditioned"
    for target in targets:
        target_direction = target.get("target_direction", "").strip()
        group_value = target.get("profile_group_value", "").strip()
        if not target_direction or not group_value:
            continue
        rule = rule_lookup.get((group_value, target_direction))
        if rule is None:
            continue
        target_slug = slugify(target["target_id"])
        for path in custom_audio_files:
            audio, sample_rate = load_audio(path)
            audio = audio.astype(np.float32)
            params = rule["method_params"]
            processed = apply_world_guided_stft_delta(
                audio,
                sample_rate=sample_rate,
                peak_limit=0.98,
                warp_ratio=float(params["warp_ratio"]),
                blend=float(params["blend"]),
                wet_mix=float(params["wet_mix"]),
                max_gain_db=float(params["max_gain_db"]),
                sp_floor_db=float(params["sp_floor_db"]),
                f0_floor_hz=float(params["f0_floor_hz"]),
                f0_ceil_hz=float(params["f0_ceil_hz"]),
                frame_period_ms=float(params["frame_period_ms"]),
                voiced_smooth_frames=int(params["voiced_smooth_frames"]),
                freq_smooth_bins=int(params["freq_smooth_bins"]),
            )
            processed_audio = custom_output_dir / target_slug / f"{path.stem}__preconditioned.wav"
            save_audio(processed_audio, processed, sample_rate)
            entries.append(
                {
                    "utt_id": path.stem,
                    "rule_id": rule["rule_id"],
                    "source_gender": "unknown",
                    "target_direction": target_direction,
                    "dataset_name": "custom_input",
                    "group_value": group_value,
                    "raw_audio": str(path),
                    "preconditioned_audio": str(processed_audio),
                    "f0_median_hz": compute_f0_median_hz(audio, sample_rate),
                    "source_kind": "custom_input",
                }
            )
    deduped: dict[tuple[str, str], dict[str, str]] = {}
    for entry in entries:
        deduped[(entry["utt_id"], entry["target_direction"])] = entry
    return list(deduped.values())


def build_rows(
    source_entries: list[dict[str, str]],
    targets: list[dict],
    output_dir: Path,
    *,
    include_raw: bool,
    include_processed: bool,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for source_entry in source_entries:
        variants: list[tuple[str, str]] = []
        if include_raw:
            variants.append(("raw", source_entry["raw_audio"]))
        if include_processed:
            variants.append(("preconditioned", source_entry["preconditioned_audio"]))
        for target in targets:
            if (
                source_entry["source_kind"] == "custom_input"
                and target.get("target_direction", "").strip() != source_entry["target_direction"]
            ):
                continue
            target_slug = slugify(target["target_id"])
            for input_variant, input_audio in variants:
                stem = Path(input_audio).stem
                output_audio = output_dir / "rendered" / target_slug / input_variant / f"{stem}__{target_slug}.wav"
                eval_item_id = f"{source_entry['utt_id']}__{input_variant}__{target_slug}"
                rows.append(
                    {
                        "eval_item_id": eval_item_id,
                        "utt_id": source_entry["utt_id"],
                        "rule_id": source_entry["rule_id"],
                        "source_gender": source_entry["source_gender"],
                        "target_direction": source_entry["target_direction"],
                        "dataset_name": source_entry["dataset_name"],
                        "group_value": source_entry["group_value"],
                        "f0_median_hz": source_entry.get("f0_median_hz", ""),
                        "source_kind": source_entry["source_kind"],
                        "input_variant": input_variant,
                        "input_audio": input_audio,
                        "output_audio": str(output_audio),
                        "target_id": target["target_id"],
                        "weight_root": target.get("weight_root", ""),
                        "model_name": target["model_name"],
                        "index_path": target.get("index_path", ""),
                        "spk_id": str(target.get("spk_id", 0)),
                        "f0_up_key": str(target.get("f0_up_key", 0)),
                        "f0_method": target.get("f0_method", "rmvpe"),
                        "index_rate": str(target.get("index_rate", 0.0)),
                        "filter_radius": str(target.get("filter_radius", 3)),
                        "resample_sr": str(target.get("resample_sr", 0)),
                        "rms_mix_rate": str(target.get("rms_mix_rate", 0.25)),
                        "protect": str(target.get("protect", 0.33)),
                        "target_notes": target.get("notes", ""),
                        "status": "pending",
                        "error_message": "",
                    }
                )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError("No rows to write.")
    fieldnames = list(rows[0].keys())
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_readme(path: Path, rows: list[dict[str, str]], summary_csv: Path, registry_path: Path) -> None:
    lines = [
        "# Stage1 RVC Cascade Eval v1",
        "",
        f"- source summary: `{summary_csv}`",
        f"- target registry: `{registry_path}`",
        f"- rows: `{len(rows)}`",
        "",
        "## Rebuild",
        "",
        "```powershell",
        ".\\python.exe .\\scripts\\build_stage1_rvc_cascade_manifest.py",
        ".\\python.exe .\\scripts\\run_stage1_rvc_cascade_batch.py",
        "```",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    summary_csv = resolve_path(args.summary_csv)
    registry_path = resolve_path(args.target_registry)
    rule_config_path = resolve_path(args.rule_config)
    data_root = resolve_path(args.data_root)
    output_dir = resolve_path(args.output_dir)
    manifest_csv = output_dir / "rvc_cascade_manifest.csv"

    with summary_csv.open("r", encoding="utf-8", newline="") as f:
        summary_rows = list(csv.DictReader(f))
    registry = load_json(registry_path)
    targets = [target for target in registry["targets"] if target.get("enabled", False)]
    rule_lookup = build_rule_lookup(load_rule_json(rule_config_path))
    source_entries = build_source_entries_from_summary(summary_rows)
    custom_audio_files = detect_custom_audio_files(data_root)
    source_entries.extend(
        build_custom_source_entries(
            custom_audio_files=custom_audio_files,
            targets=targets,
            rule_lookup=rule_lookup,
            output_dir=output_dir,
        )
    )
    rows = build_rows(
        source_entries,
        targets,
        output_dir,
        include_raw=args.include_raw,
        include_processed=args.include_processed,
    )
    write_csv(manifest_csv, rows)
    write_readme(output_dir / "README.md", rows, summary_csv, registry_path)
    print(f"Wrote {manifest_csv}")
    print(f"Rows: {len(rows)}")
    print(f"Targets: {len(targets)}")
    print(f"Custom audio files: {len(custom_audio_files)}")


if __name__ == "__main__":
    main()
