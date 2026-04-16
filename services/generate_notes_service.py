import logging
from google import genai
from core.config import get_settings
from google.genai import types

logger = logging.getLogger(__name__)

settings = get_settings()

# Initialize client once (singleton style)
gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)


def generate_note_from_transcription(transcription: str) -> str:
    if not transcription or len(transcription.strip()) < 20:
        return "Error: Transcription too short or Invalid"

    try:
        prompt = f"""
                    You are an expert academic note generator.

                    Convert the following YouTube transcript into high-quality, structured revision notes.

                    ### Instructions:
                    - Extract only meaningful insights
                    - Remove filler, repetition, promotions
                    - Use headings and subheadings
                    - Bullet points only
                    - Highlight important keywords in **bold**
                    - Convert content into:
                      - Definitions
                      - Step-by-step processes
                      - Tables (if comparison)
                      - Flowcharts (text format if needed)
                    - Add:
                      - Examples section
                      - Quick Revision Box
                      - Actionable Steps (if practical)
                    - Keep concise but complete
                    - Make output clean, structured, and revision-friendly

                    ### Transcript:
                    {transcription}
                """
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="You are a professional AI-powered academic note writer.",
                temperature=0.3,
                max_output_tokens=4096,
            ),
        )

        if not response or not response.text:
            return "Error: Empty response from AI"

        return response.text.strip()

    except Exception as e:
        logger.error(f"Gemini API error: {e}", exc_info=True)
        return f"Error generating blog: {str(e)}"
