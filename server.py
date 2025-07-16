import io
import base64
import tempfile
import shutil
import subprocess as sp
import sys
from pathlib import Path
import litserve as ls
import soundfile as sf


class AudioVocalSeparatorAPI(ls.LitAPI):
    def setup(self, device):
        """Initialize the API - no model loading needed as we use demucs subprocess"""
        print('Audio Vocal Separator API setup complete...')
    
    def decode_request(self, request):
        """Decode the incoming request"""
        return {
            "audio_content": request["audio_content"],
            "target_stem": request.get("target_stem", "vocals"),
            "model": request.get("model", "htdemucs")
        }
    
    def predict(self, inputs):
        """Perform audio separation using demucs"""
        audio_content = inputs["audio_content"]
        target_stem = inputs["target_stem"]
        model = inputs["model"]
        
        # Decode base64 audio content
        audio_data = base64.b64decode(audio_content)
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_input:
            temp_input.write(audio_data)
            temp_input_path = temp_input.name
        
        try:
            # Perform separation using your existing function logic
            vocal_data, bg_data = self._separate_audio_two_stems(
                temp_input_path, target_stem, model
            )
            
            return {
                "vocal_audio": vocal_data,
                "bg_audio": bg_data,
                "target_stem": target_stem
            }
            
        finally:
            # Clean up temp input file
            Path(temp_input_path).unlink(missing_ok=True)
    
    def _separate_audio_two_stems(self, input_audio_path, target_stem="vocals", model="htdemucs"):
        """
        Separate audio into two stems and return audio data as bytes
        """
        # Create temporary directory for demucs output
        temp_dir = Path(tempfile.mkdtemp(prefix="demucs_"))
        
        try:
            # Build demucs command with two-stems option
            cmd = ["python", "-m", "demucs.separate", "-o", str(temp_dir), "-n", model]
            cmd += [f"--two-stems={target_stem}"]
            cmd += ["--mp3", "--mp3-bitrate=320"]  # Always use MP3 for consistency
            cmd.append(input_audio_path)
            
            print(f"Running demucs separation for {target_stem}...")
            
            # Run demucs separation
            result = sp.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Demucs separation failed: {result.stderr}")
            
            # Find the separated files
            model_dir = temp_dir / model
            audio_name = Path(input_audio_path).stem
            separated_dir = model_dir / audio_name
            
            if not separated_dir.exists():
                raise Exception(f"Expected output directory {separated_dir} not found")
            
            # Read the separated audio files
            target_file = separated_dir / f"{target_stem}.mp3"
            other_file = separated_dir / f"no_{target_stem}.mp3"
            
            if not target_file.exists():
                raise Exception(f"Target stem ({target_stem}) not found in output")
            
            if not other_file.exists():
                raise Exception(f"Other stem (no_{target_stem}) not found in output")
            
            # Read audio files as bytes
            with open(target_file, 'rb') as f:
                vocal_data = f.read()
            
            with open(other_file, 'rb') as f:
                bg_data = f.read()
            
            print("Audio separation completed successfully!")
            return vocal_data, bg_data
            
        except Exception as e:
            print(f"Error during audio separation: {str(e)}")
            raise e
        
        finally:
            # Clean up temporary directory
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
    
    def encode_response(self, prediction):
        """Encode the response with base64 audio content"""
        vocal_audio_base64 = base64.b64encode(prediction["vocal_audio"]).decode("utf-8")
        bg_audio_base64 = base64.b64encode(prediction["bg_audio"]).decode("utf-8")
        
        return {
            "vocal_audio": vocal_audio_base64,
            "bg_audio": bg_audio_base64,
            "target_stem": prediction["target_stem"],
            "content_type": "audio/mp3"
        }


if __name__ == "__main__":
    api = AudioVocalSeparatorAPI()
    server = ls.LitServer(api, accelerator='cuda', devices=1)
    server.run(port=8000)