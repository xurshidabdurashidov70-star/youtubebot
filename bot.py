import os
import telebot
from pytube import YouTube
from keep_alive import keep_alive

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🎬 Salom! YouTube yuklab beruvchi botga xush kelibsiz.\n\n"
                          "🎵 Video yoki musiqa havolasini yuboring.\n"
                          "🎥 360p, 480p, 720p, 1080p sifatda yuklab olishingiz mumkin!")

@bot.message_handler(func=lambda msg: True)
def download_video(message):
    url = message.text
    if "youtube.com" not in url and "youtu.be" not in url:
        bot.reply_to(message, "⚠️ Iltimos, YouTube havolasini yuboring.")
        return

    try:
        yt = YouTube(url)
        title = yt.title
        streams = yt.streams

        msg = f"🎬 Video: {title}\nTanlang format:"
        bot.send_message(message.chat.id, msg)

        # Tugmalar bilan format tanlash
        markup = telebot.types.InlineKeyboardMarkup()
        for res in ["360p", "480p", "720p", "1080p", "audio"]:
            markup.add(telebot.types.InlineKeyboardButton(res, callback_data=f"{url}|{res}"))
        bot.send_message(message.chat.id, "📽 Formatni tanlang:", reply_markup=markup)

    except Exception as e:
        bot.reply_to(message, f"❌ Xato: {str(e)}")

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    url, res = call.data.split('|')
    yt = YouTube(url)
    file_path = None

    bot.answer_callback_query(call.id, f"⬇️ Yuklanmoqda {res}...")

    try:
        if res == "audio":
            stream = yt.streams.filter(only_audio=True).first()
            file_path = stream.download(filename="audio.mp3")
            bot.send_audio(call.message.chat.id, open(file_path, 'rb'))
        else:
            stream = yt.streams.filter(res=res, progressive=True, file_extension='mp4').first()
            if not stream:
                bot.send_message(call.message.chat.id, f"❌ {res} format topilmadi.")
                return
            file_path = stream.download(filename=f"video_{res}.mp4")
            bot.send_video(call.message.chat.id, open(file_path, 'rb'))
    except Exception as e:
        bot.send_message(call.message.chat.id, f"⚠️ Xato: {str(e)}")
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

keep_alive()
bot.polling(non_stop=True)
