from flask import Flask
import os
import subprocess
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "🕌 Zain Islamic Bot is running! 🌙"

@app.route('/health')
def health():
    return "OK"

def start_bot():
    # Start your main bot script
    subprocess.run(['python', 'main.py'])

if __name__ == '__main__':
    # Start bot in a separate thread
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Start Flask web server
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
