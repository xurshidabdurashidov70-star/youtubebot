from flask import Flask
import threading, time, requests, os

app = Flask('')

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
            requests.get("https://youtubebot-kjbb.onrender.com")
        except:
            pass

def keep_alive():
    t = threading.Thread(target=run)
    t.start()
    p = threading.Thread(target=ping)
    p.start()
