from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "tmp" / "stage1_rvc_cascade_eval" / "v1" / "rvc_cascade_manifest.csv"
DEFAULT_RVC_ROOT = ROOT / "Retrieval-based-Voice-Conversion-WebUI-7ef1986"
DEFAULT_INFER_CLI = DEFAULT_RVC_ROOT / "infer_cli.py"
DEFAULT_SUMMARY_MD = ROOT / "tmp" / "stage1_rvc_cascade_eval" / "v1" / "rvc_cascade_run_summary.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest-csv", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--rvc-root", default=str(DEFAULT_RVC_ROOT))
    parser.add_argument("--infer-cli", default=str(DEFAULT_INFER_CLI))
    parser.add_argument("--summary-md", default=str(DEFAULT_SUMMARY_MD))
    parser.add_argument("--max-rows", type=int, default=0)
    parser.add_argument("--only-pending", action="store_true", default=True)
    return parser.parse_args()


def resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return ROOT / path


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError("No rows to write.")
    fieldnames = list(rows[0].keys())
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_summary(path: Path, rows: list[dict[str, str]]) -> None:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    lines = [
        "# Stage1 RVC Cascade Run Summary",
        "",
        f"- rows: `{len(rows)}`",
    ]
    for key in sorted(counts):
        lines.append(f"- `{key}`: `{counts[key]}`")
    failed = [row for row in rows if row["status"] == "error"]
    lines.extend(["", "## Failed Rows", ""])
    if not failed:
        lines.append("- none")
    else:
        for row in failed[:10]:
            lines.append(
                f"- `{row['eval_item_id']}` | target=`{row['target_id']}` | variant=`{row['input_variant']}` | error=`{row['error_message']}`"
            )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_command(python_exe: Path, infer_cli: Path, row: dict[str, str]) -> list[str]:
    command = [
        str(python_exe),
        str(infer_cli),
        "--model_name",
        row["model_name"],
        "--input_path",
        row["input_audio"],
        "--output_path",
        row["output_audio"],
        "--f0_up_key",
        row["f0_up_key"],
        "--f0_method",
        row["f0_method"],
        "--index_rate",
        row["index_rate"],
        "--filter_radius",
        row["filter_radius"],
        "--resample_sr",
        row["resample_sr"],
        "--rms_mix_rate",
        row["rms_mix_rate"],
        "--protect",
        row["protect"],
        "--spk_id",
        row["spk_id"],
    ]
    index_path = row.get("index_path", "").strip()
    if index_path:
        command.extend(["--index_path", str(resolve_path(index_path))])
    return command


def main() -> None:
    args = parse_args()
    manifest_csv = resolve_path(args.manifest_csv)
    infer_cli = resolve_path(args.infer_cli)
    summary_md = resolve_path(args.summary_md)
    python_exe = ROOT / "python.exe"
    if not python_exe.exists():
        python_exe = Path(sys.executable)

    rows = read_rows(manifest_csv)
    processed = 0
    for row in rows:
        if args.only_pending and row["status"] == "done":
            continue
        if args.max_rows > 0 and processed >= args.max_rows:
            break
        output_audio = Path(row["output_audio"])
        if row["status"] == "done" and output_audio.exists():
            continue

        output_audio.parent.mkdir(parents=True, exist_ok=True)
        command = build_command(python_exe, infer_cli, row)
        env = dict(os.environ)
        weight_root = row.get("weight_root", "").strip()
        if weight_root:
            env["weight_root"] = str(resolve_path(weight_root))
        start = time.time()
        result = subprocess.run(
            command,
            cwd=str(resolve_path(args.rvc_root)),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        elapsed = time.time() - start
        if result.returncode == 0 and output_audio.exists():
            row["status"] = "done"
            row["error_message"] = f"ok {elapsed:.2f}s"
        else:
            row["status"] = "error"
            stderr = (result.stderr or "").strip()
            stdout = (result.stdout or "").strip()
            message = stderr or stdout or f"returncode={result.returncode}"
            row["error_message"] = message[:500]
        processed += 1
        write_rows(manifest_csv, rows)
        write_summary(summary_md, rows)
        print(f"[{processed}] {row['eval_item_id']} -> {row['status']}")

    write_rows(manifest_csv, rows)
    write_summary(summary_md, rows)
    print(f"Wrote {manifest_csv}")
    print(f"Wrote {summary_md}")


if __name__ == "__main__":
    main()
