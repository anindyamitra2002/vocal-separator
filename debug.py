import sys
import subprocess as sp

def debug_python_env():
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    
    # Check if demucs is installed
    try:
        result = sp.run([sys.executable, "-m", "demucs.separate", "--help"], 
                       capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Demucs is accessible")
        else:
            print("✗ Demucs is not accessible")
            print("Error:", result.stderr)
    except Exception as e:
        print(f"✗ Error checking demucs: {e}")

if __name__ == "__main__":
    debug_python_env()