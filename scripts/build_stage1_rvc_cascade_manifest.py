from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
import sys

import numpy as np
import pyworld

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

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
DEFAULT_TARGET_AUDIO_ROOT = ROOT / "data" / "dataset_firefly_raw"
DEFAULT_TARGET_REFERENCE_CACHE = DEFAULT_OUTPUT_DIR / "target_f0_reference_cache.json"
DEFAULT_TARGET_REFERENCE_SAMPLE_COUNT = 8


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-csv", default=str(DEFAULT_SUMMARY_CSV))
    parser.add_argument("--target-registry", default=str(DEFAULT_TARGET_REGISTRY))
    parser.add_argument("--rule-config", default=str(DEFAULT_RULE_CONFIG))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--data-root", default=str(DEFAULT_DATA_ROOT))
    parser.add_argument("--target-audio-root", default=str(DEFAULT_TARGET_AUDIO_ROOT))
    parser.add_argument("--target-reference-cache", default=str(DEFAULT_TARGET_REFERENCE_CACHE))
    parser.add_argument("--target-reference-sample-count", type=int, default=DEFAULT_TARGET_REFERENCE_SAMPLE_COUNT)
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


def save_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


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


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def detect_custom_audio_files(data_root: Path, excluded_roots: list[Path] | None = None) -> list[Path]:
    audio_exts = {".wav", ".flac", ".mp3", ".m4a", ".ogg", ".opus", ".aac"}
    excluded_roots = [root.resolve() for root in (excluded_roots or []) if root.exists()]
    paths: list[Path] = []
    for path in sorted(data_root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in audio_exts:
            continue
        if "datasets" in path.parts:
            continue
        resolved = path.resolve()
        if any(is_relative_to(resolved, root) for root in excluded_roots):
            continue
        paths.append(path)
    return paths


def compute_audio_f0_median_value(audio: np.ndarray, sample_rate: int) -> float | None:
    audio64 = audio.astype(np.float64)
    f0, _ = pyworld.harvest(audio64, sample_rate, frame_period=10.0, f0_floor=71.0, f0_ceil=800.0)
    voiced = f0[f0 > 0.0]
    if voiced.size == 0:
        return None
    return float(np.median(voiced))


def compute_file_f0_median_value(path: Path) -> float | None:
    audio, sample_rate = load_audio(path)
    return compute_audio_f0_median_value(audio, sample_rate)


def compute_f0_median_hz(audio: np.ndarray, sample_rate: int) -> str:
    value = compute_audio_f0_median_value(audio, sample_rate)
    if value is None:
        return ""
    return f"{value:.6f}"


def load_cache(path: Path) -> dict:
    if not path.exists():
        return {"files": {}}
    return load_json(path)


def get_cached_or_compute_f0(path: Path, cache: dict) -> float | None:
    file_key = str(path.resolve())
    stat = path.stat()
    files = cache.setdefault("files", {})
    cached = files.get(file_key)
    if cached and cached.get("mtime_ns") == stat.st_mtime_ns and cached.get("size") == stat.st_size:
        value = cached.get("f0_median_hz")
        return None if value in {"", None} else float(value)

    value = compute_file_f0_median_value(path)
    files[file_key] = {
        "mtime_ns": stat.st_mtime_ns,
        "size": stat.st_size,
        "f0_median_hz": None if value is None else round(value, 6),
    }
    return value


def sample_evenly(paths: list[Path], sample_count: int) -> list[Path]:
    if sample_count <= 0 or len(paths) <= sample_count:
        return paths
    selected: list[Path] = []
    seen: set[Path] = set()
    for position in np.linspace(0, len(paths) - 1, num=sample_count):
        path = paths[int(round(float(position)))]
        if path in seen:
            continue
        selected.append(path)
        seen.add(path)
    return selected


def build_target_reference_lookup(
    *,
    targets: list[dict],
    custom_audio_files: list[Path],
    fallback_target_audio_root: Path,
    cache_path: Path,
    sample_count: int,
) -> dict[str, dict[str, object]]:
    cache = load_cache(cache_path)
    lookup: dict[str, dict[str, object]] = {}

    for target in targets:
        target_audio_root = resolve_path(target.get("target_audio_root", str(fallback_target_audio_root)))
        speech_paths = sorted(
            path for path in target_audio_root.rglob("*.wav") if path.is_file() and "no_text_voice" not in path.parts
        )
        target_by_stem = {path.stem: path for path in speech_paths}
        sample_paths = sample_evenly(speech_paths, sample_count)
        required_paths = list(sample_paths)
        for source_path in custom_audio_files:
            matched = target_by_stem.get(source_path.stem)
            if matched is not None and matched not in required_paths:
                required_paths.append(matched)

        f0_by_stem: dict[str, float] = {}
        for path in required_paths:
            value = get_cached_or_compute_f0(path, cache)
            if value is not None:
                f0_by_stem[path.stem] = value

        sample_values = [f0_by_stem[path.stem] for path in sample_paths if path.stem in f0_by_stem]
        global_median = float(np.median(sample_values)) if sample_values else None
        exact_match_f0 = {
            source_path.stem: f0_by_stem[target_by_stem[source_path.stem].stem]
            for source_path in custom_audio_files
            if source_path.stem in target_by_stem and target_by_stem[source_path.stem].stem in f0_by_stem
        }

        lookup[target["target_id"]] = {
            "target_audio_root": str(target_audio_root),
            "global_median_hz": global_median,
            "sample_count": len(sample_values),
            "exact_match_f0_hz": exact_match_f0,
        }

    save_json(cache_path, cache)
    return lookup


def parse_optional_float(value: str) -> float | None:
    try:
        return None if value == "" else float(value)
    except (TypeError, ValueError):
        return None


def compute_f0_up_key(source_f0_hz: float | None, target_f0_hz: float | None) -> int:
    if source_f0_hz is None or target_f0_hz is None:
        return 0
    if source_f0_hz <= 0.0 or target_f0_hz <= 0.0:
        return 0
    return int(round(12.0 * math.log2(target_f0_hz / source_f0_hz)))


def resolve_target_f0_for_source(source_entry: dict[str, str], target_reference: dict[str, object]) -> tuple[float | None, str]:
    exact_match = target_reference.get("exact_match_f0_hz", {})
    if source_entry.get("source_kind") == "custom_input" and source_entry["utt_id"] in exact_match:
        return float(exact_match[source_entry["utt_id"]]), "exact_match_target_utt"
    global_median = target_reference.get("global_median_hz")
    if global_median is not None:
        return float(global_median), f"target_reference_sample_median_n={target_reference.get('sample_count', 0)}"
    return None, "no_target_reference"


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
    target_reference_lookup: dict[str, dict[str, object]],
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

            target_reference = target_reference_lookup.get(target["target_id"], {})
            source_f0_hz = parse_optional_float(source_entry.get("f0_median_hz", ""))
            target_f0_hz, f0_reason = resolve_target_f0_for_source(source_entry, target_reference)
            f0_up_key = compute_f0_up_key(source_f0_hz, target_f0_hz)
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
                        "f0_up_key": str(f0_up_key),
                        "f0_method": target.get("f0_method", "rmvpe"),
                        "index_rate": str(target.get("index_rate", 0.0)),
                        "filter_radius": str(target.get("filter_radius", 3)),
                        "resample_sr": str(target.get("resample_sr", 0)),
                        "rms_mix_rate": str(target.get("rms_mix_rate", 0.25)),
                        "protect": str(target.get("protect", 0.33)),
                        "target_f0_reference_hz": "" if target_f0_hz is None else f"{target_f0_hz:.6f}",
                        "f0_up_key_reason": f0_reason,
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


def write_readme(
    path: Path,
    rows: list[dict[str, str]],
    summary_csv: Path,
    registry_path: Path,
    target_reference_lookup: dict[str, dict[str, object]],
) -> None:
    lines = [
        "# Stage1 RVC Cascade Eval v1",
        "",
        f"- source summary: `{summary_csv}`",
        f"- target registry: `{registry_path}`",
        f"- rows: `{len(rows)}`",
        "",
        "## Target F0 Reference",
        "",
    ]
    for target_id, reference in sorted(target_reference_lookup.items()):
        lines.append(
            f"- `{target_id}`: root=`{reference.get('target_audio_root', '')}` | "
            f"global_median_hz=`{reference.get('global_median_hz', '')}` | "
            f"sample_count=`{reference.get('sample_count', 0)}`"
        )
    lines.extend(
        [
            "",
            "## Rebuild",
            "",
            "```powershell",
            ".\\python.exe .\\scripts\\build_stage1_rvc_cascade_manifest.py",
            ".\\python.exe .\\scripts\\run_stage1_rvc_cascade_batch.ps1",
            ".\\python.exe .\\scripts\\build_stage1_rvc_cascade_review_queue.py",
            "```",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    summary_csv = resolve_path(args.summary_csv)
    registry_path = resolve_path(args.target_registry)
    rule_config_path = resolve_path(args.rule_config)
    data_root = resolve_path(args.data_root)
    target_audio_root = resolve_path(args.target_audio_root)
    output_dir = resolve_path(args.output_dir)
    target_reference_cache = resolve_path(args.target_reference_cache)
    manifest_csv = output_dir / "rvc_cascade_manifest.csv"

    with summary_csv.open("r", encoding="utf-8", newline="") as f:
        summary_rows = list(csv.DictReader(f))
    registry = load_json(registry_path)
    targets = [target for target in registry["targets"] if target.get("enabled", False)]
    rule_lookup = build_rule_lookup(load_rule_json(rule_config_path))
    source_entries = build_source_entries_from_summary(summary_rows)

    excluded_custom_roots = [target_audio_root]
    for target in targets:
        if target.get("target_audio_root"):
            excluded_custom_roots.append(resolve_path(target["target_audio_root"]))
    custom_audio_files = detect_custom_audio_files(data_root, excluded_roots=excluded_custom_roots)

    target_reference_lookup = build_target_reference_lookup(
        targets=targets,
        custom_audio_files=custom_audio_files,
        fallback_target_audio_root=target_audio_root,
        cache_path=target_reference_cache,
        sample_count=args.target_reference_sample_count,
    )

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
        target_reference_lookup,
        output_dir,
        include_raw=args.include_raw,
        include_processed=args.include_processed,
    )
    write_csv(manifest_csv, rows)
    write_readme(output_dir / "README.md", rows, summary_csv, registry_path, target_reference_lookup)
    print(f"Wrote {manifest_csv}")
    print(f"Rows: {len(rows)}")
    print(f"Targets: {len(targets)}")
    print(f"Custom audio files: {len(custom_audio_files)}")


if __name__ == "__main__":
    main()
