import os
import time
import asyncio
import yt_dlp

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InputFile

# ================= НАСТРОЙКИ =================

BOT_TOKEN = os.getenv("BOT_TOKEN") or "8563673825:AAH9ccz0QVZGqrqPXieQfmUMkp5jZQbWsv0"
DOWNLOAD_DIR = "downloads"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
COOLDOWN = 10  # секунд между запросами

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

last_request = {}

# ================= УТИЛИТЫ =================

def is_link(text: str) -> bool:
    return text.startswith("http://") or text.startswith("https://")

def allowed(user_id: int) -> bool:
    now = time.time()
    if user_id not in last_request:
        last_request[user_id] = now
        return True
    if now - last_request[user_id] >= COOLDOWN:
        last_request[user_id] = now
        return True
    return False

# ================= HANDLERS =================

@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    await msg.answer(
        "👋 Привет, братишка!\n\n"
        "📥 Пришли ссылку на видео:\n"
        "TikTok / YouTube / VK / Insta / Shorts\n\n"
        "⚠️ Ограничение: 1 ссылка в 10 секунд"
    )

@dp.message_handler()
async def handle_link(msg: types.Message):
    user_id = msg.from_user.id
    text = msg.text.strip()

    if not is_link(text):
        await msg.answer("❌ Это не ссылка")
        return

    if not allowed(user_id):
        await msg.answer("⏳ Подожди пару секунд перед следующим запросом")
        return

    await msg.answer("⏬ Скачиваю видео, подожди...")

    ydl_opts = {
        "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
        "format": "best",
        "merge_output_format": "mp4"
    }