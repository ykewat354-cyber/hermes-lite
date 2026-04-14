#!/usr/bin/env python3
import os
import requests
import subprocess
from hermes_lite.core import HermesLite

class TelegramGateway:
    def __init__(self, bot_token, agent):
        self.bot_token = bot_token
        self.agent = agent
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
        self.last_update_id = 0

    def send_msg(self, chat_id, text):
        requests.post(f"{self.api_url}/sendMessage", json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})

    def poll(self):
        url = f"{self.api_url}/getUpdates"
        try:
            res = requests.get(url, params={"offset": self.last_update_id + 1, "timeout": 30}).json()
            for update in res.get("result", []):
                self.last_update_id = update["update_id"]
                if "message" in update:
                    chat_id = update["message"]["chat"]["id"]
                    text = update["message"].get("text", "")
                    
                    if text.startswith("/set-key"):
                        parts = text.split(" ", 1)
                        if len(parts) > 1:
                            msg = self.agent.update_api_key(parts[1].strip())
                            self.send_msg(chat_id, msg)
                        else:
                            self.send_msg(chat_id, "Bhai, key bhi bhej: `/set-key your_key`")
                    
                    elif text == "/update":
                        self.send_msg(chat_id, "🔄 Updating from GitHub... Please wait.")
                        subprocess.run(["bash", "-c", "curl -fsSL https://raw.githubusercontent.com/ykewat354-cyber/hermes-lite/main/install.sh | bash"], check=True)
                        self.send_msg(chat_id, "✅ Update Complete! Please restart the bot.")
                    
                    else:
                        reply = self.agent.chat(text)
                        self.send_msg(chat_id, reply)
        except Exception as e:
            print(f"Polling error: {e}")

def run_bot():
    token = os.getenv("TELEGRAM_BOT_TOKEN", "8519174502:AAG5JqdGkzAvgUi5ElN1PLPir3kroQx3n4c")
    # Note: Default API key is kept here as fallback, but core.py will read from config.json
    api_key = os.getenv("OPENROUTER_API_KEY", "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")
    
    agent = HermesLite(api_key=api_key)
    bot = TelegramGateway(token, agent)
    print("🚀 Hermes Lite Bot with Persistent Key logic is Live!")
    while True: bot.poll()

if __name__ == "__main__":
    run_bot()
