"""Create temporary, transcription-ready audio chunks from a meeting source."""

from pathlib import Path
import shutil
import tempfile
from urllib.parse import urlparse

import yt_dlp
from pydub import AudioSegment


YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com", "youtu.be"}


def download_youtube_audio(url: str, output_dir: Path) -> str:
    output_path = str(output_dir / "source.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "wav"}],
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(url, download=True)
    wav_path = output_dir / "source.wav"
    if not wav_path.is_file():
        raise RuntimeError("Audio download completed but did not produce a WAV file.")
    return str(wav_path)


def convert_to_wav(input_path: str, output_dir: Path) -> str:
    """Convert a local audio/video file to mono 16 kHz WAV."""
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)
    output_path = output_dir / "source.wav"
    audio.export(output_path, format="wav")
    return str(output_path)


def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list[str]:
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000
    directory = Path(wav_path).parent
    chunks = []
    for index, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk_path = directory / f"chunk_{index}.wav"
        audio[start : start + chunk_ms].export(chunk_path, format="wav")
        chunks.append(str(chunk_path))
    if not chunks:
        raise ValueError("The input recording contains no audio.")
    return chunks


def process_input(source: str) -> list[str]:
    """Return chunks stored in a dedicated temporary directory."""
    work_dir = Path(tempfile.mkdtemp(prefix="videorag_"))
    try:
        parsed = urlparse(source)
        if parsed.scheme in {"http", "https"}:
            if parsed.hostname not in YOUTUBE_HOSTS:
                raise ValueError("Only YouTube URLs are supported.")
            wav_path = download_youtube_audio(source, work_dir)
        else:
            if not Path(source).is_file():
                raise FileNotFoundError(f"Local input file was not found: {source}")
            wav_path = convert_to_wav(source, work_dir)
        return chunk_audio(wav_path)
    except Exception:
        shutil.rmtree(work_dir, ignore_errors=True)
        raise


def cleanup_audio_files(chunks: list[str]) -> None:
    """Remove only the temporary directory created by ``process_input``."""
    if chunks:
        directory = Path(chunks[0]).parent
        if directory.name.startswith("videorag_"):
            shutil.rmtree(directory, ignore_errors=True)
