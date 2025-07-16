# Vocal Separator FastAPI Server

This project provides a FastAPI server for vocal separation using Demucs.

## Requirements
- Docker (recommended for deployment)
- Or, for manual install: Ubuntu 22.04+, Python 3.8+, ffmpeg

## Quick Start (Docker)

1. **Build the Docker image:**

   ```sh
   docker build -t vocal-separator .
   ```

2. **Run the server:**

   ```sh
   docker run -p 8000:8000 vocal-separator
   ```

3. **Health check:**

   Visit [http://localhost:8000/health](http://localhost:8000/health) to verify the server is running.

## API Usage
- POST `/predict` with a base64-encoded audio file to receive separated vocals and background.
- See `server.py` for request/response details.

## Notes
- The Dockerfile installs all dependencies, including ffmpeg and Demucs.
- The server runs on port 8000 by default.
- For production, set up a reverse proxy (e.g., nginx) and restrict CORS as needed.
