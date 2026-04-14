#!/bin/bash
# ============================================================================
# Hermes Lite Installer Script
# ============================================================================
# Ultra-lightweight AI agent installer for Termux/Ubuntu
# Sets up Hermes Lite with cloud model support (OpenRouter)
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "====================================================================="
echo "    Hermes Lite Installer - Ultra-lightweight AI Agent"
echo "    Designed for Termux/Ubuntu with Cloud Model Support"
echo "====================================================================="
echo -e "${NC}"

# Detect if we're in Termux
IS_TERMUX=false
if [ -n "$TERMUX_VERSION" ] || [ -d "/data/data/com.termux" ]; then
    IS_TERMUX=true
    echo -e "${YELLOW}Detected Termux environment${NC}"
else
    echo -e "${BLUE}Detected standard Linux environment${NC}"
fi

# Create installation directory
INSTALL_DIR="$HOME/hermes-lite"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

echo -e "\n${BLUE}Setting up Hermes Lite...${NC}"

# Create virtual environment (always use python3 -m venv for consistency)
echo -e "${BLUE}Creating Python virtual environment...${NC}"
python3 -m venv venv

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip using python3 -m pip (more robust in venvs)
echo -e "${BLUE}Upgrading pip...${NC}"
python3 -m pip install --upgrade pip

# Install required packages using python3 -m pip
echo -e "${BLUE}Installing required packages...${NC}"
python3 -m pip install requests

# Create data directory for memory
echo -e "${BLUE}Setting up memory system...${NC}"
mkdir -p "$HOME/.hermes-lite/data"

# Create skills directory
echo -e "${BLUE}Setting up skills directory...${NC}"
mkdir -p "$HOME/.hermes-lite/skills"

# Create a basic configuration file
echo -e "${BLUE}Creating configuration...${NC}"
cat > "$INSTALL_DIR/config.yaml" << EOF
# Hermes Lite Configuration
model: "openai/gpt-4o-mini"  # Default model - change as needed
max_history_tokens: 1000
response_max_tokens: 150
temperature: 0.7
top_p: 0.9

# Paths
data_dir: "$HOME/.hermes-lite/data"
skills_dir: "$HOME/.hermes-lite/skills"

# OpenRouter settings (get free key at https://openrouter.ai/keys)
# Set OPENROUTER_API_KEY environment variable or uncomment below:
# openrouter_api_key: "your-key-here"
site_url: "https://hermes-lite.local"
site_name: "Hermes Lite"
EOF

# Create the hermes-lite command script
echo -e "${BLUE}Creating hermes-lite command...${NC}"
cat > "$INSTALL_DIR/hermes-lite" << 'EOF'
#!/bin/bash
# Hermes Lite Command Script
# Ultra-lightweight AI agent with cloud model support

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

# Activate virtual environment
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
else
    echo "Error: Virtual environment not found at $VENV_DIR/bin/activate"
    exit 1
fi

# Check if API key is set
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "Error: OPENROUTER_API_KEY environment variable not set"
    echo "Please get a free API key from: https://openrouter.ai/keys"
    echo "Then set it with: export OPENROUTER_API_KEY=your_key_here"
    echo "Or add it to your shell profile (~/.bashrc, ~/.zshrc, etc.)"
    exit 1
fi

# Run Hermes Lite
python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from hermes_lite.core import HermesLite
import os

# Get configuration
model = os.getenv('HERMES_LITE_MODEL', 'openai/gpt-4o-mini')
site_url = os.getenv('HERMES_LITE_SITE_URL', 'https://hermes-lite.local')
site_name = os.getenv('HERMES_LITE_SITE_NAME', 'Hermes Lite')

# Create agent instance
agent = HermesLite(
    model=model,
    api_key=os.getenv('OPENROUTER_API_KEY'),
    site_url=site_url,
    site_name=site_name
)

# Simple CLI interface
if [ \$# -eq 0 ]; then
    # Interactive mode
    echo 'Hermes Lite ready! Type \"exit\" to quit.'
    echo 'Tips: Short responses by default, type \"detail do\" for more info'
    echo ''
    while true; do
        read -p '> ' user_input
        if [[ \$user_input =~ ^(exit|quit|bye)$ ]]; then\n            echo 'Alvida bhai! Phir milenge.'
            break
        fi
        if [ -z \"\$user_input\" ]; then
            continue
        fi
        response=\$(agent.chat \"\$user_input\")
        echo \"\$response\"
        echo ''
    done
else
    # Single command mode
    prompt=\"\$*\"
    response=\$(agent.chat \"\$prompt\")
    echo \"\$response\"
fi
"
EOF

# Make the script executable
chmod +x "$INSTALL_DIR/hermes-lite"

# Add to PATH if not already there
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo -e "\n${BLUE}Adding Hermes Lite to your PATH...${NC}"
    echo '' >> "$HOME/.bashrc"
    echo '# Hermes Lite - Ultra-lightweight AI agent' >> "$HOME/.bashrc"
    echo "export PATH=\"\$INSTALL_DIR:\$PATH\"" >> "$HOME/.bashrc"
    echo '' >> "$HOME/.zshrc" 2>/dev/null || true
    echo '# Hermes Lite - Ultra-lightweight AI agent' >> "$HOME/.zshrc" 2>/dev/null || true\n    echo "export PATH=\"\$INSTALL_DIR:\$PATH\"" >> "$HOME/.zshrc" 2>/dev/null || true
    
    echo -e "${YELLOW}Please restart your terminal or run: source ~/.bashrc${NC}"
fi

# Create a simple test script
echo -e "${BLUE}Creating test script...${NC}"
cat > "$INSTALL_DIR/test_hermes_lite.sh" << 'EOF'
#!/bin/bash
# Test script for Hermes Lite

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/venv/bin/activate"

echo "Testing Hermes Lite..."
echo "Make sure OPENROUTER_API_KEY is set in your environment"

# Test import
python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
try:
    from hermes_lite.core import HermesLite\n    print('✅ HermesLite core imported successfully')
except Exception as e:
    print(f'❌ Failed to import HermesLite: {e}')
    sys.exit(1)

try:
    from hermes_lite.memory import MemorySystem
    print('✅ MemorySystem imported successfully')
except Exception as e:
    print(f'❌ Failed to import MemorySystem: {e}')
    sys.exit(1)

try:
    from hermes_lite.skills import skill_manager
    skills = skill_manager.list_skills()
    print('✅ SkillManager loaded ' + str(len(skills)) + ' skills: ' + ', '.join(skills))
except Exception as e:
    print(f'❌ Failed to load skills: {e}')
    sys.exit(1)

print('')
print('All tests passed! Hermes Lite is ready to use.')
echo 'Get your free API key from: https://openrouter.ai/keys'
echo 'Then set: export OPENROUTER_API_KEY=your_key_here'
"

EOF

chmod +x "$INSTALL_DIR/test_hermes_lite.sh"

# Final instructions
echo -e "\n${GREEN}"
echo "====================================================================="
echo "    Hermes Lite Installation Complete!"
echo "====================================================================="
echo -e "${NC}"
echo -e "${GREEN}Next steps:${NC}"
echo "1. Get a free API key from: https://openrouter.ai/keys"
echo "2. Set your API key:"
echo "   export OPENROUTER_API_KEY='your-key-here'"
echo "3. Add to your shell profile for permanence:"
echo "   echo 'export OPENROUTER_API_KEY=your-key-here' >> ~/.bashrc"
echo "4. Restart your terminal or run: source ~/.bashrc"
echo "5. Start Hermes Lite:"
echo "   hermes-lite"
echo "   OR"
echo "   $INSTALL_DIR/hermes-lite"
echo ""
echo -e "${YELLOW}To test the installation:${NC}"
echo "   $INSTALL_DIR/test_hermes_lite.sh"
echo ""
echo -e "${BLUE}Features:${NC}"
echo "  • Ultra-lightweight design (~10MB RAM)"
echo "  • Cloud model support (OpenRouter)"
echo "  • Hinglish-friendly responses"
echo "  • Permanent memory (SQLite)"
echo "  • Skill-based extensibility"
echo "  • Token-optimized for mobile usage"
echo ""
echo -e "${BLUE}Available skills:${NC}"
echo "  • web_search - Search the web (DuckDuckGo lite)"
echo "  • file_ops - File operations (read/write/delete)"
echo "  • system_info - System information"
echo "  • calculator - Mathematical expressions"
echo "  • translator - English <> Hinglish"
echo "  • full_stack_dev - Professional development workflow"
echo ""
echo -e "${GREEN}Happy coding, bhai! 🚀${NC}"
echo "====================================================================="