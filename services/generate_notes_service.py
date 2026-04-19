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
You are an expert academic note-writer. Convert the YouTube transcript below into clean, 
well-structured Markdown notes suitable for a modern web app (rendered by marked.js).

## Output Format Rules (STRICTLY FOLLOW):
- Use `#` for the main topic title (only once at the top)
- Use `##` for major sections
- Use `###` for subsections
- Use `-` for bullet points (not `*`)
- Use `**bold**` to highlight key terms and important concepts
- Use `> blockquote` for key definitions or important callouts
- Use fenced code blocks (` ``` `) for any code, commands, or technical syntax
- Use Markdown tables for comparisons (with header row and `|---|` separator)
- Use `---` (horizontal rule) to visually separate major sections
- Leave a blank line between every element (paragraphs, lists, headings)
- Do NOT output raw text walls — every piece of information must be structured
- Remove filler words, repetition, promotions, and irrelevant content

## Required Document Structure:
1. `# [Topic Title]` — one clear title
2. `## 📌 Overview` — 2–4 sentence summary of the video
3. `## 🔑 Key Concepts` — the most important ideas as bullet points
4. `## 📖 Detailed Notes` — subsections (`###`) for each major topic
   - Definitions, processes, comparisons (tables), examples
5. `## 💡 Examples` — concrete examples from the video
6. `## ⚡ Quick Revision` — 5–10 bullet points for fast review
7. `## 🚀 Actionable Steps` — only if practical/how-to content exists

---

### Transcript:
{transcription}
                """
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="You are a professional AI-powered academic note writer.",
                temperature=0.3,
                # max_output_tokens=4096,
            ),
        )

        if not response or not response.text:
            return "Error: Empty response from AI"

        return response.text.strip()

    except Exception as e:
        logger.error(f"Gemini API error: {e}", exc_info=True)
        return f"Error generating blog: {str(e)}"
