# bybit_tradingview_bot
### 概要
TradingViewのアラートを受け取り、Bybitで自動売買を行う。

### 作成する設定ファイル(config.ini)

```

[bybit]
api_key = (APIキー)
api_secret = (シークレットキー)

[trade]
symbol = BTCUSDT
lot = 0.001
max_lot = 0.01
leverage = 10

[line]
line_token = (Line Notifyのトークン)

```
