# Deployment Checklist

## Before Dry-Run

- Docker is installed and working
- Pair whitelist reviewed
- Stake amount reviewed
- Strategy file reviewed
- Historical data downloaded
- Backtest completed
- Lookahead analysis completed
- Recursive analysis completed

## Before Live Trading

- Dry-run ran for at least 14 days
- Dry-run behavior reviewed against backtest assumptions
- `config/private.live.json` created locally
- Binance API key is dedicated to this bot
- Binance API key permissions reviewed
- Host clock sync is working
- Firewall blocks public access to bot ports
- API/UI credentials changed from placeholders
- Backup process tested
- Small initial capital selected

## Go-Live Sequence

1. Stop dry-run if it is still active
2. Create a backup of the dry-run DB and configs
3. Re-check `config/live.json` and `config/private.live.json`
4. Start the live service
5. Confirm API/UI responds on localhost
6. Confirm first order sizing and stoploss behavior
7. Monitor continuously during the first session

