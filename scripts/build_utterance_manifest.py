from __future__ import annotations

import csv
import re
import wave
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "data" / "datasets"
OUT_DIR = DATA_ROOT / "_meta"
OUT_CSV = OUT_DIR / "utterance_manifest.csv"


def audio_info(path: Path) -> tuple[float, int]:
    suffix = path.suffix.lower()
    if suffix == ".wav":
        with wave.open(str(path), "rb") as wf:
            return wf.getnframes() / wf.getframerate(), wf.getframerate()
    if suffix == ".flac":
        with path.open("rb") as f:
            if f.read(4) != b"fLaC":
                raise ValueError(f"Not a FLAC file: {path}")
            while True:
                header = f.read(4)
                if len(header) != 4:
                    raise ValueError(f"STREAMINFO not found in {path}")
                is_last = (header[0] & 0x80) != 0
                block_type = header[0] & 0x7F
                block_length = int.from_bytes(header[1:4], "big")
                block_data = f.read(block_length)
                if block_type == 0:
                    sample_rate = (
                        (block_data[10] << 12)
                        | (block_data[11] << 4)
                        | ((block_data[12] & 0xF0) >> 4)
                    )
                    total_samples = (
                        ((block_data[13] & 0x0F) << 32)
                        | (block_data[14] << 24)
                        | (block_data[15] << 16)
                        | (block_data[16] << 8)
                        | block_data[17]
                    )
                    return total_samples / sample_rate, sample_rate
                if is_last:
                    raise ValueError(f"STREAMINFO not found before last block in {path}")
    raise ValueError(f"Unsupported audio format: {path}")


def vctk_gender_map() -> dict[str, str]:
    info_path = DATA_ROOT / "speech" / "vctk" / "raw" / "VCTK-Corpus-0.92" / "speaker-info.txt"
    genders: dict[str, str] = {}
    for line in info_path.read_text(encoding="utf-8").splitlines()[1:]:
        line = line.strip()
        if not line:
            continue
        parts = re.split(r"\s{2,}", line)
        if len(parts) >= 3:
            genders[parts[0]] = "female" if parts[2] == "F" else "male"
    return genders


def libritts_gender_map() -> dict[str, str]:
    info_path = DATA_ROOT / "speech" / "libritts_r" / "raw" / "LibriTTS_R" / "speakers.tsv"
    genders: dict[str, str] = {}
    with info_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            genders[row["READER"]] = "female" if row["GENDER"] == "F" else "male"
    return genders


def add_vctk_rows(rows: list[dict[str, str]]) -> None:
    root = DATA_ROOT / "speech" / "vctk" / "raw" / "VCTK-Corpus-0.92" / "wav48_silence_trimmed"
    gender_map = vctk_gender_map()
    for path in sorted(root.rglob("*_mic1.flac")):
        duration_sec, sample_rate = audio_info(path)
        speaker_id = path.parent.name
        utt_id = path.stem
        rows.append(
            {
                "utt_id": utt_id,
                "dataset_name": "VCTK Corpus 0.92",
                "split_name": "full local extraction",
                "speaker_id": speaker_id,
                "gender": gender_map.get(speaker_id, "unknown"),
                "domain": "speech",
                "language": "English",
                "path_raw": str(path.relative_to(ROOT)).replace("\\", "/"),
                "path_proc": "",
                "duration_sec": f"{duration_sec:.6f}",
                "sample_rate": str(sample_rate),
                "quality_flag": "ok",
                "notes": "canonical mic1 flac",
            }
        )


def add_libritts_rows(rows: list[dict[str, str]]) -> None:
    root = DATA_ROOT / "speech" / "libritts_r" / "raw" / "LibriTTS_R"
    gender_map = libritts_gender_map()
    for split_name in ("dev-clean", "test-clean"):
        split_root = root / split_name
        for path in sorted(split_root.rglob("*.wav")):
            duration_sec, sample_rate = audio_info(path)
            speaker_id = path.parts[-3]
            utt_id = path.stem
            rows.append(
                {
                    "utt_id": utt_id,
                    "dataset_name": "LibriTTS-R",
                    "split_name": split_name,
                    "speaker_id": speaker_id,
                    "gender": gender_map.get(speaker_id, "unknown"),
                    "domain": "speech",
                    "language": "English",
                    "path_raw": str(path.relative_to(ROOT)).replace("\\", "/"),
                    "path_proc": "",
                    "duration_sec": f"{duration_sec:.6f}",
                    "sample_rate": str(sample_rate),
                    "quality_flag": "ok",
                    "notes": "",
                }
            )


def add_vocalset_rows(rows: list[dict[str, str]]) -> None:
    root = DATA_ROOT / "singing" / "vocalset" / "raw" / "VocalSet1-2" / "data_by_singer"
    for path in sorted(root.rglob("*.wav")):
        duration_sec, sample_rate = audio_info(path)
        speaker_id = path.parts[-4]
        gender = "female" if speaker_id.startswith("female") else "male"
        utt_id = path.stem
        rows.append(
            {
                "utt_id": utt_id,
                "dataset_name": "VocalSet 1.2",
                "split_name": "full local extraction",
                "speaker_id": speaker_id,
                "gender": gender,
                "domain": "singing",
                "language": "mixed / vocalise + excerpt",
                "path_raw": str(path.relative_to(ROOT)).replace("\\", "/"),
                "path_proc": "",
                "duration_sec": f"{duration_sec:.6f}",
                "sample_rate": str(sample_rate),
                "quality_flag": "ok",
                "notes": "canonical tree data_by_singer",
            }
        )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    add_vctk_rows(rows)
    add_libritts_rows(rows)
    add_vocalset_rows(rows)

    fieldnames = [
        "utt_id",
        "dataset_name",
        "split_name",
        "speaker_id",
        "gender",
        "domain",
        "language",
        "path_raw",
        "path_proc",
        "duration_sec",
        "sample_rate",
        "quality_flag",
        "notes",
    ]

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {OUT_CSV}")
    print(f"Rows: {len(rows)}")


if __name__ == "__main__":
    main()
