# REST API Documentation

## Base URL

```
http://localhost:5000
```

## Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Description:** Verify API server is running

**Response:**
```json
{
  "status": "healthy"
}
```

**Example:**
```bash
curl http://localhost:5000/health
```

---

### 2. Process Question

**Endpoint:** `POST /process`

**Description:** Process a farming question and get answer

**Request:**
```json
{
  "question": "My tomato leaves are turning yellow"
}
```

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| question | string | Yes | Farming question to ask |

**Response:**
```json
{
  "question": "My tomato leaves are turning yellow",
  "answer": "Tomato leaves turning yellow...",
  "timestamp": "2024-05-09T10:30:00.000Z"
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| question | string | The processed question |
| answer | string | The generated answer |
| timestamp | string | ISO format timestamp |

**Status Codes:**
| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (missing question) |
| 500 | Server error |

**Examples:**

cURL:
```bash
curl -X POST http://localhost:5000/process \
  -H "Content-Type: application/json" \
  -d '{"question": "How to grow better tomatoes?"}'
```

Python:
```python
import requests

url = "http://localhost:5000/process"
data = {"question": "What fertilizer is good for rice?"}
response = requests.post(url, json=data)
print(response.json())
```

JavaScript:
```javascript
fetch('http://localhost:5000/process', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    question: "How to control pests in cotton?"
  })
})
.then(r => r.json())
.then(data => console.log(data.answer))
```

---

## Error Handling

### Missing Question
```bash
curl -X POST http://localhost:5000/process -H "Content-Type: application/json" -d '{}'
```

Response:
```json
{
  "error": "No question provided"
}
```

---

## Rate Limiting

Currently no rate limiting. For production, implement:

```python
from flask_limiter import Limiter

limiter = Limiter(
    app=app,
    key_func=lambda: request.remote_addr,
    default_limits=["100 per hour"]
)

@limiter.limit("10 per minute")
@app.route('/process', methods=['POST'])
def process():
    # ...
```

---

## CORS Configuration

For cross-origin requests, enable CORS:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
```

---

## Sample Requests & Responses

### Request 1: Disease Diagnosis

**Request:**
```bash
curl -X POST http://localhost:5000/process \
  -H "Content-Type: application/json" \
  -d '{
    "question": "My tomato plants have brown spots on leaves, what should I do?"
  }'
```

**Response:**
```json
{
  "question": "My tomato plants have brown spots on leaves, what should I do?",
  "answer": "Brown spots on tomato leaves could indicate Early Blight or Late Blight. Treatment: Remove affected leaves, ensure good air circulation, apply fungicide (copper or sulfur-based), avoid watering foliage.",
  "timestamp": "2024-05-09T10:30:45.123Z"
}
```

### Request 2: Crop Management

**Request:**
```bash
curl -X POST http://localhost:5000/process \
  -H "Content-Type: application/json" \
  -d '{
    "question": "When is the best time to harvest my rice crop?"
  }'
```

**Response:**
```json
{
  "question": "When is the best time to harvest my rice crop?",
  "answer": "Rice is ready to harvest when 90-95% of grain is hard. This typically occurs 30-35 days after flowering. Moisture should be 14-20%. Look for light straw color. Best to harvest early morning when plants are cool.",
  "timestamp": "2024-05-09T10:31:20.456Z"
}
```

---

## Usage Scenarios

### 1. Mobile App Integration

Mobile apps can call the API:

```javascript
// React Native example
const askFarmer = async (question) => {
  try {
    const response = await fetch('http://192.168.1.100:5000/process', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({question})
    });
    const data = await response.json();
    return data.answer;
  } catch (error) {
    console.error(error);
  }
};
```

### 2. Local Network Access

Run on Pi, access from laptop:
```bash
# On Pi
python main.py --mode api

# From laptop
curl http://<pi-ip>:5000/health
curl -X POST http://<pi-ip>:5000/process \
  -H "Content-Type: application/json" \
  -d '{"question": "..."}'
```

### 3. Batch Processing

```python
import requests

questions = [
    "How to grow tomatoes?",
    "What is good rice fertilizer?",
    "How to control cotton pests?"
]

answers = []
for q in questions:
    response = requests.post(
        'http://localhost:5000/process',
        json={'question': q}
    )
    answers.append(response.json()['answer'])
```

---

## Performance Considerations

### Timeouts

Default timeout: 60 seconds (for AI generation)

Configure:
```python
@app.route('/process', methods=['POST'])
def process(timeout=60):
    # ...
```

### Concurrent Requests

Currently sequential processing. For production:

```python
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=2)

@app.route('/process', methods=['POST'])
def process():
    future = executor.submit(process_question, question)
    return future.result(timeout=60)
```

---

## Deployment Options

### Local Development
```bash
python main.py --mode api
# http://localhost:5000
```

### Production (Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

### With Reverse Proxy (Nginx)
```nginx
server {
    listen 80;
    server_name farmer-assistant.local;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

---

## Debugging & Logging

### Enable Verbose Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check API Status
```bash
# Health check
curl -v http://localhost:5000/health

# Check logs
tail -f farmer_assistant.log
```

---

## Future Enhancements

- [ ] Authentication/API keys
- [ ] Response caching
- [ ] Streaming responses
- [ ] Batch endpoints
- [ ] WebSocket support for real-time updates
- [ ] OpenAPI/Swagger documentation

---

For more information, see [Architecture](ARCHITECTURE.md) and [Installation](INSTALLATION.md).
