from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np
import pyworld

from apply_stage0_rule_preconditioner import load_audio, resolve_path, save_audio
from build_stage0_speech_listening_pack import TARGET_DIRECTION_BY_SOURCE_GENDER, load_source_rows, select_rows


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RULE_CONFIG = ROOT / "experiments" / "stage0_baseline" / "v1_full" / "speech_vocal_tract_morph_candidate_v1.json"
DEFAULT_INPUT_CSV = ROOT / "experiments" / "fixed_eval" / "v1_2" / "fixed_eval_review_final_v1_2.csv"
DEFAULT_OUTPUT_DIR = ROOT / "tmp" / "stage0_speech_vocal_tract_listening_pack" / "v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rule-config", default=str(DEFAULT_RULE_CONFIG))
    parser.add_argument("--input-csv", default=str(DEFAULT_INPUT_CSV))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--samples-per-cell", type=int, default=2)
    parser.add_argument("--audio-format", choices=["wav", "flac"], default="wav")
    parser.add_argument("--peak-limit", type=float, default=0.98)
    return parser.parse_args()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_rule_lookup(rule_config: dict) -> dict[tuple[str, str], dict]:
    return {
        (rule["match"]["group_value"], rule["target_direction"]): rule
        for rule in rule_config["rules"]
        if rule.get("enabled", False)
    }


def analyze_world(
    audio: np.ndarray,
    sample_rate: int,
    *,
    frame_period_ms: float,
    f0_floor_hz: float,
    f0_ceil_hz: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    audio64 = audio.astype(np.float64)
    f0, t = pyworld.harvest(
        audio64,
        sample_rate,
        frame_period=frame_period_ms,
        f0_floor=f0_floor_hz,
        f0_ceil=f0_ceil_hz,
    )
    f0 = pyworld.stonemask(audio64, f0, t, sample_rate)
    sp = pyworld.cheaptrick(audio64, f0, t, sample_rate)
    ap = pyworld.d4c(audio64, f0, t, sample_rate)
    return f0, sp, ap


def warp_spectral_envelope(
    sp: np.ndarray,
    *,
    sample_rate: int,
    warp_ratio: float,
    blend: float,
    max_gain_db: float,
    sp_floor_db: float,
) -> np.ndarray:
    if sp.size == 0:
        return sp
    fft_size = (sp.shape[1] - 1) * 2
    freqs_hz = np.linspace(0.0, sample_rate / 2.0, sp.shape[1], dtype=np.float64)
    source_freqs = np.clip(freqs_hz / max(warp_ratio, 1e-6), 0.0, sample_rate / 2.0)
    floor_linear = math.pow(10.0, sp_floor_db / 20.0)
    warped = np.empty_like(sp)
    for frame_idx in range(sp.shape[0]):
        original = np.maximum(sp[frame_idx], floor_linear)
        warped_frame = np.interp(source_freqs, freqs_hz, original, left=original[0], right=original[-1])
        delta_db = 20.0 * np.log10(np.maximum(warped_frame, floor_linear) / np.maximum(original, floor_linear))
        delta_db = np.clip(delta_db, -abs(max_gain_db), abs(max_gain_db))
        gain = np.power(10.0, (delta_db * blend) / 20.0)
        warped[frame_idx] = original * gain
    return warped


def apply_world_vocal_tract_morph(
    audio: np.ndarray,
    *,
    sample_rate: int,
    peak_limit: float,
    warp_ratio: float,
    blend: float,
    max_gain_db: float,
    sp_floor_db: float,
    f0_floor_hz: float,
    f0_ceil_hz: float,
    frame_period_ms: float,
) -> np.ndarray:
    f0, sp, ap = analyze_world(
        audio,
        sample_rate,
        frame_period_ms=frame_period_ms,
        f0_floor_hz=f0_floor_hz,
        f0_ceil_hz=f0_ceil_hz,
    )
    warped_sp = warp_spectral_envelope(
        sp,
        sample_rate=sample_rate,
        warp_ratio=warp_ratio,
        blend=blend,
        max_gain_db=max_gain_db,
        sp_floor_db=sp_floor_db,
    )
    out = pyworld.synthesize(f0, warped_sp, ap, sample_rate, frame_period_ms).astype(np.float32)
    out = out[: len(audio)]
    if len(out) < len(audio):
        out = np.pad(out, (0, len(audio) - len(out)))
    peak = float(np.max(np.abs(out))) if out.size else 0.0
    if peak > peak_limit and peak > 0:
        out = out * (peak_limit / peak)
    return out.astype(np.float32)


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
        "method_family",
        "method_params",
        "rule_notes",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_readme(path: Path, rows: list[dict[str, str]]) -> None:
    lines = [
        "# Stage0 Speech Vocal Tract Listening Pack v1",
        "",
        "- purpose: `WORLD source-filter vocal-tract morph after lightweight null result`",
        f"- rows: `{len(rows)}`",
        "",
        "## Rebuild",
        "",
        "```powershell",
        ".\\python.exe .\\scripts\\build_stage0_speech_vocal_tract_listening_pack.py",
        ".\\python.exe .\\scripts\\build_stage0_rule_review_queue.py `",
        "  --rule-config experiments/stage0_baseline/v1_full/speech_vocal_tract_morph_candidate_v1.json `",
        "  --summary-csv tmp/stage0_speech_vocal_tract_listening_pack/v1/listening_pack_summary.csv `",
        "  --output-csv tmp/stage0_speech_vocal_tract_listening_pack/v1/listening_review_queue.csv `",
        "  --summary-md tmp/stage0_speech_vocal_tract_listening_pack/v1/listening_review_quant_summary.md",
        "```",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    rule_config = load_json(resolve_path(args.rule_config))
    rule_lookup = build_rule_lookup(rule_config)
    selected_rows = select_rows(load_source_rows(resolve_path(args.input_csv)), samples_per_cell=args.samples_per_cell)
    output_dir = resolve_path(args.output_dir)
    originals_dir = output_dir / "original"
    processed_dir = output_dir / "processed"
    summary_rows: list[dict[str, str]] = []

    for row in selected_rows:
        target_direction = TARGET_DIRECTION_BY_SOURCE_GENDER[row["gender"]]
        rule = rule_lookup[(row["dataset_name"], target_direction)]
        params = rule["method_params"]
        input_audio = resolve_path(row["path_raw"])
        dataset_slug = "libritts_r" if row["dataset_name"] == "LibriTTS-R" else "vctk"
        stem = f"{dataset_slug}__{row['gender']}__{target_direction}__vtmorph__{row['utt_id']}"
        original_copy = originals_dir / f"{stem}.{args.audio_format}"
        processed_audio = processed_dir / f"{stem}.{args.audio_format}"

        audio, sample_rate = load_audio(input_audio)
        audio = audio.astype(np.float32)
        save_audio(original_copy, audio, sample_rate)
        out = apply_world_vocal_tract_morph(
            audio,
            sample_rate=sample_rate,
            peak_limit=args.peak_limit,
            warp_ratio=float(params["warp_ratio"]),
            blend=float(params["blend"]),
            max_gain_db=float(params["max_gain_db"]),
            sp_floor_db=float(params["sp_floor_db"]),
            f0_floor_hz=float(params["f0_floor_hz"]),
            f0_ceil_hz=float(params["f0_ceil_hz"]),
            frame_period_ms=float(params["frame_period_ms"]),
        )
        save_audio(processed_audio, out, sample_rate)

        summary_rows.append(
            {
                "rule_id": rule["rule_id"],
                "utt_id": row["utt_id"],
                "source_gender": row["gender"],
                "target_direction": target_direction,
                "group_value": row["dataset_name"],
                "f0_condition": rule["match"]["f0_condition"],
                "f0_median_hz": row["f0_median_hz"],
                "input_audio": str(input_audio),
                "original_copy": str(original_copy),
                "processed_audio": str(processed_audio),
                "confidence": rule["confidence"],
                "strength_label": rule["strength"]["label"],
                "alpha_default": f"{rule['strength']['alpha_default']:.3f}",
                "alpha_max": f"{rule['strength']['alpha_max']:.3f}",
                "dataset_name": row["dataset_name"],
                "eval_bucket": row["eval_bucket"],
                "duration_sec": row["duration_sec"],
                "selection_rank": row["selection_rank"],
                "selection_score": row["selection_score"],
                "method_family": rule["method_family"],
                "method_params": json.dumps(rule["method_params"], ensure_ascii=False, sort_keys=True),
                "rule_notes": rule.get("notes", ""),
            }
        )

    summary_path = output_dir / "listening_pack_summary.csv"
    write_summary(summary_path, summary_rows)
    write_readme(output_dir / "README.md", summary_rows)
    print(f"Wrote {summary_path}")
    print(f"Selected rows: {len(summary_rows)}")
    print(f"Output dir: {output_dir}")


if __name__ == "__main__":
    main()
