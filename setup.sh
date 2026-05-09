#!/bin/bash
# Setup script for Farmer Assistant on Raspberry Pi

set -e

echo "========================================="
echo "Farmer Assistant - Raspberry Pi Setup"
echo "========================================="

# Check if running on Raspberry Pi
if [[ ! -f /proc/device-tree/model ]]; then
    echo "Warning: Not running on Raspberry Pi. Some features may not work."
fi

# Update system
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    portaudio19-dev \
    libatlas-base-dev \
    libjasper-dev \
    libtiff5 \
    libharfbuzz0b \
    libwebp6 \
    i2c-tools \
    python3-smbus \
    git

# Enable I2C
echo "Enabling I2C interface..."
sudo raspi-config nonint do_i2c 0

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Ollama
echo "Installing Ollama..."
curl https://ollama.ai/install.sh | sh

# Enable Ollama service
echo "Enabling Ollama service..."
sudo systemctl enable ollama
sudo systemctl start ollama

# Wait for Ollama to start
echo "Waiting for Ollama to start..."
sleep 5

# Pull Phi3 model
echo "Pulling Phi3 model (this may take a few minutes)..."
ollama pull phi3

# Create data directories
echo "Creating data directories..."
mkdir -p data/audio
mkdir -p data/knowledge_base
mkdir -p logs

# Copy configuration files
echo "Setting up configuration files..."
cp config.example.json config.json
cp .env.example .env

echo "========================================="
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit config.json for your settings"
echo "2. Connect microphone and LCD display"
echo "3. Run: python main.py --mode demo"
echo "4. For interactive mode: python main.py"
echo "========================================="
