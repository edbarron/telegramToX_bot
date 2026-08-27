# path: pulso_bot/telegram_to_x_bot.py
from __future__ import annotations

import os
import sys
import logging
from pathlib import Path

# 1) Cargar .env (por qué: os.getenv no lee .env)
try:
    from dotenv import load_dotenv  # pip install python-dotenv
    # Carga desde CWD y desde la carpeta del script
    load_dotenv(override=False)
    load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env", override=False)
except Exception:
    pass

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger("pulso_bot")

def need_env(name: str, aliases: list[str] | None = None) -> str:
    """Busca una ENV por nombre y alias; aborta si no existe.
    Por qué: tu .env usa CONSUMER_* pero el código usa API_*."""
    names = [name] + (aliases or [])
    for n in names:
        val = os.getenv(n)
        if val is not None and val.strip() != "":
            if n != name:
                # Exporta a la clave esperada para el resto del código
                os.environ[name] = val
            return val
    log.error("Falta variable de entorno: %s (aliases: %s)", name, aliases)
    sys.exit(2)

# === ENV requeridas ===
TELEGRAM_BOT_TOKEN = need_env("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID_STR = need_env("TELEGRAM_CHANNEL_ID")

# Notar los alias con tus nombres del .env
TWITTER_BEARER_TOKEN = need_env("TWITTER_BEARER_TOKEN")
TWITTER_API_KEY = need_env("TWITTER_API_KEY", aliases=["TWITTER_CONSUMER_KEY"])
TWITTER_API_SECRET = need_env("TWITTER_API_SECRET", aliases=["TWITTER_CONSUMER_SECRET"])
TWITTER_ACCESS_TOKEN = need_env("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = need_env("TWITTER_ACCESS_SECRET")

# Canal puede ser negativo
try:
    TELEGRAM_CHANNEL_ID = int(TELEGRAM_CHANNEL_ID_STR)
except ValueError:
    log.error("TELEGRAM_CHANNEL_ID debe ser entero (puede ser negativo). Valor: %r", TELEGRAM_CHANNEL_ID_STR)
    sys.exit(2)

# ================= Resto: tu bot =================
import json
from datetime import datetime, timedelta
import tweepy
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

CONTADOR_PATH = "contador.json"

# Twitter clients
auth = tweepy.OAuth1UserHandler(
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_SECRET
)
api = tweepy.API(auth, wait_on_rate_limit=True)

client = tweepy.Client(
    bearer_token=TWITTER_BEARER_TOKEN,
    consumer_key=TWITTER_API_KEY,
    consumer_secret=TWITTER_API_SECRET,
    access_token=TWITTER_ACCESS_TOKEN,
    access_token_secret=TWITTER_ACCESS_SECRET,
    wait_on_rate_limit=True,
)

# Contador
def cargar_contador():
    if not os.path.exists(CONTADOR_PATH):
        return {"requests_usados": 0, "ultima_actualizacion": datetime.utcnow().isoformat()}
    with open(CONTADOR_PATH, "r") as f:
        data = json.load(f)
    try:
        ultima = datetime.fromisoformat(data.get("ultima_actualizacion", ""))
    except Exception:
        ultima = datetime.utcnow()
    ahora = datetime.utcnow()
    if ahora - ultima > timedelta(hours=24):
        log.info("🕛 Contador reiniciado (nueva ventana de 24h)")
        return {"requests_usados": 0, "ultima_actualizacion": ahora.isoformat()}
    if not isinstance(data.get("requests_usados"), int):
        data["requests_usados"] = 0
    return data

def guardar_contador(data):
    tmp = f"{CONTADOR_PATH}.tmp"
    with open(tmp, "w") as f:
        json.dump(data, f)
    os.replace(tmp, CONTADOR_PATH)

def incrementar_requests(cantidad=1):
    data = cargar_contador()
    data["requests_usados"] = max(0, data["requests_usados"] + cantidad)
    data["ultima_actualizacion"] = datetime.utcnow().isoformat()
    guardar_contador(data)
    log.info("📊 Requests usados hoy: %s / %s", data["requests_usados"], 500)

# Publicación
def publicar_tweet(texto, archivo_path=None):
    log.info("📤 Enviando tweet: %s", (texto or "")[:50].replace("\n", " "))
    try:
        text = (texto or "").strip()
        if len(text) > 280:
            text = text[:277] + "…"
        if archivo_path:
            media = api.media_upload(archivo_path)
            client.create_tweet(text=text, media_ids=[media.media_id])
            incrementar_requests(2)
        else:
            client.create_tweet(text=text)
            incrementar_requests(1)
        log.info("✅ Publicado en X")
    except tweepy.errors.TooManyRequests:
        log.error("❌ Límite de rate alcanzado (429)")
    except tweepy.errors.Forbidden as e:
        resp = getattr(e, "response", None)
        log.error("❌ Forbidden: %s", getattr(resp, "text", e))
    except Exception as e:
        log.exception("❌ Error inesperado publicando en X: %s", e)

# Telegram
async def manejar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if msg is None or msg.chat_id != TELEGRAM_CHANNEL_ID:
        return
    texto = msg.caption if msg.caption else msg.text or "📝 Sin texto"
    archivo_path = None
    try:
        if msg.photo:
            photo = msg.photo[-1]
            archivo_path = "temp.jpg"
            await (await photo.get_file()).download_to_drive(archivo_path)
        elif msg.video:
            archivo_path = "temp.mp4"
            await (await msg.video.get_file()).download_to_drive(archivo_path)
        publicar_tweet(texto, archivo_path)
    finally:
        if archivo_path and os.path.exists(archivo_path):
            try:
                os.remove(archivo_path)
            except Exception:
                log.warning("No se pudo borrar %s", archivo_path)

# Run
if __name__ == "__main__":
    log.info("🤖 PulsoBot activo...")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, manejar_mensaje))
    app.run_polling()
