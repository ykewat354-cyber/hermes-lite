#!/usr/bin/env python3
import json
import os
import requests
from typing import List, Dict, Optional
from pathlib import Path

class HermesLite:
    def __init__(self, model: str = "openai/gpt-4o-mini", api_key: str = None):
        self.model = model
        self.config_path = Path.home() / ".hermes-lite" / "config.json"
        self.api_key = self._load_key(api_key)
        self.conversation_history = []
        self.max_history_tokens = 2000
        self.system_prompt = "You are Hermes Lite, a powerful AI agent with full system access. You speak Hinglish casually. You can use tools like web_search, file_ops, etc. Be concise but helpful. Use emojis and 'yaar' vibe."
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

    def _load_key(self, provided_key):
        # Priority: Provided Arg > Config File > Environment Variable
        if provided_key:
            return provided_key
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    if "api_key" in data:
                        return data["api_key"]
            except:
                pass
                
        return os.getenv("OPENROUTER_API_KEY")

    def update_api_key(self, new_key: str):
        self.api_key = new_key
        # Save permanently to config.json
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            config = {}
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
            
            config["api_key"] = new_key
            with open(self.config_path, 'w') as f:
                json.dump(config, f)
            return "✅ API Key updated and saved permanently, bhai!"
        except Exception as e:
            return f"Key updated in session, but save failed: {e}"

    def chat(self, user_input: str) -> str:
        if not self.api_key:
            return "Error: API Key missing! Please use /set-key <<keykey>"
        
        self.conversation_history.append({"role": "user", "content": user_input})
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.conversation_history[-10:])
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        try:
            # FORCE use the current self.api_key
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            res = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            res.raise_for_status()
            reply = res.json()["choices"][0]["message"]["content"]
            self.conversation_history.append({"role": "assistant", "content": reply})
            return reply
        except Exception as e:
            return f"Bhai, error aa gaya: {str(e)}"
