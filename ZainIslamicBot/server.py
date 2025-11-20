from flask import Flask
import os
import threading
import time

app = Flask(__name__)

@app.route('/')
def home():
    return "🕌 Zain Islamic Bot is running! 🌙"

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    # Import and run your main bot
    from main import main
    main()

if __name__ == '__main__':
    print("🚀 Starting web server and bot...")
    
    # Start bot in a separate thread
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Give bot time to start
    time.sleep(3)
    
    # Start Flask web server
    port = int(os.environ.get('PORT', 10000))
    print(f"🌐 Starting web server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
