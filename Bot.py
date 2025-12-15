import os
import time
import yt_dlp

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InputFile

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not set")

DOWNLOAD_DIR = "downloads"
MAX_FILE_SIZE = 49 * 1024 * 1024
COOLDOWN = 10

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

last_request = {}

def allowed(user_id):
    now = time.time()
    if user_id not in last_request or now - last_request[user_id] >= COOLDOWN:
        last_request[user_id] = now
        return True
    return False

@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    await msg.answer(
        "👋 Кинь ссылку на видео\n"
        "TikTok / VK / Insta / Shorts\n\n"
        "⏱ 1 ссылка / 10 сек"
    )

@dp.message_handler()
async def download(msg: types.Message):
    if not msg.text.startswith("http"):
        return

    if not allowed(msg.from_user.id):
        await msg.answer("⏳ Подожди немного")
        return

    await msg.answer("⏬ Качаю...")

    ydl_opts = {
        "outtmpl": f"{DOWNLOAD_DIR}/%(id)s.%(ext)s",
        "format": "best[filesize_approx<=49M]/best",
        "quiet": True,
        "noplaylist": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(msg.text, download=True)
            filename = ydl.prepare_filename(info)

        if os.path.getsize(filename) > MAX_FILE_SIZE:
            os.remove(filename)
            await msg.answer("⚠️ Видео слишком большое")
            return

        await msg.answer_video(InputFile(filename))
        os.remove(filename)

    except Exception as e:
        await msg.answer("❌ Не удалось скачать")
        print(e)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
