import logging
import os
import tempfile

from faster_whisper import WhisperModel, BatchedInferencePipeline
from pydub import AudioSegment

logger = logging.getLogger(__name__)

# Singleton Model (Load model once)

model: WhisperModel | None = None
batched_model: BatchedInferencePipeline | None = None


def getmodel() -> BatchedInferencePipeline:
    global model, batched_model
    if batched_model is None:
        # 1. Load the base model first
        model = WhisperModel(
            model_size_or_path="base",
            device="cpu",
            compute_type="int8",
            cpu_threads=4,
        )

        # 2. Wrap it in the batched pipeline AFTER it is loaded
        batched_model = BatchedInferencePipeline(model=model)

        logger.info("default WhisperModel loaded.")

    return batched_model


def transcribe_audio_whisper(file_path: str) -> str:
    tmp_path: str | None = None

    try:
        if not os.path.exists(file_path):
            return "Transcription Failed: File not found"

        # 1. Load Audio File
        audio = AudioSegment.from_file(file_path)

        # 2. Normalize for Whisper
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

        # 3. Convert to temp WAV (required)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            audio.export(tmp.name, format="wav")
            tmp_path = tmp.name

        # initialiazed the model
        batchedmodel = getmodel()

        # 4. Transcribe

        # Transcribe with batching and VAD enabled
        segments, info = batchedmodel.transcribe(
            tmp_path, batch_size=16, vad_filter=True, beam_size=5
        )

        transcript = " ".join([segment.text for segment in segments])

        logger.info(
            "Transcribed %.1f sec audio -> %d chars",
            info.duration,
            len(transcript),
        )

        return transcript

    except Exception as e:
        logger.error(f"Transcription error: {e}", exc_info=True)
        return f"Transcription Failed: {e}"

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
