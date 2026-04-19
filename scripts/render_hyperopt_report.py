from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stdout-path", required=True)
    parser.add_argument("--artifact-dir", required=True)
    parser.add_argument("--output-path", required=True)
    parser.add_argument("--strategy", required=True)
    parser.add_argument("--timerange", required=True)
    parser.add_argument("--loss-function", required=True)
    parser.add_argument("--epochs", type=int, required=True)
    parser.add_argument("--spaces", required=True)
    return parser.parse_args()


def latest_artifacts(artifact_dir: Path) -> list[Path]:
    if not artifact_dir.exists():
        return []
    candidates = [path for path in artifact_dir.iterdir() if path.is_file()]
    candidates.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    return candidates[:5]


def extract_json_objects(text: str) -> list[dict]:
    objects: list[dict] = []
    for line in text.splitlines():
        candidate = line.strip()
        if not candidate.startswith("{") or not candidate.endswith("}"):
            continue
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            objects.append(payload)
    return objects


def flatten_first_level(payload: dict) -> list[tuple[str, str]]:
    flattened: list[tuple[str, str]] = []
    for key, value in payload.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            flattened.append((str(key), str(value)))
    return flattened


def main() -> None:
    args = parse_args()
    stdout_path = Path(args.stdout_path)
    artifact_dir = Path(args.artifact_dir)
    output_path = Path(args.output_path)

    text = stdout_path.read_text(encoding="utf-8", errors="ignore")
    artifacts = latest_artifacts(artifact_dir)
    json_objects = extract_json_objects(text)
    best_payload = json_objects[-1] if json_objects else {}

    lines: list[str] = []
    lines.append(f"# Hyperopt Report - {args.strategy}")
    lines.append("")
    lines.append(f"- Generated: `{dt.datetime.now().isoformat(timespec='seconds')}`")
    lines.append(f"- Strategy: `{args.strategy}`")
    lines.append(f"- Timerange: `{args.timerange}`")
    lines.append(f"- Epochs: `{args.epochs}`")
    lines.append(f"- Spaces: `{args.spaces}`")
    lines.append(f"- Loss function: `{args.loss_function}`")
    lines.append(f"- Raw log: `{stdout_path}`")
    lines.append("")

    if best_payload:
        lines.append("## Parsed JSON Snapshot")
        lines.append("")
        for key, value in flatten_first_level(best_payload):
            lines.append(f"- {key}: `{value}`")
        lines.append("")

    if artifacts:
        lines.append("## Recent Artifacts")
        lines.append("")
        for artifact in artifacts:
            lines.append(f"- `{artifact}`")
        lines.append("")

    lines.append("## Raw Hyperopt Output")
    lines.append("")
    lines.append("```text")
    lines.append(text.strip())
    lines.append("```")
    lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
