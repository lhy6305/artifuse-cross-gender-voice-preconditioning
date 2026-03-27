from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import librosa
import numpy as np
import scipy.fft

from apply_stage0_rule_preconditioner import load_audio, resolve_path, save_audio
from build_stage0_speech_listening_pack import TARGET_DIRECTION_BY_SOURCE_GENDER, load_source_rows, select_rows


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RULE_CONFIG = ROOT / "experiments" / "stage0_baseline" / "v1_full" / "speech_conditional_envelope_transport_candidate_v1.json"
DEFAULT_INPUT_CSV = ROOT / "experiments" / "fixed_eval" / "v1_2" / "fixed_eval_review_final_v1_2.csv"
DEFAULT_REFERENCE_CSV = ROOT / "data" / "datasets" / "_meta" / "utterance_manifest_clean_speech_v1.csv"
DEFAULT_OUTPUT_DIR = ROOT / "artifacts" / "listening_review" / "stage0_speech_conditional_envelope_transport_listening_pack" / "v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rule-config", default=str(DEFAULT_RULE_CONFIG))
    parser.add_argument("--input-csv", default=str(DEFAULT_INPUT_CSV))
    parser.add_argument("--reference-csv", default=str(DEFAULT_REFERENCE_CSV))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--samples-per-cell", type=int, default=2)
    parser.add_argument("--reference-samples-per-cell", type=int, default=24)
    parser.add_argument("--audio-format", choices=["wav", "flac"], default="wav")
    parser.add_argument("--n-fft", type=int, default=2048)
    parser.add_argument("--hop-length", type=int, default=256)
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


def safe_rms(audio: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(audio.astype(np.float64))))) if audio.size else 0.0


def analyze_f0(audio: np.ndarray, sample_rate: int, world_sr: int, frame_period_ms: float) -> tuple[np.ndarray, np.ndarray]:
    if sample_rate != world_sr:
        audio_world = librosa.resample(audio.astype(np.float32), orig_sr=sample_rate, target_sr=world_sr).astype(np.float64)
    else:
        audio_world = audio.astype(np.float64)
    import pyworld

    f0, time_axis = pyworld.harvest(audio_world, world_sr, frame_period=frame_period_ms, f0_floor=71.0, f0_ceil=800.0)
    f0 = pyworld.stonemask(audio_world, f0, time_axis, world_sr)
    return f0, time_axis


def stft_frame_centers_sec(frame_count: int, n_fft: int, hop_length: int, sample_rate: int) -> np.ndarray:
    return (np.arange(frame_count, dtype=np.float64) * hop_length + n_fft / 2.0) / sample_rate


def interpolate_track(frame_times_sec: np.ndarray, world_times_sec: np.ndarray, values: np.ndarray) -> np.ndarray:
    if frame_times_sec.size == 0 or world_times_sec.size == 0 or values.size == 0:
        return np.zeros(frame_times_sec.shape[0], dtype=np.float32)
    return np.interp(frame_times_sec, world_times_sec, values, left=values[0], right=values[-1]).astype(np.float32)


def interpolate_voiced_mask(frame_times_sec: np.ndarray, world_times_sec: np.ndarray, f0: np.ndarray) -> np.ndarray:
    if frame_times_sec.size == 0 or world_times_sec.size == 0 or f0.size == 0:
        return np.zeros(frame_times_sec.shape[0], dtype=np.float32)
    voiced = (f0 > 0.0).astype(np.float32)
    interpolated = np.interp(frame_times_sec, world_times_sec, voiced, left=voiced[0], right=voiced[-1])
    if interpolated.size > 2:
        interpolated = np.convolve(interpolated, np.array([0.2, 0.6, 0.2], dtype=np.float32), mode="same")
    return np.clip(interpolated.astype(np.float32), 0.0, 1.0)


def read_reference_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    output: list[dict[str, str]] = []
    for row in rows:
        if row.get("domain") != "speech":
            continue
        if row.get("gender") not in {"female", "male"}:
            continue
        if not row.get("path_raw"):
            continue
        output.append(row)
    return output


def select_reference_rows(rows: list[dict[str, str]], samples_per_cell: int) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row["dataset_name"], row["gender"])].append(row)
    selected: list[dict[str, str]] = []
    for key in sorted(grouped):
        group_rows = sorted(grouped[key], key=lambda row: row.get("utt_id", ""))
        if samples_per_cell > 0:
            selected.extend(group_rows[:samples_per_cell])
        else:
            selected.extend(group_rows)
    return selected


def f0_bucket_name(f0_hz: float, edges_hz: list[float]) -> str:
    for index, edge_hz in enumerate(edges_hz):
        if f0_hz < edge_hz:
            return f"b{index}"
    return f"b{len(edges_hz)}"


def build_smoothing_kernel(size: int) -> np.ndarray:
    if size <= 1:
        return np.ones(1, dtype=np.float32)
    kernel = np.hanning(size).astype(np.float32)
    if float(np.sum(kernel)) <= 0.0:
        kernel = np.ones(size, dtype=np.float32)
    return kernel / np.sum(kernel)


def smooth_along_time(values: np.ndarray, voiced_mask: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    if values.size == 0 or kernel.size <= 1:
        return values
    output = np.empty_like(values)
    denominator = np.convolve(voiced_mask.astype(np.float32), kernel, mode="same") + 1e-6
    for coeff_idx in range(values.shape[0]):
        weighted = np.convolve(values[coeff_idx] * voiced_mask, kernel, mode="same")
        output[coeff_idx] = weighted / denominator
    return output


def extract_reference_frames(
    audio: np.ndarray,
    *,
    sample_rate: int,
    n_fft: int,
    hop_length: int,
    keep_coeffs: int,
    proxy_coeffs: int,
    world_sr: int,
    frame_period_ms: float,
    frame_stride: int,
    f0_bucket_edges_hz: list[float],
) -> list[tuple[str, np.ndarray, np.ndarray]]:
    stft = librosa.stft(audio.astype(np.float32), n_fft=n_fft, hop_length=hop_length)
    magnitude = np.abs(stft).astype(np.float32)
    if magnitude.size == 0:
        return []
    log_mag = np.log(np.maximum(magnitude, 1e-7))
    cep = scipy.fft.dct(log_mag, type=2, axis=0, norm="ortho").astype(np.float32)
    f0, world_times_sec = analyze_f0(audio, sample_rate, world_sr, frame_period_ms)
    frame_times_sec = stft_frame_centers_sec(cep.shape[1], n_fft, hop_length, sample_rate)
    voiced_mask = interpolate_voiced_mask(frame_times_sec, world_times_sec, f0)
    frame_f0 = interpolate_track(frame_times_sec, world_times_sec, f0)

    coeff_count = min(int(keep_coeffs), int(cep.shape[0] - 1))
    proxy_count = min(int(proxy_coeffs), coeff_count)
    if coeff_count <= 0 or proxy_count <= 0:
        return []

    frames: list[tuple[str, np.ndarray, np.ndarray]] = []
    stride = max(int(frame_stride), 1)
    for frame_idx in range(0, cep.shape[1], stride):
        if voiced_mask[frame_idx] < 0.5:
            continue
        current_f0 = float(frame_f0[frame_idx])
        if current_f0 <= 0.0:
            continue
        full_vector = cep[1 : 1 + coeff_count, frame_idx].astype(np.float32, copy=True)
        proxy_vector = full_vector[:proxy_count].astype(np.float32, copy=True)
        frames.append((f0_bucket_name(current_f0, f0_bucket_edges_hz), proxy_vector, full_vector))
    return frames


def build_reference_bank(
    reference_rows: list[dict[str, str]],
    *,
    n_fft: int,
    hop_length: int,
    keep_coeffs: int,
    proxy_coeffs: int,
    world_sr: int,
    frame_period_ms: float,
    frame_stride: int,
    f0_bucket_edges_hz: list[float],
) -> dict[tuple[str, str, str], dict[str, np.ndarray]]:
    bank: dict[tuple[str, str, str], dict[str, list[np.ndarray]]] = defaultdict(lambda: {"proxy": [], "full": []})
    for row in reference_rows:
        audio, sample_rate = load_audio(resolve_path(row["path_raw"]))
        frames = extract_reference_frames(
            audio,
            sample_rate=sample_rate,
            n_fft=n_fft,
            hop_length=hop_length,
            keep_coeffs=keep_coeffs,
            proxy_coeffs=proxy_coeffs,
            world_sr=world_sr,
            frame_period_ms=frame_period_ms,
            frame_stride=frame_stride,
            f0_bucket_edges_hz=f0_bucket_edges_hz,
        )
        for bucket, proxy_vector, full_vector in frames:
            for key in (
                (row["dataset_name"], row["gender"], bucket),
                (row["dataset_name"], row["gender"], "all"),
            ):
                bank[key]["proxy"].append(proxy_vector)
                bank[key]["full"].append(full_vector)

    packed: dict[tuple[str, str, str], dict[str, np.ndarray]] = {}
    for key, value in bank.items():
        packed[key] = {
            "proxy": np.stack(value["proxy"], axis=0).astype(np.float32),
            "full": np.stack(value["full"], axis=0).astype(np.float32),
        }
    return packed


def nearest_target_vector(
    current_proxy: np.ndarray,
    *,
    dataset_name: str,
    target_gender: str,
    bucket: str,
    reference_bank: dict[tuple[str, str, str], dict[str, np.ndarray]],
    nearest_k: int,
) -> np.ndarray | None:
    candidates = [
        reference_bank.get((dataset_name, target_gender, bucket)),
        reference_bank.get((dataset_name, target_gender, "all")),
    ]
    bank = next((item for item in candidates if item is not None), None)
    if bank is None:
        return None
    proxy_matrix = bank["proxy"]
    full_matrix = bank["full"]
    if proxy_matrix.size == 0 or full_matrix.size == 0:
        return None

    distances = np.sum(np.square(proxy_matrix - current_proxy[None, :]), axis=1)
    k = max(1, min(int(nearest_k), int(distances.shape[0])))
    nearest_indices = np.argpartition(distances, kth=k - 1)[:k]
    target_vectors = full_matrix[nearest_indices]
    if k == 1:
        return target_vectors[0].astype(np.float32, copy=True)

    weights = 1.0 / np.maximum(distances[nearest_indices], 1e-4)
    weights = weights / np.sum(weights)
    return np.sum(target_vectors * weights[:, None], axis=0).astype(np.float32)


def apply_conditional_envelope_transport(
    audio: np.ndarray,
    *,
    sample_rate: int,
    n_fft: int,
    hop_length: int,
    peak_limit: float,
    world_sr: int,
    frame_period_ms: float,
    dataset_name: str,
    target_gender: str,
    reference_bank: dict[tuple[str, str, str], dict[str, np.ndarray]],
    keep_coeffs: int,
    proxy_coeffs: int,
    nearest_k: int,
    transport_ratio: float,
    blend: float,
    max_envelope_gain_db: float,
    max_frame_delta_l2: float,
    time_smooth_frames: int,
    f0_bucket_edges_hz: list[float],
) -> np.ndarray:
    stft = librosa.stft(audio.astype(np.float32), n_fft=n_fft, hop_length=hop_length)
    magnitude = np.abs(stft).astype(np.float32)
    phase = np.angle(stft)
    if magnitude.size == 0:
        return audio.astype(np.float32)

    log_mag = np.log(np.maximum(magnitude, 1e-7))
    cep = scipy.fft.dct(log_mag, type=2, axis=0, norm="ortho").astype(np.float32)
    f0, world_times_sec = analyze_f0(audio, sample_rate, world_sr, frame_period_ms)
    frame_times_sec = stft_frame_centers_sec(cep.shape[1], n_fft, hop_length, sample_rate)
    voiced_mask = interpolate_voiced_mask(frame_times_sec, world_times_sec, f0)
    frame_f0 = interpolate_track(frame_times_sec, world_times_sec, f0)

    coeff_count = min(int(keep_coeffs), int(cep.shape[0] - 1))
    proxy_count = min(int(proxy_coeffs), coeff_count)
    if coeff_count <= 0 or proxy_count <= 0:
        return audio.astype(np.float32)

    frame_delta = np.zeros((coeff_count, cep.shape[1]), dtype=np.float32)
    voiced_binary = np.zeros(cep.shape[1], dtype=np.float32)
    for frame_idx in range(cep.shape[1]):
        if voiced_mask[frame_idx] < 0.5:
            continue
        current_f0 = float(frame_f0[frame_idx])
        if current_f0 <= 0.0:
            continue
        current_full = cep[1 : 1 + coeff_count, frame_idx].astype(np.float32, copy=False)
        target_full = nearest_target_vector(
            current_full[:proxy_count],
            dataset_name=dataset_name,
            target_gender=target_gender,
            bucket=f0_bucket_name(current_f0, f0_bucket_edges_hz),
            reference_bank=reference_bank,
            nearest_k=nearest_k,
        )
        if target_full is None:
            continue
        delta = (target_full[:coeff_count] - current_full) * float(transport_ratio)
        delta_norm = float(np.linalg.norm(delta))
        if delta_norm > max_frame_delta_l2 > 0.0:
            delta = delta * (max_frame_delta_l2 / delta_norm)
        frame_delta[:, frame_idx] = delta
        voiced_binary[frame_idx] = 1.0

    smoothed_delta = smooth_along_time(frame_delta, voiced_binary, build_smoothing_kernel(int(time_smooth_frames)))
    output_cep = np.array(cep, dtype=np.float32, copy=True)
    output_cep[1 : 1 + coeff_count, :] += smoothed_delta * voiced_mask[None, :]

    modified_log_mag = scipy.fft.idct(output_cep, type=2, axis=0, norm="ortho").astype(np.float32)
    max_delta_ln = max_envelope_gain_db / 20.0 * math.log(10.0)
    delta_log_mag = np.clip(modified_log_mag - log_mag, -max_delta_ln, max_delta_ln)
    adjusted_mag = magnitude * np.exp(float(blend) * delta_log_mag)
    out = librosa.istft(adjusted_mag * np.exp(1j * phase), hop_length=hop_length, length=len(audio))

    in_rms = safe_rms(audio)
    out_rms = safe_rms(out)
    if in_rms > 1e-8 and out_rms > 1e-8:
        out = out * (in_rms / out_rms)

    peak = float(np.max(np.abs(out))) if out.size else 0.0
    if peak > peak_limit and peak > 0.0:
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
        f"# Stage0 Speech Conditional Envelope Transport Listening Pack {pack_version}",
        "",
        "- purpose: `content-and-f0-conditioned reference envelope transport probe`",
        f"- rows: `{len(rows)}`",
        "",
        "## Rebuild",
        "",
        "```powershell",
        ".\\python.exe .\\scripts\\build_stage0_speech_conditional_envelope_transport_listening_pack.py",
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

    enabled_rules = [rule for rule in rule_config["rules"] if rule.get("enabled", False)]
    max_keep_coeffs = max(int(rule["method_params"]["keep_coeffs"]) for rule in enabled_rules)
    max_proxy_coeffs = max(int(rule["method_params"]["proxy_coeffs"]) for rule in enabled_rules)
    max_reference_stride = max(int(rule["method_params"].get("reference_frame_stride", 1)) for rule in enabled_rules)
    f0_bucket_edges_hz = [float(value) for value in enabled_rules[0]["method_params"]["f0_bucket_edges_hz"]]

    reference_rows = select_reference_rows(
        read_reference_rows(resolve_path(args.reference_csv)),
        samples_per_cell=args.reference_samples_per_cell,
    )
    reference_bank = build_reference_bank(
        reference_rows,
        n_fft=args.n_fft,
        hop_length=args.hop_length,
        keep_coeffs=max_keep_coeffs,
        proxy_coeffs=max_proxy_coeffs,
        world_sr=args.world_sr,
        frame_period_ms=args.frame_period_ms,
        frame_stride=max_reference_stride,
        f0_bucket_edges_hz=f0_bucket_edges_hz,
    )

    output_dir = resolve_path(args.output_dir)
    originals_dir = output_dir / "original"
    processed_dir = output_dir / "processed"
    summary_rows: list[dict[str, str]] = []

    for row in selected_rows:
        target_direction = TARGET_DIRECTION_BY_SOURCE_GENDER[row["gender"]]
        target_gender = "female" if target_direction == "feminine" else "male"
        rule = rule_lookup[(row["dataset_name"], target_direction)]
        params = rule["method_params"]

        input_audio = resolve_path(row["path_raw"])
        dataset_slug = "libritts_r" if row["dataset_name"] == "LibriTTS-R" else "vctk"
        stem = f"{dataset_slug}__{row['gender']}__{target_direction}__cet__{row['utt_id']}"
        original_copy = originals_dir / f"{stem}.{args.audio_format}"
        processed_audio = processed_dir / f"{stem}.{args.audio_format}"

        audio, sample_rate = load_audio(input_audio)
        save_audio(original_copy, audio, sample_rate)
        out = apply_conditional_envelope_transport(
            audio,
            sample_rate=sample_rate,
            n_fft=args.n_fft,
            hop_length=args.hop_length,
            peak_limit=args.peak_limit,
            world_sr=args.world_sr,
            frame_period_ms=args.frame_period_ms,
            dataset_name=row["dataset_name"],
            target_gender=target_gender,
            reference_bank=reference_bank,
            keep_coeffs=int(params["keep_coeffs"]),
            proxy_coeffs=int(params["proxy_coeffs"]),
            nearest_k=int(params["nearest_k"]),
            transport_ratio=float(params["transport_ratio"]),
            blend=float(params["blend"]),
            max_envelope_gain_db=float(params["max_envelope_gain_db"]),
            max_frame_delta_l2=float(params["max_frame_delta_l2"]),
            time_smooth_frames=int(params["time_smooth_frames"]),
            f0_bucket_edges_hz=[float(value) for value in params["f0_bucket_edges_hz"]],
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
    print(f"Reference rows: {len(reference_rows)}")
    print(f"Reference banks: {len(reference_bank)}")
    print(f"Selected rows: {len(summary_rows)}")
    print(f"Output dir: {output_dir}")


if __name__ == "__main__":
    main()
