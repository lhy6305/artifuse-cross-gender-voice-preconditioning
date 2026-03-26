from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

from select_stage0_candidate_rules import load_config as load_rule_config
from select_stage0_candidate_rules import matches_range, parse_float, select_rules


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RULE_CONFIG = ROOT / "experiments" / "stage0_baseline" / "v1_full" / "rule_candidate_v1.json"
DEFAULT_PROFILE_CONFIG = ROOT / "experiments" / "stage0_baseline" / "v1_full" / "rule_candidate_band_gain_profiles_v1.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rule-config", default=str(DEFAULT_RULE_CONFIG))
    parser.add_argument("--profile-config", default=str(DEFAULT_PROFILE_CONFIG))
    parser.add_argument("--input-audio")
    parser.add_argument("--output-audio")
    parser.add_argument("--input-csv")
    parser.add_argument("--output-dir")
    parser.add_argument("--summary-csv")
    parser.add_argument("--domain")
    parser.add_argument("--group-value")
    parser.add_argument("--target-direction", choices=["feminine", "masculine"])
    parser.add_argument("--f0-median-hz", type=float)
    parser.add_argument("--path-field", default="path_raw")
    parser.add_argument("--domain-field", default="domain")
    parser.add_argument("--group-field", default="coarse_style")
    parser.add_argument("--f0-field", default="f0_median_hz")
    parser.add_argument("--utt-id-field", default="utt_id")
    parser.add_argument("--n-fft", type=int, default=2048)
    parser.add_argument("--hop-length", type=int, default=512)
    parser.add_argument("--peak-limit", type=float, default=0.98)
    parser.add_argument("--audio-format", choices=["wav", "flac"], default="wav")
    return parser.parse_args()


def resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return ROOT / path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_audio(path: Path) -> tuple[np.ndarray, int]:
    audio, sample_rate = sf.read(path, always_2d=False)
    audio = np.asarray(audio, dtype=np.float32)
    if audio.ndim == 2:
        audio = audio.mean(axis=1)
    if audio.size == 0:
        raise ValueError("empty audio")
    return audio, sample_rate


def save_audio(path: Path, audio: np.ndarray, sample_rate: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(path, audio, sample_rate, subtype="PCM_16")


def build_profile_lookup(profile_config: dict) -> dict[str, dict]:
    return {rule["rule_id"]: rule for rule in profile_config["rules"]}


def build_gain_curve(
    *,
    freqs_hz: np.ndarray,
    band_edges_hz: list[list[int]],
    gain_db: list[float],
) -> np.ndarray:
    curve_db = np.zeros_like(freqs_hz, dtype=np.float32)
    for (low_hz, high_hz), gain in zip(band_edges_hz, gain_db):
        if high_hz <= low_hz:
            continue
        mask = (freqs_hz >= low_hz) & (freqs_hz < high_hz)
        curve_db[mask] = gain
    curve_db = np.convolve(curve_db, np.array([0.2, 0.6, 0.2], dtype=np.float32), mode="same")
    return np.power(10.0, curve_db / 20.0, dtype=np.float32)


def apply_band_gain(
    *,
    audio: np.ndarray,
    sample_rate: int,
    profile_rule: dict,
    n_fft: int,
    hop_length: int,
    peak_limit: float,
) -> np.ndarray:
    stft = librosa.stft(audio, n_fft=n_fft, hop_length=hop_length)
    magnitude, phase = np.abs(stft), np.angle(stft)
    freqs_hz = librosa.fft_frequencies(sr=sample_rate, n_fft=n_fft)
    profile = profile_rule["prototype_profile"]
    gain_curve = build_gain_curve(
        freqs_hz=freqs_hz,
        band_edges_hz=profile["band_edges_hz"],
        gain_db=profile["gain_db_default"],
    )
    adjusted = magnitude * gain_curve[:, None]
    out = librosa.istft(adjusted * np.exp(1j * phase), hop_length=hop_length, length=len(audio))
    peak = float(np.max(np.abs(out)))
    if peak > peak_limit and peak > 0:
        out = out * (peak_limit / peak)
    return out.astype(np.float32)


def resolve_profile_rule(
    *,
    rule_config: dict,
    profile_lookup: dict[str, dict],
    domain: str,
    group_value: str,
    target_direction: str,
    f0_median_hz: float | None,
) -> tuple[dict | None, dict | None]:
    matched_rules = select_rules(
        rule_config,
        domain=domain,
        group_value=group_value,
        target_direction=target_direction,
        f0_median_hz=f0_median_hz,
    )
    if not matched_rules:
        return None, None
    selected = matched_rules[0]
    return selected, profile_lookup.get(selected["rule_id"])


def process_one(
    *,
    rule_config: dict,
    profile_lookup: dict[str, dict],
    input_audio: Path,
    output_audio: Path,
    domain: str,
    group_value: str,
    target_direction: str,
    f0_median_hz: float | None,
    n_fft: int,
    hop_length: int,
    peak_limit: float,
) -> dict[str, str]:
    selected_rule, profile_rule = resolve_profile_rule(
        rule_config=rule_config,
        profile_lookup=profile_lookup,
        domain=domain,
        group_value=group_value,
        target_direction=target_direction,
        f0_median_hz=f0_median_hz,
    )
    if selected_rule is None or profile_rule is None:
        return {
            "status": "no_rule",
            "rule_id": "",
            "input_audio": str(input_audio),
            "output_audio": "",
            "domain": domain,
            "group_value": group_value,
            "target_direction": target_direction,
            "f0_median_hz": "" if f0_median_hz is None else f"{f0_median_hz:.6f}",
        }

    audio, sample_rate = load_audio(input_audio)
    out = apply_band_gain(
        audio=audio,
        sample_rate=sample_rate,
        profile_rule=profile_rule,
        n_fft=n_fft,
        hop_length=hop_length,
        peak_limit=peak_limit,
    )
    save_audio(output_audio, out, sample_rate)
    return {
        "status": "ok",
        "rule_id": selected_rule["rule_id"],
        "input_audio": str(input_audio),
        "output_audio": str(output_audio),
        "domain": domain,
        "group_value": group_value,
        "target_direction": target_direction,
        "f0_median_hz": "" if f0_median_hz is None else f"{f0_median_hz:.6f}",
    }


def write_summary(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "status",
        "rule_id",
        "input_audio",
        "output_audio",
        "domain",
        "group_value",
        "target_direction",
        "f0_median_hz",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def batch_process(args: argparse.Namespace, rule_config: dict, profile_lookup: dict[str, dict]) -> None:
    input_csv = resolve_path(args.input_csv)
    output_dir = resolve_path(args.output_dir)
    summary_path = resolve_path(args.summary_csv) if args.summary_csv else output_dir / "summary.csv"
    rows_out: list[dict[str, str]] = []

    with input_csv.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            input_audio = resolve_path(row[args.path_field])
            utt_id = row.get(args.utt_id_field, input_audio.stem)
            output_audio = output_dir / f"{utt_id}.{args.audio_format}"
            rows_out.append(
                process_one(
                    rule_config=rule_config,
                    profile_lookup=profile_lookup,
                    input_audio=input_audio,
                    output_audio=output_audio,
                    domain=row[args.domain_field],
                    group_value=row.get(args.group_field, ""),
                    target_direction=args.target_direction,
                    f0_median_hz=parse_float(row.get(args.f0_field)),
                    n_fft=args.n_fft,
                    hop_length=args.hop_length,
                    peak_limit=args.peak_limit,
                )
            )

    write_summary(summary_path, rows_out)
    ok_count = sum(1 for row in rows_out if row["status"] == "ok")
    print(f"Wrote {summary_path}")
    print(f"Rows: {len(rows_out)}")
    print(f"Processed: {ok_count}")
    print(f"No rule: {len(rows_out) - ok_count}")


def main() -> None:
    args = parse_args()
    rule_config = load_rule_config(resolve_path(args.rule_config))
    profile_lookup = build_profile_lookup(load_json(resolve_path(args.profile_config)))

    if args.input_csv:
        if not args.output_dir:
            raise ValueError("--output-dir is required in batch mode.")
        if not args.target_direction:
            raise ValueError("--target-direction is required in batch mode.")
        batch_process(args, rule_config, profile_lookup)
        return

    if not all([args.input_audio, args.output_audio, args.domain, args.group_value, args.target_direction]):
        raise ValueError(
            "Single mode requires --input-audio, --output-audio, --domain, --group-value, and --target-direction."
        )

    result = process_one(
        rule_config=rule_config,
        profile_lookup=profile_lookup,
        input_audio=resolve_path(args.input_audio),
        output_audio=resolve_path(args.output_audio),
        domain=args.domain,
        group_value=args.group_value,
        target_direction=args.target_direction,
        f0_median_hz=args.f0_median_hz,
        n_fft=args.n_fft,
        hop_length=args.hop_length,
        peak_limit=args.peak_limit,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
