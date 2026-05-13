import logging
import os

from faster_whisper import WhisperModel, BatchedInferencePipeline

logger = logging.getLogger(__name__)

TRANSCRIPTION_FAILED_PREFIX = "Transcription Failed:"

# Singleton Model (Load model once)

model: WhisperModel | None = None
batched_model: BatchedInferencePipeline | None = None


def transcription_succeeded(transcript: str | None) -> bool:
    return bool(transcript) and not transcript.startswith(TRANSCRIPTION_FAILED_PREFIX)


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
    try:
        if not os.path.exists(file_path):
            return f"{TRANSCRIPTION_FAILED_PREFIX} File not found"

        # initialiazed the model
        batchedmodel = getmodel()

        segments, info = batchedmodel.transcribe(
            file_path, batch_size=16, vad_filter=True, beam_size=5
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
        return f"{TRANSCRIPTION_FAILED_PREFIX} {e}"
