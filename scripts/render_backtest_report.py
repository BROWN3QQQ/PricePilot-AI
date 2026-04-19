from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path
from typing import Iterable


INTERESTING_LABELS = {
    "Starting balance",
    "Final balance",
    "Absolute profit",
    "Total profit %",
    "CAGR %",
    "Sortino",
    "Sharpe",
    "Calmar",
    "Profit factor",
    "Expectancy (Ratio)",
    "Trades/day",
    "Avg. daily profit %",
    "Max % of account underwater",
    "Drawdown",
    "Market change",
    "Total/Daily Avg Trades",
    "Total trade volume",
    "Best Pair",
    "Worst Pair",
    "Win  Draw  Loss  Win%",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stdout-path", required=True)
    parser.add_argument("--artifact-dir", required=True)
    parser.add_argument("--output-path", required=True)
    parser.add_argument("--strategy", required=True)
    parser.add_argument("--timerange", required=True)
    parser.add_argument("--timeframe-detail", required=True)
    parser.add_argument("--notes", default="")
    return parser.parse_args()


def parse_table_metrics(lines: Iterable[str]) -> dict[str, str]:
    metrics: dict[str, str] = {}
    for raw_line in lines:
        line = raw_line.strip()
        if "│" not in line:
            continue
        parts = [part.strip() for part in line.split("│") if part.strip()]
        if len(parts) < 2:
            continue
        key = parts[0]
        value = parts[1]
        if key in INTERESTING_LABELS and key not in metrics:
            metrics[key] = value
    return metrics


def latest_artifacts(artifact_dir: Path) -> list[Path]:
    if not artifact_dir.exists():
        return []
    candidates = [
        path
        for path in artifact_dir.iterdir()
        if path.is_file() and path.suffix.lower() in {".zip", ".json"}
    ]
    candidates.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    return candidates[:3]


def main() -> None:
    args = parse_args()
    stdout_path = Path(args.stdout_path)
    artifact_dir = Path(args.artifact_dir)
    output_path = Path(args.output_path)

    text = stdout_path.read_text(encoding="utf-8", errors="ignore")
    metrics = parse_table_metrics(text.splitlines())
    artifacts = latest_artifacts(artifact_dir)

    lines: list[str] = []
    lines.append(f"# Backtest Report - {args.strategy}")
    lines.append("")
    lines.append(f"- Generated: `{dt.datetime.now().isoformat(timespec='seconds')}`")
    lines.append(f"- Strategy: `{args.strategy}`")
    lines.append(f"- Timerange: `{args.timerange}`")
    lines.append(f"- Timeframe detail: `{args.timeframe_detail}`")
    if args.notes:
        lines.append(f"- Notes: `{args.notes}`")
    lines.append(f"- Raw log: `{stdout_path}`")
    lines.append("")

    if metrics:
        lines.append("## Key Metrics")
        lines.append("")
        for key, value in metrics.items():
            lines.append(f"- {key}: `{value}`")
        lines.append("")

    if artifacts:
        lines.append("## Recent Artifacts")
        lines.append("")
        for artifact in artifacts:
            lines.append(f"- `{artifact}`")
        lines.append("")

    lines.append("## Raw Backtest Output")
    lines.append("")
    lines.append("```text")
    lines.append(text.strip())
    lines.append("```")
    lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
