# Vocal Separator FastAPI Server

A FastAPI server for high-quality vocal separation using [Demucs](https://github.com/facebookresearch/demucs). Upload an audio file and receive separated vocals and background tracks via a simple API.

---

## Features
- 🎤 **Vocal/Instrument Separation**: Extract vocals (or other stems) from music tracks using Demucs.
- 🚀 **FastAPI-based**: Simple, production-ready HTTP API.
- 🐳 **Docker Support**: Easy deployment with Docker.
- 🔥 **GPU Acceleration**: Uses CUDA if available.

---

## Running on Lightning Studio (Recommended for Free GPU)

[Lightning Studio](https://lightning.ai/studio) is a free cloud platform that provides instant access to GPUs for ML and audio projects. You can run this server on Lightning Studio for free GPU acceleration, no setup required!

**Steps:**
1. **Sign up and launch a workspace:**
   - Go to [lightning.ai/studio](https://lightning.ai/studio) and sign in with your GitHub or email.
   - Start a new workspace with GPU enabled (choose a template or blank workspace).
2. **Clone this repository:**
   ```sh
   git clone <your-repo-url>
   cd vocal-separator
   ```
3. **(Option 1) Run with Docker:**
   ```sh
   docker build -t vocal-separator .
   docker run -p 8000:8000 vocal-separator
   ```
   _or_
   **(Option 2) Run with Python:**
   ```sh
   python -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install --user -U demucs
   python server.py
   ```
4. **Access the server:**
   - Use the Lightning Studio web interface to open the forwarded port (usually 8000).
   - Test with `/health` or `/predict` as described below.

_**Tip:** Lightning Studio is the easiest way to get free GPU for this project!_

---

## Requirements
- **Docker** (recommended for deployment)
- Or, for manual install:
  - Ubuntu 22.04+ (or compatible Linux/Windows/Mac)
  - Python 3.8+
  - [ffmpeg](https://ffmpeg.org/)

---

## Setup

### 1. Docker (Recommended)

**Build the Docker image:**
```sh
docker build -t vocal-separator .
```

**Run the server:**
```sh
docker run -p 8000:8000 vocal-separator
```

### 2. Manual (Python Virtual Environment)

**Install system dependencies:**
- Linux: `sudo apt-get update && sudo apt-get install ffmpeg git`
- Windows: [Download ffmpeg](https://ffmpeg.org/download.html) and add to PATH.

**Create and activate a virtual environment:**
```sh
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**Install Python dependencies:**
```sh
pip install --upgrade pip
pip install -r requirements.txt
pip install --user -U demucs  # Ensures latest Demucs
```

**Run the server:**
```sh
python server.py
```

---

## API Usage

### Health Check
- **GET** `/health`  
  _Returns 200 OK if the server is running._

### Predict (Vocal Separation)
- **POST** `/predict`
- **Request Body (JSON):**
  ```json
  {
    "audio_content": "<base64-encoded-audio>",
    "target_stem": "vocals",      // optional, default: "vocals"
    "model": "htdemucs"           // optional, default: "htdemucs"
  }
  ```
- **Response (JSON):**
  ```json
  {
    "vocal_audio": "<base64-encoded-mp3>",
    "bg_audio": "<base64-encoded-mp3>",
    "target_stem": "vocals",
    "content_type": "audio/mp3"
  }
  ```

#### Example (Python)
```python
import requests, base64
with open('input.wav', 'rb') as f:
    audio_b64 = base64.b64encode(f.read()).decode()
resp = requests.post('http://localhost:8000/predict', json={"audio_content": audio_b64})
result = resp.json()
with open('vocals.mp3', 'wb') as f:
    f.write(base64.b64decode(result['vocal_audio']))
```

---

## Notes
- The server runs on port 8000 by default.
- For production, use a reverse proxy (e.g., nginx) and restrict CORS as needed.
- Demucs models and ffmpeg are installed automatically in Docker; for manual install, ensure both are available.
- GPU acceleration is used if available (CUDA required).

---

## Troubleshooting
- **Demucs errors**: Ensure ffmpeg and Demucs are installed and available in your PATH.
- **Large files**: The server may require increased memory for long audio files.
- **Windows**: Use `python` instead of `python3` in commands if needed.

---

## License
See [Demucs license](https://github.com/facebookresearch/demucs) and this repository for details.
