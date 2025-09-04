import requests
import os
from urllib.parse import urlparse
from pathlib import Path
import subprocess

def download_url_to_file(url, dest):
    # supports http(s) and file://
    if url.startswith("file://"):
        src = urlparse(url).path
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        Path(dest).write_bytes(Path(src).read_bytes())
        return dest
    r = requests.get(url, stream=True, timeout=30)
    r.raise_for_status()
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, 'wb') as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)
    return dest

def ensure_wav_16khz(src_path, out_path):
    """
    Convert audio to 16kHz mono WAV using ffmpeg (ffmpeg must be installed).
    """
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    cmd = ["ffmpeg", "-y", "-i", src_path, "-ac", "1", "-ar", "16000", out_path]
    subprocess.run(cmd, check=True)
    return out_path
