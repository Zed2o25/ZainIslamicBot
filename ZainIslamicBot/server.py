from flask import Flask
import os
import threading
import asyncio
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    return "🕌 Zain Islamic Bot is running! 🌙"

@app.route('/health')
def health():
    return "OK", 200

async def run_bot_async():
    """Run the bot using asyncio"""
    try:
        # Import and run the main bot function
        from main import main_async
        await main_async()
    except Exception as e:
        logger.error(f"Bot error: {e}")

def run_bot():
    """Run the bot in a separate thread with asyncio"""
    try:
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_bot_async())
    except Exception as e:
        logger.error(f"Bot thread error: {e}")

if __name__ == '__main__':
    print("🚀 Starting web server and bot...")
    
    # Start bot in a separate thread
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Start Flask web server
    port = int(os.environ.get('PORT', 10000))
    print(f"🌐 Starting web server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
