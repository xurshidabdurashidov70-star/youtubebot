import os
from telebot import TeleBot, types
from pytube import YouTube
from keep_alive import keep_alive

# 🔐 Tokenni olish
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN topilmadi! Render Environment'da qo'shganmisan?")

bot = TeleBot(TOKEN, parse_mode="HTML")

# 🔸 /start komandasi
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🎬 Salom! Menga YouTube havolasini yubor, men uni yuklab beraman!")

# 🔸 YouTube linkni qabul qilish
@bot.message_handler(func=lambda msg: True)
def handle_url(message):
    url = message.text.strip()
    if "youtube.com" not in url and "youtu.be" not in url:
        bot.reply_to(message, "❌ Bu YouTube havolasi emas.")
        return

    markup = types.InlineKeyboardMarkup(row_width=4)
    btn360 = types.InlineKeyboardButton("360p", callback_data=f"{url}|360p")
    btn480 = types.InlineKeyboardButton("480p", callback_data=f"{url}|480p")
    btn720 = types.InlineKeyboardButton("720p", callback_data=f"{url}|720p")
    btn1080 = types.InlineKeyboardButton("1080p", callback_data=f"{url}|1080p")
    btnaudio = types.InlineKeyboardButton("🎧 Audio", callback_data=f"{url}|audio")
    markup.add(btn360, btn480, btn720, btn1080, btnaudio)

    bot.send_message(message.chat.id, "📥 Qaysi formatni yuklaymiz?", reply_markup=markup)

# 🔸 Tugma bosilganda
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    url, quality = call.data.split("|")
    bot.answer_callback_query(call.id, f"{quality} format tanlandi! Yuklab olinmoqda...")

    try:
        yt = YouTube(url)

        if quality == "audio":
            stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
            filename = "audio.mp3"
        else:
            stream = yt.streams.filter(res=quality).first()
            if not stream:
                bot.send_message(call.message.chat.id, f"❌ {quality} format topilmadi.")
                return
            filename = f"video_{quality}.mp4"

        file = stream.download(filename=filename)

        with open(file, "rb") as f:
            bot.send_document(call.message.chat.id, f)

        os.remove(file)
    except Exception as e:
        bot.send_message(call.message.chat.id, f"⚠️ Xatolik:\n{e}")

# 🔸 Ishga tushirish
if __name__ == "__main__":
    keep_alive()
    print("🚀 Bot ishga tushdi va faol holatda!")
    bot.infinity_polling(skip_pending=True)
