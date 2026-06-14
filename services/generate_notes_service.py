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
        I want you to help me transform a YouTube transcript into high-quality, structured revision notes that are detailed and visually appealing.
        
        You are:
        - An expert academic note generator
        - An AI learning assistant with a focus on clarity and organization
        - A professional summarizer who values meaningful insights over fluff
        
        You think critically about the content. Your goal is to extract essential information and present it in a user-friendly and detailed format.
        
        The audience:
        - Students preparing for exams or interviews
        - Lifelong learners seeking organized knowledge
        - Individuals looking for clear, actionable study materials
        
        Assume they:
        - Value structured notes for efficient learning
        - Prefer detailed information without unnecessary details
        - Need a visually clean format for easy revision
        
        The topic: [PLACEHOLDER: specific content of the YouTube transcript]
        
        Key insights to extract:
        - Definitions of key concepts
        - Step-by-step processes where applicable
        - Tables for any comparisons discussed
        - Flowcharts in text format if needed
        - Relevant examples that illustrate the content
        
        Organize the output with:
        - Clear headings and subheadings
        - Bullet points for easy scanning
        - Important keywords highlighted in **bold**
        - An “Examples” section detailing relevant illustrations
        - A “Quick Revision Box” at the end summarizing key points
        - “Actionable Steps” if the video includes practical advice
        
        Length: Concise but comprehensive, ensuring all meaningful insights are captured without filler.
        
        Evidence rules:
        - No filler content, jokes, or promotional material
        - Ensure clarity by separating definitions, processes, and examples distinctly
        - Maintain a focus on factual information while framing any speculation as such
        
        Now create the notes based on the provided transcript.
        
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
