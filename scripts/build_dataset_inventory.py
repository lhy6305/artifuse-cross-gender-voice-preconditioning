from __future__ import annotations

import csv
import re
import wave
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "data" / "datasets"
OUT_DIR = DATA_ROOT / "_meta"
OUT_CSV = OUT_DIR / "dataset_inventory.csv"


@dataclass
class Summary:
    dataset_name: str
    split_name: str
    domain: str
    language: str
    num_speakers: int
    num_male: int
    num_female: int
    total_hours: float
    avg_minutes_per_spk: float
    clean_level: str
    accompaniment_residual: str
    reverb_level: str
    sample_rate: str
    license_name: str
    num_utterances: int
    local_root: str
    notes: str


def wav_stats(paths: list[Path]) -> tuple[int, float, str]:
    total_seconds = 0.0
    sample_rates: set[int] = set()
    for path in paths:
        suffix = path.suffix.lower()
        if suffix == ".wav":
            with wave.open(str(path), "rb") as wf:
                total_seconds += wf.getnframes() / wf.getframerate()
                sample_rates.add(wf.getframerate())
        elif suffix == ".flac":
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
                        total_seconds += total_samples / sample_rate
                        sample_rates.add(sample_rate)
                        break
                    if is_last:
                        raise ValueError(f"STREAMINFO not found before last block in {path}")
        else:
            raise ValueError(f"Unsupported audio format for stats: {path}")
    if not sample_rates:
        sample_rate_text = ""
    elif len(sample_rates) == 1:
        sample_rate_text = str(next(iter(sample_rates)))
    else:
        sample_rate_text = "/".join(str(x) for x in sorted(sample_rates))
    return len(paths), total_seconds / 3600.0, sample_rate_text


def parse_vctk() -> Summary:
    dataset_root = DATA_ROOT / "speech" / "vctk" / "raw" / "VCTK-Corpus-0.92"
    speaker_info = dataset_root / "speaker-info.txt"
    wav_root = dataset_root / "wav48_silence_trimmed"

    speaker_gender: dict[str, str] = {}
    for line in speaker_info.read_text(encoding="utf-8").splitlines()[1:]:
        line = line.strip()
        if not line:
            continue
        parts = re.split(r"\s{2,}", line)
        if len(parts) < 3:
            continue
        speaker_gender[parts[0]] = parts[2]

    wavs = sorted(wav_root.rglob("*_mic1.flac"))
    local_speakers = sorted({p.parent.name for p in wavs})
    num_utterances, total_hours, sample_rate = wav_stats(wavs)
    num_female = sum(1 for spk in local_speakers if speaker_gender.get(spk) == "F")
    num_male = sum(1 for spk in local_speakers if speaker_gender.get(spk) == "M")

    return Summary(
        dataset_name="VCTK Corpus 0.92",
        split_name="full local extraction",
        domain="speech",
        language="English",
        num_speakers=len(local_speakers),
        num_male=num_male,
        num_female=num_female,
        total_hours=round(total_hours, 2),
        avg_minutes_per_spk=round((total_hours * 60.0) / len(local_speakers), 2),
        clean_level="high",
        accompaniment_residual="none",
        reverb_level="low / controlled",
        sample_rate=sample_rate,
        license_name="CC BY 4.0",
        num_utterances=num_utterances,
        local_root=str(wav_root.relative_to(ROOT)).replace("\\", "/"),
        notes=(
            "Use wav48_silence_trimmed/*_mic1.flac as canonical audio tree to avoid "
            "double-counting mic2 duplicates; speaker-info.txt provides gender metadata."
        ),
    )


def parse_libritts_r() -> Summary:
    dataset_root = DATA_ROOT / "speech" / "libritts_r" / "raw" / "LibriTTS_R"
    speakers_tsv = dataset_root / "speakers.tsv"

    speaker_gender: dict[str, str] = {}
    with speakers_tsv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            speaker_gender[row["READER"]] = row["GENDER"]

    split_roots = [dataset_root / "dev-clean", dataset_root / "test-clean"]
    local_speakers: set[str] = set()
    wavs: list[Path] = []
    for split_root in split_roots:
        for speaker_dir in split_root.iterdir():
            if speaker_dir.is_dir():
                local_speakers.add(speaker_dir.name)
        wavs.extend(split_root.rglob("*.wav"))

    num_utterances, total_hours, sample_rate = wav_stats(sorted(wavs))
    num_female = sum(1 for spk in local_speakers if speaker_gender.get(spk) == "F")
    num_male = sum(1 for spk in local_speakers if speaker_gender.get(spk) == "M")

    return Summary(
        dataset_name="LibriTTS-R",
        split_name="dev-clean + test-clean (local)",
        domain="speech",
        language="English",
        num_speakers=len(local_speakers),
        num_male=num_male,
        num_female=num_female,
        total_hours=round(total_hours, 2),
        avg_minutes_per_spk=round((total_hours * 60.0) / len(local_speakers), 2),
        clean_level="medium-high",
        accompaniment_residual="none",
        reverb_level="low / book-reading dependent",
        sample_rate=sample_rate,
        license_name="CC BY 4.0",
        num_utterances=num_utterances,
        local_root=str(dataset_root.relative_to(ROOT)).replace("\\", "/"),
        notes="Only dev-clean and test-clean are extracted locally; speakers.tsv provides gender metadata.",
    )


def parse_vocalset() -> Summary:
    dataset_root = DATA_ROOT / "singing" / "vocalset" / "raw" / "VocalSet1-2"
    singer_root = dataset_root / "data_by_singer"

    speaker_dirs = sorted(p.name for p in singer_root.iterdir() if p.is_dir())
    num_female = sum(1 for name in speaker_dirs if name.startswith("female"))
    num_male = sum(1 for name in speaker_dirs if name.startswith("male"))
    wavs = sorted(singer_root.rglob("*.wav"))
    num_utterances, total_hours, sample_rate = wav_stats(wavs)

    return Summary(
        dataset_name="VocalSet 1.2",
        split_name="full local extraction (canonical tree: data_by_singer)",
        domain="singing",
        language="mixed / vocalise + excerpt",
        num_speakers=len(speaker_dirs),
        num_male=num_male,
        num_female=num_female,
        total_hours=round(total_hours, 2),
        avg_minutes_per_spk=round((total_hours * 60.0) / len(speaker_dirs), 2),
        clean_level="high",
        accompaniment_residual="none",
        reverb_level="low / controlled",
        sample_rate=sample_rate,
        license_name="CC BY 4.0",
        num_utterances=num_utterances,
        local_root=str(singer_root.relative_to(ROOT)).replace("\\", "/"),
        notes=(
            "Count only data_by_singer to avoid triple-counting duplicated files. "
            "Package readme indicates 11 male / 9 female, which matches directory names."
        ),
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = [parse_vctk(), parse_libritts_r(), parse_vocalset()]
    fieldnames = [
        "dataset_name",
        "split_name",
        "domain",
        "language",
        "num_speakers",
        "num_male",
        "num_female",
        "total_hours",
        "avg_minutes_per_spk",
        "clean_level",
        "accompaniment_residual",
        "reverb_level",
        "sample_rate",
        "license_name",
        "num_utterances",
        "local_root",
        "notes",
    ]

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)

    print(f"Wrote {OUT_CSV}")
    for row in rows:
        print(
            f"{row.dataset_name}: speakers={row.num_speakers}, "
            f"male={row.num_male}, female={row.num_female}, "
            f"hours={row.total_hours}, utterances={row.num_utterances}, sr={row.sample_rate}"
        )


if __name__ == "__main__":
    main()
