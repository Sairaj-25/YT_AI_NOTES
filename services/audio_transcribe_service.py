import logging
import os
import tempfile

from faster_whisper import WhisperModel
from pydub import AudioSegment

logger = logging.getLogger(__name__)

# Singleton Model (Load model once)

_model: WhisperModel | None = None

def get_model() -> WhisperModel:
    global _model
    if _model is None:
        _model = WhisperModel(
            "small",
            device="cpu",
            compute_type="int8"
        )
        logger.info("WhisperModel loaded.")
    return _model

def transcribe_audio_whisper(file_path: str) -> str:
    tmp_path: str | None = None

    try:
        if not os.path.exists(file_path):
            return "Transcription Failed: File not found"
        
        #1. Load Audio File
        audio = AudioSegment.from_file(file_path)

        #2. Normalize for Whisper
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

        #3. Convert to temp WAV (required)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            audio.export(tmp.name, format="wav")
            tmp_path = tmp.name

        #4. Transcribe
        model = get_model()
        segments, info = model.transcribe(tmp_path, beam_size=5)

        transcript = " ".join(seg.text for seg in segments).strip()

        logger.info(
            "Transcribed %.1f sec audio -> %d chars",
            info.duration,
            len(transcript),
        )

        return transcript or "No speech detected"
    
    except Exception as e:
        logger.error(f"Transcription error: {e}", exc_info=True)
        return f"Transcription Failed: {e}"
    
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        
