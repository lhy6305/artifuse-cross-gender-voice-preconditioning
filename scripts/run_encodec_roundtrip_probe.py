from __future__ import annotations

import argparse
import csv
from pathlib import Path

import torch
import torchaudio
from encodec import EncodecModel


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE_QUEUE = (
    ROOT
    / "artifacts"
    / "listening_review"
    / "stage0_speech_lsf_machine_sweep_v9_fixed8"
    / "split_core_focus_v9a"
    / "listening_review_queue.csv"
)
DEFAULT_OUTPUT_DIR = (
    ROOT
    / "artifacts"
    / "diagnostics"
    / "encodec_roundtrip_probe"
    / "v1_fixed8_bw24"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template-queue", default=str(DEFAULT_TEMPLATE_QUEUE))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--repository", default="")
    parser.add_argument("--bandwidth", type=float, default=24.0)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--max-rows", type=int, default=0)
    return parser.parse_args()


def resolve_path(value: str | Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return ROOT / path


def choose_device(value: str) -> str:
    if value != "auto":
        return value
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def read_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
        return rows, list(rows[0].keys()) if rows else []


def write_rows(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_audio_mono(path: Path, sample_rate: int) -> torch.Tensor:
    audio, src_sr = torchaudio.load(path)
    if audio.shape[0] > 1:
        audio = torch.mean(audio, dim=0, keepdim=True)
    if src_sr != sample_rate:
        audio = torchaudio.functional.resample(audio, src_sr, sample_rate)
    return audio


def build_readme(*, template_queue: Path, output_dir: Path, bandwidth: float, repository: str, rows: int) -> str:
    rel_template = template_queue.relative_to(ROOT).as_posix()
    rel_output = output_dir.relative_to(ROOT).as_posix()
    repository_value = repository or "torch hub cache"
    return (
        "# Encodec Roundtrip Probe v1\n\n"
        f"- purpose: `measure source-preserving carrier ceiling before ATRR edit injection`\n"
        f"- rows: `{rows}`\n"
        f"- bandwidth_kbps: `{bandwidth:.1f}`\n"
        f"- repository: `{repository_value}`\n\n"
        "## Rebuild\n\n"
        "```powershell\n"
        ".\\python.exe .\\scripts\\run_encodec_roundtrip_probe.py `\n"
        f"  --template-queue {rel_template} `\n"
        f"  --output-dir {rel_output} `\n"
        f"  --bandwidth {bandwidth:.1f}\n"
        "```\n"
    )


def build_summary(*, bandwidth: float, repository: str, rows: int, sample_rate: int, device: str) -> str:
    repository_value = repository or "torch hub cache"
    return (
        "# Encodec Roundtrip Probe Summary v1\n\n"
        f"- rows: `{rows}`\n"
        f"- sample_rate: `{sample_rate}`\n"
        f"- bandwidth_kbps: `{bandwidth:.1f}`\n"
        f"- device: `{device}`\n"
        f"- repository: `{repository_value}`\n"
        "- note: `this probe measures source roundtrip naturalness only`\n"
        "- note: `no ATRR target edit is injected in this stage`\n"
    )


def main() -> None:
    args = parse_args()
    template_queue = resolve_path(args.template_queue)
    output_dir = resolve_path(args.output_dir)
    repository = resolve_path(args.repository) if args.repository else None
    device = choose_device(args.device)

    rows, fieldnames = read_rows(template_queue)
    if not rows:
        raise ValueError("Template queue is empty.")
    if args.max_rows > 0:
        rows = rows[: args.max_rows]

    model = EncodecModel.encodec_model_24khz(pretrained=True, repository=repository)
    model.set_target_bandwidth(float(args.bandwidth))
    model = model.to(device).eval()

    processed_dir = output_dir / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    output_rows: list[dict[str, str]] = []
    for row in rows:
        source_path = resolve_path(row["input_audio"])
        audio = load_audio_mono(source_path, int(model.sample_rate)).to(device)
        with torch.no_grad():
            encoded_frames = model.encode(audio.unsqueeze(0))
            reconstructed = model.decode(encoded_frames).detach().cpu().squeeze(0)
        output_path = processed_dir / f"{row['record_id']}__encodec_bw{int(args.bandwidth)}.wav"
        torchaudio.save(str(output_path), reconstructed, sample_rate=int(model.sample_rate))

        updated = dict(row)
        updated["processed_audio"] = str(output_path)
        output_rows.append(updated)

    queue_path = output_dir / "listening_review_queue.csv"
    readme_path = output_dir / "README.md"
    summary_path = output_dir / "ENCODEC_ROUNDTRIP_SUMMARY.md"
    write_rows(queue_path, output_rows, fieldnames)
    readme_path.write_text(
        build_readme(
            template_queue=template_queue,
            output_dir=output_dir,
            bandwidth=float(args.bandwidth),
            repository=str(repository) if repository else "",
            rows=len(output_rows),
        ),
        encoding="utf-8",
    )
    summary_path.write_text(
        build_summary(
            bandwidth=float(args.bandwidth),
            repository=str(repository) if repository else "",
            rows=len(output_rows),
            sample_rate=int(model.sample_rate),
            device=device,
        ),
        encoding="utf-8",
    )
    print(f"Wrote {queue_path}")
    print(f"Wrote {readme_path}")
    print(f"Wrote {summary_path}")
    print(f"Rows: {len(output_rows)}")


if __name__ == "__main__":
    main()
