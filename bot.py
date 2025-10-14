from keep_alive import keep_alive
import telebot
from telebot import types
from pytube import YouTube
import os

# === Telegram bot tokenini o'qish ===
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# === /start komandasi ===
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🎥 Salom! Menga YouTube havolasini yubor, men uni yuklab beraman.")

# === YouTube havola yuborilganda ===
@bot.message_handler(func=lambda m: True)
def handle_url(message):
    url = message.text.strip()
    if "youtube.com" not in url and "youtu.be" not in url:
        bot.reply_to(message, "❌ Bu YouTube havolasi emas.")
        return

    # Tugmalarni gorizontal tarzda yaratish
    markup = types.InlineKeyboardMarkup(row_width=4)
    btn360 = types.InlineKeyboardButton("360p", callback_data=f"{url}|360p")
    btn480 = types.InlineKeyboardButton("480p", callback_data=f"{url}|480p")
    btn720 = types.InlineKeyboardButton("720p", callback_data=f"{url}|720p")
    btnaudio = types.InlineKeyboardButton("Audio", callback_data=f"{url}|audio")
    markup.add(btn360, btn480, btn720, btnaudio)

    bot.send_message(message.chat.id, "🎬 Qaysi formatda yuklaymiz?", reply_markup=markup)

# === Tugma bosilganda (callback handler) ===
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    url, quality = call.data.split("|")
    bot.answer_callback_query(call.id, f"{quality} format tanlandi, yuklab olinmoqda... ⏳")

    try:
        yt = YouTube(url)
        if quality == "audio":
            stream = yt.streams.filter(only_audio=True).first()
            filename = "audio.mp3"
        else:
            stream = yt.streams.filter(res=quality, progressive=True).first()
            if not stream:
                bot.send_message(call.message.chat.id, f"❌ {quality} format topilmadi.")
                return
            filename = f"video_{quality}.mp4"

        file = stream.download(filename=filename)

        with open(file, "rb") as video:
            bot.send_document(call.message.chat.id, video)

        os.remove(file)

    except Exception as e:
        bot.send_message(call.message.chat.id, f"⚠️ Xatolik:\n{e}")

# === Keep Alive ishga tushirish va botni polling qilish ===
if __name__ == "__main__":
    keep_alive()  # 🔥 bu Flask server + pingni ishga tushiradi
    bot.infinity_polling()
