import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from instaloader import Instaloader, Post
from pydub import AudioSegment
import requests

# بارگذاری متغیرهای محیطی از Environment Variables
TELEGRAM_TOKEN = os.getenv("7972095626:AAGT1lbF_p1SseA5RfjXjKoasZdmk5k3cyA")
AUDD_API_TOKEN = os.getenv("31ab6158d8c1dce8aaca889d53b27f1e")

# دیباگ: چاپ توکن‌ها
print("7972095626:AAGT1lbF_p1SseA5RfjXjKoasZdmk5k3cyA", TELEGRAM_TOKEN)
print("31ab6158d8c1dce8aaca889d53b27f1e", AUDD_API_TOKEN)

# بررسی توکن تلگرام
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN is not set in environment variables")

# تنظیمات اولیه
L = Instaloader()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لینک ریلز اینستاگرام رو بفرست تا آهنگش رو پیدا کنم.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "instagram.com" in url:
        await update.message.reply_text("در حال پردازش لینک...")
        try:
            # استخراج shortcode از لینک
            shortcode = url.split("/")[-2]
            post = Post.from_shortcode(L.context, shortcode)
            # دانلود ویدیو
            L.download_post(post, target="downloads")
            video_path = f"downloads/{shortcode}.mp4"
            audio_path = f"downloads/{shortcode}.mp3"
            # تبدیل ویدیو به صوت
            video = AudioSegment.from_file(video_path)
            video.export(audio_path, format="mp3")
            # شناسایی آهنگ با AudD.io
            if AUDD_API_TOKEN:
                with open(audio_path, "rb") as audio_file:
                    response = requests.post(
                        "https://api.audd.io/",
                        files={"file": audio_file},
                        data={"api_token": AUDD_API_TOKEN}
                    )
                result = response.json()
                if result["status"] == "success" and result["result"]:
                    song = result["result"]
                    await update.message.reply_text(f"آهنگ پیدا شد!\nنام: {song['title']}\nخواننده: {song['artist']}")
                else:
                    await update.message.reply_text("آهنگ پیدا نشد!")
            else:
                await update.message.reply_text("توکن AudD.io تنظیم نشده است!")
            # حذف فایل‌های موقت
            os.remove(video_path)
            os.remove(audio_path)
        except Exception as e:
            await update.message.reply_text(f"خطا: {str(e)}")
    else:
        await update.message.reply_text("لطفاً یک لینک معتبر اینستاگرام بفرستید.")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()