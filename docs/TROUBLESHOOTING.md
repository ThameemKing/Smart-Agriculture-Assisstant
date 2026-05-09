# Troubleshooting Guide

## Common Issues & Solutions

### Installation Issues

#### "No module named 'RPi.GPIO'"

**Problem:** ImportError when running on non-Raspberry Pi

**Solution:**
- This is expected behavior
- App will run in software mode (no hardware)
- To test with hardware simulation, mock the module:

```python
import sys
from unittest.mock import MagicMock

sys.modules['RPi.GPIO'] = MagicMock()
```

---

#### "pip install fails with portaudio errors"

**Problem:** Cannot install PyAudio on Windows/Linux

**Linux Solution:**
```bash
sudo apt-get install portaudio19-dev python3-dev
pip install pyaudio
```

**macOS Solution:**
```bash
brew install portaudio
pip install pyaudio
```

**Windows Solution:**
```bash
pip install pipwin
pipwin install pyaudio
```

---

### Ollama Issues

#### "Cannot connect to Ollama"

**Problem:** `requests.exceptions.ConnectionError`

**Checklist:**
```bash
# 1. Is Ollama running?
ps aux | grep ollama

# 2. Is it listening on correct port?
netstat -tuln | grep 11434

# 3. Try connecting manually
curl http://localhost:11434/api/tags

# 4. Check Ollama logs
journalctl -u ollama -n 50
```

**Solutions:**
```bash
# Start Ollama service
systemctl start ollama

# Or run manually
ollama serve

# Restart if hanging
systemctl restart ollama
```

---

#### "Model 'phi3' not found"

**Problem:** Ollama returns model not found error

**Solution:**
```bash
# Pull the model (takes 5-10 minutes, ~2GB)
ollama pull phi3

# Verify it's loaded
ollama list

# Test the model
ollama run phi3 "What is farming?"
```

---

#### "Ollama responds slowly (60+ seconds)"

**Problem:** AI generation takes too long

**Causes & Solutions:**
1. **Insufficient RAM:**
   - Phi3 requires 2GB minimum
   - Check: `free -h`
   - Solution: Close other applications

2. **Slow disk:**
   - Check if running from microSD
   - Solution: Use SSD if available

3. **CPU throttling:**
   ```bash
   # Check CPU speed
   cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq
   
   # Disable throttling (careful!)
   echo performance | sudo tee /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
   ```

4. **Need performance upgrade:**
   - Use Pi 5 (2-3x faster)
   - Add Coral USB TPU (5-10x faster)
   - Use Jetson Nano (20x faster)

---

### Speech/Audio Issues

#### "Microphone not detected"

**Problem:** PyAudio cannot find microphone

**Debugging:**
```bash
# List audio devices
python3 << 'EOF'
import pyaudio
p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print(f"{i}: {info['name']} (in:{info['maxInputChannels']}, out:{info['maxOutputChannels']})")
EOF

# Also try:
arecord -l
aplay -l
```

**Solutions:**
```bash
# 1. Plug in USB microphone
# 2. Update ALSA config
sudo alsamixer  # Select correct device

# 3. Set default device in ~/.asoundrc
pcm.!default {
    type hw
    card 1
}
```

**Update config.py:**
```python
# Set correct device index
AUDIO_DEVICE_INDEX = 1  # Use device from list above
```

---

#### "Audio level too low"

**Problem:** Speech recognition fails with quiet audio

**Solutions:**
```bash
# Increase microphone gain
alsamixer
# Arrow up to increase input gain

# Test recording
arecord -D plughw:1,0 test.wav
aplay test.wav
```

---

#### "Whisper transcription fails"

**Problem:** Speech-to-text returns empty or gibberish

**Debugging:**
```python
# Test Whisper directly
import whisper

model = whisper.load_model("tiny")
result = model.transcribe("audio.wav", language="en")
print(result)
```

**Solutions:**
1. Check audio quality (16kHz, mono)
2. Ensure speech is clear enough
3. Check language setting
4. Try larger model: `whisper.load_model("base")`

---

#### "Text-to-speech not working"

**Problem:** No audio output or pyttsx3 error

**Debugging:**
```python
# Test TTS directly
import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.say("Test message")
engine.runAndWait()
```

**Solutions:**
```bash
# Check if speaker is working
aplay /usr/share/sounds/freedesktop/stereo/complete.oga

# Install espeak if not present
sudo apt-get install espeak

# List available voices
espeak --voices
```

---

### Hardware Issues

#### "GPIO button not responding"

**Problem:** Button presses not detected

**Debugging:**
```bash
# Check GPIO library
python3 -c "import RPi.GPIO; print('GPIO OK')"

# Test GPIO directly
python3 << 'EOF'
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)

print("Waiting for button on GPIO 17...")
while True:
    state = GPIO.input(17)
    print(f"Button state: {state}")
    time.sleep(0.1)
EOF
```

**Solutions:**
1. Check wiring (GPIO 17, GND)
2. Verify resistor (10kΩ pull-up)
3. Test with multimeter
4. Check GPIO permissions: `sudo usermod -a -G gpio pi`

---

#### "LCD I2C display not detected"

**Problem:** LCD doesn't show anything

**Debugging:**
```bash
# Scan I2C bus
i2cdetect -y 1

# Check if addresses 0x27 or 0x3F appear
# Example output:
#      0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
# 00:                         -- -- -- -- -- -- -- --
# 10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 20: -- -- -- -- -- -- -- 27 -- -- -- -- -- -- -- --
```

**Solutions:**
1. Check wiring (SDA, SCL, VCC, GND)
2. Enable I2C: `raspi-config → 3 Interface Options → I2C`
3. Verify power supply (5V)
4. Update LCD address in config if not 0x27

---

### Knowledge Base Issues

#### "Search returns no results"

**Problem:** TF-IDF search not finding relevant documents

**Debugging:**
```python
from src.core.knowledge_base import KnowledgeBase
from src.utils.config import Config

config = Config()
kb = KnowledgeBase(config)

# Check loaded documents
print(f"Documents: {len(kb.documents)}")
for doc in kb.documents:
    print(f"- {doc['topic']}")

# Test search
results = kb.search("tomato leaves yellow")
print(results)
```

**Solutions:**
1. Ensure documents are loaded
2. Add more farming knowledge
3. Lower similarity threshold in config
4. Use different search query

---

#### "Knowledge base file is corrupted"

**Problem:** JSON parsing error

**Solution:**
```bash
# Validate JSON
python3 << 'EOF'
import json

with open('data/knowledge_base/farming_knowledge.json', 'r') as f:
    try:
        data = json.load(f)
        print("JSON valid")
    except json.JSONDecodeError as e:
        print(f"Error: {e}")
EOF

# Restore from backup
cp data/knowledge_base/farming_knowledge.json.bak data/knowledge_base/farming_knowledge.json
```

---

### Performance Issues

#### "Application runs slowly"

**Diagnosis:**
```bash
# Check CPU usage
top -p $(pgrep -f main.py)

# Check memory
free -h
ps aux | grep main.py

# Check disk
df -h
```

**Solutions:**

1. **High CPU:** Normal during AI generation
2. **High Memory:** Close other processes
3. **Low Disk:** Clean up `data/audio/` and logs

---

#### "Frequent timeout errors"

**Problem:** Requests timing out

**Causes:**
- Ollama overloaded
- Insufficient RAM
- Slow disk access

**Solutions:**
```python
# Increase timeout in config.json
{
  "ai_timeout": 120,  # 120 seconds instead of 60
  "ollama_url": "http://localhost:11434"
}
```

---

### API Issues

#### "API server not responding"

**Problem:** Cannot connect to localhost:5000

**Debugging:**
```bash
# Check if API is running
ps aux | grep main.py

# Check port
netstat -tuln | grep 5000

# Try connecting
curl -v http://localhost:5000/health
```

**Solution:**
```bash
# Start API server
python main.py --mode api

# Or with specific host/port
python main.py --mode api --host 0.0.0.0 --port 8000
```

---

#### "CORS errors from browser"

**Problem:** Cross-origin request blocked

**Solution:** Add CORS support in main.py:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
```

---

### System Issues

#### "Out of disk space"

**Problem:** "No space left on device"

**Solution:**
```bash
# Check usage
du -sh data/*
du -sh logs/*

# Clean up old audio
rm -rf data/audio/*

# Clean pip cache
pip cache purge

# Clean system
sudo apt-get clean
sudo apt-get autoclean

# Check what's using space
du -sh /* | sort -rh | head
```

---

#### "Memory leak / slowly increasing RAM"

**Problem:** RAM usage grows over time

**Debugging:**
```python
# Add memory profiling
from memory_profiler import profile

@profile
def process_question(self):
    # ... code ...
```

**Solution:**
```bash
# Monitor memory
watch -n 1 'ps aux | grep main.py | grep -v grep'

# Add restart script
# (Restart app daily)
*/0 6 * * * systemctl restart farmer-assistant
```

---

## Getting Help

1. **Check logs:**
   ```bash
   tail -f farmer_assistant.log
   ```

2. **Enable debug mode:**
   ```bash
   python main.py --verbose
   ```

3. **Test components individually:**
   ```python
   # Test each module
   from src.core.speech_processor import SpeechProcessor
   from src.core.ai_engine import AIEngine
   from src.core.knowledge_base import KnowledgeBase
   ```

4. **Report issues:**
   - Open GitHub issue with:
     - Error message
     - System info (Pi model, OS version)
     - Steps to reproduce
     - Log output

---

## Useful Commands

```bash
# System info
uname -a
cat /etc/os-release
free -h
df -h

# Process info
ps aux | grep main.py
kill <pid>

# Network
ping -c 4 google.com
curl http://localhost:11434/api/tags

# Audio
arecord -l
aplay -l
amixer sset 'Mic' 70%

# I2C/GPIO
i2cdetect -y 1
gpio readall

# Logs
journalctl -u ollama -n 50
dmesg | tail -20
```

---

For additional help, see:
- [Installation Guide](INSTALLATION.md)
- [Architecture](ARCHITECTURE.md)
- [API Documentation](API.md)
- GitHub Issues: https://github.com/ThameemKing/Smart-Agriculture-Assisstant/issues
