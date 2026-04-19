# Incident Response

## Immediate Actions

If the bot behaves unexpectedly:

1. Stop new trading activity
2. Preserve logs and databases
3. Determine whether funds are still at exchange or in open orders
4. Revoke or rotate keys if compromise is suspected

## Common Cases

### API Key Exposure

1. Stop the live service
2. Revoke the Binance API key immediately
3. Generate a new key
4. Update `config/private.live.json`
5. Review access logs and recent orders

### Repeated Order Rejections

1. Stop live trading
2. Inspect pair filters, minimum notional, and stake size
3. Verify account permissions and balances
4. Review the last bot log entries before restarting

### Time Drift / Authentication Failures

1. Verify system time sync
2. Restart the bot only after time is corrected
3. Re-check network latency and host load

### Stoploss Cascade

1. Pause bot entry activity
2. Preserve DB and logs
3. Review whether protections triggered as expected
4. Do not resume until market regime and configuration are reviewed

## Evidence To Preserve

- `user_data/logs/*.log`
- `user_data/*.sqlite`
- active config files
- Binance order history during the incident window

