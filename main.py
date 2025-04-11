
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import hmac, hashlib, os, json
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "6393934084"
TELEGRAM_SECRET = hashlib.sha256(BOT_TOKEN.encode()).digest()

LICENSES_FILE = "licenses.json"

def load_licenses():
    if not os.path.exists(LICENSES_FILE):
        return {}
    with open(LICENSES_FILE, "r") as f:
        return json.load(f)

def save_licenses(data):
    with open(LICENSES_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.get("/auth")
async def auth(request: Request):
    query = dict(request.query_params)
    received_hash = query.pop("hash", "")
    data_check_string = "\n".join([f"{k}={v}" for k, v in sorted(query.items())])
    hmac_hash = hmac.new(TELEGRAM_SECRET, msg=data_check_string.encode(), digestmod=hashlib.sha256).hexdigest()

    if not hmac.compare_digest(hmac_hash, received_hash):
        return HTMLResponse("<h2 style='color:red;'>❌ Подпись недействительна. Вход запрещён.</h2>", status_code=403)

    user_id = str(query.get("id"))
    licenses = load_licenses()

    if user_id in licenses:
        return HTMLResponse(f"<h2 style='color:#00ff88;'>✅ Добро пожаловать, {query.get('first_name')}!</h2><p>Доступ разрешён.</p>")
    else:
        return HTMLResponse(f"<h2 style='color:orange;'>⛔ Привет, {query.get('first_name')}!</h2><p>Ваш Telegram ID не активирован. Оплатите подписку для доступа.</p>")

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request):
    query = dict(request.query_params)
    user_id = query.get("id")

    if user_id != ADMIN_ID:
        return HTMLResponse("<h1 style='color:red;'>Доступ запрещён</h1>", status_code=403)

    licenses = load_licenses()
    html = f"""
    <html><head>
    <style>
    body {{ background: #0f0f0f; color: #fff; font-family: sans-serif; padding: 2rem; }}
    input, button {{ padding: 0.5rem; margin: 0.5rem; border-radius: 6px; }}
    table {{ margin-top: 1rem; }}
    td {{ padding: 0.4rem 1rem; }}
    .danger {{ color: #f44336; }}
    .success {{ color: #00ff88; }}
    </style>
    </head><body>
    <h1>👑 Админ-панель ProfitBot</h1>
    <form method="post" action="/admin/add?id={ADMIN_ID}">
        <input type="text" name="new_id" placeholder="Telegram ID">
        <button type="submit">➕ Добавить</button>
    </form>
    <h2>📋 Текущие ID с доступом:</h2>
    <table>
    {''.join(f"<tr><td>{uid}</td><td><a href='/admin/delete?id={ADMIN_ID}&remove_id={uid}' class='danger'>Удалить ❌</a></td></tr>" for uid in licenses)}
    </table>
    </body></html>
    """
    return HTMLResponse(html)

@app.post("/admin/add")
async def admin_add(request: Request, new_id: str = Form(...)):
    query = dict(request.query_params)
    if query.get("id") != ADMIN_ID:
        return HTMLResponse("Доступ запрещён", status_code=403)

    licenses = load_licenses()
    licenses[new_id] = "2025-12-31"
    save_licenses(licenses)
    return RedirectResponse(url=f"/admin?id={ADMIN_ID}", status_code=302)

@app.get("/admin/delete")
async def admin_delete(request: Request):
    query = dict(request.query_params)
    if query.get("id") != ADMIN_ID:
        return HTMLResponse("Доступ запрещён", status_code=403)

    remove_id = query.get("remove_id")
    licenses = load_licenses()
    if remove_id in licenses:
        del licenses[remove_id]
        save_licenses(licenses)
    return RedirectResponse(url=f"/admin?id={ADMIN_ID}", status_code=302)
<<<<<<< HEAD

=======
>>>>>>> 8ab444c (Add admin panel)
