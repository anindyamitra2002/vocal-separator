import os
import shutil
import subprocess as sp
import sys
from pathlib import Path

def separate_audio(input_audio_path, output_vocal_path, output_bg_path, 
                  model="htdemucs", mp3_output=True, mp3_bitrate=320, 
                  float32=False, int24=False, verbose=True):
    """
    Separate audio into vocals and background music using Demucs (Windows-compatible).
    
    Args:
        input_audio_path (str): Path to the input audio file
        output_vocal_path (str): Path where the vocal track will be saved
        output_bg_path (str): Path where the background music will be saved
        model (str): Demucs model to use (default: "htdemucs")
        mp3_output (bool): Whether to output as MP3 (default: True)
        mp3_bitrate (int): MP3 bitrate if mp3_output is True (default: 320)
        float32 (bool): Output as float32 WAV files (ignored if mp3_output is True)
        int24 (bool): Output as int24 WAV files (ignored if mp3_output is True)
        verbose (bool): Whether to print progress information
    
    Returns:
        bool: True if separation was successful, False otherwise
    """
    
    # Validate input file
    input_path = Path(input_audio_path)
    if not input_path.exists():
        print(f"Error: Input file {input_audio_path} does not exist.")
        return False
    
    # Create temporary directory for demucs output
    temp_dir = Path("temp_demucs_output")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    try:
        # Build demucs command
        cmd = ["python3", "-m", "demucs.separate", "-o", str(temp_dir), "-n", model]
        
        if mp3_output:
            cmd += ["--mp3", f"--mp3-bitrate={mp3_bitrate}"]
        if float32:
            cmd += ["--float32"]
        if int24:
            cmd += ["--int24"]
        
        # Add input file to command
        cmd.append(str(input_path))
        
        if verbose:
            print(f"Separating audio file: {input_audio_path}")
            print(f"Command: {' '.join(cmd)}")
            print("Processing... (this may take a while)")
        
        # Run demucs separation - simple version without real-time output
        result = sp.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print("Error: Demucs separation failed.")
            print("STDERR:", result.stderr)
            return False
        
        if verbose:
            print("Demucs processing completed. Locating output files...")
        
        # Find the separated files
        # Demucs creates a folder structure like: temp_dir/model_name/filename/
        model_dir = temp_dir / model
        audio_name = input_path.stem
        separated_dir = model_dir / audio_name
        
        if not separated_dir.exists():
            print(f"Error: Expected output directory {separated_dir} not found.")
            print(f"Available directories in {model_dir}:")
            if model_dir.exists():
                for item in model_dir.iterdir():
                    print(f"  - {item}")
            return False
        
        # Look for vocals and accompaniment files
        extension = "mp3" if mp3_output else "wav"
        vocal_file = separated_dir / f"vocals.{extension}"
        
        # Background could be named "no_vocals", "accompaniment", or "other"
        bg_file = None
        for bg_name in ["no_vocals", "accompaniment", "other"]:
            potential_bg = separated_dir / f"{bg_name}.{extension}"
            if potential_bg.exists():
                bg_file = potential_bg
                break
        
        # If still not found, try to find any file that's not vocals
        if bg_file is None:
            for file in separated_dir.iterdir():
                if file.suffix.lower() in ['.mp3', '.wav'] and 'vocals' not in file.stem:
                    bg_file = file
                    break
        
        if verbose:
            print(f"Files found in {separated_dir}:")
            for file in separated_dir.iterdir():
                print(f"  - {file.name}")
        
        # Copy files to target locations
        if vocal_file.exists():
            shutil.copy2(vocal_file, output_vocal_path)
            if verbose:
                print(f"Vocal track saved to: {output_vocal_path}")
        else:
            print("Warning: Vocal track not found in output.")
            return False
        
        if bg_file and bg_file.exists():
            shutil.copy2(bg_file, output_bg_path)
            if verbose:
                print(f"Background track saved to: {output_bg_path}")
        else:
            print("Warning: Background track not found in output.")
            return False
        
        if verbose:
            print("Audio separation completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"Error during audio separation: {str(e)}")
        return False
    
    finally:
        # Clean up temporary directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

def separate_audio_two_stems(input_audio_path, output_vocal_path, output_bg_path, 
                           target_stem="vocals", model="htdemucs", mp3_output=True, 
                           mp3_bitrate=320, verbose=True):
    """
    Separate audio into two stems: target stem and everything else (Windows-compatible).
    This is more efficient when you only need vocals vs background.
    
    Args:
        input_audio_path (str): Path to the input audio file
        output_vocal_path (str): Path where the target stem will be saved
        output_bg_path (str): Path where the other stem will be saved
        target_stem (str): The stem to isolate ("vocals", "drums", "bass", "other")
        model (str): Demucs model to use (default: "htdemucs")
        mp3_output (bool): Whether to output as MP3 (default: True)
        mp3_bitrate (int): MP3 bitrate if mp3_output is True (default: 320)
        verbose (bool): Whether to print progress information
    
    Returns:
        bool: True if separation was successful, False otherwise
    """
    
    # Validate input file
    input_path = Path(input_audio_path)
    if not input_path.exists():
        print(f"Error: Input file {input_audio_path} does not exist.")
        return False
    
    # Create temporary directory for demucs output
    temp_dir = Path("temp_demucs_output")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    try:
        # Build demucs command with two-stems option
        cmd = ["python3", "-m", "demucs.separate", "-o", str(temp_dir), "-n", model]
        cmd += [f"--two-stems={target_stem}"]
        
        if mp3_output:
            cmd += ["--mp3", f"--mp3-bitrate={mp3_bitrate}"]
        
        # Add input file to command
        cmd.append(str(input_path))
        
        if verbose:
            print(f"Separating audio file: {input_audio_path}")
            print(f"Target stem: {target_stem}")
            print(f"Command: {' '.join(cmd)}")
            print("Processing... (this may take a while)")
        
        # Run demucs separation - simple version without real-time output
        result = sp.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print("Error: Demucs separation failed.")
            print("STDERR:", result.stderr)
            return False
        
        if verbose:
            print("Demucs processing completed. Locating output files...")
        
        # Find the separated files
        model_dir = temp_dir / model
        audio_name = input_path.stem
        separated_dir = model_dir / audio_name
        
        if not separated_dir.exists():
            print(f"Error: Expected output directory {separated_dir} not found.")
            print(f"Available directories in {model_dir}:")
            if model_dir.exists():
                for item in model_dir.iterdir():
                    print(f"  - {item}")
            return False
        
        # In two-stems mode, we get the target stem and "no_{target_stem}"
        extension = "mp3" if mp3_output else "wav"
        target_file = separated_dir / f"{target_stem}.{extension}"
        other_file = separated_dir / f"no_{target_stem}.{extension}"
        
        if verbose:
            print(f"Files found in {separated_dir}:")
            for file in separated_dir.iterdir():
                print(f"  - {file.name}")
        
        # Copy files to target locations
        if target_file.exists():
            shutil.copy2(target_file, output_vocal_path)
            if verbose:
                print(f"Target stem ({target_stem}) saved to: {output_vocal_path}")
        else:
            print(f"Warning: Target stem ({target_stem}) not found in output.")
            return False
        
        if other_file.exists():
            shutil.copy2(other_file, output_bg_path)
            if verbose:
                print(f"Other stem (no_{target_stem}) saved to: {output_bg_path}")
        else:
            print(f"Warning: Other stem (no_{target_stem}) not found in output.")
            return False
        
        if verbose:
            print("Audio separation completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"Error during audio separation: {str(e)}")
        return False
    
    finally:
        # Clean up temporary directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

# Example usage:
if __name__ == "__main__":
    # Example 1: Two-stems separation (more efficient for vocals vs background)
    success = separate_audio_two_stems(
        input_audio_path="s_jaishakar_audio.mp3",
        output_vocal_path="vocals.mp3",
        output_bg_path="no_vocals.mp3",
        target_stem="vocals",
        model="htdemucs"
    )
    
    # Example 2: Full separation (4 stems)
    # success = separate_audio(
    #     input_audio_path="s_jaishakar_audio.mp3",
    #     output_vocal_path="vocals.mp3",
    #     output_bg_path="background.mp3",
    #     model="htdemucs",
    #     mp3_output=True,
    #     mp3_bitrate=320
    # )
    
    if success:
        print("Separation completed successfully!")
    else:
        print("Separation failed!")