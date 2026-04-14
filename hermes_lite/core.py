#!/usr/bin/env python3
import json
import os
import requests
from typing import List, Dict, Optional
from datetime import datetime

class HermesLite:
    def __init__(self, model: str = "openai/gpt-4o-mini", api_key: str = None):
        self.model = model
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.conversation_history = []
        self.max_history_tokens = 2000
        self.system_prompt = "You are Hermes Lite, a powerful AI agent with full system access. You speak Hinglish casually. You can use tools like web_search, file_ops, etc. Be concise but helpful. Use emojis and 'yaar' vibe."
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

    def update_api_key(self, new_key: str):
        self.api_key = new_key
        return "✅ API Key updated successfully, bhai!"

    def chat(self, user_input: str) -> str:
        if not self.api_key:
            return "Error: API Key missing! Please use /set-key <key>"
        
        self.conversation_history.append({"role": "user", "content": user_input})
        
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.conversation_history[-10:]) # Context window
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        try:
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            res = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            res.raise_for_status()
            reply = res.json()["choices"][0]["message"]["content"]
            self.conversation_history.append({"role": "assistant", "content": reply})
            return reply
        except Exception as e:
            return f"Bhai, error aa gaya: {str(e)}"
