from __future__ import annotations

import argparse
import datetime as dt
import json
import sqlite3
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db-path", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--mode", required=True)
    parser.add_argument("--days", type=int, default=1)
    parser.add_argument("--date", default="")
    return parser.parse_args()


def table_columns(connection: sqlite3.Connection, table_name: str) -> set[str]:
    rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {row[1] for row in rows}


def pick_first(columns: set[str], candidates: list[str]) -> str | None:
    for candidate in candidates:
        if candidate in columns:
            return candidate
    return None


def to_iso_window(args: argparse.Namespace) -> tuple[str, str, str]:
    if args.date:
        base_date = dt.date.fromisoformat(args.date)
    else:
        base_date = dt.datetime.now().date()
    start_date = base_date - dt.timedelta(days=max(args.days - 1, 0))
    start_dt = dt.datetime.combine(start_date, dt.time.min)
    end_dt = dt.datetime.combine(base_date + dt.timedelta(days=1), dt.time.min)
    label = f"{start_date.isoformat()}_to_{base_date.isoformat()}"
    return start_dt.isoformat(sep=" "), end_dt.isoformat(sep=" "), label


def fetch_rows(connection: sqlite3.Connection, query: str, parameters: tuple[Any, ...]) -> list[sqlite3.Row]:
    cursor = connection.execute(query, parameters)
    return cursor.fetchall()


def sum_numeric(rows: list[sqlite3.Row], column: str) -> float:
    total = 0.0
    for row in rows:
        value = row[column]
        if value is not None:
            total += float(value)
    return total


def main() -> None:
    args = parse_args()
    db_path = Path(args.db_path)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not db_path.exists():
        raise SystemExit(f"Database not found: {db_path}")

    start_dt, end_dt, label = to_iso_window(args)

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row

    columns = table_columns(connection, "trades")
    close_date_col = pick_first(columns, ["close_date_utc", "close_date"])
    open_date_col = pick_first(columns, ["open_date_utc", "open_date"])
    profit_abs_col = pick_first(columns, ["close_profit_abs", "profit_abs"])
    profit_ratio_col = pick_first(columns, ["close_profit", "profit_ratio"])
    pair_col = pick_first(columns, ["pair"])
    exit_reason_col = pick_first(columns, ["exit_reason", "sell_reason"])
    stake_col = pick_first(columns, ["stake_amount"])

    if not close_date_col or not open_date_col or not pair_col:
        raise SystemExit("Unsupported trades table schema.")

    closed_rows = fetch_rows(
        connection,
        f"""
        SELECT *
        FROM trades
        WHERE is_open = 0
          AND {close_date_col} >= ?
          AND {close_date_col} < ?
        ORDER BY {close_date_col} ASC
        """,
        (start_dt, end_dt),
    )

    open_rows = fetch_rows(
        connection,
        f"""
        SELECT *
        FROM trades
        WHERE is_open = 1
        ORDER BY {open_date_col} ASC
        """,
        (),
    )

    realized_pnl = sum_numeric(closed_rows, profit_abs_col) if profit_abs_col else 0.0
    avg_profit_ratio = (
        sum_numeric(closed_rows, profit_ratio_col) / len(closed_rows)
        if closed_rows and profit_ratio_col
        else 0.0
    )
    wins = 0
    losses = 0
    draws = 0
    exit_reason_counts: dict[str, int] = {}
    pair_pnl: dict[str, float] = {}

    for row in closed_rows:
        profit_ratio = float(row[profit_ratio_col]) if profit_ratio_col and row[profit_ratio_col] is not None else 0.0
        pair = str(row[pair_col])
        pair_pnl[pair] = pair_pnl.get(pair, 0.0) + (
            float(row[profit_abs_col]) if profit_abs_col and row[profit_abs_col] is not None else 0.0
        )

        if profit_ratio > 0:
            wins += 1
        elif profit_ratio < 0:
            losses += 1
        else:
            draws += 1

        if exit_reason_col and row[exit_reason_col]:
            key = str(row[exit_reason_col])
            exit_reason_counts[key] = exit_reason_counts.get(key, 0) + 1

    best_pair = None
    worst_pair = None
    if pair_pnl:
        best_pair = max(pair_pnl.items(), key=lambda item: item[1])
        worst_pair = min(pair_pnl.items(), key=lambda item: item[1])

    open_exposure = 0.0
    open_positions: list[dict[str, Any]] = []
    for row in open_rows:
        stake_amount = float(row[stake_col]) if stake_col and row[stake_col] is not None else 0.0
        open_exposure += stake_amount
        open_positions.append(
            {
                "pair": row[pair_col],
                "open_date": row[open_date_col],
                "stake_amount": stake_amount,
            }
        )

    payload = {
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "mode": args.mode,
        "window_start": start_dt,
        "window_end": end_dt,
        "db_path": str(db_path),
        "closed_trade_count": len(closed_rows),
        "open_trade_count": len(open_rows),
        "realized_pnl_abs": realized_pnl,
        "average_profit_ratio": avg_profit_ratio,
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "best_pair": best_pair,
        "worst_pair": worst_pair,
        "exit_reasons": exit_reason_counts,
        "open_exposure": open_exposure,
        "open_positions": open_positions,
    }

    prefix = f"{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}-{args.mode}-{label}"
    json_path = output_dir / f"{prefix}.json"
    md_path = output_dir / f"{prefix}.md"

    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")

    lines: list[str] = []
    lines.append(f"# Daily Trading Report - {args.mode}")
    lines.append("")
    lines.append(f"- Generated: `{payload['generated_at']}`")
    lines.append(f"- Window: `{start_dt}` to `{end_dt}`")
    lines.append(f"- Database: `{db_path}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Closed trades: `{len(closed_rows)}`")
    lines.append(f"- Open trades: `{len(open_rows)}`")
    lines.append(f"- Realized PnL: `{realized_pnl:.4f}`")
    lines.append(f"- Average profit ratio: `{avg_profit_ratio:.4%}`")
    lines.append(f"- Wins / Draws / Losses: `{wins} / {draws} / {losses}`")
    lines.append(f"- Open exposure: `{open_exposure:.4f}`")
    lines.append("")

    if best_pair:
        lines.append("## Pair Performance")
        lines.append("")
        lines.append(f"- Best pair: `{best_pair[0]}` -> `{best_pair[1]:.4f}`")
        lines.append(f"- Worst pair: `{worst_pair[0]}` -> `{worst_pair[1]:.4f}`")
        lines.append("")

    if exit_reason_counts:
        lines.append("## Exit Reasons")
        lines.append("")
        for reason, count in sorted(exit_reason_counts.items(), key=lambda item: (-item[1], item[0])):
            lines.append(f"- {reason}: `{count}`")
        lines.append("")

    if open_positions:
        lines.append("## Open Positions")
        lines.append("")
        for position in open_positions:
            lines.append(
                f"- {position['pair']}: opened `{position['open_date']}`, stake `{position['stake_amount']:.4f}`"
            )
        lines.append("")

    lines.append(f"- JSON summary: `{json_path}`")
    lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"Daily report written to {md_path}")


if __name__ == "__main__":
    main()
