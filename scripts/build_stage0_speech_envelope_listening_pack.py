from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import librosa
import numpy as np

from apply_stage0_rule_preconditioner import load_audio, resolve_path, save_audio
from build_stage0_speech_listening_pack import TARGET_DIRECTION_BY_SOURCE_GENDER, load_source_rows, select_rows


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RULE_CONFIG = ROOT / "experiments" / "stage0_baseline" / "v1_full" / "speech_envelope_warp_candidate_v1.json"
DEFAULT_INPUT_CSV = ROOT / "experiments" / "fixed_eval" / "v1_2" / "fixed_eval_review_final_v1_2.csv"
DEFAULT_OUTPUT_DIR = ROOT / "artifacts" / "listening_review" / "stage0_speech_envelope_listening_pack" / "v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rule-config", default=str(DEFAULT_RULE_CONFIG))
    parser.add_argument("--input-csv", default=str(DEFAULT_INPUT_CSV))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--samples-per-cell", type=int, default=2)
    parser.add_argument("--audio-format", choices=["wav", "flac"], default="wav")
    parser.add_argument("--n-fft", type=int, default=2048)
    parser.add_argument("--hop-length", type=int, default=256)
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


def smooth_along_freq(log_mag: np.ndarray, window_bins: int) -> np.ndarray:
    window = max(3, int(window_bins))
    if window % 2 == 0:
        window += 1
    kernel = np.ones(window, dtype=np.float32) / window
    return np.apply_along_axis(lambda col: np.convolve(col, kernel, mode="same"), 0, log_mag)


def build_voiced_mask(audio: np.ndarray, n_fft: int, hop_length: int, gate_db: float) -> np.ndarray:
    rms = librosa.feature.rms(y=audio.astype(np.float32), frame_length=n_fft, hop_length=hop_length, center=True)[0]
    rms_db = librosa.amplitude_to_db(np.maximum(rms, 1e-8), ref=np.max)
    mask = (rms_db >= -abs(gate_db)).astype(np.float32)
    if mask.size > 2:
        mask = np.convolve(mask, np.array([0.2, 0.6, 0.2], dtype=np.float32), mode="same")
    return np.clip(mask, 0.0, 1.0)


def warp_envelope(
    smoothed_log_mag: np.ndarray,
    *,
    warp_factor: float,
    max_envelope_gain_db: float,
) -> np.ndarray:
    freq_bins, frame_count = smoothed_log_mag.shape
    source_idx = np.arange(freq_bins, dtype=np.float32) / max(warp_factor, 1e-6)
    source_idx = np.clip(source_idx, 0.0, float(freq_bins - 1))
    warped = np.empty_like(smoothed_log_mag)
    for frame_idx in range(frame_count):
        warped[:, frame_idx] = np.interp(
            np.arange(freq_bins, dtype=np.float32),
            source_idx,
            smoothed_log_mag[:, frame_idx],
            left=float(smoothed_log_mag[0, frame_idx]),
            right=float(smoothed_log_mag[-1, frame_idx]),
        )
    max_delta_ln = max_envelope_gain_db / 20.0 * np.log(10.0)
    return np.clip(warped - smoothed_log_mag, -max_delta_ln, max_delta_ln)


def apply_voiced_envelope_warp(
    audio: np.ndarray,
    *,
    sample_rate: int,
    n_fft: int,
    hop_length: int,
    peak_limit: float,
    warp_factor: float,
    blend: float,
    envelope_smooth_bins: int,
    max_envelope_gain_db: float,
    voiced_rms_gate_db: float,
) -> np.ndarray:
    stft = librosa.stft(audio.astype(np.float32), n_fft=n_fft, hop_length=hop_length)
    magnitude = np.abs(stft).astype(np.float32)
    phase = np.angle(stft)
    log_mag = np.log(np.maximum(magnitude, 1e-7))
    smoothed_log_mag = smooth_along_freq(log_mag, envelope_smooth_bins)
    delta_log_env = warp_envelope(
        smoothed_log_mag,
        warp_factor=warp_factor,
        max_envelope_gain_db=max_envelope_gain_db,
    )
    voiced_mask = build_voiced_mask(audio, n_fft=n_fft, hop_length=hop_length, gate_db=voiced_rms_gate_db)
    voiced_mask = voiced_mask[: magnitude.shape[1]]
    blended_delta = delta_log_env * (blend * voiced_mask[None, :])
    adjusted_mag = magnitude * np.exp(blended_delta)
    out = librosa.istft(adjusted_mag * np.exp(1j * phase), hop_length=hop_length, length=len(audio))
    peak = float(np.max(np.abs(out)))
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


def write_readme(path: Path, rows: list[dict[str, str]], *, rule_config_path: Path) -> None:
    pack_dir = path.parent
    pack_version = pack_dir.name
    try:
        rule_config_rel = rule_config_path.relative_to(ROOT).as_posix()
    except ValueError:
        rule_config_rel = str(rule_config_path)
    summary_rel = (pack_dir / "listening_pack_summary.csv").relative_to(ROOT).as_posix()
    queue_rel = (pack_dir / "listening_review_queue.csv").relative_to(ROOT).as_posix()
    summary_md_rel = (pack_dir / "listening_review_quant_summary.md").relative_to(ROOT).as_posix()
    lines = [
        f"# Stage0 Speech Envelope Listening Pack {pack_version}",
        "",
        "- purpose: `voiced-envelope-warp audibility probe after static EQ null result`",
        f"- rows: `{len(rows)}`",
        "",
        "## Rebuild",
        "",
        "```powershell",
        ".\\python.exe .\\scripts\\build_stage0_speech_envelope_listening_pack.py",
        ".\\python.exe .\\scripts\\build_stage0_rule_review_queue.py `",
        f"  --rule-config {rule_config_rel} `",
        f"  --summary-csv {summary_rel} `",
        f"  --output-csv {queue_rel} `",
        f"  --summary-md {summary_md_rel}",
        "```",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    rule_config_path = resolve_path(args.rule_config)
    rule_config = load_json(rule_config_path)
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
        stem = f"{dataset_slug}__{row['gender']}__{target_direction}__envwarp__{row['utt_id']}"
        original_copy = originals_dir / f"{stem}.{args.audio_format}"
        processed_audio = processed_dir / f"{stem}.{args.audio_format}"

        audio, sample_rate = load_audio(input_audio)
        save_audio(original_copy, audio, sample_rate)
        out = apply_voiced_envelope_warp(
            audio,
            sample_rate=sample_rate,
            n_fft=args.n_fft,
            hop_length=args.hop_length,
            peak_limit=args.peak_limit,
            warp_factor=float(params["warp_factor"]),
            blend=float(params["blend"]),
            envelope_smooth_bins=int(params["envelope_smooth_bins"]),
            max_envelope_gain_db=float(params["max_envelope_gain_db"]),
            voiced_rms_gate_db=float(params["voiced_rms_gate_db"]),
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
    write_readme(output_dir / "README.md", summary_rows, rule_config_path=rule_config_path)
    print(f"Wrote {summary_path}")
    print(f"Selected rows: {len(summary_rows)}")
    print(f"Output dir: {output_dir}")


if __name__ == "__main__":
    main()
