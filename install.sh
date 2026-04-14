#!/bin/bash
# ============================================================================
# Hermes Lite Installer Script (V6 - Zero Dependency Edition)
# ============================================================================
# No Git needed. Downloads source files directly via GitHub API.
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
echo "    V6 - Zero Dependency Edition"
echo "====================================================================="
echo -e "${NC}"

# 1. Ensure Pip is installed
echo -e "\n${BLUE}Step 1: Verifying Python Pip...${NC}"
if ! python3 -m pip --version &> /dev/null; then
    echo -e "${YELLOW}Pip not found. Attempting to install...${NC}"
    if python3 -m ensurepip --upgrade 2>/dev/null; then
        echo "✅ Pip installed via ensurepip"
    else
        curl -sSL https://bootstrap.pypa.io/get-pip.py -o get-pip.py
        python3 get-pip.py --break-system-packages || python3 get-pip.py
        rm get-pip.py
        echo "✅ Pip installed via get-pip.py"
    fi
fi

# 2. Setup Directories
INSTALL_DIR="$HOME/hermes-lite"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

echo -e "\n${BLUE}Step 2: Setting up directories...${NC}"
mkdir -p "$HOME/.hermes-lite/data"
mkdir -p "$HOME/.hermes-lite/skills"

# 3. Download Source Code via API (Gittless Method)
echo -e "\n${BLUE}Step 3: Downloading Hermes Lite source code...${NC}"
mkdir -p "hermes_lite"

# List of files to download from the repo
FILES=(
    "hermes_lite/core.py"
    "hermes_lite/memory.py"
    "hermes_lite/skills.py"
    "hermes_lite/telegram_gateway.py"
)

for FILE in "${FILES[@]}"; do
    echo -n "Downloading $FILE... "
    URL="https://raw.githubusercontent.com-ykewat354-cyber/hermes-lite/main/$FILE"
    # Since raw.githubusercontent is standard, we use it
    URL="https://raw.githubusercontent.com/ykewat354-cyber/hermes-lite/main/$FILE"
    curl -sSL "$URL" -o "$FILE"
    if [ -s "$FILE" ]; then
        echo "✅"
    else
        echo -e "${RED}❌ Failed${NC}"
        exit 1
    fi
done

# 4. Install Dependencies
echo -e "\n${BLUE}Step 4: Installing required packages...${NC}"
if python3 -m pip install requests --break-system-packages 2>/dev/null; then
    echo "✅ Requests installed successfully"
elif python3 -m pip install requests 2>/dev/null; then
    echo "✅ Requests installed successfully"
else
    echo -e "${RED}❌ Failed to install requests. Try: apt install python3-requests${NC}"
    exit 1
fi

# 5. Configuration
echo -e "\n${BLUE}Step 5: Creating configuration...${NC}"
cat <<EOF > "$INSTALL_DIR/config.yaml"
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

# 6. Create the Execution Command
echo -e "\n${BLUE}Step 6: Creating hermes-lite command...${NC}"
cat <<'EOF' > "$INSTALL_DIR/hermes-lite"
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "Error: OPENROUTER_API_KEY not set!"
    echo "Get a free key from: https://openrouter.ai/keys"
    echo "Set it with: export OPENROUTER_API_KEY=your_key"
    exit 1
fi

python3 -c "
import sys
import os
sys.path.insert(0, '$SCRIPT_DIR')
try:
    from hermes_lite.core import HermesLite
except ImportError:
    print('Error: Core files missing. Please re-run install.sh')
    sys.exit(1)

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

# 7. Path Setup
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$HOME/.bashrc"
    echo -e "${YELLOW}Please run: source ~/.bashrc${NC}"
fi

echo -e "\n${GREEN}====================================================================="
echo "    Hermes Lite Installation Complete! (V6 - Zero Dependency)"
echo "====================================================================="
echo -e "${NC}"
echo -e "${GREEN}Final Steps:${NC}"
echo "1. Set your key: export OPENROUTER_API_KEY='your_key'"
echo "2. Load path: source ~/.bashrc"
echo "3. Launch: hermes-lite"
echo ""
echo -e "${GREEN}Happy coding, bhai! 🚀${NC}"
