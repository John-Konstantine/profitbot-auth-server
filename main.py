from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import hmac
import hashlib
import os
import json
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_SECRET = hashlib.sha256(BOT_TOKEN.encode()).digest()

@app.get("/auth")
async def auth(request: Request):
    query = dict(request.query_params)
    received_hash = query.pop("hash", "")
    data_check_string = "\n".join([f"{k}={v}" for k, v in sorted(query.items())])

    hmac_hash = hmac.new(TELEGRAM_SECRET, msg=data_check_string.encode(), digestmod=hashlib.sha256).hexdigest()

    if not hmac.compare_digest(hmac_hash, received_hash):
        return HTMLResponse("<h2>❌ Подпись недействительна. Вход запрещён.</h2>", status_code=403)

    user_id = str(query.get("id"))
    licenses = {}
    try:
        with open("licenses.json", "r") as f:
            licenses = json.load(f)
    except FileNotFoundError:
        pass

    if user_id in licenses:
        return HTMLResponse(f"<h2>✅ Добро пожаловать, {query.get('first_name')}!</h2><p>Доступ разрешён.</p>")
    else:
        return HTMLResponse(f"<h2>⛔ Привет, {query.get('first_name')}!</h2><p>Ваш Telegram ID не активирован. Оплатите подписку для доступа.</p>")
