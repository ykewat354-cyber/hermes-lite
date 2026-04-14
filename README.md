# 🚀 Hermes Lite
**The ultra-lightweight, token-optimized AI agent designed for the mobile era.**

[![Platform: Termux/Ubuntu](https://img.shields.io/badge/Platform-Termux%2FUbuntu-blue)](https://github.com/{USERNAME}/{REPO_NAME})
[![Model: OpenRouter](https://img.shields.io/badge/Model-OpenRouter-green)](https://openrouter.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](https://opensource.org/licenses/MIT)

---

## 🌟 What is Hermes Lite?
Hermes Lite is not just another bot; it's a highly efficient AI companion built specifically to run on resource-constrained devices like Android phones (via Termux). It speaks **Hinglish**, remembers your preferences forever, and can be controlled both from the terminal and Telegram.

### ⚡ Key Highlights
- **🔋 Ultra-Efficient**: Consumes ~10MB RAM. No heavy overhead.
- **🗣️ Hinglish Native**: Converses like a friend ("yaar" vibe).
- **🧠 Permanent Memory**: Powered by SQLite to keep track of your history across sessions.
- **🛠️ Skill-Based**: Modular architecture. Add new capabilities as lightweight plugins.
- **📱 Telegram Integrated**: Turn your agent into a bot with one command.

---

## 🛠️ Quick Installation

One command to rule them all. Run this in your Termux or Ubuntu terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/ykewat354-cyber/hermes-lite/main/install.sh | bash
```

### ⚙️ Post-Installation Setup
1. **Get an API Key**: Get a free key from [OpenRouter](https://openrouter.ai/keys).
2. **Configure Key**:
   ```bash
   export OPENROUTER_API_KEY='your_key_here'
   # To make it permanent:
   echo 'export OPENROUTER_API_KEY=your_key_here' >> ~/.bashrc
   source ~/.bashrc
   ```

---

## 🎮 How to Use

### 1. Interactive Chat
```bash
hermes-lite
```
*Tip: Type `detail do` if you want a detailed explanation instead of a concise answer.*

### 2. Telegram Bot Mode
```bash
export TELEGRAM_BOT_TOKEN='your_bot_token_from_botfather'
hermes-lite telegram
```

### 3. Manage Skills
```bash
hermes-lite list-skills
```

---

## 🛠️ Built-in Skills

| Skill | Capability | Description |
| :--- | :--- | :--- |
| `web_search` | 🌐 Search | Lightweight web scraping via DuckDuckGo Lite. |
| `file_ops` | 📂 Files | Read, write, delete, and manage local files. |
| `full_stack_dev`| 💻 Coding | Senior Architect workflow: Plan $ightarrow$ Implement $ightarrow$ Test $ightarrow$ Deploy. |
| `system_info` | 💻 System | Real-time hardware and OS diagnostic info. |
| `calculator` | 🔢 Math | High-precision mathematical expression evaluation. |
| `translator` | 🗣️ Lang | Quick English $\leftrightarrow$ Hinglish translation. |

---

## 📂 Folder Structure
```text
hermes-lite/
├── install.sh             # The magic installer
├── hermes_lite/           # Core Source Code
│   ├── core.py            # AI Logic & OpenRouter Integration
│   ├── memory.py          # SQLite Permanent Memory
│   ├── skills.py          # Skill Management Engine
│   ├── telegram_gateway.py# Telegram Bot Integration
│   └── skills/            # Custom Skill Plugins
└── README.md              # Documentation
```

---

## 🤝 Contributing
Feel free to fork this repo and add your own skills! Just drop a `.py` file in the `skills/` folder, and Hermes will automatically discover it.

**Created with ❤️ by [ykewat354-cyber](https://github.com/ykewat354-cyber)**
