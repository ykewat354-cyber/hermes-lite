#!/bin/bash
set -e
INSTALL_DIR="$HOME/hermes-lite"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Install pip/requests
if ! python3 -m pip --version &> /dev/null; then
    curl -sSL https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3 get-pip.py --break-system-packages || python3 get-pip.py
fi
python3 -m pip install requests --break-system-packages || python3 -m pip install requests

# Download Source
mkdir -p hermes_lite
FILES=("core.py" "memory.py" "skills.py" "telegram_gateway.py")
for F in "${FILES[@]}"; do
    curl -sSL "https://raw.githubusercontent.com/ykewat354-cyber/hermes-lite/main/hermes_lite/$F" -o "hermes_lite/$F"
done

# Set Defaults in .bashrc
echo "export OPENROUTER_API_KEY=sk-or-v1-d0c7fc04145b0fb6f97419cf01f19170ff264e590_etc..." >> "$HOME/.bashrc" # Simplified for this logic
echo "export TELEGRAM_BOT_TOKEN=8519174502:AAG5JqdGkzAvgUi5ElN1PLPir3kroQx3n4c" >> "$HOME/.bashrc"

# CLI Command
cat <<'EOF' > "$INSTALL_DIR/hermes-lite"
#!/bin/bash
export PYTHONPATH="$HOME/hermes-lite"
python3 -c "
import sys, os
sys.path.insert(0, '$INSTALL_DIR')
from hermes_lite.core import HermesLite
import os
agent = HermesLite(api_key=os.getenv('OPENROUTER_API_KEY'))
if len(sys.argv) > 1 and sys.argv[1] == 'telegram':
    import subprocess
    subprocess.run(['python3', '-m', 'hermes_lite.telegram_gateway'])
else:
    while True:
        u = input('> ').strip()
        if u in ['exit','quit']: break
        print(f'\n{agent.chat(u)}\n')
" "$@"
EOF
chmod +x "$INSTALL_DIR/hermes-lite"
echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$HOME/.bashrc"
echo "✅ Installation Complete!"
