from flask import Flask
import threading, time, requests, os

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot is alive!"

def run():
    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def ping():
    while True:
        time.sleep(600)
        try:
            requests.get("https://youtubebot-kjbb.onrender.com")  # 🔗 o'zingni URL
        except:
            pass

def keep_alive():
    threading.Thread(target=run).start()
    threading.Thread(target=ping).start()
