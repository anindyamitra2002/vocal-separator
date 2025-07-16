import io
import base64
import tempfile
import shutil
import subprocess as sp
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from loguru import logger
logger.add("app.log", rotation="5 MB", level="INFO", enqueue=True, backtrace=True, diagnose=True)

app = FastAPI()

# Allow CORS for all origins (customize for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AudioSeparationRequest(BaseModel):
    audio_content: str  # base64-encoded audio
    target_stem: str = "vocals"
    model: str = "htdemucs"

class AudioSeparationResponse(BaseModel):
    vocal_audio: str  # base64-encoded mp3
    bg_audio: str     # base64-encoded mp3
    target_stem: str
    content_type: str = "audio/mp3"


def separate_audio_two_stems(input_audio_path, target_stem="vocals", model="htdemucs"):
    temp_dir = Path(tempfile.mkdtemp(prefix="demucs_"))
    try:
        cmd = ["python", "-m", "demucs.separate", "-o", str(temp_dir), "-n", model]
        cmd += [f"--two-stems={target_stem}"]
        cmd += ["--mp3", "--mp3-bitrate=320"]
        cmd.append(input_audio_path)
        print(f"Running demucs separation for {target_stem}...")
        result = sp.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Demucs separation failed: {result.stderr}")
        model_dir = temp_dir / model
        audio_name = Path(input_audio_path).stem
        separated_dir = model_dir / audio_name
        if not separated_dir.exists():
            raise Exception(f"Expected output directory {separated_dir} not found")
        target_file = separated_dir / f"{target_stem}.mp3"
        other_file = separated_dir / f"no_{target_stem}.mp3"
        if not target_file.exists():
            raise Exception(f"Target stem ({target_stem}) not found in output")
        if not other_file.exists():
            raise Exception(f"Other stem (no_{target_stem}) not found in output")
        with open(target_file, 'rb') as f:
            vocal_data = f.read()
        with open(other_file, 'rb') as f:
            bg_data = f.read()
        print("Audio separation completed successfully!")
        return vocal_data, bg_data
    except Exception as e:
        print(f"Error during audio separation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

@app.post("/predict", response_model=AudioSeparationResponse)
def separate_audio(request: AudioSeparationRequest):
    logger.info(f"Received request for separation: target_stem={request.target_stem}, model={request.model}")
    audio_data = base64.b64decode(request.audio_content)
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_input:
        temp_input.write(audio_data)
        temp_input_path = temp_input.name
    try:
        logger.info(f"Running demucs separation for {request.target_stem} with model {request.model}")
        vocal_data, bg_data = separate_audio_two_stems(
            temp_input_path, request.target_stem, request.model
        )
        logger.info("Demucs separation completed successfully!")
        vocal_audio_base64 = base64.b64encode(vocal_data).decode("utf-8")
        bg_audio_base64 = base64.b64encode(bg_data).decode("utf-8")
        return AudioSeparationResponse(
            vocal_audio=vocal_audio_base64,
            bg_audio=bg_audio_base64,
            target_stem=request.target_stem,
            content_type="audio/mp3"
        )
    except Exception as e:
        logger.error(f"Error during audio separation: {str(e)}")
        raise
    finally:
        Path(temp_input_path).unlink(missing_ok=True)

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)