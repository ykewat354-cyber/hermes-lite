#!/usr/bin/env python3
"""
Hermes Lite Telegram Gateway
Connects the ultra-lightweight Hermes Lite core to Telegram Bot API
"""

import os
import requests
import json
from typing import Dict, Any
from hermes_lite.core import HermesLite

class TelegramGateway:
    def __init__(self, bot_token: str, agent: HermesLite):
        self.bot_token = bot_token
        self.agent = agent
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
        self.last_update_id = 0

    def send_message(self, chat_id: int, text: str):
        """Send a message to a Telegram chat"""
        url = f"{self.api_url}/sendMessage"
        payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
        try:
            requests.post(url, json=payload, timeout=10)
        except Exception as e:
            print(f"Error sending message: {e}")

    def poll_updates(self):
        """Poll for new messages from Telegram"""
        url = f"{self.api_url}/getUpdates"
        params = {"offset": self.last_update_id + 1, "timeout": 30}
        
        try:
            response = requests.get(url, params=params, timeout=35)
            response.raise_for_status()
            updates = response.json().get("result", [])
            
            for update in updates:
                self.last_update_id = update["update_id"]
                if "message" in update and "text" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    user_text = update["message"]["text"]
                    
                    # Send "Typing..." action
                    self.send_action(chat_id)
                    
                    # Get response from Hermes Lite agent
                    response_text = self.agent.chat(user_text)
                    self.send_message(chat_id, response_text)
                    
        except Exception as e:
            print(f"Polling error: {e}")

    def send_action(self, chat_id: int):
        """Send typing action to let user know agent is thinking"""
        url = f"{self.api_url}/sendChatAction"
        payload = {"chat_id": chat_id, "action": "typing"}
        try:
            requests.post(url, json=payload, timeout=5)
        except:
            pass

def run_telegram_bot():
    import argparse
    parser = argparse.ArgumentParser(description="Hermes Lite Telegram Bot Gateway")
    parser.add_argument("--token", help="Telegram Bot Token from BotFather")
    parser.add_argument("--model", default="openai/gpt-4o-mini", help="OpenRouter model")
    args = parser.parse_args()

    token = args.token or os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Error: Telegram Bot Token is required!")
        print("Use --token YOUR_TOKEN or set TELEGRAM_BOT_TOKEN env var")
        return

    # Initialize Agent
    try:
        from hermes_lite.core import HermesLite
        agent = HermesLite(model=args.model)
    except Exception as e:
        print(f"Agent init error: {e}")
        return

    gateway = TelegramGateway(token, agent)
    print(f"🚀 Hermes Lite Bot started! Polling messages...")
    
    while True:
        gateway.poll_updates()

if __name__ == "__main__":
    run_telegram_bot()
