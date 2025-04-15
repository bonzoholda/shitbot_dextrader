import os
import time
import threading
import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

# Import your full bot class and dependencies from the current file
from shitbot_dextrader import TradingBot  # Make sure this import works correctly

app = FastAPI()
templates = Jinja2Templates(directory="templates")

bot = TradingBot()

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
    
    while True:
        try:
            bot.trading_execution()
        except Exception as e:
            logging.error(f"Error in bot: {e}")
        time.sleep(15)

threading.Thread(target=start_bot, daemon=True).start()

# HTML page that auto-refreshes logs
#@app.get("/", response_class=HTMLResponse)
#@app.get("/logs", response_class=HTMLResponse)
def logs(request: Request):
    try:
        with open("bot.log", "r") as f:
            lines = f.readlines()[-20:]
    except FileNotFoundError:
        lines = ["Log file not found."]

    return templates.TemplateResponse("logs.html", {
        "request": request,
        "logs": "".join(lines)
    })

def get_status():
    try:
        stats = bot.get_account_stats()
        return JSONResponse(stats)
    except Exception as e:
        return JSONResponse({"error": str(e)})
        
@app.get("/", response_class=HTMLResponse)
@app.get("/status", response_class=HTMLResponse)
def show_status(request: Request):
    try:
        logs(request: Request)
        stats = bot.get_account_stats()
        return templates.TemplateResponse("status.html", {
            "request": request,
            "stats": stats,
            "logs": logs
        })
    except Exception as e:
        return HTMLResponse(content=f"<pre>Error: {e}</pre>", status_code=500)
