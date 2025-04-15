import os
import time
import threading
import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Import your full bot class and dependencies from the current file
from shitbot_dextrader import TradingBot  # Make sure this import works correctly

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Configure logging to both file and console
logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
logging.getLogger().addHandler(console_handler)

# Start your trading bot in a background thread
def start_bot():
    bot = TradingBot()
    while True:
        try:
            bot.trading_execution()
        except Exception as e:
            logging.error(f"Error in bot: {e}")
        time.sleep(15)

threading.Thread(target=start_bot, daemon=True).start()

# HTML page that auto-refreshes logs
@app.get("/", response_class=HTMLResponse)
@app.get("/logs", response_class=HTMLResponse)
def logs(request: Request):
    try:
        with open("bot.log", "r") as f:
            lines = f.readlines()[-10:]
    except FileNotFoundError:
        lines = ["Log file not found."]

    return templates.TemplateResponse("logs.html", {
        "request": request,
        "logs": "".join(lines)
    })
