# Installation Guide

## System Requirements

### Minimum (Demo Mode)
- Python 3.8+
- 4GB RAM
- 2GB free disk space
- Linux/macOS/Windows

### Recommended (Production on Raspberry Pi)
- Raspberry Pi 4B with 8GB RAM
- 64-bit Raspberry Pi OS (Bullseye or later)
- 16GB microSD card (minimum)
- 5V 3A power supply
- USB microphone
- 16x2 LCD I2C display (optional)
- Push button for GPIO input

## Installation Steps

### 1. System Prerequisites

#### On Raspberry Pi:
```bash
sudo apt-get update
sudo apt-get upgrade -y

# Install Python development tools
sudo apt-get install -y python3-dev python3-pip python3-venv

# Install audio libraries
sudo apt-get install -y portaudio19-dev
sudo apt-get install -y libatlas-base-dev libjasper-dev libtiff5
sudo apt-get install -y libharfbuzz0b libwebp6

# Install I2C tools (for LCD)
sudo apt-get install -y i2c-tools python3-smbus

# Enable I2C interface
sudo raspi-config nonint do_i2c 0

# Verify I2C
i2cdetect -y 1
```

#### On macOS:
```bash
brew install portaudio
brew install python3
```

#### On Windows:
- Download Python 3.8+ from python.org
- Install Visual C++ Build Tools
- Install portaudio: `choco install portaudio`

### 2. Clone Repository

```bash
git clone https://github.com/ThameemKing/Smart-Agriculture-Assisstant.git
cd Smart-Agriculture-Assisstant
```

### 3. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Install Ollama

#### On Raspberry Pi:
```bash
curl https://ollama.ai/install.sh | sh

# Start Ollama service
systemctl start ollama
systemctl enable ollama

# Pull Phi3 model (takes 5-10 minutes, ~2GB)
ollama pull phi3

# Test Ollama
curl http://localhost:11434/api/tags
```

#### On macOS:
```bash
brew install ollama
ollama serve &
ollama pull phi3
```

#### On Windows:
- Download from https://ollama.ai/download
- Run installer
- Open PowerShell and run:
  ```powershell
  ollama serve
  # In another terminal:
  ollama pull phi3
  ```

### 6. Configure Application

```bash
# Copy configuration templates
cp config.example.json config.json
cp .env.example .env

# Edit configuration (optional)
nano config.json
nano .env
```

### 7. Set Up Audio

#### Test Microphone:
```bash
# Record test audio
arecord -D plughw:1,0 -f cd test.wav

# Play back
aplay test.wav

# List available devices
arecord -l
```

#### Configure Audio Devices:
Edit `src/utils/config.py` to specify your audio device:
```python
AUDIO_DEVICE_INDEX = 1  # Change as needed
```

### 8. Set Up Hardware (Optional)

#### GPIO Button Setup:
```bash
# Wiring (GPIO 17):
# Button → GPIO 17
# Button GND → GND
# 10kΩ pull-up resistor recommended
```

#### LCD I2C Display Setup:
```bash
# Wiring:
# SDA → GPIO 2 (physical pin 3)
# SCL → GPIO 3 (physical pin 5)
# VCC → 5V (physical pin 2)
# GND → GND (physical pin 6)

# Scan I2C addresses to find LCD
i2cdetect -y 1

# Common address: 0x27 or 0x3F
```

### 9. Verify Installation

```bash
# Test Python imports
python3 -c "
from src.core.speech_processor import SpeechProcessor
from src.core.ai_engine import AIEngine
from src.core.knowledge_base import KnowledgeBase
print('✓ All core modules loaded successfully')
"

# Check Ollama
curl http://localhost:11434/api/tags

# Run demo
python3 main.py --mode demo
```

## Troubleshooting Installation

### Issue: "No module named 'RPi.GPIO'"
**Solution:** This is expected on non-Raspberry Pi systems. The app will run in software mode.

### Issue: "Ollama not responding"
**Solution:**
```bash
# Check if Ollama is running
systemctl status ollama

# Restart Ollama
systemctl restart ollama

# Or run manually
ollama serve
```

### Issue: "Microphone not detected"
**Solution:**
```bash
# List audio devices
arecord -l

# Test recording
arecord -D plughw:1,0 test.wav

# Update config with correct device index
```

### Issue: "LCD not detected"
**Solution:**
```bash
# Scan I2C bus
i2cdetect -y 1

# If no device found:
# 1. Check wiring
# 2. Verify I2C is enabled: raspi-config
# 3. Check power supply
```

### Issue: "Low disk space on Raspberry Pi"
**Solution:**
```bash
# Check disk usage
df -h

# Clean cache
sudo apt-get clean
pip cache purge

# Remove large files
rm -rf data/audio/*
```

## Post-Installation Setup

### Create Data Directories
```bash
mkdir -p data/audio
mkdir -p data/knowledge_base
mkdir -p logs
```

### Initialize Knowledge Base
```bash
python3 -c "
from src.core.knowledge_base import KnowledgeBase
from src.utils.config import Config

config = Config()
kb = KnowledgeBase(config)
print(f'Loaded {len(kb.documents)} documents')
"
```

### Add Custom Knowledge
Edit `data/knowledge_base/farming_knowledge.json` to add your own agricultural advice.

### Configure Auto-start (Optional)

Create `/etc/systemd/system/farmer-assistant.service`:
```ini
[Unit]
Description=Farmer Assistant Service
After=network.target ollama.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Smart-Agriculture-Assisstant
Environment="PATH=/home/pi/Smart-Agriculture-Assisstant/venv/bin"
ExecStart=/home/pi/Smart-Agriculture-Assisstant/venv/bin/python3 main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable farmer-assistant
sudo systemctl start farmer-assistant
```

## Performance Optimization

### For Raspberry Pi 4:

1. **Increase GPU Memory:**
   ```bash
   sudo raspi-config
   # Performance Options → GPU Memory → 256MB
   ```

2. **Disable Unnecessary Services:**
   ```bash
   sudo systemctl disable bluetooth
   sudo systemctl disable avahi-daemon
   ```

3. **Use SSD (Optional):**
   - For Pi 4 with USB 3.0 ports
   - Significantly faster than microSD

4. **Overclock (Advanced):**
   ```bash
   # Add to /boot/config.txt
   over_voltage=2
   arm_freq=1900
   ```

## Next Steps

1. Run demo: `python3 main.py --mode demo`
2. Test with hardware: `python3 main.py`
3. Read [Architecture Guide](ARCHITECTURE.md)
4. Check [API Documentation](API.md)
5. Explore [Troubleshooting](TROUBLESHOOTING.md)

---

For issues or questions, please open an issue on GitHub.
