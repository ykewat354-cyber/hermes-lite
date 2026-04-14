#!/bin/bash
# ============================================================================
# Hermes Lite Installer Script (V2 - No Venv Edition)
# ============================================================================
# Ultra-lightweight AI agent installer for Termux/Ubuntu
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "====================================================================="
echo "    Hermes Lite Installer - Ultra-lightweight AI Agent"
echo "    Direct Installation Mode (No-Venv)"
echo "====================================================================="
echo -e "${NC}"

# Installation directory
INSTALL_DIR="$HOME/hermes-lite"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

echo -e "\n${BLUE}Setting up Hermes Lite...${NC}"

# Install dependencies globally
echo -e "${BLUE}Installing required packages...${NC}"
# Handle PEP 668 (externally-managed-environment) error for newer Ubuntu/Debian
if python3 -m pip install requests 2>/dev/null; then
    echo "✅ Requests installed successfully"
else
    echo -e "${YELLOW}Using --break-system-packages flag for system install...${NC}"
    python3 -m pip install requests --break-system-packages
fi

# Create data and skills directories
echo -e "${BLUE}Setting up system directories...${NC}"
mkdir -p "$HOME/.hermes-lite/data"
mkdir -p "$HOME/.hermes-lite/skills"

# Create configuration
echo -e "${BLUE}Creating configuration...${NC}"
cat > "$INSTALL_DIR/config.yaml" << EOF
model: "openai/gpt-4o-mini"
max_history_tokens: 1000
response_max_tokens: 150
temperature: 0.7
top_p: 0.9
data_dir: "$HOME/.hermes-lite/data"
skills_dir: "$HOME/.hermes-lite/skills"
site_url: "https://hermes-lite.local"
site_name: "Hermes Lite"
EOF

# Create the hermes-lite command script
echo -e "${BLUE}Creating hermes-lite command...${NC}"
cat > "$INSTALL_DIR/hermes-lite" << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if API key is set
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "Error: OPENROUTER_API_KEY environment variable not set"
    echo "Please get a free API key from: https://openrouter.ai/keys"
    echo "Then set it with: export OPENROUTER_API_KEY=your_key_here"
    exit 1
fi

python3 -c "
import sys
import os
sys.path.insert(0, '$SCRIPT_DIR')
from hermes_lite.core import HermesLite

model = os.getenv('HERMES_LITE_MODEL', 'openai/gpt-4o-mini')
agent = HermesLite(
    model=model,
    api_key=os.getenv('OPENROUTER_API_KEY'),
    site_url='https://hermes-lite.local',
    site_name='Hermes Lite'
)

if len(sys.argv) > 1:
    cmd = sys.argv[1].lower()
    if cmd == 'telegram':
        import subprocess
        subprocess.run(['python3', '-m', 'hermes_lite.telegram_gateway'])
        sys.exit(0)
    elif cmd == 'list-skills':
        from hermes_lite.skills import skill_manager
        print('Available Skills:', skill_manager.list_skills())
        sys.exit(0)

print('Hermes Lite ready! Type \"exit\" to quit.')
while True:
    try:
        user_input = input('> ').strip()
        if user_input.lower() in ['exit', 'quit', 'bye']: break
        if not user_input: continue
        print(f'\n{agent.chat(user_input)}\n')
    except KeyboardInterrupt: break
" "$@"
EOF

chmod +x "$INSTALL_DIR/hermes-lite"

# Add to PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$HOME/.bashrc"
    echo -e "${YELLOW}Please run: source ~/.bashrc${NC}"
fi

echo -e "\n${GREEN}====================================================================="
echo "    Hermes Lite Installation Complete! (V2 - No Venv)"
echo "====================================================================="
echo -e "${NC}"
echo -e "${GREEN}Next steps:${NC}"
echo "1. Set your API key: export OPENROUTER_API_KEY='your-key-here'"
echo "2. Restart terminal: source ~/.bashrc"
echo "3. Start: hermes-lite"
echo ""
echo -e "${GREEN}Happy coding, bhai! 🚀${NC}"
