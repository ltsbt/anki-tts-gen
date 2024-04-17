import subprocess
import os


def tts_gen(
    output_dir: str,
    model_path: str,
    audio_index: int,
    phrase: str,
):
    """Generate TTS audio file"""
    ps = subprocess.Popen(
        ["echo", phrase],
        stdout=subprocess.PIPE,
    )
    subprocess.check_output(
        [
            "piper-tts",
            "-m",
            model_path,
            "-f",
            f"tts_{audio_index}.wav",
        ],
        cwd=f"{output_dir}{os.sep}audios",
        stdin=ps.stdout,
    )
