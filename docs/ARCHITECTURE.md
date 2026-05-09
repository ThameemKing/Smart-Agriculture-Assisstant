# System Architecture

## Overview

Farmer Assistant is a modular IoT system designed for offline operation on low-power edge devices, specifically Raspberry Pi. The architecture emphasizes privacy, reliability, and minimal latency.

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface                            │
│  (Voice, Button, LCD Display)                               │
└────────────────┬────────────────────────────────────────────┘
                 │
┌─────────────────▼────────────────────────────────────────────┐
│                    Main Application (main.py)               │
│  - Input handling                                           │
│  - Orchestration                                            │
│  - State management                                         │
└──────────┬────────────┬──────────────┬──────────────────────┘
           │            │              │
    ┌──────▼────┐ ┌─────▼─────┐ ┌─────▼──────┐
    │   Speech  │ │     AI    │ │ Knowledge  │
    │Processor  │ │  Engine   │ │   Base     │
    └──────┬────┘ └─────┬─────┘ └─────┬──────┘
           │            │              │
    ┌──────▼────────────▼──────────────▼──────────┐
    │         Core Processing Pipeline            │
    │ Speech→Text | AI→Generation | Search→Match │
    └─────────────┬──────────────────────────────┘
                  │
┌─────────────────▼────────────────────────────────────────────┐
│                  External Services                           │
│  - Ollama API (AI model)                                    │
│  - Whisper (Speech recognition)                            │
│  - espeak (Text-to-speech)                                 │
└─────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Speech Processor (`src/core/speech_processor.py`)

**Purpose:** Handle audio capture and conversion

**Key Functions:**
- `record_audio()` - Capture microphone input
- `speech_to_text()` - Convert audio to text using Whisper
- `text_to_speech()` - Convert text to audio using espeak

**Technology Stack:**
- PyAudio - Audio capture
- Whisper Tiny - Speech recognition (multilingual)
- pyttsx3/espeak - Text-to-speech

**Performance:**
- Recording: ~1s for 10-second window
- STT: ~3-5s per query
- TTS: ~2-5s per answer

### 2. AI Engine (`src/core/ai_engine.py`)

**Purpose:** Generate farming advice using LLM

**Key Functions:**
- `generate_answer()` - Create response using Phi3 model
- `_build_prompt()` - Format prompt with context
- `get_model_info()` - Retrieve model details

**Technology Stack:**
- Ollama - Model serving framework
- Phi3 Mini - 2B parameter LLM
- Request library - HTTP communication

**Model Details:**
```
Model: Phi3 Mini
Parameters: 2B
Quantization: fp16
RAM Usage: ~2GB
Response Time: 10-30s on Pi 4
```

### 3. Knowledge Base (`src/core/knowledge_base.py`)

**Purpose:** Store and search farming information

**Key Functions:**
- `load_knowledge_base()` - Initialize documents
- `search()` - Semantic similarity search using TF-IDF
- `add_document()` - Add new farming advice

**Technology Stack:**
- scikit-learn - TF-IDF vectorization
- NumPy - Vector operations
- JSON - Data storage

**Search Algorithm:**
```
1. Query → TF-IDF vectorization
2. Cosine similarity with all documents
3. Top-K (default 3) results above threshold
4. Combine results → Context for AI
```

### 4. GPIO Interface (`src/hardware/gpio_interface.py`)

**Purpose:** Handle button input from farmer

**Key Functions:**
- `wait_for_button()` - Block until button press
- `cleanup()` - Release GPIO resources

**Hardware Details:**
- GPIO Pin: 17 (BCM)
- Pull-up resistor: 10kΩ recommended
- Debounce time: 200ms (configurable)

### 5. LCD Display (`src/hardware/lcd_display.py`)

**Purpose:** Show system status to user

**Key Functions:**
- `display()` - Show message on LCD
- `clear()` - Clear display
- `cleanup()` - Release I2C resources

**Hardware Details:**
- Type: 16x2 Character LCD I2C
- Address: 0x27 (default), 0x3F (alternative)
- Connection: I2C (pins 2, 3)

### 6. Configuration (`src/utils/config.py`)

**Purpose:** Centralized settings management

**Configuration Sources:**
1. Hardcoded defaults
2. Environment variables (.env)
3. JSON config file (config.json)

**Priority:** JSON file > Environment > Defaults

## Data Flow

### Query Processing Pipeline

```
User Input
    │
    ├─→ [1] Audio Recording (GPIO trigger)
    │         │
    │         └─→ PyAudio captures 10-second window
    │
    ├─→ [2] Speech-to-Text
    │         │
    │         └─→ Whisper converts audio to text
    │
    ├─→ [3] Knowledge Search
    │         │
    │         └─→ TF-IDF finds relevant documents
    │
    ├─→ [4] Prompt Construction
    │         │
    │         └─→ System prompt + context + question
    │
    ├─→ [5] AI Generation (Ollama/Phi3)
    │         │
    │         └─→ LLM generates contextual answer
    │
    └─→ [6] Text-to-Speech
              │
              └─→ espeak outputs audio to speaker
```

**Latency Breakdown (Typical):**
```
Audio Recording:        1000 ms
Speech-to-Text:         3500 ms
Knowledge Search:        100 ms
Prompt Building:         10 ms
AI Generation:          15000 ms
Text-to-Speech:         3000 ms
────────────────────────────────
Total:                 ~22-30 seconds
```

## Database Design

### Knowledge Base Structure

```json
{
  "documents": [
    {
      "id": 1,
      "topic": "Tomato Diseases",
      "content": "Detailed farming advice...",
      "keywords": ["tomato", "disease", "leaf"]
    }
  ]
}
```

**Storage:** 
- Format: JSON (human-readable, easy to edit)
- Location: `data/knowledge_base/farming_knowledge.json`
- Size: ~50KB (scalable to GB with pagination)

**Indexing:**
- Type: TF-IDF vectorization (sklearn)
- Rebuilt on: New documents added
- No persistent index (computed at startup)

## Communication Protocols

### 1. Ollama API
```
POST /api/generate
Request: {
  "model": "phi3",
  "prompt": "...",
  "stream": false
}
Response: {
  "response": "...",
  "done": true
}
```

### 2. Hardware I/O
- GPIO: BCM numbering
- I2C: Address 0x27
- UART: Optional for logging

## Security & Privacy

### Local Processing
- ✅ No cloud APIs required
- ✅ All inference on-device
- ✅ No data leaves the system
- ✅ Works offline/air-gapped

### Data Handling
- Audio files stored temporarily
- Deleted after processing
- No persistent logging of conversations

## Scalability Considerations

### For Production Deployment

1. **Horizontal Scaling:**
   - Multiple Pi units
   - Redis for knowledge base caching
   - Load balancer for API mode

2. **Vertical Scaling:**
   - Upgrade to Pi 5
   - Add USB TPU accelerators
   - Use faster storage (SSD)

3. **Knowledge Base Expansion:**
   - Currently: 5-10 documents
   - Scalable to: 1000+ documents (with pagination)
   - Consider: Vector DB (Pinecone, Qdrant) for large-scale

## Performance Optimization

### Current Bottlenecks
1. AI Generation (60% of latency) → Use TPU
2. Speech-to-Text (15% of latency) → Larger model/GPU
3. TTS (15% of latency) → Offline TTS with NN

### Optimization Path
```
v1.0 (Current)     → 20-30s latency
  ↓
v1.1 (TPU support) → 5-10s latency
  ↓
v2.0 (Jetson Nano) → 2-3s latency
```

## Testing & Validation

### Unit Tests
- Test each component in isolation
- Mock external services
- Verify data formats

### Integration Tests
- End-to-end query processing
- Component interaction
- Error handling

### Performance Tests
- Latency measurement
- Memory profiling
- CPU utilization

## Deployment Modes

### 1. Interactive Mode (Default)
- Hardware button triggers queries
- Real-time response
- For farm usage

### 2. Demo Mode
- Predefined questions
- No hardware required
- For testing/presentation

### 3. API Mode
- REST endpoints
- HTTP-based
- For integration with apps

### 4. Batch Mode (Future)
- Process multiple questions
- Offline storage
- For research

## Failure Handling

### Graceful Degradation
- Ollama down → Return cached answers
- Microphone error → Text input fallback
- LCD unavailable → Console output
- Knowledge base empty → Generic response

### Error Recovery
```python
try:
    answer = ai_engine.generate_answer(question, context)
except OllamaTimeoutError:
    answer = "Please try again"
except MicrophoneError:
    answer = "Use text input"
```

## Future Architecture Enhancements

1. **Semantic Caching:** Cache frequent Q&A
2. **Fine-tuning:** Adapt model to local farming
3. **Multi-agent:** Specialized sub-models
4. **Federated Learning:** Improve with farming community data
5. **Mobile Integration:** Sync with smartphones

---

For implementation details, see individual component files in `src/`.
