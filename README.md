Introducing ShitBot_DEXtrader!
v1.0, for Polygon network.
-------------------------

This DEX trader bot runs 24/7 with following strategy:
- Open a new position based on signals (combination of Moving Average & RSI Divergence, whichever comes first).
- The trade volume will use 16% of portfolio value and if the volume is < wallet balance (USDT balance for Buy, WMATIC or WPOL balance for Sell).
- Once the position gets opened, the bot will monitor it to hit either TP/SL (by default, the bot uses 5% price difference to trigger trailing TP or SL).
- When SL gets hit, instead of closing the position the bot will do DCA (a new Buy for Long position, or a new Sell for Short position, then restart scanning new signals).
- The volume management will maintain maximum 6 Buys/6 Sells in a row (DCA due to SL hit)
- The portfolio growth will automatically compound the profit for new position.


## 🚀 Deploy Your Own Copy

Click the button below to deploy the bot to Railway (almost free cloud hosting, you can log in there using google or github account):

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/template/IYTjWn?referralCode=u300S7)

### 🧪 Requirements

You'll need to provide the following while start deploying your bot:
- ✅ Your wallet address + private key (for on-chain trading)
- ✅ Load your Polygon wallet with at least 20USDT (for initial portfolio, 100USDT is recommended) and 10POL (for gas fee, might be sufficient for up to 1000 transactions).

We recommend creating a new wallet just for the bot.

