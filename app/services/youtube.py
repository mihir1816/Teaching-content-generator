# app/services/youtube_transcript.py

import re
from typing import Dict
from langdetect import detect
from langchain_community.document_loaders import YoutubeLoader
from app.services.translate import translate_to_english


def get_transcript_text(url_or_id: str) -> Dict[str, str]:
    """
    Fetch YouTube transcript and translate if needed.
    
    Args:
        url_or_id: YouTube URL or video ID
    
    Returns:
        {
            "video_id": str,
            "language": str,
            "text": str
        }
    """
    # Extract video ID
    match = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})", url_or_id)
    if not match:
        raise ValueError(f"Invalid YouTube URL or ID: {url_or_id}")
    
    video_id = match.group(1)
    
    try:
        # Load transcript
        loader = YoutubeLoader.from_youtube_url(
            url_or_id,
            add_video_info=False,
            language=["en", "hi"],
        )
        docs = loader.load()
        
        if not docs or not docs[0].page_content.strip():
            raise RuntimeError("Transcript is empty or unavailable")
        
        # Combine text
        text = " ".join([doc.page_content for doc in docs])
        
        # Detect language
        try:
            detected_lang = detect(text) if len(text.strip()) >= 50 else "en"
        except Exception:
            detected_lang = "unknown"
        
        # Translate if needed
        final_language = detected_lang
        if detected_lang not in ["en", "unknown"]:
            text = translate_to_english(text, source_lang=detected_lang)
            final_language = "en"
        elif detected_lang == "unknown":
            try:
                text = translate_to_english(text, source_lang="auto")
                final_language = "en"
            except Exception:
                pass
        
        return {
            "video_id": video_id,
            "language": final_language,
            "text": text.strip(),
        }

    except Exception as e:
        raise RuntimeError(f"Failed to fetch transcript: {e}") from e