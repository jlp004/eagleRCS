if [ "$EUID" -ne 0 ]; then
  echo "Please run this script with sudo or as root."
  exit 1
fi

if !command -v python3 >/dev/null 2>&1; then
    if command -v apt &> /dev/null; then
        echo "Installing python3 through apt"
        apt update && apt install -y python3-venv
    elif command -v dnf &> /dev/null; then
        echo "Installing python3 through dnf"
        dnf install -y python3
    elif command -v pacman &> /dev/null; then
        echo "Installing python3 through pacman"
        pacman -S --noconfirm python3
    else
        echo "Python not installed; unknown package manager. Please install python3 manually"
        exit 1
    fi
fi

python3 -m venv .venv
source .venv/bin/activate
.venv/bin/pip install --upgrade pip
.venv/bin/pip install pyfhel

echo "Setup complete."
