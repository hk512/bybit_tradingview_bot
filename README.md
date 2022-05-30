# bybit_tradingview_bot
### 概要
TradingViewのアラートを受け取り、Bybitで自動売買を行う。

### 作成する設定ファイル(config.ini)

```

[bybit]
api_key = (APIキー)
api_secret = (シークレットキー)

[trade]
symbol = BTCUSD
derivative_type = 'inverse'
lot = 100
max_lot = 1000
leverage = 10

[line]
line_token = (Line Notifyのトークン)

```
