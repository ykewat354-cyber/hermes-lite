#!/usr/bin/env python3
"""
Hermes Lite Core - Ultra-lightweight AI agent using cloud models (OpenRouter)
Optimized for token efficiency, hinglish-friendly, terminal-first design
"""

import json
import os
import sys
import requests
from typing import List, Dict, Optional, Generator
from datetime import datetime

class HermesLite:
    def __init__(self, model: str = "openai/gpt-4o-mini", api_key: str = None, 
                 site_url: str = "https://hermes-lite.local", site_name: str = "Hermes Lite"):
        """
        Initialize Hermes Lite with cloud model support
        
        Args:
            model: Model identifier (e.g., "openai/gpt-4o-mini", "anthropic/claude-3-haiku")
            api_key: OpenRouter API key (can also be set via OPENROUTER_API_KEY env var)
            site_url: Your site URL for OpenRouter rankings (optional)
            site_name: Your site name for OpenRouter rankings (optional)
        """
        self.model = model
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key required. Set OPENROUTER_API_KEY env var or pass api_key parameter.")
        
        self.site_url = site_url
        self.site_name = site_name
        self.conversation_history: List[Dict] = []
        self.max_history_tokens = 1000  # Keep context window small for efficiency
        self.system_prompt = """You are Hermes Lite, a helpful and witty AI assistant who speaks Hinglish casually like a close friend. 
Be concise by default - short sentences, minimal fluff. 
Only give detail if user asks for explanation or says 'detail do'. 
Use humor, emojis occasionally, and keep it chatty like yaar ki baat."""
        
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        # Optional headers for OpenRouter rankings
        if self.site_url:
            self.headers["HTTP-Referer"] = self.site_url
        if self.site_name:
            self.headers["X-Title"] = self.site_name
    
    def _count_tokens(self, text: str) -> int:
        """Rough token estimation - 4 chars per token average"""
        return len(text) // 4
    
    def _truncate_history(self):
        """Keep conversation history within token limit"""
        if not self.conversation_history:
            return
            
        total_tokens = sum(self._count_tokens(msg["content"]) for msg in self.conversation_history)
        
        while total_tokens > self.max_history_tokens and len(self.conversation_history) > 1:
            # Remove oldest exchange (user + assistant pair)
            removed = self.conversation_history.pop(0)
            total_tokens -= self._count_tokens(removed["content"])
    
    def chat(self, user_input: str, stream: bool = False) -> str:
        """Main chat function - sends query to OpenRouter and returns response"""
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_input})
        self._truncate_history()
        
        # Prepare messages for OpenRouter
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.conversation_history)
        
        # OpenRouter API payload (similar to OpenAI format)
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 150  # Limit response length for token efficiency
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=self.headers,
                stream=stream,
                timeout=30
            )
            response.raise_for_status()
            
            if stream:
                return self._handle_stream_response(response)
            else:
                result = response.json()
                assistant_response = result["choices"][0]["message"]["content"]
                
                # Add assistant response to history
                self.conversation_history.append({"role": "assistant", "content": assistant_response})
                self._truncate_history()
                
                return assistant_response
                
        except requests.exceptions.RequestException as e:
            return f"Arre bhai, connection error ho gaya: {str(e)}. Internet connection aur API key check karo?"
        except (KeyError, IndexError) as e:
            return f"Arre bhai, API response format samajh nahi aaya: {str(e)}"
    
    def _handle_stream_response(self, response) -> str:
        """Handle streaming response from OpenRouter"""
        full_response = ""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    if "choices" in data and len(data["choices"]) > 0:
                        delta = data["choices"][0].get("delta", {})
                        if "content" in delta:
                            content = delta["content"]
                            full_response += content
                            # Print token by token for streaming effect
                            print(content, end="", flush=True)
                    if data.get("choices", [{}])[0].get("finish_reason") is not None:
                        break
                except json.JSONDecodeError:
                    continue
        
        print()  # New line after streaming
        # Add to history
        self.conversation_history.append({"role": "assistant", "content": full_response})
        self._truncate_history()
        return full_response
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        return "History clear kar diya bhai! Naya shuru karte hain."
    
    def get_history(self) -> List[Dict]:
        """Get conversation history"""
        return self.conversation_history.copy()

def main():
    """Simple CLI interface for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Hermes Lite - Your personal AI assistant (Cloud Models)")
    parser.add_argument("--model", default="openai/gpt-4o-mini", help="Model to use (e.g., openai/gpt-4o-mini, anthropic/claude-3-haiku)")
    parser.add_argument("--api-key", help="OpenRouter API key (can also use OPENROUTER_API_KEY env var)")
    parser.add_argument("--site-url", default="https://hermes-lite.local", help="Your site URL for rankings")
    parser.add_argument("--site-name", default="Hermes Lite", help="Your site name for rankings")
    parser.add_argument("--prompt", help="Direct prompt to send")
    parser.add_argument("--stream", action="store_true", help="Stream response")
    
    args = parser.parse_args()
    
    try:
        agent = HermesLite(
            model=args.model,
            api_key=args.api_key,
            site_url=args.site_url,
            site_name=args.site_name
        )
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set OPENROUTER_API_KEY environment variable or use --api-key argument")
        sys.exit(1)
    
    if args.prompt:
        response = agent.chat(args.prompt, stream=args.stream)
        if not args.stream:
            print(response)
    else:
        print("Hermes Lite ready! Type 'exit' to quit.")
        print("Tips: Short responses by default, type 'detail do' for more info\n")
        print("Get your free API key from: https://openrouter.ai/keys\n")
        
        while True:
            try:
                user_input = input("> ").strip()
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("Alvida bhai! Phir milenge.")
                    break
                if not user_input:
                    continue
                    
                response = agent.chat(user_input, stream=args.stream)
                if not args.stream:
                    print(f"\n{response}\n")
                    
            except KeyboardInterrupt:
                print("\nAlvida bhai! Phir milenge.")
                break

if __name__ == "__main__":
    main()