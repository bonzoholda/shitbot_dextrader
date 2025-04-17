Introducing ShitBot_DEXtrader!
v1.0 (Free/”coffee cup” version for Polygon network)
-------------------------
Grow your portfolio automatically in a decentralized way!


This DEX trading bot runs 24/7, coded in Python and hosted through the Railway platform. Anyone can deploy their own client with a single click.

The bot is using following strategy:

- Open a new position based on signals (combination of Moving Average & RSI Divergence, whichever comes first).
- The trade volume will use 16% of portfolio value, and the new position will be opened only if the volume is less than wallet balance (USDT balance for Buy, WMATIC balance for Sell).
- Once the position gets opened, the bot will monitor it to hit TP/SL (by default, the bot uses 3% price difference to trigger trailing TP and -5% for SL).
- If the TP target gets hit, it will trigger trailing to maximize the result. The position will then be closed after callback rate crosses previous highest long/lowest short.
- When SL gets hit, instead of closing the position the bot will do DCA (a new Buy for Long position, or a new Sell for Short position, then restart scanning new signals).
- Automatic trade volume management will maintain maximum 6 Buys/6 Sells in a row.
- The portfolio growth will automatically compound the profit for the new position.


## 🚀 Deploy Your Own Copy

Click the button below to deploy the bot to Railway (almost free cloud hosting, you can log in there using google or github account):

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/template/tROma6?referralCode=u300S7)

Once your bot gets deployed, go to the Railway dashboard, click on the bot template/architecture, go to settings, navigate to generate public html, set port 8000, then generate URL/link. That will be your account dashboard to monitor the bot performance and your portfolio.

Here’s sample of testing dashboard which can be seen for public, you’ll get exactly the same dashboard for your account (with slightly different URL indicating your bot name):

https://shitbotdextrader-production.up.railway.app/


### 🧪 Requirements

You'll need to provide the following while start deploying your bot:
- ✅ Your wallet address + private key (for on-chain trading)
- ✅ Load your Polygon wallet with at least 20USDT (for initial portfolio, 100USDT is recommended) and 10POL (for gas fee, might be sufficient for up to 1000 transactions).

We recommend creating a new wallet just for the bot.


Wanna buy a cup of coffee for the shitdev? You might throw some POL or USDT to this wallet:

0x4A6Eb7dE1779a7D3Cdcf7440252D436d49c0FE30

