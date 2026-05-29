import logging
from google import genai
from core.config import get_settings
from google.genai import types

logger = logging.getLogger(__name__)

settings = get_settings()

# Initialize client once (singleton style)
gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)


def generate_note_from_transcription(transcription: str) -> str:  # always returns str
    if not transcription or len(transcription.strip()) < 20:
        return "Error: Transcription too short or Invalid"

    try:
        prompt = f"""
You are a professional AI learning assistant.

Convert this YouTube transcript into high-quality, structured revision notes.

Instructions:

• Extract only meaningful insights.
• Remove filler, jokes, repetition, and promotions.
• Organize content into sections with headings.
• Use bullet points.
• Highlight important keywords in bold.
• Convert explanations into:
  - Definitions
  - Step-by-step processes
  - Tables (if comparison discussed)
  - Flowcharts (text format if needed)
• Add examples separately under an “Examples” section.
• Add a “Quick Revision Box” at the end.
• Add “Actionable Steps” if the video is practical.
• Keep output concise but complete.

Output must look clean, like premium AI-generated notes.

You are an expert academic note generator.
Transform the provided content into professional, high-quality smart notes similar to NoteGPT.
Summarize the following content into smart structured notes:

- Use headings and subheadings
- Bullet format only
- Highlight keywords
- Include summary box at end
- Keep concise but comprehensive
- Make it visually clean and revision-friendly

---

### Transcript:
{transcription}
                """
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="You are a professional AI-powered academic note writer.",
                temperature=0.7,
                max_output_tokens=8192,
            ),
        )

        if not response or not response.text:
            return "Error: Empty response from AI"

        return response.text.strip()

    except Exception as e:
        logger.error(f"Gemini API error: {e}", exc_info=True)
        return f"Error generating blog: {str(e)}"
