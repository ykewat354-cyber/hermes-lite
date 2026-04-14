#!/usr/bin/env python3
import sys
import os
from hermes_lite.core import HermesLite
from hermes_lite.skills import skill_manager

def main():
    # Load config from env or defaults
    model = os.getenv('HERMES_LITE_MODEL', 'openai/gpt-4o-mini')
    api_key = os.getenv('OPENROUTER_API_KEY')
    
    if not api_key:
        print("Error: OPENROUTER_API_KEY not set!")
        sys.exit(1)

    # Initialize Agent
    try:
        agent = HermesLite(model=model, api_key=api_key)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "telegram":
            print("Starting Telegram Gateway...")
            import subprocess
            # Run the gateway separately
            subprocess.run(["python3", "-m", "hermes_lite.telegram_gateway"])
            return
        
        elif command == "list-skills":
            print("Available Skills:", skill_manager.list_skills())
            return
        
        elif command == "test":
            print("Running basic test...")
            print(agent.chat("Hi, are you working?"))
            return

    # Default Interactive Mode
    print("Hermes Lite ready! Type 'exit' to quit.")
    print("Tips: 'detail do' for more info | Use 'hermes-lite telegram' for Bot mode\n")
    
    while True:
        try:
            user_input = input("> ").strip()
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("Alvida bhai! Phir milenge.")
                break
            if not user_input:
                continue
            print(f"\n{agent.chat(user_input)}\n")
        except KeyboardInterrupt:
            print("\nAlvida bhai!")
            break

if __name__ == "__main__":
    main()
