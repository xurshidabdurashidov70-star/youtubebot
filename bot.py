import os
from pytube import YouTube
from telebot import TeleBot, types
from keep_alive import keep_alive
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🎬 Salom! YouTube yuklab beruvchi botga xush kelibsiz!\n\n"
                          "📎 Video havolasini yuboring.\n"
                          "🎥 360p, 480p, 720p sifatlar mavjud.\n"
                          "🎵 Faqat audio yuklash ham mumkin.")

@bot.message_handler(func=lambda m: True)
def handle_link(message):
    url = message.text.strip()
    if "youtube.com" not in url and "youtu.be" not in url:
        bot.reply_to(message, "⚠️ Iltimos, to‘g‘ri YouTube havolasini yuboring.")
        return

    yt = YouTube(url)
    markup = types.InlineKeyboardMarkup()
    for res in ["360p", "480p", "720p", "audio"]:
        markup.add(types.InlineKeyboardButton(res, callback_data=f"{url}|{res}"))

    bot.send_message(message.chat.id, f"🎬 {yt.title}\nFormatni tanlang:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def download_video(call):
    url, quality = call.data.split("|")
    yt = YouTube(url)
    chat_id = call.message.chat.id

    try:
        if quality == "audio":
            stream = yt.streams.filter(only_audio=True).first()
            filename = "audio.mp3"
        else:
            stream = yt.streams.filter(progressive=True, res=quality).first()
            if not stream:
                bot.send_message(chat_id, f"❌ {quality} format topilmadi.")
                return
            filename = f"video_{quality}.mp4"

        bot.answer_callback_query(call.id, f"⬇️ Yuklanmoqda ({quality})...")
        file_path = stream.download(filename=filename)

        file_size = os.path.getsize(file_path) / (1024 * 1024)
        if file_size > 45:
            bot.send_message(chat_id, f"⚠️ Fayl juda katta ({file_size:.1f} MB), Render cheklovi 50 MB!")
            os.remove(file_path)
            return

        if quality == "audio":
            bot.send_audio(chat_id, open(file_path, 'rb'))
        else:
            bot.send_video(chat_id, open(file_path, 'rb'))

        os.remove(file_path)

    except Exception as e:
        bot.send_message(chat_id, f"❌ Yuklab olishda xato: {str(e)}")

keep_alive()
bot.polling(non_stop=True)

