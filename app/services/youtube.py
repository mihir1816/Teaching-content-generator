# import re
# from typing import Optional, List, Dict
# import app.config as cfg
# from app.services.translate import translate_to_english

# try:
#     from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
# except ImportError as e:
#     raise ImportError(
#         "youtube-transcript-api is required. Install it with: "
#         "pip install youtube-transcript-api"
#     ) from e

# YOUTUBE_ID_PATTERN = re.compile(
#     r"""
#     (?:
#         (?:https?://)?                                     # optional scheme
#         (?:www\.)?
#         (?:youtube\.com/(?:watch\?v=|embed/|shorts/)|youtu\.be/)  # host + path patterns
#         ([A-Za-z0-9_-]{11})                                # capture the 11-char video id
#     )
#     |
#     ^([A-Za-z0-9_-]{11})$                                  # OR just the raw 11-char id
#     """,
#     re.VERBOSE,
# )

# def extract_video_id(url_or_id: str) -> str:
#     m = YOUTUBE_ID_PATTERN.search(url_or_id.strip())
#     if not m:
#         raise ValueError(f"Could not parse a valid YouTube video ID from: {url_or_id!r}")
#     vid = m.group(1) or m.group(2)
#     return vid

# def _pick_best_transcript(video_id: str, language_preference: Optional[List[str]] = None):
#     """
#     Try to get transcripts in preferred languages first, then fall back to any.
#     """
#     transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
#     language_preference = language_preference or [cfg.PREFERRED_LANGUAGE]

#     # 1) Manually created in preferred languages
#     for lang in language_preference:
#         try:
#             return transcripts.find_manually_created_transcript([lang])
#         except Exception:
#             pass

#     # 2) Auto-generated in preferred languages
#     for lang in language_preference:
#         try:
#             return transcripts.find_generated_transcript([lang])
#         except Exception:
#             pass

#     # 3) Any manually created
#     try:
#         for tr in transcripts:
#             if not tr.is_generated:
#                 return tr
#     except Exception:
#         pass

#     # 4) Any auto-generated
#     try:
#         for tr in transcripts:
#             if tr.is_generated:
#                 return tr
#     except Exception:
#         pass

#     raise NoTranscriptFound(video_id)

# def _normalize_segments(segments: List[Dict]) -> str:
#     text_parts = [seg.get("text", "") for seg in segments if seg.get("text")]
#     raw = " ".join(text_parts)
#     cleaned = " ".join(raw.split())
#     return cleaned.strip()

# def get_transcript_text(url_or_id: str) -> Dict[str, str]:
#     """
#     - Prefer English transcript.
#     - If English is not available, fetch any transcript and translate to English via LibreTranslate.
#     - Returns: {'video_id': '...', 'language': 'en', 'text': '...'}
#     """
#     video_id = extract_video_id(url_or_id)
#     try:
#         # Try preferred English first
#         tr = _pick_best_transcript(video_id, language_preference=[cfg.PREFERRED_LANGUAGE])
#         segments = tr.fetch()
#         text = _normalize_segments(segments)

#         # If transcript language isn't English, translate it
#         final_language = tr.language_code
#         if (final_language or "").lower() != "en":
#             text = translate_to_english(text, source_lang=final_language)
#             final_language = "en"

#         return {
#             "video_id": video_id,
#             "language": final_language,
#             "text": text,
#         }

#     except TranscriptsDisabled:
#         raise RuntimeError("Transcripts are disabled for this video.")
#     except NoTranscriptFound:
#         # Try: any available language → translate to English
#         try:
#             tr_any = _pick_best_transcript(video_id, language_preference=None)
#             segments = tr_any.fetch()
#             text_any = _normalize_segments(segments)
#             text_en = translate_to_english(text_any, source_lang=tr_any.language_code)
#             return {
#                 "video_id": video_id,
#                 "language": "en",
#                 "text": text_en,
#             }
#         except Exception as e:
#             raise RuntimeError(f"No transcript available in any language: {e}") from e
#     except Exception as e:
#         raise RuntimeError(f"Failed to fetch transcript: {e}") from e

import re
from typing import Optional, List, Dict
import app.config as cfg
from app.services.translate import translate_to_english

try:
    from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
except ImportError as e:
    raise ImportError(
        "youtube-transcript-api is required. Install it with: "
        "pip install youtube-transcript-api"
    ) from e

YOUTUBE_ID_PATTERN = re.compile(
    r"""
    (?:
        (?:https?://)?                                     # optional scheme
        (?:www\.)?
        (?:youtube\.com/(?:watch\?v=|embed/|shorts/)|youtu\.be/)  # host + path patterns
        ([A-Za-z0-9_-]{11})                                # capture the 11-char video id
    )
    |
    ^([A-Za-z0-9_-]{11})$                                  # OR just the raw 11-char id
    """,
    re.VERBOSE,
)

def extract_video_id(url_or_id: str) -> str:
    m = YOUTUBE_ID_PATTERN.search(url_or_id.strip())
    if not m:
        raise ValueError(f"Could not parse a valid YouTube video ID from: {url_or_id!r}")
    vid = m.group(1) or m.group(2)
    return vid

def _pick_best_transcript(video_id: str, language_preference: Optional[List[str]] = None):
    """
    Try to get transcripts in preferred languages first, then fall back to any.
    Uses the correct API method: get_transcripts() or list_transcripts()
    """
    language_preference = language_preference or [cfg.PREFERRED_LANGUAGE]
    
    # Try using list_transcripts() - available in newer versions
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # 1) Manually created in preferred languages
        for lang in language_preference:
            try:
                return transcript_list.find_manually_created_transcript([lang])
            except Exception:
                pass

        # 2) Auto-generated in preferred languages
        for lang in language_preference:
            try:
                return transcript_list.find_generated_transcript([lang])
            except Exception:
                pass

        # 3) Any manually created
        try:
            for tr in transcript_list:
                if not tr.is_generated:
                    return tr
        except Exception:
            pass

        # 4) Any auto-generated
        try:
            for tr in transcript_list:
                if tr.is_generated:
                    return tr
        except Exception:
            pass
            
    except AttributeError:
        # Fallback for older versions that don't have list_transcripts()
        # Try direct fetch with language codes
        for lang in language_preference:
            try:
                segments = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
                # Create a simple object to mimic the transcript structure
                class SimpleTranscript:
                    def __init__(self, segs, lang):
                        self._segments = segs
                        self.language_code = lang
                        self.is_generated = True  # Assume generated if we can't tell
                    
                    def fetch(self):
                        return self._segments
                
                return SimpleTranscript(segments, lang)
            except Exception:
                pass
        
        # Try without language specification
        try:
            segments = YouTubeTranscriptApi.get_transcript(video_id)
            class SimpleTranscript:
                def __init__(self, segs):
                    self._segments = segs
                    self.language_code = "unknown"
                    self.is_generated = True
                
                def fetch(self):
                    return self._segments
            
            return SimpleTranscript(segments)
        except Exception:
            pass

    raise NoTranscriptFound(
        video_id=video_id,
        requested_language_codes=language_preference or [],
        transcript_data={}
    )

def _normalize_segments(segments: List[Dict]) -> str:
    text_parts = [seg.get("text", "") for seg in segments if seg.get("text")]
    raw = " ".join(text_parts)
    cleaned = " ".join(raw.split())
    return cleaned.strip()

def get_transcript_text(url_or_id: str) -> Dict[str, str]:
    """
    - Prefer English transcript.
    - If English is not available, fetch any transcript and translate to English via LibreTranslate.
    - Returns: {'video_id': '...', 'language': 'en', 'text': '...'}
    """
    video_id = extract_video_id(url_or_id)
    try:
        # Try preferred English first
        tr = _pick_best_transcript(video_id, language_preference=[cfg.PREFERRED_LANGUAGE])
        segments = tr.fetch()
        text = _normalize_segments(segments)

        # If transcript language isn't English, translate it
        final_language = getattr(tr, 'language_code', 'unknown')
        if (final_language or "").lower() not in ["en", "unknown"]:
            text = translate_to_english(text, source_lang=final_language)
            final_language = "en"
        elif final_language == "unknown":
            # Try to translate anyway if language is unknown
            try:
                text = translate_to_english(text, source_lang="auto")
                final_language = "en"
            except Exception:
                # If translation fails, keep original
                pass

        return {
            "video_id": video_id,
            "language": final_language,
            "text": text,
        }

    except TranscriptsDisabled:
        raise RuntimeError("Transcripts are disabled for this video.")
    except NoTranscriptFound as e:
        # Try: any available language → translate to English
        try:
            tr_any = _pick_best_transcript(video_id, language_preference=None)
            segments = tr_any.fetch()
            text_any = _normalize_segments(segments)
            lang_code = getattr(tr_any, 'language_code', 'auto')
            text_en = translate_to_english(text_any, source_lang=lang_code)
            return {
                "video_id": video_id,
                "language": "en",
                "text": text_en,
            }
        except NoTranscriptFound:
            raise RuntimeError(f"No transcript available for video: {video_id}")
        except Exception as ex:
            raise RuntimeError(f"No transcript available in any language: {ex}") from ex
    except Exception as e:
        raise RuntimeError(f"Failed to fetch transcript: {e}") from e