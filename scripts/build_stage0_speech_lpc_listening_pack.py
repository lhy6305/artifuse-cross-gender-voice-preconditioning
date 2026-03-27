from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import librosa
import numpy as np
import scipy.signal

from apply_stage0_rule_preconditioner import load_audio, resolve_path, save_audio
from build_stage0_speech_listening_pack import TARGET_DIRECTION_BY_SOURCE_GENDER, load_source_rows, select_rows


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RULE_CONFIG = ROOT / "experiments" / "stage0_baseline" / "v1_full" / "speech_lpc_resonance_candidate_v1.json"
DEFAULT_INPUT_CSV = ROOT / "experiments" / "fixed_eval" / "v1_2" / "fixed_eval_review_final_v1_2.csv"
DEFAULT_OUTPUT_DIR = ROOT / "artifacts" / "listening_review" / "stage0_speech_lpc_listening_pack" / "v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rule-config", default=str(DEFAULT_RULE_CONFIG))
    parser.add_argument("--input-csv", default=str(DEFAULT_INPUT_CSV))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--samples-per-cell", type=int, default=2)
    parser.add_argument("--audio-format", choices=["wav", "flac"], default="wav")
    parser.add_argument("--peak-limit", type=float, default=0.98)
    parser.add_argument("--world-sr", type=int, default=16000)
    parser.add_argument("--frame-period-ms", type=float, default=10.0)
    return parser.parse_args()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_rule_lookup(rule_config: dict) -> dict[tuple[str, str], dict]:
    return {
        (rule["match"]["group_value"], rule["target_direction"]): rule
        for rule in rule_config["rules"]
        if rule.get("enabled", False)
    }


def analyze_f0(audio: np.ndarray, sample_rate: int, world_sr: int, frame_period_ms: float) -> tuple[np.ndarray, np.ndarray]:
    if sample_rate != world_sr:
        audio_world = librosa.resample(audio.astype(np.float32), orig_sr=sample_rate, target_sr=world_sr).astype(np.float64)
    else:
        audio_world = audio.astype(np.float64)
    import pyworld

    f0, time_axis = pyworld.harvest(audio_world, world_sr, frame_period=frame_period_ms, f0_floor=71.0, f0_ceil=800.0)
    f0 = pyworld.stonemask(audio_world, f0, time_axis, world_sr)
    return f0, time_axis


def frame_centers_sec(frame_count: int, frame_length: int, hop_length: int, sample_rate: int) -> np.ndarray:
    return (np.arange(frame_count, dtype=np.float64) * hop_length + frame_length / 2.0) / sample_rate


def interpolate_voiced_mask(frame_times_sec: np.ndarray, world_times_sec: np.ndarray, f0: np.ndarray) -> np.ndarray:
    if frame_times_sec.size == 0 or world_times_sec.size == 0 or f0.size == 0:
        return np.zeros(frame_times_sec.shape[0], dtype=np.float32)
    voiced = (f0 > 0.0).astype(np.float32)
    interpolated = np.interp(frame_times_sec, world_times_sec, voiced, left=voiced[0], right=voiced[-1])
    if interpolated.size > 2:
        interpolated = np.convolve(interpolated, np.array([0.2, 0.6, 0.2], dtype=np.float32), mode="same")
    return np.clip(interpolated.astype(np.float32), 0.0, 1.0)


def safe_rms(audio: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(audio.astype(np.float64))))) if audio.size else 0.0


def stable_lpc(frame: np.ndarray, order: int) -> np.ndarray | None:
    try:
        coeffs = librosa.lpc(frame.astype(np.float64), order=order)
    except Exception:
        return None
    coeffs = np.asarray(coeffs, dtype=np.float64)
    if not np.all(np.isfinite(coeffs)):
        return None
    roots = np.roots(coeffs)
    if roots.size == 0:
        return None
    clipped_roots = []
    for root in roots:
        radius = abs(root)
        angle = np.angle(root)
        if radius >= 0.995:
            radius = 0.995
        clipped_roots.append(radius * np.exp(1j * angle))
    stabilized = np.poly(np.array(clipped_roots, dtype=np.complex128)).real.astype(np.float64)
    if abs(stabilized[0]) <= 1e-8:
        return None
    stabilized = stabilized / stabilized[0]
    return stabilized


def select_positive_roots(roots: np.ndarray) -> list[tuple[int, float, float]]:
    selected: list[tuple[int, float, float]] = []
    for idx, root in enumerate(roots):
        if np.imag(root) <= 1e-6:
            continue
        selected.append((idx, abs(root), float(np.angle(root))))
    selected.sort(key=lambda item: item[2])
    return selected


def find_conjugate_index(roots: np.ndarray, target_idx: int) -> int | None:
    target = np.conjugate(roots[target_idx])
    best_idx = None
    best_dist = float("inf")
    for idx, root in enumerate(roots):
        if idx == target_idx:
            continue
        dist = abs(root - target)
        if dist < best_dist:
            best_dist = dist
            best_idx = idx
    return best_idx if best_dist < 1e-3 else None


def edit_lpc_roots(
    coeffs: np.ndarray,
    *,
    sample_rate: int,
    search_ranges_hz: list[list[float]],
    shift_ratios: list[float],
) -> np.ndarray | None:
    roots = np.roots(coeffs)
    if roots.size == 0:
        return None
    edited = roots.astype(np.complex128).copy()
    positive_roots = select_positive_roots(roots)
    nyquist_hz = sample_rate / 2.0

    for search_range_hz, shift_ratio in zip(search_ranges_hz, shift_ratios):
        low_hz, high_hz = float(search_range_hz[0]), float(search_range_hz[1])
        candidate = None
        for idx, radius, angle in positive_roots:
            freq_hz = angle * sample_rate / (2.0 * math.pi)
            if low_hz <= freq_hz <= high_hz:
                candidate = (idx, radius, angle, freq_hz)
                break
        if candidate is None:
            continue
        idx, radius, angle, freq_hz = candidate
        target_hz = min(max(freq_hz * float(shift_ratio), low_hz), min(high_hz * 1.35, nyquist_hz * 0.94))
        target_angle = target_hz * 2.0 * math.pi / sample_rate
        edited[idx] = radius * np.exp(1j * target_angle)
        conj_idx = find_conjugate_index(roots, idx)
        if conj_idx is not None:
            edited[conj_idx] = np.conjugate(edited[idx])

    new_coeffs = np.poly(edited).real.astype(np.float64)
    if abs(new_coeffs[0]) <= 1e-8:
        return None
    new_coeffs = new_coeffs / new_coeffs[0]
    new_roots = np.roots(new_coeffs)
    if np.any(np.abs(new_roots) >= 0.999):
        clipped = []
        for root in new_roots:
            radius = min(abs(root), 0.995)
            clipped.append(radius * np.exp(1j * np.angle(root)))
        new_coeffs = np.poly(np.array(clipped, dtype=np.complex128)).real.astype(np.float64)
        new_coeffs = new_coeffs / new_coeffs[0]
    return new_coeffs


def overlap_add(frames: list[np.ndarray], frame_length: int, hop_length: int, output_length: int) -> np.ndarray:
    if not frames:
        return np.zeros(output_length, dtype=np.float32)
    total_length = max(output_length, (len(frames) - 1) * hop_length + frame_length)
    output = np.zeros(total_length, dtype=np.float64)
    weight = np.zeros(total_length, dtype=np.float64)
    window = np.sqrt(np.hanning(frame_length).astype(np.float64) + 1e-8)
    for frame_idx, frame in enumerate(frames):
        start = frame_idx * hop_length
        output[start : start + frame_length] += frame.astype(np.float64) * window
        weight[start : start + frame_length] += np.square(window)
    output = output / np.maximum(weight, 1e-8)
    return output[:output_length].astype(np.float32)


def apply_lpc_resonance_shift(
    audio: np.ndarray,
    *,
    sample_rate: int,
    peak_limit: float,
    world_sr: int,
    frame_period_ms: float,
    frame_length: int,
    hop_length: int,
    lpc_order: int,
    search_ranges_hz: list[list[float]],
    shift_ratios: list[float],
    blend: float,
) -> np.ndarray:
    if audio.size < frame_length:
        padded = np.pad(audio.astype(np.float32), (0, frame_length - int(audio.size)))
    else:
        padded = audio.astype(np.float32)
    frames = librosa.util.frame(padded, frame_length=frame_length, hop_length=hop_length).T
    f0, world_times_sec = analyze_f0(audio, sample_rate, world_sr, frame_period_ms)
    frame_times = frame_centers_sec(frames.shape[0], frame_length, hop_length, sample_rate)
    voiced_mask = interpolate_voiced_mask(frame_times, world_times_sec, f0)

    analysis_window = np.hanning(frame_length).astype(np.float32)
    out_frames: list[np.ndarray] = []
    for frame, voiced_value in zip(frames, voiced_mask, strict=False):
        if voiced_value < 0.5:
            out_frames.append(frame.astype(np.float32))
            continue
        frame_for_analysis = frame.astype(np.float32) * analysis_window
        coeffs = stable_lpc(frame_for_analysis, lpc_order)
        if coeffs is None:
            out_frames.append(frame.astype(np.float32))
            continue
        edited_coeffs = edit_lpc_roots(
            coeffs,
            sample_rate=sample_rate,
            search_ranges_hz=search_ranges_hz,
            shift_ratios=shift_ratios,
        )
        if edited_coeffs is None:
            out_frames.append(frame.astype(np.float32))
            continue

        residual = scipy.signal.lfilter(coeffs, [1.0], frame.astype(np.float64))
        synthesized = scipy.signal.lfilter([1.0], edited_coeffs, residual).astype(np.float32)
        synth_rms = safe_rms(synthesized)
        frame_rms = safe_rms(frame)
        if synth_rms > 1e-8 and frame_rms > 1e-8:
            synthesized = synthesized * (frame_rms / synth_rms)
        blended = (1.0 - blend) * frame.astype(np.float32) + blend * synthesized
        out_frames.append(blended.astype(np.float32))

    out = overlap_add(out_frames, frame_length, hop_length, len(audio))
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
        f"# Stage0 Speech LPC Listening Pack {pack_version}",
        "",
        "- purpose: `lpc residual-preserving pole edit probe after representation-layer pivot`",
        f"- rows: `{len(rows)}`",
        "",
        "## Rebuild",
        "",
        "```powershell",
        ".\\python.exe .\\scripts\\build_stage0_speech_lpc_listening_pack.py",
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
        stem = f"{dataset_slug}__{row['gender']}__{target_direction}__lpc__{row['utt_id']}"
        original_copy = originals_dir / f"{stem}.{args.audio_format}"
        processed_audio = processed_dir / f"{stem}.{args.audio_format}"

        audio, sample_rate = load_audio(input_audio)
        save_audio(original_copy, audio, sample_rate)
        out = apply_lpc_resonance_shift(
            audio,
            sample_rate=sample_rate,
            peak_limit=args.peak_limit,
            world_sr=args.world_sr,
            frame_period_ms=args.frame_period_ms,
            frame_length=int(params["frame_length"]),
            hop_length=int(params["hop_length"]),
            lpc_order=int(params["lpc_order"]),
            search_ranges_hz=params["search_ranges_hz"],
            shift_ratios=[float(value) for value in params["shift_ratios"]],
            blend=float(params["blend"]),
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
